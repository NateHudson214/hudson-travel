"""All provider interactions are httpx MockTransport; never paid network calls."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import sqlite3
import threading
from uuid import uuid4

import httpx
import pytest

from backend.app.main import app
from backend.app.skills import provider
from backend.app.skills.sessions import open_sessions, SessionConflict
from backend.app.skills.live import LiveStore

NOW = datetime(2026,10,26,tzinfo=timezone.utc).isoformat()
SELECTION = {'reply_id':'explain_available_skill','fact_ids':['no_typing_required']}


def reply(selection=SELECTION):
    return {'status':'completed','output':[{'type':'message','role':'assistant','status':'completed',
            'content':[{'type':'output_text','text':json.dumps(selection)}]}]}


def body(**values):
    return {'conversation_id':str(uuid4()),'request_id':str(uuid4()),'session_id':None,
            'placement':'before','expected_revision':0,'message':'Fictional typing question',
            'history_epoch':0,'allow_live':True,**values}


@pytest.fixture
def live_client(client, tmp_path, monkeypatch):
    monkeypatch.setattr(app.state,'skills_database_path',tmp_path/'skills.sqlite3')
    monkeypatch.setattr(app.state,'skills_live_enabled_provider',lambda:True)
    monkeypatch.setattr(app.state,'openai_key_provider',lambda:'TEST_ONLY_NOT_A_KEY')
    calls=[]
    def handler(request):
        calls.append(json.loads(request.content))
        return httpx.Response(200,json=reply())
    monkeypatch.setattr(app.state,'skills_live_transport_provider',lambda:httpx.MockTransport(handler))
    return client,calls


def post(client,payload,code=200):
    result=client.post('/api/skills/conversations/turns',json=payload)
    assert result.status_code==code,result.text
    return result.json()


def budget(client):
    return client.get('/api/skills/model-status').json()['budget']


def test_disabled_and_explicit_disclosure_gate_never_dispatch(live_client,monkeypatch):
    c,calls=live_client
    monkeypatch.setattr(app.state,'skills_live_enabled_provider',lambda:False)
    assert post(c,body())['run']['mode']=='mock'
    monkeypatch.setattr(app.state,'skills_live_enabled_provider',lambda:True)
    assert post(c,body(allow_live=False))['run']['mode']=='mock'
    assert calls==[]
    assert budget(c)['reserved_calls']==0


def test_transport_boundary_and_saved_live_provenance(live_client):
    c,calls=live_client;p=body();r=post(c,p)
    assert r['run']['status']=='completed' and r['run']['mode']=='live'
    assert r['messages'][1]['source']=='live-selected-template'
    assert r['messages'][1]['fact_ids']==['no_typing_required']
    request=calls[0]
    assert request['model']=='gpt-6-luna' and request['store'] is False
    assert request['max_output_tokens']==512 and request['service_tier']=='default'
    assert request['text']['format']['strict'] is True
    assert 'tools' not in request
    assert p['conversation_id'] not in json.dumps(request)
    assert provider.PROMPT_HASH and 'untrusted' in request['instructions']
    assert post(c,p)=={**r,'replayed':True}
    assert len(calls)==1
    assert budget(c)['reserved_micro']==100000
    post(c,{**p,'message':'changed'},409)


@pytest.mark.parametrize('status,category',[(401,'authentication'),(403,'authentication'),(429,'rate_limit'),(500,'provider_http')])
def test_http_errors_sanitized_and_counted(live_client,monkeypatch,status,category):
    c,_=live_client
    monkeypatch.setattr(app.state,'skills_live_transport_provider',lambda:httpx.MockTransport(lambda r:httpx.Response(status,text='PRIVATE')))
    r=post(c,body())
    assert r['run']['status']=='failed' and r['run']['error_category']==category
    assert 'PRIVATE' not in json.dumps(r)
    assert budget(c)['reserved_calls']==1
    with sqlite3.connect(app.state.skills_database_path) as db:
        assert 'PRIVATE' not in '\n'.join(db.iterdump())


@pytest.mark.parametrize('data',[
    reply({'reply_id':'unapproved','fact_ids':[]}),
    reply({'reply_id':'neutral_acknowledgment','fact_ids':['breathing_sequence']}),
    reply({'reply_id':'neutral_acknowledgment','fact_ids':[],'prose':'PRIVATE'}),
    {'status':'incomplete','output':[]},
    {'status':'completed','output':[{'type':'function_call'}]},
])
def test_rejected_provider_output_never_rendered(live_client,monkeypatch,data):
    c,_=live_client
    monkeypatch.setattr(app.state,'skills_live_transport_provider',lambda:httpx.MockTransport(lambda r:httpx.Response(200,json=data)))
    r=post(c,body())
    assert r['run']['error_category']=='response_rejected'
    assert r['messages'][1]['source']=='application-fallback'
    assert budget(c)['reserved_calls']==1


def test_timeout_is_finite_no_retry(live_client,monkeypatch):
    c,_=live_client;calls=[]
    async def slow(request):
        calls.append(request)
        await asyncio.sleep(1)
        return httpx.Response(200,json=reply())
    monkeypatch.setattr(provider,'TIMEOUT_SECONDS',0.03)
    monkeypatch.setattr(app.state,'skills_live_transport_provider',lambda:httpx.MockTransport(slow))
    r=post(c,body())
    assert r['run']['error_category']=='timeout'
    assert len(calls)==1 and budget(c)['reserved_calls']==1


def test_missing_configuration_and_invalid_message_do_not_charge(live_client,monkeypatch):
    c,calls=live_client
    post(c,body(message=' '),422)
    monkeypatch.setattr(app.state,'openai_key_provider',lambda:None)
    post(c,body(),503)
    assert calls==[] and budget(c)['reserved_calls']==0


def test_ten_call_dollar_cap_survives_clear_and_new_connections(live_client,monkeypatch):
    c,calls=live_client
    for _ in range(10): assert post(c,body())['run']['mode']=='live'
    assert budget(c)['reserved_calls']==10 and budget(c)['reserved_micro']==1000000
    assert post(c,body())['run']['mode']=='mock'
    clear=c.request('DELETE','/api/skills/history',json={'request_id':str(uuid4()),'expected_epoch':0,'confirm':True})
    assert clear.status_code==200
    assert post(c,body(history_epoch=1))['run']['mode']=='mock'
    monkeypatch.setattr(app.state,'skills_live_enabled_provider',lambda:False)
    monkeypatch.setattr(app.state,'skills_live_enabled_provider',lambda:True)
    assert budget(c)['reserved_calls']==10 and len(calls)==10
    with sqlite3.connect(app.state.skills_database_path) as db:
        assert db.execute('PRAGMA foreign_key_check').fetchall()==[]
        assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'


def test_pending_duplicate_cancel_and_late_result_are_atomic(live_client,monkeypatch):
    c,_=live_client;entered=threading.Event();release=threading.Event();calls=[]
    async def blocking(request):
        calls.append(request);entered.set()
        while not release.is_set(): await asyncio.sleep(0.005)
        return httpx.Response(200,json=reply())
    monkeypatch.setattr(app.state,'skills_live_transport_provider',lambda:httpx.MockTransport(blocking))
    p=body()
    with ThreadPoolExecutor(max_workers=1) as pool:
        running=pool.submit(post,c,p)
        assert entered.wait(2)
        pending=post(c,p)
        assert pending['run']['status']=='pending'
        assert c.get(f"/api/skills/runs/{p['request_id']}?history_epoch=0").json()['run']['status']=='pending'
        post(c,body(conversation_id=p['conversation_id'],expected_revision=1),409)
        # This independent write proves no SQLite write lock spans the request.
        assert c.post('/api/skills/sessions',json={'session_id':str(uuid4())}).status_code==201
        cancelled=c.post(f"/api/skills/runs/{p['request_id']}/cancel",json={'history_epoch':0})
        assert cancelled.json()['run']['status']=='cancelled'
        release.set();result=running.result(3)
    assert result['run']['status']=='cancelled' and len(calls)==1
    assert budget(c)['reserved_calls']==1
    assert len(c.get('/api/skills/conversations/'+p['conversation_id']).json()['messages'])==2


def test_history_clear_during_dispatch_never_recreates_records(live_client,monkeypatch):
    c,_=live_client;entered=threading.Event();release=threading.Event()
    async def blocking(request):
        entered.set()
        while not release.is_set(): await asyncio.sleep(0.005)
        return httpx.Response(200,json=reply())
    monkeypatch.setattr(app.state,'skills_live_transport_provider',lambda:httpx.MockTransport(blocking))
    p=body()
    with ThreadPoolExecutor(max_workers=1) as pool:
        running=pool.submit(lambda:c.post('/api/skills/conversations/turns',json=p))
        assert entered.wait(2)
        assert c.request('DELETE','/api/skills/history',json={'request_id':str(uuid4()),'expected_epoch':0,'confirm':True}).status_code==200
        release.set();assert running.result(3).status_code==409
    post(c,p,409)
    assert c.get('/api/skills/conversations').json()['conversations']==[]
    assert budget(c)['reserved_calls']==1


def test_cancel_before_send_and_restart_recovery_do_not_redispatch(live_client):
    c,calls=live_client;p=body()
    assert c.post(f"/api/skills/runs/{p['request_id']}/cancel",json={'history_epoch':0}).status_code==200
    post(c,p,409)
    assert calls==[] and budget(c)['reserved_calls']==0
    with open_sessions(app.state.skills_database_path,app.state.database_path) as store:
        p=body();pending,context=LiveStore(store.connection).prepare(p,NOW)
        assert context and pending['run']['status']=='pending'
        store.connection.execute('UPDATE skills_run_control SET deadline=0');store.connection.commit()
    result=c.get(f"/api/skills/runs/{p['request_id']}?history_epoch=0").json()
    assert result['run']['status']=='failed' and result['run']['error_category']=='interrupted'
    assert post(c,p)['run']['status']=='failed'
    assert calls==[] and budget(c)['reserved_calls']==1


def test_new_process_recovery_and_preference_context(live_client,monkeypatch):
    from backend.app.skills import live
    c,_=live_client
    assert c.post('/api/skills/preferences',json={'request_id':str(uuid4()),'expected_revision':0,'action':'save','display_settings':{'simpler_view':True,'motion_mode':'static'}}).status_code==200
    with open_sessions(app.state.skills_database_path,app.state.database_path) as store:
        p=body();_,context=LiveStore(store.connection).prepare(p,NOW)
        assert context['saved_display']=={'simpler_view':True,'motion_mode':'static'}
    monkeypatch.setattr(live,'BOOT_TIME',live.time.time()+1)
    assert post(c,p)['run']['error_category']=='interrupted'


def test_v4_migration_preserves_mock_records(live_client):
    c,_=live_client;p=body(allow_live=False);before=post(c,p)
    with sqlite3.connect(app.state.skills_database_path) as db:
        db.execute('DROP TABLE skills_run_control');db.execute('DROP TABLE skills_call_budget')
        old=json.loads(db.execute('SELECT payload_json FROM skills_model_runs WHERE request_id=?',(p['request_id'],)).fetchone()[0]);old.pop('allow_live')
        db.execute('UPDATE skills_model_runs SET payload_json=? WHERE request_id=?',(json.dumps(old,sort_keys=True,separators=(',',':')),p['request_id']))
        db.execute('PRAGMA user_version=4');db.execute("UPDATE skills_metadata SET value='4'")
    assert post(c,p)=={**before,'replayed':True}
    assert budget(c)['reserved_calls']==0
    with sqlite3.connect(app.state.skills_database_path) as db:
        assert db.execute('PRAGMA user_version').fetchone()[0]==5


def test_atomic_budget_with_parallel_turns(live_client):
    c,calls=live_client
    with ThreadPoolExecutor(max_workers=6) as pool:
        results=list(pool.map(lambda _:post(c,body()),range(13)))
    assert sum(r['run']['mode']=='live' for r in results)==10
    assert len(calls)==10 and budget(c)['reserved_calls']==10


def test_dollar_limit_independent_of_call_limit(live_client):
    c,calls=live_client;budget(c)
    with sqlite3.connect(app.state.skills_database_path) as db:
        db.execute('UPDATE skills_call_budget SET dollar_limit_micro=100000')
    assert post(c,body())['run']['mode']=='live'
    assert post(c,body())['run']['mode']=='mock'
    assert len(calls)==1


def test_completion_save_failure_never_repeats_dispatch(live_client):
    c,calls=live_client;budget(c)
    with sqlite3.connect(app.state.skills_database_path) as db:
        db.execute("CREATE TRIGGER reject_final BEFORE UPDATE ON skills_model_runs WHEN NEW.status='completed' BEGIN SELECT RAISE(ABORT,'test'); END")
    p=body();post(c,p,503)
    result=post(c,p)
    assert result['run']['status']=='pending' and len(calls)==1
    assert budget(c)['reserved_calls']==1


def test_context_preflight_failure_has_no_records_or_reservation(live_client,monkeypatch):
    c,calls=live_client
    monkeypatch.setattr(provider,'MAX_INPUT_BYTES',100)
    post(c,body(),503)
    assert calls==[] and budget(c)['reserved_calls']==0
    assert c.get('/api/skills/conversations').json()['conversations']==[]


@pytest.mark.parametrize('part',[
    {'type':'refusal','refusal':'PRIVATE'},
    {'type':'output_text','text':'{"reply_id":"neutral_acknowledgment","reply_id":"support_signpost","fact_ids":[]}'},
    {'type':'output_text','text':'prose before {}'},
])
def test_strict_parser_rejects_refusal_duplicate_keys_and_prose(part):
    data=reply();data['output'][0]['content']=[part]
    with pytest.raises(provider.ProviderFailure):provider.parse_response(data)


def test_host_configuration_defaults_to_mock_and_requires_exact_opt_in(monkeypatch,tmp_path):
    from backend.app import config
    monkeypatch.setattr(config,'ENV_FILE',tmp_path/'missing.env')
    monkeypatch.delenv('SKILLS_MODEL_MODE',raising=False)
    assert config.skills_live_enabled() is False
    for value in ['mock','LIVE','true','unknown']:
        monkeypatch.setenv('SKILLS_MODEL_MODE',value)
        assert config.skills_live_enabled() is False
    monkeypatch.setenv('SKILLS_MODEL_MODE','live')
    assert config.skills_live_enabled() is True
