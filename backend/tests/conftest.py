import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.config import Settings
@pytest.fixture
def client(tmp_path):
    config=Settings(_env_file=None,data_dir=tmp_path,checkpoint_backend='memory')
    app=create_app(config)
    with TestClient(app) as client: yield client
