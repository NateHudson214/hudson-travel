from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import sqlite3
from uuid import uuid4

import pytest

from backend.app.main import app
from backend.app.skills.routes import mock_selector
from backend.app.skills.replies import FALLBACK_TEXT


@pytest.fixture
def chat_client(client, tmp_path, monkeypatch):
    # Patch State storage directly so pytest undo restores dynamic attributes.
    monkeypatch.setitem(app.state._state, 'skills_database_path', tmp_path/'skills.sqlite3')
    monkeypatch.setitem(app.state._state, 'skills_now_provider', lambda: datetime(2026,10,26,tzinfo=timezone.utc))
    def forbidden(*args, **kwargs):
        pytest.fail('Mock conversation invoked a travel provider')
    monkeypatch.setitem(app.state._state, 'advisor_query_proposer', forbidden)
    monkeypatch.setitem(app.state._state, 'advisor_answer_generator', forbidden)
    yield client
    app.dependency_overrides.pop(mock_selector, None)


def body(**values):
    return {'conversation_id':str(uuid4()), 'request_id':str(uuid4()), 'session_id':None,
            'expected_revision':0, 'placement':'before', 'message':'Fictional question about typing.', **values}


def post(client, payload, code=200):
    r=client.post('/api/skills/conversations/turns',json=payload)
    assert r.status_code==code, r.text
    return r.json()


def detail(client,cid,**params):
    r=client.get('/api/skills/conversations/'+cid, params=params)
    assert r.status_code==200, r.text
    return r.json()


def test_mock_turn_normalizes_and_persists_only_reviewed_reply(chat_client, database_path):
    before=hashlib.sha256(database_path.read_bytes()).hexdigest()
    result=post(chat_client,body(message='  Fictional typing question  '))
    assert result['run']['mode']=='mock'
    assert result['run']['model_id']=='local-fixed-fixture-v1'
    assert result['messages'][0]['content']=='Fictional typing question'
    assert result['messages'][1]['reply_id']=='explain_available_skill'
    assert result['messages'][1]['fact_ids']==['no_typing_required','pause_or_stop']
    assert 'No typing is required' in result['messages'][1]['content']
    cid=result['conversation']['conversation_id']
    assert detail(chat_client,cid)['messages']==result['messages']
    assert hashlib.sha256(database_path.read_bytes()).hexdigest()==before
    with sqlite3.connect(app.state.skills_database_path) as c:
        assert c.execute('pragma foreign_key_check').fetchall()==[]
        assert c.execute('select count(*) from skills_model_runs').fetchone()[0]==1


def test_exact_request_retry_returns_original_pair_after_later_turn(chat_client):
    first=body(); original=post(chat_client,first)
    second=post(chat_client,body(conversation_id=first['conversation_id'],expected_revision=2,message='Fictional second turn'))
    replay=post(chat_client,first)
    assert replay=={**original,'replayed':True}
    assert second['conversation']['revision']==4
    assert len(detail(chat_client,first['conversation_id'])['messages'])==4
    post(chat_client,{**first,'message':'changed'},409)
    post(chat_client,body(conversation_id=first['conversation_id']),409)
    post(chat_client,body(conversation_id=first['conversation_id'],expected_revision=4,placement='after'),409)


@pytest.mark.parametrize('changes',[
    {'message':''},{'message':'   '},{'message':'x'*501},{'message':42},
    {'placement':'during'},{'expected_revision':True},{'expected_revision':-1},
    {'mode':'live'},{'reply_id':'untrusted'},{'request_id':'not-id'},
])
def test_rejects_invalid_contract_without_writes(chat_client,changes):
    post(chat_client,body(**changes),422)
    assert chat_client.get('/api/skills/conversations').json()['conversations']==[]


@pytest.mark.parametrize('selection',[
    {'reply_id':'new','fact_ids':[]},
    {'reply_id':'neutral_acknowledgment','fact_ids':[],'content':'unapproved'},
    {'reply_id':'neutral_acknowledgment','fact_ids':['breathing_sequence']},
    None,
])
def test_rejected_mock_is_saved_as_sanitized_fallback(chat_client,selection):
    app.dependency_overrides[mock_selector]=lambda: lambda context: selection
    result=post(chat_client,body())
    assert result['run']['status']=='failed'
    assert result['run']['error_category']=='mock_reply_rejected'
    assert result['messages'][1]['source']=='application-fallback'
    assert result['messages'][1]['content']==FALLBACK_TEXT
    assert result['messages'][1]['reply_id'] is None
    assert result['messages'][1]['fact_ids']==[]


def test_exception_sanitized_and_no_raw_output_persisted(chat_client):
    def fail(context): raise TimeoutError('PRIVATE_RAW_ERROR')
    app.dependency_overrides[mock_selector]=lambda: fail
    result=post(chat_client,body())
    assert 'PRIVATE_RAW_ERROR' not in json.dumps(result)
    with sqlite3.connect(app.state.skills_database_path) as c:
        assert 'PRIVATE_RAW_ERROR' not in '\n'.join(c.iterdump())


def test_context_is_bounded_to_this_conversation_and_has_no_ids(chat_client):
    seen=[]
    def select(context):
        seen.append(context)
        return {'reply_id':'explain_available_skill','fact_ids':['breathing_sequence','pause_or_stop']}
    app.dependency_overrides[mock_selector]=lambda: select
    post(chat_client,body(message='OTHER_CONVERSATION_SECRET'))
    cid=str(uuid4())
    for n in range(7):
        post(chat_client,body(conversation_id=cid,expected_revision=n*2,message='Fictional '+('x'*480)))
    context=seen[-1]
    assert len(context['history'])<=6
    assert sum(len(m['content']) for m in context['history'])<=3000
    assert all(set(m)=={'role','content'} for m in context['history'])
    assert 'OTHER_CONVERSATION_SECRET' not in json.dumps(context)
    assert cid not in json.dumps(context)
    assert 'breathing_sequence' in context['catalog']['facts']


def test_after_association_requires_terminal_session_and_never_changes_it(chat_client):
    sid=str(uuid4())
    chat_client.post('/api/skills/sessions',json={'session_id':sid})
    post(chat_client,body(session_id=sid,placement='after'),409)
    chat_client.post(f'/api/skills/sessions/{sid}/events',json={
        'event_id':str(uuid4()),'sequence':1,'expected_revision':0,'kind':'stop',
        'snapshot':{'active_ms':0,'pause_ms':0,'support_ms':0,'setup_ms':0,'cycles_completed':0,'phase':'inhale','phase_remaining_ms':4000}})
    before=chat_client.get('/api/skills/sessions/'+sid).json()
    result=post(chat_client,body(session_id=sid,placement='after'))
    assert result['conversation']['session_id']==sid
    assert result['messages'][1]['reply_id']=='neutral_acknowledgment'
    assert chat_client.get('/api/skills/sessions/'+sid).json()==before
    post(chat_client,body(session_id=sid,placement='before'),409)
    post(chat_client,body(session_id=str(uuid4()),placement='after'),404)


def test_history_pages_no_text_previews_and_message_page_boundaries(chat_client):
    ids=[]
    for _ in range(3): ids.append(post(chat_client,body())['conversation']['conversation_id'])
    r=chat_client.get('/api/skills/conversations',params={'limit':2}).json()
    assert len(r['conversations'])==2
    assert 'content' not in json.dumps(r)
    other=chat_client.get('/api/skills/conversations',params={'limit':2,'cursor':r['next_cursor']}).json()
    assert {x['conversation_id'] for x in r['conversations']+other['conversations']}==set(ids)
    first=detail(chat_client,ids[0],limit=1)
    second=detail(chat_client,ids[0],limit=1,after_sequence=first['next_after_sequence'])
    assert [first['messages'][0]['role'],second['messages'][0]['role']]==['user','assistant']
    assert second['next_after_sequence'] is None
    assert chat_client.get('/api/skills/conversations?cursor=bad').status_code==400
    assert chat_client.get('/api/skills/conversations?limit=51').status_code==422
    assert chat_client.get('/api/skills/conversations/'+str(uuid4())).status_code==404


def test_concurrent_retry_and_stale_turn_are_atomic(chat_client):
    payload=body()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _: post(chat_client,payload),range(2)))
    assert sorted(r['replayed'] for r in results)==[False,True]
    cid=payload['conversation_id']
    with ThreadPoolExecutor(max_workers=2) as pool:
        codes=list(pool.map(lambda _: chat_client.post('/api/skills/conversations/turns',json=body(conversation_id=cid,expected_revision=2)).status_code, range(2)))
    assert sorted(codes)==[200,409]
    assert len(detail(chat_client,cid)['messages'])==4


def test_insert_failure_rolls_back_pair_and_run(chat_client):
    chat_client.get('/api/skills/conversations')
    with sqlite3.connect(app.state.skills_database_path) as c:
        c.execute("CREATE TRIGGER reject_mock BEFORE INSERT ON skills_model_runs BEGIN SELECT RAISE(ABORT,'test'); END")
    post(chat_client,body(),503)
    with sqlite3.connect(app.state.skills_database_path) as c:
        assert c.execute('select count(*) from skills_messages').fetchone()[0]==0
        assert c.execute('select count(*) from skills_conversations').fetchone()[0]==0


def test_v1_migration_preserves_sessions_and_new_connections_restore_chat(chat_client):
    sid=str(uuid4()); chat_client.post('/api/skills/sessions',json={'session_id':sid})
    before=chat_client.get('/api/skills/sessions/'+sid).json()
    with sqlite3.connect(app.state.skills_database_path) as c:
        for table in ('skills_run_control','skills_call_budget','skills_history_state','skills_preferences','skills_model_runs','skills_messages','skills_conversations'): c.execute('DROP TABLE '+table)
        c.execute('pragma user_version=1'); c.execute("UPDATE skills_metadata SET value='1'")
    result=post(chat_client,body())
    # Requests close connections, then reopen and check the migrated schema.
    assert chat_client.get('/api/skills/sessions/'+sid).json()==before
    assert detail(chat_client,result['conversation']['conversation_id'])['messages']==result['messages']
    with sqlite3.connect(app.state.skills_database_path) as c:
        assert c.execute('pragma user_version').fetchone()[0]==5
        assert c.execute("select value from skills_metadata where key='schema_version'").fetchone()[0]=='5'


def test_request_owned_connection_can_exit_on_another_worker(tmp_path):
    from backend.app.skills.sessions import open_sessions
    context = open_sessions(tmp_path / 'skills.sqlite3', tmp_path / 'travel.sqlite3')
    with ThreadPoolExecutor(max_workers=1) as pool:
        store = pool.submit(context.__enter__).result()
        # FastAPI's sync dependency enter, route and teardown may change workers.
        assert store.history()['sessions'] == []
        context.__exit__(None, None, None)


def test_incomplete_legacy_schema_is_rejected_before_migration(chat_client):
    path = app.state.skills_database_path
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE skills_metadata (key TEXT PRIMARY KEY, value TEXT)")
        connection.execute("INSERT INTO skills_metadata VALUES ('schema_version','1')")
        connection.execute("CREATE TABLE skills_sessions (session_id TEXT, settings_json TEXT, revision INTEGER)")
        connection.execute("CREATE TABLE skills_session_events (event_id TEXT, session_id TEXT, sequence INTEGER, payload_json TEXT)")
        connection.execute('PRAGMA user_version=1')
    post(chat_client, body(), 503)
    with sqlite3.connect(path) as connection:
        assert connection.execute('PRAGMA user_version').fetchone()[0] == 1
        assert len(connection.execute("SELECT name FROM sqlite_schema WHERE type='table'").fetchall()) == 3
