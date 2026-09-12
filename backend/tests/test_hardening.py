import json,time
from datetime import datetime,timezone,timedelta
import pytest
import pymupdf
from app.artifacts import inspect_pdf,check_statements
from app.providers import MockProvider
from app.models import Decision,uid
from app.config import Settings,ROOT
from app.main import create_app
from fastapi.testclient import TestClient
from helpers import prepare,start

def test_actual_pdf_content_loss_rejected(client,tmp_path):
    run=start(client,prepare(client));store=client.app.state.store;r=store.get(run['id']);draft=store.get(r['draft_ids'][-1])
    pdf=pymupdf.open(r['pdf_path']);page=pdf[0];rectangle=page.search_for(draft['header']['name'])[0];page.add_redact_annot(rectangle);page.apply_redactions()
    target=tmp_path/'missing-content.pdf';pdf.save(target);pdf.close()
    check=inspect_pdf(target,draft);assert not check['passed'];assert 'pdf_content_mismatch' in check['issues']

def test_expiry_deletes_only_own_session(client):
    client.post('/api/sessions',json={'demo':True});first=client.get('/api/evidence').json()['session'];client.post('/api/demo',json={'scenario':'frontend'})
    store=client.app.state.store;one=store.get(first['id']);one['expires_at']=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat();store.update(one['id'],one)
    client.cookies.clear();client.post('/api/sessions',json={'demo':False});second=client.get('/api/evidence').json()['session']
    assert not store.get(first['id']);assert not (store.directory/first['id']).exists();assert store.get(second['id'])

def test_input_version_and_origin_guards(client):
    payload=prepare(client);payload['expected_input_version']-=1
    assert client.post('/api/runs',json=payload,headers={'Idempotency-Key':'wrong-version'}).status_code==409
    assert client.post('/api/sessions',json={'demo':True},headers={'Origin':'https://evil.example'}).status_code==403

def test_url_failure_really_uses_kb(tmp_path):
    class URLFirst(MockProvider):
        def call(self,task,schema,payload):
            result=super().call(task,schema,payload)
            if task=='research':
                url=next((s for s in payload['sources'] if s['slot']=='official_url'),None)
                if url: result.tool='research_official_urls';result.source_ids=[url['id']]
            return result
    with TestClient(create_app(Settings(_env_file=None,data_dir=tmp_path),provider_factory=URLFirst)) as client:
        payload=prepare(client);client.post('/api/sources',data={'slot':'official_url','text':'https://cedarworks.example/about'})
        data=client.get('/api/evidence').json();payload['source_ids']=[s['id'] for s in data['sources']];payload['expected_input_version']=data['session']['input_version']
        run=start(client,payload);assert run['status']=='completed'
        result=client.get('/api/runs/'+run['id']+'/result').json();assert [r['provenance'] for r in result['research']]==['unavailable_url','supplied_kb']
        assert run['research_calls']==2

@pytest.mark.parametrize('claim',['Mira authored 80 Vitest unit tests.','Campus Room Booker ? January 2025 to April 2025.'])
def test_conflicting_sources_cannot_release(client,claim):
    payload=prepare(client);source=client.post('/api/sources',data={'slot':'evidence','text':claim}).json()['source_id']
    data=client.get('/api/evidence').json()
    for e in data['evidence']:
        if e['source_id']==source: client.post('/api/evidence/decisions',json={'evidence_id':e['id'],'decision':'include'})
    data=client.get('/api/evidence').json();payload['source_ids']=[s['id'] for s in data['sources']];payload['expected_input_version']=data['session']['input_version']
    run=start(client,payload);assert run['status']=='needs_review';assert run['revision_count']==1

def test_hostile_context_is_unclear_not_a_skill(client):
    client.post('/api/sessions',json={'demo':True})
    client.post('/api/sources',data={'slot':'evidence','text':(ROOT/'sample-data/adversarial-input.txt').read_text()})
    evidence=client.get('/api/evidence').json()['evidence']
    credential=[e for e in evidence if 'AWS certification' in e['exact_excerpt']]
    assert credential and all(e['support_status']=='unclear' for e in credential)
