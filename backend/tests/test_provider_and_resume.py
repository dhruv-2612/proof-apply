from types import SimpleNamespace
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.config import Settings
from app.main import create_app
from app.models import Decision
from app.providers import GeminiProvider,ProviderError
from helpers import prepare,start,wait_run

def test_structured_output_schema_repair_is_bounded():
    provider=GeminiProvider.__new__(GeminiProvider);events=[];calls=[]
    provider.event=lambda *a,**k:events.append(a)
    def request(body,config):
        calls.append(config)
        return SimpleNamespace(text='{"unknown":"invalid"}')
    provider._request=request
    with pytest.raises(ProviderError) as error: provider.call('coordinator',Decision,{'allowed_actions':['research']})
    assert error.value.code=='invalid_model_output' and len(calls)==2
    assert all(c.response_json_schema['additionalProperties'] is False for c in calls)

def test_transient_retry_can_recover_without_mode_change(monkeypatch):
    class Quota(Exception):
        code=429
        response=SimpleNamespace(headers={'Retry-After':'2'})
    calls=[]
    def generate(**kwargs):
        calls.append(kwargs)
        if len(calls)==1: raise Quota()
        return SimpleNamespace(text='recovered')
    provider=GeminiProvider.__new__(GeminiProvider);provider.run={'model_attempts':0};provider.config=Settings(_env_file=None);provider.save=lambda:None;provider.event=lambda *a,**k:None
    provider.client=SimpleNamespace(models=SimpleNamespace(generate_content=generate));monkeypatch.setattr('app.providers.time.sleep',lambda _:None)
    assert provider._request('fictional',{}).text=='recovered'
    assert provider.mode=='gemini' and provider.run['model_attempts']==2

def test_sqlite_clarification_survives_local_restart(tmp_path):
    config=Settings(_env_file=None,data_dir=tmp_path,checkpoint_backend='sqlite')
    with TestClient(create_app(config)) as first:
        payload=prepare(first);payload['source_ids']=[s['id'] for s in first.get('/api/evidence').json()['sources'] if s['slot']!='company']
        run=start(first,payload);assert run['status']=='awaiting_input';cookie=first.cookies.get('proofapply_session')
    with TestClient(create_app(config)) as second:
        second.cookies.set('proofapply_session',cookie)
        restored=second.get('/api/runs/'+run['id']).json();assert restored['status']=='awaiting_input'
        response=second.post('/api/runs/'+run['id']+'/resume',json={'question_id':restored['pending_question']['id'],'answer':'Fictional supplied KB: CedarWorks makes booking software with accessible forms.','expected_version':restored['version']},headers={'Idempotency-Key':'restart-reply'})
        assert response.status_code==202
        assert wait_run(second,run['id'])['status']=='completed'

def test_single_letter_degree_abbreviation_is_preserved(client):
    client.post('/api/sessions',json={'demo':False})
    client.post('/api/sources',data={'slot':'resume','text':'EDUCATION\nB. Tech in Information Technology at Example Institute.'})
    evidence=client.get('/api/evidence').json()['evidence']
    assert len(evidence)==1 and evidence[0]['exact_excerpt'].startswith('B. Tech')


def test_https_origin_works_behind_production_proxy(tmp_path):
    config=Settings(_env_file=None,data_dir=tmp_path,app_env='production',checkpoint_backend='memory')
    with TestClient(create_app(config)) as client:
        response=client.post('/api/sessions',json={'demo':True},headers={'Origin':'https://testserver'})
        assert response.status_code==201
        assert 'Secure' in response.headers['set-cookie']
        rejected=client.post('/api/sessions',json={'demo':True},headers={'Origin':'https://another.example'})
        assert rejected.status_code==403
