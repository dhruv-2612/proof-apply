from helpers import prepare,start

def test_normal_real_pdf_offline_provider(client):
    run=start(client,prepare(client))
    assert run['status']=='completed',client.get('/api/runs/'+run['id']+'/result').json().get('evaluations',run)
    result=client.get('/api/runs/'+run['id']+'/result').json()
    assert round(result['coverage']['percent'])==92
    docker=[m for m in result['matches'] if m['status']=='missing']
    assert len(docker)==1
    assert result['revision_count']==0
    assert result['evaluations']['checks']['pdf']['page_count']==1
    assert len(result['artifacts'])==3
    for artifact in result['artifacts']:
        response=client.get(artifact['href']);assert response.status_code==200
    assert run['model_attempts']==0

def test_platform_gap_different_route(client):
    run=start(client,prepare(client,'platform'))
    assert run['status']=='completed',client.get('/api/runs/'+run['id']+'/result').json().get('evaluations',run)
    result=client.get('/api/runs/'+run['id']+'/result').json()
    assert round(result['coverage']['percent'])==11
    assert len([m for m in result['matches'] if m['status']=='missing'])==4
    events=client.get('/api/runs/'+run['id']+'/events').json()['events']
    assert any(e['action']=='read_evidence' for e in events)
    assert all(e['mode']=='mock' for e in events)
