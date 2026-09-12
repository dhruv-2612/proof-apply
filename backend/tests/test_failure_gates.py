"""Controlled fault injection. These are not observed spontaneous Gemini failures."""
import time, json, threading
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.config import Settings
from app.providers import MockProvider, ProviderError, GeminiProvider
from app.models import uid, Writing, Decision
from app.artifacts import inspect_pdf, release_gate
from helpers import prepare,start,wait_run

@pytest.mark.parametrize('mutation',['metric40','test80','ownership','certification','company_role','malformed','uncertain'],ids=str)
def test_injected_bad_claim_cannot_release_initial_draft(tmp_path,mutation):
    class FaultProvider(MockProvider):
        def call(self,task,schema,payload):
            result=super().call(task,schema,payload)
            if task=='writer' and not payload['revision']:
                if mutation=='malformed': raise ProviderError('invalid_model_output')
                s=result.statements[0]
                if mutation=='metric40': s.text='Reduced booking time by 40%.'
                if mutation=='test80':
                    s=next(s for s in result.statements if '18' in s.text);s.text=s.text.replace('18','80')
                if mutation=='ownership': s.text='Led a team of three and designed the backend REST API.'
                if mutation=='certification': s.text='AWS-certified cloud engineer.'
                if mutation=='company_role': s.text='Kubernetes expert.';s.evidence_ids=[payload['requirements'][0]['jd_source_id']]
            if task=='reviewer' and mutation=='uncertain':
                for v in result.verdicts: v.status='uncertain';v.reason='Unable to establish source support.'
            return result
    with TestClient(create_app(Settings(_env_file=None,data_dir=tmp_path,checkpoint_backend='memory'),provider_factory=FaultProvider)) as client:
        run=start(client,prepare(client))
        stored=client.app.state.store.get(run['id'])
        if mutation=='malformed': assert run['status']=='blocked';return
        first=client.app.state.store.get(stored['evaluation_ids'][0])
        assert not first['checks']['passed']
        assert run['revision_count']==1
        if mutation=='uncertain': assert run['status']=='needs_review';assert client.get('/api/runs/'+run['id']+'/result').json()['artifacts']==[]
        else:
            assert run['status']=='completed'
            final=client.app.state.store.get(stored['evaluation_ids'][-1]);assert final['checks']['passed']
            assert first['draft_hash']!=final['draft_hash']
            assert first['pdf_hash']!=final['pdf_hash']

def test_illegal_supervisor_finalization_rejected(tmp_path):
    class BadSupervisor(MockProvider):
        def call(self,task,schema,payload):
            if task=='coordinator': return Decision(action='finalize',reason='Skip all checks')
            return super().call(task,schema,payload)
    with TestClient(create_app(Settings(_env_file=None,data_dir=tmp_path),provider_factory=BadSupervisor)) as client:
        run=start(client,prepare(client));assert run['status']=='blocked';assert run['error']['code']=='illegal_coordinator_action'

def test_no_kb_pause_resume_and_duplicate_reply(client):
    payload=prepare(client)
    sources=client.get('/api/evidence').json()['sources'];payload['source_ids']=[s['id'] for s in sources if s['slot']!='company']
    run=start(client,payload);assert run['status']=='awaiting_input'
    reply={'question_id':run['pending_question']['id'],'answer':'Fictional CedarWorks Labs makes scheduling software. Supplied team knowledge.','expected_version':run['version']}
    url='/api/runs/'+run['id']+'/resume';headers={'Idempotency-Key':'same-reply-001'}
    first=client.post(url,json=reply,headers=headers);assert first.status_code==202
    second=client.post(url,json=reply,headers=headers);assert second.status_code==202
    final=wait_run(client,run['id']);assert final['status']=='completed'
    assert final['clarification_count']==1

def test_stop_on_missing_research(client):
    payload=prepare(client);payload['source_ids']=[s['id'] for s in client.get('/api/evidence').json()['sources'] if s['slot']!='company']
    run=start(client,payload)
    client.post('/api/runs/'+run['id']+'/resume',json={'question_id':run['pending_question']['id'],'exclude':True,'expected_version':run['version']},headers={'Idempotency-Key':'stop-reply-001'})
    assert wait_run(client,run['id'])['status']=='blocked'

def test_duplicate_start_and_other_session_download(client):
    payload=prepare(client);run=start(client,payload)
    duplicate=client.post('/api/runs',json=payload,headers={'Idempotency-Key':'test-start-001'})
    assert duplicate.json()['id']==run['id']
    result=client.get('/api/runs/'+run['id']+'/result').json();link=result['artifacts'][0]['href']
    client.cookies.clear();client.post('/api/sessions',json={'demo':False})
    assert client.get('/api/runs/'+run['id']).status_code==404
    assert client.get(link).status_code==404

def test_pdf_and_draft_tampering_reject_download(client):
    from pathlib import Path
    payload=prepare(client);run=start(client,payload);store=client.app.state.store;r=store.get(run['id'])
    d=store.get(r['draft_ids'][-1]);e=store.get(r['evaluation_ids'][-1]);artifacts=[store.get(a) for a in r['artifact_ids']]
    assert not release_gate(r,d,e,artifacts,store)
    d['statements'][0]['text']='Tampered after evaluation.'
    assert 'draft_hash_mismatch' in release_gate(r,d,e,artifacts,store)
    pdf=next(a for a in artifacts if a['kind']=='pdf');path=Path(pdf['path']);path.write_bytes(path.read_bytes()+b'tamper')
    assert client.get('/api/artifacts/'+pdf['id']).status_code==409

@pytest.mark.parametrize('always',[False,True])
def test_real_overflow_rerenders_once(tmp_path,always):
    class Overflow(MockProvider):
        def call(self,task,schema,payload):
            result=super().call(task,schema,payload)
            if task=='writer' and (always or not payload['revision']):
                original=max(result.statements,key=lambda s:len(s.text));result.statements=[original.model_copy(update={'id':uid()}) for _ in range(40)]
            return result
    with TestClient(create_app(Settings(_env_file=None,data_dir=tmp_path),provider_factory=Overflow)) as client:
        run=start(client,prepare(client));assert run['revision_count']==1
        assert run['status']==('needs_review' if always else 'completed')
        r=client.app.state.store.get(run['id']);first=client.app.state.store.get(r['evaluation_ids'][0])
        assert 'page_limit' in first['checks']['pdf']['issues']

def test_reviewer_failure_never_becomes_mock_live_pass(tmp_path):
    class Failing(MockProvider):
        def call(self,task,schema,payload):
            if task=='reviewer': raise ProviderError('quota_exhausted')
            return super().call(task,schema,payload)
    with TestClient(create_app(Settings(_env_file=None,data_dir=tmp_path),provider_factory=Failing)) as client:
        run=start(client,prepare(client));assert run['status']=='needs_review'
        assert client.get('/api/runs/'+run['id']+'/result').json()['artifacts']==[]

def test_cancel_while_writer_is_pending(tmp_path):
    entered=threading.Event();released=threading.Event()
    class Slow(MockProvider):
        def call(self,task,schema,payload):
            if task=='writer': entered.set();released.wait(5)
            return super().call(task,schema,payload)
    with TestClient(create_app(Settings(_env_file=None,data_dir=tmp_path),provider_factory=Slow)) as client:
        payload=prepare(client);response=client.post('/api/runs',json=payload,headers={'Idempotency-Key':'cancel-start'})
        id=response.json()['id'];assert entered.wait(5)
        run=client.get('/api/runs/'+id).json();assert client.post('/api/runs/'+id+'/cancel',json={'expected_version':run['version']}).status_code==202
        released.set()
        for _ in range(30):
            if not client.app.state.jobs.busy: break
            time.sleep(.1)
        assert client.get('/api/runs/'+id).json()['status']=='cancelled'
        assert client.get('/api/runs/'+id+'/result').json()['artifacts']==[]

def test_gemini_transient_retry_is_bounded(monkeypatch):
    from types import SimpleNamespace
    class Quota(Exception):
        code=429
        response=SimpleNamespace(headers={'Retry-After':'3'})
    calls=[];sleeps=[]
    def fake(**kwargs): calls.append(1);raise Quota()
    provider=GeminiProvider.__new__(GeminiProvider);provider.run={'model_attempts':0};provider.config=Settings(_env_file=None);provider.save=lambda:None;provider.event=lambda *a,**k:None
    provider.client=SimpleNamespace(models=SimpleNamespace(generate_content=fake))
    monkeypatch.setattr('app.providers.time.sleep',lambda seconds:sleeps.append(seconds))
    with pytest.raises(ProviderError,match='unavailable'): provider._request('fictional',{})
    assert len(calls)==2 and provider.run['model_attempts']==2 and sleeps==[3]

def test_embedded_instructions_not_promoted(client):
    from app.config import ROOT
    payload=prepare(client)
    response=client.post('/api/sources',data={'slot':'evidence'},files={'file':('adversarial.txt',(ROOT/'sample-data/adversarial-input.txt').read_bytes(),'text/plain')})
    assert response.status_code==201
    data=client.get('/api/evidence').json()
    for e in data['evidence']:
        if e['source_id']==response.json()['source_id']:
            client.post('/api/evidence/decisions',json={'evidence_id':e['id'],'decision':'exclude'})
    data=client.get('/api/evidence').json();payload['source_ids']=[s['id'] for s in data['sources']];payload['expected_input_version']=data['session']['input_version']
    run=start(client,payload);result=client.get('/api/runs/'+run['id']+'/result').json()
    assert run['status']=='completed';assert round(result['coverage']['percent'])==92

def test_api_live_disabled_does_not_fallback(client):
    payload=prepare(client);payload['mode']='gemini'
    response=client.post('/api/runs',json=payload,headers={'Idempotency-Key':'live-not-ready'})
    assert response.status_code==503
    assert not client.app.state.store.list('run')
