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


def test_portable_model_schema_keeps_strict_local_limits():
    import json
    from pydantic import ValidationError
    from app.models import Requirements
    from app.providers import gemini_schema
    wire=gemini_schema(Requirements)
    assert '$ref' not in json.dumps(wire) and '$defs' not in wire
    assert wire['properties']['requirements']['items']['additionalProperties'] is False
    data={'requirements':[{'id':'r','jd_source_id':'jd','text':'React','original_excerpt':'React','importance':'required','normalized_terms':[]}]}
    Requirements.model_validate(data)
    data['requirements'][0]['text']='x'*501
    with pytest.raises(ValidationError): Requirements.model_validate(data)
    data['requirements']=[]
    with pytest.raises(ValidationError): Requirements.model_validate(data)


def test_portable_schema_preserves_fields_named_like_keywords():
    from pydantic import Field
    from app.models import Strict
    from app.providers import gemini_schema
    class Named(Strict):
        title:str=Field(max_length=10)
        default:str
    assert set(gemini_schema(Named)['properties'])=={'title','default'}


def test_coordinator_generation_schema_limits_action_to_current_choices():
    from types import SimpleNamespace
    provider=GeminiProvider.__new__(GeminiProvider);provider.event=lambda *a,**k:None
    schemas=[]
    def request(body,config):
        schemas.append(config.response_json_schema)
        return SimpleNamespace(text='{"action":"draft","reason":"Render supported evidence with honest gaps."}')
    provider._request=request
    provider.call('coordinator',Decision,{'allowed_actions':['draft']})
    assert schemas[0]['properties']['action']['enum']==['draft']


def test_expected_qualification_cannot_become_unqualified_degree(client):
    from app.artifacts import check_statements
    from app.extraction import eligible_evidence
    run=start(client,prepare(client));store=client.app.state.store;r=store.get(run['id'])
    draft=store.get(r['draft_ids'][-1]);statement=next(s for s in draft['statements'] if 'expected graduation' in s['text'])
    statement['text']=statement['text'].replace(', expected graduation','')
    errors=check_statements(draft,eligible_evidence(store,r['session_id'],r['source_ids']),store.list('source',r['session_id']),r['requirements'])
    assert any(e['category']=='qualification_status' for e in errors)


def test_summary_cannot_borrow_technology_from_other_claims(client):
    from app.artifacts import check_statements
    from app.extraction import eligible_evidence
    run=start(client,prepare(client));store=client.app.state.store;r=store.get(run['id'])
    draft=store.get(r['draft_ids'][-1]);statement=next(s for s in draft['statements'] if 'B.Tech' in s['text'])
    statement['text']+=' Practical React and TypeScript experience.'
    errors=check_statements(draft,eligible_evidence(store,r['session_id'],r['source_ids']),store.list('source',r['session_id']),r['requirements'])
    assert any(e['category']=='uncited_named_fact' for e in errors)


def test_course_provider_requires_its_own_citation():
    from app.artifacts import check_statements
    evidence=[{'id':'completion','claim_id':'c1','source_id':'source','locator':'1','exact_excerpt':'Completed an introductory course.','context_excerpt':'Completed an introductory course.'},
              {'id':'provider','claim_id':'c2','source_id':'source','locator':'2','exact_excerpt':'Provider: Acorn Learning Academy.','context_excerpt':'Provider: Acorn Learning Academy.'}]
    sources=[{'id':'source','role':'candidate','locator_map':[{'locator':e['locator'],'text':e['exact_excerpt']} for e in evidence]}]
    statement={'id':'s','section':'Coursework','text':'Completed an introductory course through Acorn Learning Academy.','evidence_ids':['completion'],'claim_ids':['c1'],'requirement_ids':[]}
    assert any(e['category']=='uncited_named_fact' for e in check_statements({'statements':[statement]},evidence,sources,[]))
    statement.update(evidence_ids=['completion','provider'],claim_ids=['c1','c2'])
    assert check_statements({'statements':[statement]},evidence,sources,[])==[]
