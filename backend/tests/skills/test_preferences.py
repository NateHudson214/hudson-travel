from concurrent.futures import ThreadPoolExecutor
import hashlib
import sqlite3
from uuid import uuid4

import pytest
from backend.app.main import app


@pytest.fixture
def prefs_client(client, tmp_path, monkeypatch):
    monkeypatch.setattr(app.state, 'skills_database_path', tmp_path/'skills.sqlite3')
    def forbidden(*args, **kwargs):
        pytest.fail('Display choices reached a live model provider')
    monkeypatch.setattr(app.state, 'advisor_query_proposer', forbidden)
    monkeypatch.setattr(app.state, 'advisor_answer_generator', forbidden)
    return client


def body(action='save', revision=0, **changes):
    return {'request_id':str(uuid4()), 'expected_revision':revision, 'action':action,
            'display_settings':{'simpler_view':True,'motion_mode':'static'} if action=='save' else None,
            **changes}


def read(client):
    r=client.get('/api/skills/preferences')
    assert r.status_code==200, r.text
    return r.json()['preferences']


def post(client, payload, code=200):
    r=client.post('/api/skills/preferences',json=payload)
    assert r.status_code==code, r.text
    return r.json()


def test_default_save_reload_and_reset_are_explicit_and_leave_history_alone(prefs_client, database_path):
    travel_hash=hashlib.sha256(database_path.read_bytes()).hexdigest()
    assert read(prefs_client)=={'revision':0,'updated_at':None,'last_setup':None}
    sid=str(uuid4())
    prefs_client.post('/api/skills/sessions',json={'session_id':sid,'display_settings':{'motion_mode':'gentle'}})
    cid=str(uuid4())
    prefs_client.post('/api/skills/conversations/turns',json={
        'conversation_id':cid,'request_id':str(uuid4()),'placement':'before','expected_revision':0,'message':'Fictional setup question'})
    # Starting a session or receiving a mock reply never saves a preference.
    assert read(prefs_client)['last_setup'] is None
    session=prefs_client.get('/api/skills/sessions/'+sid).json()
    chat=prefs_client.get('/api/skills/conversations/'+cid).json()
    payload=body()
    saved=post(prefs_client,payload)
    assert saved['preferences']['last_setup']==payload['display_settings']
    assert read(prefs_client)==saved['preferences']
    assert post(prefs_client,payload)=={**saved,'replayed':True}
    cleared=post(prefs_client,body('reset',1))
    assert cleared['preferences']['last_setup'] is None
    assert cleared['preferences']['revision']==2
    assert read(prefs_client)==cleared['preferences']
    assert prefs_client.get('/api/skills/sessions/'+sid).json()==session
    assert prefs_client.get('/api/skills/conversations/'+cid).json()==chat
    assert hashlib.sha256(database_path.read_bytes()).hexdigest()==travel_hash
    # Old retries cannot resurrect a setup after reset, even after reopening.
    post(prefs_client,payload,409)
    with sqlite3.connect(app.state.skills_database_path) as c:
        assert c.execute('select count(*) from skills_preferences').fetchone()[0]==1


@pytest.mark.parametrize('changes',[
    {'action':'start'}, {'request_id':'bad'}, {'expected_revision':True},
    {'expected_revision':-1}, {'display_settings':None},
    {'display_settings':{'simpler_view':'yes'}},
    {'display_settings':{'motion_mode':'flash'}},
    {'display_settings':{'motion_mode':'static','timer':100}},
    {'mode':'live'}, {'action':'reset','display_settings':{'motion_mode':'static'}},
])
def test_strict_choices_cannot_change_timing_or_enable_live_mode(prefs_client,changes):
    post(prefs_client,body(**changes),422)
    assert read(prefs_client)['revision']==0


def test_stale_tabs_and_changed_latest_request_are_rejected(prefs_client):
    payload=body();post(prefs_client,payload)
    post(prefs_client,{**payload,'display_settings':{'simpler_view':False,'motion_mode':'system'}},409)
    post(prefs_client,body('reset',0),409)
    assert read(prefs_client)['last_setup']==payload['display_settings']


def test_concurrent_save_reset_has_one_winner_and_exact_retry(prefs_client):
    read(prefs_client)
    requests=[body(),body('reset')]
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses=list(pool.map(lambda payload:prefs_client.post('/api/skills/preferences',json=payload),requests))
    assert sorted(r.status_code for r in responses)==[200,409]
    winner=next(i for i,r in enumerate(responses) if r.status_code==200)
    assert post(prefs_client,requests[winner])['replayed']
    assert read(prefs_client)['revision']==1


def test_failed_reset_rolls_back_and_travel_remains_available(prefs_client):
    post(prefs_client,body())
    with sqlite3.connect(app.state.skills_database_path) as c:
        c.execute("CREATE TRIGGER reject_preferences BEFORE UPDATE ON skills_preferences BEGIN SELECT RAISE(ABORT,'private error'); END")
    result=post(prefs_client,body('reset',1),503)
    assert 'private error' not in str(result)
    assert read(prefs_client)['revision']==1
    assert read(prefs_client)['last_setup']['motion_mode']=='static'
    assert prefs_client.get('/api/trips?hotel_name=Harbor%20Lantern%20Hotel').status_code==200


def test_v2_migration_keeps_existing_conversation_and_session(prefs_client):
    sid=str(uuid4());prefs_client.post('/api/skills/sessions',json={'session_id':sid})
    payload={'conversation_id':str(uuid4()),'request_id':str(uuid4()),'expected_revision':0,'placement':'before','message':'Fictional prior conversation'}
    before=prefs_client.post('/api/skills/conversations/turns',json=payload).json()
    session=prefs_client.get('/api/skills/sessions/'+sid).json()
    with sqlite3.connect(app.state.skills_database_path) as c:
        c.execute('DROP TABLE skills_run_control')
        c.execute('DROP TABLE skills_call_budget')
        c.execute('DROP TABLE skills_history_state')
        c.execute('DROP TABLE skills_preferences')
        c.execute('PRAGMA user_version=2')
        c.execute("UPDATE skills_metadata SET value='2'")
    assert read(prefs_client)['last_setup'] is None
    assert prefs_client.get('/api/skills/sessions/'+sid).json()==session
    assert prefs_client.get('/api/skills/conversations/'+payload['conversation_id']).json()['messages']==before['messages']
    assert prefs_client.post('/api/skills/conversations/turns',json=payload).json()['replayed']
    with sqlite3.connect(app.state.skills_database_path) as c:
        assert c.execute('PRAGMA user_version').fetchone()[0]==5
        assert c.execute('PRAGMA foreign_key_check').fetchall()==[]


@pytest.mark.parametrize('table,column', [('skills_messages','content'), ('skills_sessions','active_ms')])
def test_partial_v2_fails_without_migration_writes(prefs_client,table,column):
    read(prefs_client)
    with sqlite3.connect(app.state.skills_database_path) as c:
        c.execute('DROP TABLE skills_run_control')
        c.execute('DROP TABLE skills_call_budget')
        c.execute('DROP TABLE skills_history_state')
        c.execute('DROP TABLE skills_preferences')
        c.execute(f'ALTER TABLE {table} RENAME COLUMN {column} TO broken_column')
        c.execute('PRAGMA user_version=2')
        c.execute("UPDATE skills_metadata SET value='2'")
    assert prefs_client.get('/api/skills/preferences').status_code==503
    with sqlite3.connect(app.state.skills_database_path) as c:
        assert c.execute('PRAGMA user_version').fetchone()[0]==2
        assert c.execute("SELECT count(*) FROM sqlite_schema WHERE name='skills_preferences'").fetchone()[0]==0


def test_missing_preference_record_fails_safely_without_touching_history(prefs_client):
    read(prefs_client)
    with sqlite3.connect(app.state.skills_database_path) as connection:
        connection.execute('DELETE FROM skills_preferences')
    assert prefs_client.get('/api/skills/preferences').status_code == 503
    post(prefs_client, body('reset'), 503)
    assert prefs_client.get('/api/skills/sessions').json()['sessions'] == []
    assert prefs_client.get('/api/trips?hotel_name=Harbor%20Lantern%20Hotel').status_code == 200
