import time

def prepare(client,scenario='frontend'):
    client.post('/api/sessions',json={'demo':True})
    info=client.post('/api/demo',json={'scenario':scenario}).json()
    data=client.get('/api/evidence').json()
    for e in data['evidence']:
        response=client.post('/api/evidence/decisions',json={'evidence_id':e['id'],'decision':'include' if e['support_status']=='self_reported' else 'exclude'})
        assert response.status_code==200,response.text
    data=client.get('/api/evidence').json()
    return {**info,'mode':'mock','page_limit':1,'expected_input_version':data['session']['input_version']}

def wait_run(client,id):
    for _ in range(150):
        run=client.get('/api/runs/'+id).json()
        if run['status'] not in ('running','queued'): return run
        time.sleep(.1)
    raise AssertionError('Run did not terminate')

def start(client,payload,key='test-start-001'):
    response=client.post('/api/runs',json=payload,headers={'Idempotency-Key':key})
    assert response.status_code==202,response.text
    return wait_run(client,response.json()['id'])
