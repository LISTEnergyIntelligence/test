from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_invalid_dataset():
    response = client.get('/fetch/energy_charts/unknown?start_date=2024-01-01&end_date=2024-01-02')
    assert response.status_code == 400
