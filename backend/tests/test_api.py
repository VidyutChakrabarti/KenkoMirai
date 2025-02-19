from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_simulation():
    response = client.get("/simulation?steps=10")
    assert response.status_code == 200
    data = response.json()
    assert "final" in data
