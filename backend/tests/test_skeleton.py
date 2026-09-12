from fastapi.testclient import TestClient
from app.main import app
def test_health_is_local_and_sanitized():
    assert TestClient(app).get('/api/health').json() == {'status': 'ok'}
