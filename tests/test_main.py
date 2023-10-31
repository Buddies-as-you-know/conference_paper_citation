from fastapi.testclient import TestClient

from backend.main import (
    app,  # プロジェクトのディレクトリ構造に応じて適切なインポートパスを使用してください。
)

client = TestClient(app)


def test_search_venue() -> None:
    # 正常なリクエストのテスト
    response = client.post(
        "/search/", data={"venue": "IEEE International Conference on Robotics and Automation"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "sorted_data" in data

    # APIエラーのテスト（例：存在しないvenueを指定）
    response = client.post("/search/", data={"venue": "NonExistentVenue"})
    assert response.status_code == 400  # もしくはAPIが返す適切なエラーコード
    assert "error" in response.json()

    # venueパラメータがない場合のテスト
    response = client.post("/search/")
    assert response.status_code == 422
    assert "detail" in response.json()
