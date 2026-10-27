"""Conversation schema, read-only history, and the deterministic mock path."""
import base64
import hashlib
import json
from uuid import uuid4, UUID

from .replies import approved_context, render_reply, FALLBACK_TEXT, CONTEXT_VERSION
from .sessions import canonical_json, InvalidCursor, SessionConflict, SessionNotFound, TERMINAL

TABLES = {"skills_conversations", "skills_messages", "skills_model_runs"}
SCHEMA = (
    """CREATE TABLE skills_conversations (
        conversation_id TEXT PRIMARY KEY,
        session_id TEXT REFERENCES skills_sessions(session_id) ON DELETE SET NULL,
        placement TEXT NOT NULL CHECK (placement IN ('before','after')),
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
        revision INTEGER NOT NULL CHECK (revision >= 0)
    )""",
    """CREATE TABLE skills_messages (
        message_id TEXT PRIMARY KEY,
        conversation_id TEXT NOT NULL REFERENCES skills_conversations(conversation_id) ON DELETE CASCADE,
        sequence INTEGER NOT NULL CHECK (sequence > 0),
        role TEXT NOT NULL CHECK (role IN ('user','assistant')),
        content TEXT NOT NULL CHECK (length(content) BETWEEN 1 AND 600),
        source TEXT NOT NULL CHECK (source IN ('user','mock-selected-template','live-selected-template','application-fallback')),
        created_at TEXT NOT NULL,
        reply_id TEXT, fact_ids_json TEXT,
        UNIQUE (conversation_id, sequence)
    )""",
    """CREATE TABLE skills_model_runs (
        request_id TEXT PRIMARY KEY,
        conversation_id TEXT NOT NULL REFERENCES skills_conversations(conversation_id) ON DELETE CASCADE,
        user_message_id TEXT NOT NULL REFERENCES skills_messages(message_id) ON DELETE CASCADE,
        payload_json TEXT NOT NULL, response_json TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('pending','cancelled','completed','failed')),
        mode TEXT NOT NULL CHECK (mode IN ('mock','live')), model_id TEXT NOT NULL,
        context_version TEXT NOT NULL, context_hash TEXT NOT NULL,
        error_category TEXT, created_at TEXT NOT NULL
    )""",
    "CREATE INDEX skills_conversation_order ON skills_conversations(created_at DESC, conversation_id DESC)",
)


def fixed_mock(context):
    """Deterministic fixture selection, not a claim of model understanding."""
    if context['placement'] == 'after':
        return {'reply_id': 'neutral_acknowledgment', 'fact_ids': ['static_display_option']}
    return {'reply_id': 'explain_available_skill', 'fact_ids': ['no_typing_required', 'pause_or_stop']}


def message_view(row):
    result = dict(row)
    result['fact_ids'] = json.loads(result.pop('fact_ids_json') or '[]')
    return result


class ConversationStore:
    def __init__(self, connection):
        self.connection = connection

    def get(self, cid):
        row = self.connection.execute('SELECT * FROM skills_conversations WHERE conversation_id=?', (cid,)).fetchone()
        if row is None:
            raise SessionNotFound()
        return dict(row)

    def turn(self, body, now, selector=fixed_mock):
        # The fixture is synchronous and local. A live adapter must use a separate,
        # durable pending/cancelled lifecycle and release locks before network I/O.
        cid = body['conversation_id']
        encoded = canonical_json(body)
        with self.connection:
            self.connection.execute('BEGIN IMMEDIATE')
            from .history import require_epoch
            require_epoch(self.connection, body.get('history_epoch', 0))
            old_run = self.connection.execute('SELECT * FROM skills_model_runs WHERE request_id=?', (body['request_id'],)).fetchone()
            if old_run:
                if canonical_json({'history_epoch': 0, 'allow_live': False, **json.loads(old_run['payload_json'])}) != canonical_json({'history_epoch': 0, 'allow_live': False, **body}):
                    raise SessionConflict('Request ID was already used with different data.')
                return {**json.loads(old_run['response_json']), 'replayed': True}
            if self.connection.execute("SELECT 1 FROM skills_model_runs WHERE conversation_id=? AND status='pending'", (cid,)).fetchone():
                raise SessionConflict('A conversation turn is pending.')
            if self.connection.execute('SELECT 1 FROM skills_run_control WHERE request_id=? AND cancelled=1', (body['request_id'],)).fetchone():
                raise SessionConflict('This turn was cancelled. Choose a new turn.')
            existing = self.connection.execute('SELECT * FROM skills_conversations WHERE conversation_id=?', (cid,)).fetchone()
            session = None
            if body['session_id']:
                session = self.connection.execute('SELECT skill_id,skill_version,status FROM skills_sessions WHERE session_id=?', (body['session_id'],)).fetchone()
                if session is None:
                    raise SessionNotFound()
                if body['placement'] != 'after' or session['status'] not in TERMINAL:
                    raise SessionConflict('Associated conversation requires a finished session.')
            if existing is None:
                if body['expected_revision'] != 0:
                    raise SessionConflict('The conversation is stale. Open saved history.')
                self.connection.execute('INSERT INTO skills_conversations VALUES (?,?,?,?,?,0)', (cid, body['session_id'], body['placement'], now, now))
                revision = 0
            else:
                if (existing['placement'] != body['placement'] or existing['session_id'] != body['session_id'] or existing['revision'] != body['expected_revision']):
                    raise SessionConflict('The conversation is stale or its placement changed. Open saved history.')
                revision = existing['revision']
            history = [dict(row) for row in self.connection.execute(
                'SELECT role,content FROM skills_messages WHERE conversation_id=? ORDER BY sequence DESC LIMIT 6', (cid,)
            )][::-1]
            while sum(len(row['content']) for row in history) > 3000:
                history = history[2:]
            context = {
                'catalog': approved_context(), 'placement': body['placement'],
                'session': dict(session) if session else None,
                'history': history, 'message': body['message'],
            }
            reply_id, facts, category = None, [], None
            try:
                selection = selector(context)
                content = render_reply(selection)
                reply_id, facts = selection['reply_id'], selection['fact_ids']
                status, source = 'completed', 'mock-selected-template'
            except Exception:
                content, status, source, category = FALLBACK_TEXT, 'failed', 'application-fallback', 'mock_reply_rejected'
            user_id = str(uuid4())
            messages = []
            for offset, role, text, origin, rid, ids in [
                (1, 'user', body['message'], 'user', None, []),
                (2, 'assistant', content, source, reply_id, facts),
            ]:
                mid = user_id if role == 'user' else str(uuid4())
                self.connection.execute('INSERT INTO skills_messages VALUES (?,?,?,?,?,?,?,?,?)',
                    (mid,cid,revision+offset,role,text,origin,now,rid,canonical_json(ids)))
                messages.append(message_view(self.connection.execute('SELECT * FROM skills_messages WHERE message_id=?',(mid,)).fetchone()))
            self.connection.execute('UPDATE skills_conversations SET revision=?,updated_at=? WHERE conversation_id=?', (revision+2,now,cid))
            run = {'request_id': body['request_id'], 'status': status, 'mode': 'mock',
                   'model_id': 'local-fixed-fixture-v1', 'context_version': CONTEXT_VERSION,
                   'context_hash': hashlib.sha256(canonical_json(context).encode()).hexdigest(), 'error_category': category}
            response = {'conversation': self.get(cid), 'messages': messages, 'run': run, 'replayed': False}
            self.connection.execute('INSERT INTO skills_model_runs VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                (body['request_id'],cid,user_id,encoded,canonical_json(response),status,'mock',run['model_id'],CONTEXT_VERSION,run['context_hash'],category,now))
            return response

    def detail(self, cid, after=0, limit=50):
        with self.connection:
            self.connection.execute('BEGIN')
            conversation = self.get(cid)
            rows = self.connection.execute('SELECT * FROM skills_messages WHERE conversation_id=? AND sequence>? ORDER BY sequence LIMIT ?', (cid,after,limit+1)).fetchall()
        return {'conversation': conversation, 'messages': [message_view(r) for r in rows[:limit]],
                'next_after_sequence': rows[limit-1]['sequence'] if len(rows)>limit else None}

    def history(self, limit=20, cursor=None):
        params, where = [], ''
        if cursor:
            try:
                value = json.loads(base64.b64decode(cursor, altchars=b'-_', validate=True))
                if type(value) is not list or len(value)!=2 or any(type(v) is not str for v in value):
                    raise ValueError()
                from datetime import datetime
                datetime.fromisoformat(value[0]); UUID(value[1])
                params = value
                where = 'WHERE (created_at,conversation_id) < (?,?)'
            except (ValueError,TypeError,UnicodeError):
                raise InvalidCursor() from None
        rows = self.connection.execute('SELECT * FROM skills_conversations '+where+' ORDER BY created_at DESC,conversation_id DESC LIMIT ?', [*params,limit+1]).fetchall()
        cursor = base64.urlsafe_b64encode(canonical_json([rows[limit-1]['created_at'],rows[limit-1]['conversation_id']]).encode()).decode() if len(rows)>limit else None
        return {'conversations': [dict(r) for r in rows[:limit]], 'next_cursor': cursor}
