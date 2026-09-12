"""Local-only parser/layout rehearsal for the user's supplied documents. Never calls Gemini."""
from pathlib import Path
import tempfile,sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.main import create_app
from app.config import ROOT,Settings
from app.extraction import extract
from fastapi.testclient import TestClient
paths=list((ROOT/'sample-docs').iterdir());resume=next(p for p in paths if p.suffix=='.docx');jd=next(p for p in paths if p.suffix=='.pdf')
chunks=extract(resume.read_bytes(),resume.name);job=extract(jd.read_bytes(),jd.name)
name=chunks[0]['text'];contacts=' | '.join(c['text'] for c in chunks if '@' in c['text'])
if len(contacts)>240: raise ValueError('Confirm a shorter contact header locally before rendering.')
out=ROOT/'output/private/local-sample';out.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as folder:
    with TestClient(create_app(Settings(_env_file=None,data_dir=Path(folder),checkpoint_backend='memory',llm_mode='mock'))) as client:
        client.post('/api/sessions',json={'demo':False})
        for slot,path in [('resume',resume),('job',jd)]:
            client.post('/api/sources',data={'slot':slot},files={'file':(path.name,path.read_bytes())}).raise_for_status()
        client.post('/api/sources',data={'slot':'company','text':'Supplied role/company context extracted locally from the supplied Amazon job posting. No external research was performed.\n'+job[0]['text']}).raise_for_status()
        data=client.get('/api/evidence').json()
        for e in data['evidence']:
            client.post('/api/evidence/decisions',json={'evidence_id':e['id'],'decision':'include' if e['support_status']=='self_reported' else 'exclude','reason':'Local extractive parser/layout rehearsal; user must review before use.'}).raise_for_status()
        data=client.get('/api/evidence').json()
        response=client.post('/api/runs',headers={'Idempotency-Key':'local-sample-'+str(time.time_ns())},json={'source_ids':[s['id'] for s in data['sources']],'role_title':'Product Manager, Amazon Business India','company_name':'Amazon','header':{'name':name,'contact':contacts},'page_limit':1,'mode':'mock','expected_input_version':data['session']['input_version']});response.raise_for_status();run=response.json()
        for _ in range(200):
            run=client.get('/api/runs/'+run['id']).json()
            if run['status'] not in ('queued','running'): break
            time.sleep(.1)
        result=client.get('/api/runs/'+run['id']+'/result').json()
        (out/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        if result.get('preview_url'):
            preview=client.get(result['preview_url']);(out/'resume.png').write_bytes(preview.content)
        for a in result['artifacts']:
            response=client.get(a['href']);response.raise_for_status();(out/('resume.pdf' if a['kind']=='pdf' else 'report.'+('md' if a['kind']=='markdown' else 'json'))).write_bytes(response.content)
        print(json.dumps({'status':run['status'],'mode':run['mode'],'model_attempts':run['model_attempts'],'page_count':result.get('evaluations',{}).get('checks',{}).get('pdf',{}).get('page_count'),'issues':[i['category'] for i in result.get('evaluations',{}).get('issues',[])],'output':'output/private/local-sample'},indent=2))
