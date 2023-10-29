from fastapi.testclient import TestClient
from backend.main import app  # プロジェクトのディレクトリ構造に応じて適切なインポートパスを使用してください。

client = TestClient(app)

def test_read_root()->None:
    response = client.get("/")
    assert response.status_code == 200
    assert "request" in response.text

def test_search_venue()->None:
    response = client.post("/search/", json={"venue": "IEEE International Conference on Robotics and Automation"})
    assert response.status_code == 200
    assert response.json()["total"] is not None
    assert isinstance(response.json()["sorted_data"], list)

