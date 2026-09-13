"""Explicit live evaluation with one controlled bad claim; never a normal demo mode."""
import argparse, json, sys, time
from pathlib import Path
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from app.config import settings, ROOT
from app.main import create_app
from app.providers import GeminiProvider

class ControlledFeedback(GeminiProvider):
    def call(self,task,schema,payload):
        result=super().call(task,schema,payload)
        if task=='writer' and not payload.get('revision'):
            statement=next((s for s in result.statements if s.section=='Projects'),result.statements[0])
            statement.text += ' Reduced booking time by 40%.'
            self.event('evaluation_harness','controlled_fault','Controlled evaluation only: appended unsupported 40% saving to a real Gemini draft while retaining valid evidence IDs.',status='error')
        return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-label',default='gemini-feedback')
    args=parser.parse_args()
    if not args.output_label or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in args.output_label):parser.error('Output label must use lowercase letters, numbers and hyphens.')
    out=ROOT/'output/examples'/args.output_label
    if (out/'trace.json').exists():parser.error('Output label already contains a run. Choose a fresh --output-label.')
    if not settings.live_ready():raise SystemExit('Live free-tier capability gate is not ready. No request sent.')
    config=settings.model_copy(update={'data_dir':ROOT/'tmp'/('live-feedback-'+uuid4().hex),'checkpoint_backend':'memory'})
    out.mkdir(parents=True,exist_ok=True)
    with TestClient(create_app(config,provider_factory=ControlledFeedback)) as client:
        client.post('/api/sessions',json={'demo':True}).raise_for_status()
        response=client.post('/api/demo',json={'scenario':'frontend'});response.raise_for_status();info=response.json()
        ledger=client.get('/api/evidence').json()
        for evidence in ledger['evidence']:
            client.post('/api/evidence/decisions',json={'evidence_id':evidence['id'],'decision':'include' if evidence['support_status']=='self_reported' else 'exclude'}).raise_for_status()
        version=client.get('/api/evidence').json()['session']['input_version']
        response=client.post('/api/runs',json={**info,'mode':'gemini','page_limit':1,'expected_input_version':version},headers={'Idempotency-Key':uuid4().hex});response.raise_for_status();run=response.json()
        deadline=time.monotonic()+650
        while run['status'] in ('queued','running') and time.monotonic()<deadline:
            time.sleep(2);response=client.get('/api/runs/'+run['id']);response.raise_for_status();run=response.json();print(run['graph_stage'],run['status'],flush=True)
        result=client.get('/api/runs/'+run['id']+'/result').json();events=client.get('/api/runs/'+run['id']+'/events').json()
        stored=client.app.state.store.get(run['id']);store=client.app.state.store
        evaluations=[store.get(id) for id in stored['evaluation_ids']]
        drafts=[store.get(id) for id in stored['draft_ids']]
        for draft in drafts:
            for ext in ['pdf','png']:
                path=store.folder(run['session_id'])/(draft['id']+'.'+ext)
                if path.exists():(out/('draft-'+str(draft['version'])+'.'+ext)).write_bytes(path.read_bytes())
        label='Live Gemini evaluation with a deliberately injected 40% claim. The injected text is not a spontaneous model error. All model responses, including reviewer and revision, came from Gemini.'
        (out/'trace.json').write_text(json.dumps({'label':label,'run':run,'events':events,'evaluations':evaluations,'drafts':drafts},indent=2),encoding='utf-8')
        (out/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        (out/'README.md').write_text('# Controlled live feedback evaluation\n\n'+label+'\n\nStatus: '+run['status']+'. Model attempts: '+str(run['model_attempts'])+'. Automatic revisions: '+str(run['revision_count'])+'.\n',encoding='utf-8')
        if run['status']=='completed':
            for artifact in result['artifacts']:
                r=client.get(artifact['href']);r.raise_for_status();name='resume.pdf' if artifact['kind']=='pdf' else 'report.'+('md' if artifact['kind']=='markdown' else 'json');(out/name).write_bytes(r.content)
            r=client.get(result['preview_url']);r.raise_for_status();(out/'resume.png').write_bytes(r.content)
        print(json.dumps({'status':run['status'],'revision_count':run['revision_count'],'model_attempts':run['model_attempts'],'initial_gate_failed':bool(evaluations and not evaluations[0]['checks']['passed']),'final_gate_passed':bool(evaluations and evaluations[-1]['checks']['passed'])},indent=2))
