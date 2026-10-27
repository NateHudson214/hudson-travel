"""Durable live-turn lifecycle. No database transaction spans provider I/O."""
import hashlib
import json
import time
from uuid import uuid4

from .conversations import ConversationStore, message_view
from .history import require_epoch
from .provider import MODEL, PROMPT_HASH, request_body
from .replies import approved_context, render_reply, FALLBACK_TEXT, CONTEXT_VERSION
from .sessions import canonical_json, SessionConflict, SessionNotFound, TERMINAL

BOOT_TIME = time.time()
RESERVATION_MICRO = 100000  # $0.10; never refunded, even if dispatch is interrupted.


class LiveStore(ConversationStore):
    def response(self, rid, replayed=False):
        row = self.connection.execute('SELECT response_json FROM skills_model_runs WHERE request_id=?', (rid,)).fetchone()
        if row is None:
            raise SessionNotFound()
        return {**json.loads(row['response_json']), 'replayed': replayed}

    def recover(self, now):
        # Lazy recovery on the next skills conversation/status request. Never
        # redispatch a request after restart, expiry, or an ambiguous disconnect.
        rows = self.connection.execute('''SELECT r.request_id,c.epoch FROM skills_model_runs r
            JOIN skills_run_control c USING(request_id) WHERE r.status='pending'
            AND (c.deadline<=? OR c.deadline-10<?)''', (time.time(), BOOT_TIME)).fetchall()
        for row in rows:
            self.finish(row['request_id'], row['epoch'], now, category='interrupted')

    def prepare(self, body, now):
        self.recover(now)
        cid, rid = body['conversation_id'], body['request_id']
        encoded = canonical_json(body)
        with self.connection:
            self.connection.execute('BEGIN IMMEDIATE')
            require_epoch(self.connection, body.get('history_epoch', 0))
            old = self.connection.execute('SELECT * FROM skills_model_runs WHERE request_id=?', (rid,)).fetchone()
            if old:
                if old['payload_json'] != encoded:
                    raise SessionConflict('Request ID was already used with different data.')
                return self.response(rid, True), None
            control = self.connection.execute('SELECT * FROM skills_run_control WHERE request_id=?', (rid,)).fetchone()
            if control:
                raise SessionConflict('This turn was cancelled. Choose a new turn.')
            if self.connection.execute("SELECT 1 FROM skills_model_runs WHERE conversation_id=? AND status='pending'", (cid,)).fetchone():
                raise SessionConflict('A conversation turn is pending.')
            existing = self.connection.execute('SELECT * FROM skills_conversations WHERE conversation_id=?', (cid,)).fetchone()
            session = None
            if body['session_id']:
                session = self.connection.execute('SELECT skill_id,skill_version,status FROM skills_sessions WHERE session_id=?', (body['session_id'],)).fetchone()
                if session is None:
                    raise SessionNotFound()
                if body['placement'] != 'after' or session['status'] not in TERMINAL:
                    raise SessionConflict('Associated conversation requires a finished session.')
            revision = body['expected_revision']
            if existing is None:
                if revision != 0:
                    raise SessionConflict('The conversation is stale. Open saved history.')
            elif (existing['revision'] != revision or existing['placement'] != body['placement'] or existing['session_id'] != body['session_id']):
                raise SessionConflict('The conversation is stale or its placement changed. Open saved history.')
            history = [dict(r) for r in self.connection.execute('SELECT role,content FROM skills_messages WHERE conversation_id=? ORDER BY sequence DESC LIMIT 6', (cid,))][::-1]
            while sum(len(r['content']) for r in history) > 3000:
                history = history[2:]
            prefs = self.connection.execute('SELECT has_saved,simpler_view,motion_mode FROM skills_preferences WHERE singleton_id=1').fetchone()
            context = {'catalog': approved_context(), 'placement': body['placement'],
                       'session': dict(session) if session else None, 'history': history,
                       'message': body['message'],
                       'saved_display': {'simpler_view': bool(prefs['simpler_view']), 'motion_mode': prefs['motion_mode']} if prefs['has_saved'] else None}
            request_body(context)  # Bound input before counting a dispatch.
            budget = self.connection.execute('SELECT * FROM skills_call_budget WHERE singleton_id=1').fetchone()
            if budget['reserved_calls'] >= budget['call_limit'] or budget['reserved_micro'] + RESERVATION_MICRO > budget['dollar_limit_micro']:
                return None, None  # Caller switches to its labeled mock path.
            if existing is None:
                self.connection.execute('INSERT INTO skills_conversations VALUES (?,?,?,?,?,0)', (cid,body['session_id'],body['placement'],now,now))
            uid = str(uuid4())
            self.connection.execute('INSERT INTO skills_messages VALUES (?,?,?,?,?,?,?,?,?)', (uid,cid,revision+1,'user',body['message'],'user',now,None,'[]'))
            self.connection.execute('UPDATE skills_conversations SET revision=?,updated_at=? WHERE conversation_id=?', (revision+1,now,cid))
            run = {'request_id': rid, 'status': 'pending', 'mode': 'live', 'model_id': MODEL,
                   'context_version': 'skills-selector-v1/'+CONTEXT_VERSION,
                   'context_hash': hashlib.sha256((PROMPT_HASH+canonical_json(context)).encode()).hexdigest(), 'error_category': None}
            response = {'conversation': self.get(cid), 'messages': [message_view(self.connection.execute('SELECT * FROM skills_messages WHERE message_id=?',(uid,)).fetchone())], 'run': run, 'replayed': False}
            self.connection.execute('INSERT INTO skills_model_runs VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', (rid,cid,uid,encoded,canonical_json(response),'pending','live',MODEL,run['context_version'],run['context_hash'],None,now))
            self.connection.execute('INSERT INTO skills_run_control VALUES (?,?,?,0)', (rid,body.get('history_epoch',0),time.time()+10))
            self.connection.execute('UPDATE skills_call_budget SET reserved_calls=reserved_calls+1,reserved_micro=reserved_micro+? WHERE singleton_id=1', (RESERVATION_MICRO,))
        return response, context

    def finish(self, rid, epoch, now, selection=None, category=None, cancelled=False):
        with self.connection:
            self.connection.execute('BEGIN IMMEDIATE')
            require_epoch(self.connection, epoch)
            row = self.connection.execute('SELECT * FROM skills_model_runs WHERE request_id=?', (rid,)).fetchone()
            if row is None:
                raise SessionConflict('This turn is no longer saved. Reload before continuing.')
            control = self.connection.execute('SELECT * FROM skills_run_control WHERE request_id=?', (rid,)).fetchone()
            if row['status'] != 'pending':
                return self.response(rid, True)
            if control is None or control['epoch'] != epoch:
                raise SessionConflict('The pending turn is no longer valid.')
            if control['deadline'] <= time.time():
                category = 'interrupted'
            rid_reply, facts = None, []
            content, status, source = FALLBACK_TEXT, 'failed', 'application-fallback'
            if cancelled:
                status, category = 'cancelled', 'cancelled'
            elif category is None:
                try:
                    content = render_reply(selection)
                    rid_reply, facts = selection['reply_id'], selection['fact_ids']
                    status, source = 'completed', 'live-selected-template'
                except (ValueError, TypeError):
                    category = 'response_rejected'
            response = json.loads(row['response_json'])
            conversation = self.get(row['conversation_id'])
            mid = str(uuid4())
            self.connection.execute('INSERT INTO skills_messages VALUES (?,?,?,?,?,?,?,?,?)', (mid,row['conversation_id'],conversation['revision']+1,'assistant',content,source,now,rid_reply,canonical_json(facts)))
            self.connection.execute('UPDATE skills_conversations SET revision=revision+1,updated_at=? WHERE conversation_id=?', (now,row['conversation_id']))
            response['conversation'] = self.get(row['conversation_id'])
            response['messages'].append(message_view(self.connection.execute('SELECT * FROM skills_messages WHERE message_id=?',(mid,)).fetchone()))
            response['run'].update(status=status,error_category=category)
            self.connection.execute('UPDATE skills_model_runs SET status=?,error_category=?,response_json=? WHERE request_id=? AND status=\'pending\'', (status,category,canonical_json(response),rid))
            if cancelled:
                self.connection.execute('UPDATE skills_run_control SET cancelled=1 WHERE request_id=?',(rid,))
            return response

    def cancel(self, rid, epoch, now):
        with self.connection:
            self.connection.execute('BEGIN IMMEDIATE')
            require_epoch(self.connection, epoch)
            row = self.connection.execute('SELECT status FROM skills_model_runs WHERE request_id=?',(rid,)).fetchone()
            if row is None:
                self.connection.execute('INSERT OR IGNORE INTO skills_run_control VALUES (?,?,0,1)', (rid,epoch))
                return {'status':'cancelled'}
        if row['status'] == 'pending':
            return self.finish(rid,epoch,now,cancelled=True)
        return self.response(rid,True)
