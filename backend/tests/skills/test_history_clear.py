from concurrent.futures import ThreadPoolExecutor
import hashlib
import sqlite3
from threading import Event
from uuid import uuid4

import pytest
from backend.app.main import app
from backend.app.skills.routes import mock_selector


@pytest.fixture
def history_client(client,tmp_path,monkeypatch):
    # Patch State storage directly so pytest undo restores dynamic attributes.
    monkeypatch.setitem(app.state._state,'skills_database_path',tmp_path/'skills.sqlite3')
    def forbidden(*args,**kwargs): pytest.fail('Clear history invoked a live provider')
    monkeypatch.setitem(app.state._state,'advisor_query_proposer',forbidden)
    monkeypatch.setitem(app.state._state,'advisor_answer_generator',forbidden)
    yield client
    app.dependency_overrides.pop(mock_selector,None)


def epoch(client):
    response=client.get('/api/skills/history')
    assert response.status_code==200,response.text
    return response.json()['history_epoch']


def clear_body(generation=0,**changes):
    return {'request_id':str(uuid4()),'expected_epoch':generation,'confirm':True,**changes}


def clear(client,payload=None,code=200):
    r=client.request('DELETE','/api/skills/history',json=payload or clear_body())
    assert r.status_code==code,r.text
    return r.json()


def session_body(generation=0):
    return {'session_id':str(uuid4()),'history_epoch':generation}


def turn_body(generation=0):
    return {'conversation_id':str(uuid4()),'request_id':str(uuid4()),'placement':'before',
            'expected_revision':0,'message':'Fictional clear-history test','history_epoch':generation}


def event_body(generation=0):
    return {'event_id':str(uuid4()),'sequence':1,'expected_revision':0,'kind':'start','history_epoch':generation,
            'snapshot':{'active_ms':0,'pause_ms':0,'support_ms':0,'setup_ms':0,'cycles_completed':0,'phase':'inhale','phase_remaining_ms':4000}}


def populate(client,generation=0):
    s=session_body(generation);t=turn_body(generation);e=event_body(generation)
    assert client.post('/api/skills/sessions',json=s).status_code==201
    assert client.post('/api/skills/sessions/'+s['session_id']+'/events',json=e).status_code==200
    assert client.post('/api/skills/conversations/turns',json=t).status_code==200
    return s,t,e


def test_atomic_clear_preserves_preferences_and_travel_and_blocks_all_old_writes(history_client,database_path):
    c=history_client;s,t,e=populate(c)
    c.post('/api/skills/preferences',json={'request_id':str(uuid4()),'expected_revision':0,'action':'save','display_settings':{'simpler_view':True,'motion_mode':'static'}})
    preferences=c.get('/api/skills/preferences').json()
    travel=hashlib.sha256(database_path.read_bytes()).hexdigest()
    payload=clear_body();result=clear(c,payload)
    assert result['history_epoch']==1
    assert list(result['deleted'].values())==[1,1,1,2,1]
    assert c.get('/api/skills/sessions').json()['sessions']==[]
    assert c.get('/api/skills/conversations').json()['conversations']==[]
    assert c.get('/api/skills/sessions/'+s['session_id']).status_code==404
    assert c.get('/api/skills/conversations/'+t['conversation_id']).status_code==404
    assert c.post('/api/skills/sessions',json=s).status_code==409
    assert c.post('/api/skills/conversations/turns',json=t).status_code==409
    assert c.post('/api/skills/sessions/'+s['session_id']+'/events',json=e).status_code==409
    # Requests never dispatched before deletion still carry the old generation.
    assert c.post('/api/skills/sessions',json=session_body()).status_code==409
    assert c.post('/api/skills/conversations/turns',json=turn_body()).status_code==409
    assert c.get('/api/skills/preferences').json()==preferences
    assert hashlib.sha256(database_path.read_bytes()).hexdigest()==travel
    assert clear(c,payload)=={**result,'replayed':True}
    with sqlite3.connect(app.state.skills_database_path) as db:
        assert db.execute('pragma foreign_key_check').fetchall()==[]
        assert db.execute('select count(*) from skills_model_runs').fetchone()[0]==0


def test_lost_clear_response_retry_does_not_delete_new_history_or_preferences(history_client):
    c=history_client;payload=clear_body();clear(c,payload)
    populate(c,1)
    clear(c,payload)
    assert len(c.get('/api/skills/sessions').json()['sessions'])==1
    assert len(c.get('/api/skills/conversations').json()['conversations'])==1
    clear(c,clear_body(1))
    clear(c,payload,409)
    assert epoch(c)==2
    assert c.post('/api/skills/sessions',json=session_body(1)).status_code==409
    assert c.post('/api/skills/sessions',json=session_body(2)).status_code==201


@pytest.mark.parametrize('changes',[
    {'confirm':False},{'confirm':1},{'confirm':'true'},{'expected_epoch':True},
    {'expected_epoch':-1},{'request_id':'bad'},{'delete_preferences':True},
])
def test_requires_strict_confirmation_without_deleting(history_client,changes):
    populate(history_client)
    clear(history_client,clear_body(**changes),422)
    assert epoch(history_client)==0
    assert len(history_client.get('/api/skills/sessions').json()['sessions'])==1


def test_missing_confirmation_and_stale_or_changed_clear_are_rejected(history_client):
    payload=clear_body();payload.pop('confirm')
    clear(history_client,payload,422)
    payload=clear_body();clear(history_client,payload)
    clear(history_client,{**payload,'expected_epoch':1},409)
    clear(history_client,clear_body(),409)
    assert epoch(history_client)==1


def test_clear_failure_rolls_back_every_table_and_generation(history_client):
    populate(history_client)
    with sqlite3.connect(app.state.skills_database_path) as db:
        db.execute("CREATE TRIGGER block_session_delete BEFORE DELETE ON skills_sessions BEGIN SELECT RAISE(ABORT,'PRIVATE'); END")
    result=clear(history_client,code=503)
    assert 'PRIVATE' not in str(result)
    assert epoch(history_client)==0
    assert len(history_client.get('/api/skills/conversations').json()['conversations'])==1
    assert len(history_client.get('/api/skills/sessions').json()['sessions'])==1
    with sqlite3.connect(app.state.skills_database_path) as db:
        assert db.execute('select count(*) from skills_messages').fetchone()[0]==2
        assert db.execute('select count(*) from skills_model_runs').fetchone()[0]==1


def test_concurrent_same_clear_is_idempotent_and_different_clear_is_stale(history_client):
    c=history_client;populate(c);payload=clear_body()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:clear(c,payload),range(2)))
    assert sorted(r['replayed'] for r in results)==[False,True]
    assert epoch(c)==1
    clear(c,clear_body(),409)


def test_in_progress_mock_commit_is_deleted_then_cannot_be_replayed(history_client):
    entered=Event();release=Event()
    def slow(context):
        entered.set();assert release.wait(1)
        return {'reply_id':'neutral_acknowledgment','fact_ids':[]}
    app.dependency_overrides[mock_selector]=lambda:slow
    payload=turn_body();epoch(history_client)
    with ThreadPoolExecutor(max_workers=2) as pool:
        sent=pool.submit(history_client.post,'/api/skills/conversations/turns',json=payload)
        assert entered.wait(1)
        clearing=pool.submit(clear,history_client)
        release.set()
        assert sent.result().status_code==200
        assert clearing.result()['history_epoch']==1
    assert history_client.post('/api/skills/conversations/turns',json=payload).status_code==409
    assert history_client.get('/api/skills/conversations').json()['conversations']==[]


def test_previously_open_connection_cannot_write_after_clear(history_client):
    from backend.app.skills.sessions import open_sessions,SessionConflict
    from backend.app.skills.conversations import ConversationStore
    path=app.state.skills_database_path
    with open_sessions(path,path.parent/'unrelated.sqlite3') as store:
        clear(history_client)
        with pytest.raises(SessionConflict):
            store.create(str(uuid4()),{'simpler_view':False,'motion_mode':'system'},'2026-10-26T00:00:00Z')
        with pytest.raises(SessionConflict):
            ConversationStore(store.connection).turn(turn_body(),'2026-10-26T00:00:00Z')


def test_v3_migration_preserves_records_and_preference_revision(history_client):
    c=history_client;populate(c)
    before=c.get('/api/skills/preferences').json()
    with sqlite3.connect(app.state.skills_database_path) as db:
        db.execute('drop table skills_run_control')
        db.execute('drop table skills_call_budget')
        db.execute('drop table skills_history_state')
        db.execute('pragma user_version=3')
        db.execute("update skills_metadata set value='3'")
    assert epoch(c)==0
    assert c.get('/api/skills/preferences').json()==before
    assert len(c.get('/api/skills/sessions').json()['sessions'])==1
    assert len(c.get('/api/skills/conversations').json()['conversations'])==1
    clear(c)
    assert epoch(c)==1  # Fresh request/connection retains the increment.


def test_missing_generation_state_fails_closed_instead_of_resetting_to_zero(history_client):
    populate(history_client)
    with sqlite3.connect(app.state.skills_database_path) as db:
        db.execute('DELETE FROM skills_history_state')
    assert history_client.get('/api/skills/history').status_code==503
    assert history_client.post('/api/skills/sessions',json=session_body()).status_code==503
    assert history_client.post('/api/skills/conversations/turns',json=turn_body()).status_code==503
    clear(history_client,code=503)
    assert len(history_client.get('/api/skills/conversations').json()['conversations'])==1


def test_pre_generation_retries_survive_migration_only_until_first_clear(history_client):
    import json
    c=history_client;s,t,e=populate(c)
    with sqlite3.connect(app.state.skills_database_path) as db:
        for table,key in [('skills_session_events','event_id'),('skills_model_runs','request_id')]:
            row=db.execute('SELECT '+key+',payload_json FROM '+table).fetchone()
            old=json.loads(row[1]);old.pop('history_epoch')
            db.execute('UPDATE '+table+' SET payload_json=? WHERE '+key+'=?',(json.dumps(old,sort_keys=True,separators=(',',':')),row[0]))
        db.execute('DROP TABLE skills_run_control')
        db.execute('DROP TABLE skills_call_budget')
        db.execute('DROP TABLE skills_history_state')
        db.execute('PRAGMA user_version=3');db.execute("UPDATE skills_metadata SET value='3'")
    assert epoch(c)==0
    assert c.post('/api/skills/sessions/'+s['session_id']+'/events',json=e).json()['replayed']
    assert c.post('/api/skills/conversations/turns',json=t).json()['replayed']
    clear(c)
    assert c.post('/api/skills/sessions/'+s['session_id']+'/events',json=e).status_code==409
    assert c.post('/api/skills/conversations/turns',json=t).status_code==409
