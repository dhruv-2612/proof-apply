"""Reproduce checked fictional output over the real HTTP API. Explicit mode required."""
import argparse,json,time
from pathlib import Path
import httpx
p=argparse.ArgumentParser();p.add_argument('--mode',choices=['mock','gemini'],default='mock');p.add_argument('--scenario',choices=['frontend','platform'],default='frontend');p.add_argument('--url',default='http://127.0.0.1:8000');args=p.parse_args()
root=Path(__file__).resolve().parents[2]
out=root/'output/examples'/(args.mode+'-'+args.scenario);out.mkdir(parents=True,exist_ok=True)
with httpx.Client(base_url=args.url,timeout=30) as client:
    client.post('/api/sessions',json={'demo':True}).raise_for_status()
    demo=client.post('/api/demo',json={'scenario':args.scenario});demo.raise_for_status();info=demo.json()
    data=client.get('/api/evidence').json()
    for e in data['evidence']:
        client.post('/api/evidence/decisions',json={'evidence_id':e['id'],'decision':'include' if e['support_status']=='self_reported' else 'exclude'}).raise_for_status()
    version=client.get('/api/evidence').json()['session']['input_version']
    response=client.post('/api/runs',headers={'Idempotency-Key':'example-'+str(time.time_ns())},json={**info,'mode':args.mode,'page_limit':1,'expected_input_version':version});response.raise_for_status();run=response.json()
    while run['status'] in ('queued','running'):
        time.sleep(2);run=client.get('/api/runs/'+run['id']).json()
        print(run['graph_stage'],run['status'],flush=True)
    result=client.get('/api/runs/'+run['id']+'/result').json()
    events=client.get('/api/runs/'+run['id']+'/events').json()
    (out/'trace.json').write_text(json.dumps({'run':run,'events':events},indent=2),encoding='utf-8')
    (out/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    if run['status']=='completed':
        for a in result['artifacts']:
            content=client.get(a['href']);content.raise_for_status();(out/('resume.pdf' if a['kind']=='pdf' else 'report.'+('md' if a['kind']=='markdown' else 'json'))).write_bytes(content.content)
        preview=client.get(result['preview_url']);preview.raise_for_status();(out/'resume.png').write_bytes(preview.content)
    print(json.dumps({'mode':args.mode,'status':run['status'],'coverage':result.get('coverage'),'model_attempts':run['model_attempts'],'output':str(out)},indent=2))
