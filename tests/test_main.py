# Replace 'main' with the actual name of your file where the FastAPI app is defined
import pytest
import requests_mock
from fastapi.testclient import TestClient

from backend.main import (
    app,
)

client = TestClient(app)

# This test assumes you have a 'requests_mock' fixture available.
# You may need to install 'pytest-requests-mock' or similar library and set it up accordingly.


@pytest.fixture
def mock_request():
    with requests_mock.Mocker() as m:
        yield m


def test_search_venue_success(mock_request):
    # Mock the response from the external API
    endpoint = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
    mock_data = {
        "total": 1,
        "data": [
            {
                "title": "Example Paper",
                "year": 2021,
                "referenceCount": 10,
                "citationCount": 5,
                "influentialCitationCount": 1,
                "isOpenAccess": True,
                "fieldsOfStudy": ["Computer Science"],
                "authors": [{"authorId": "1234", "name": "John Doe"}],
                "venue": "Example Venue",
            }
        ],
    }
    mock_request.get(endpoint, json=mock_data)

    # Call the endpoint
    response = client.post("/search/", data={"venues": ["Example Venue"]})

    # Check that the response is as expected
    assert response.status_code == 200
    assert response.json() == {"total": 1, "sorted_data": mock_data["data"]}


def test_search_venue_api_failure(mock_request):
    # Mock the response to simulate an API failure
    endpoint = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
    mock_request.get(endpoint, status_code=500)

    # Call the endpoint
    response = client.post("/search/", data={"venues": ["Bad Venue"]})

    # Check that the response indicates an API request failure
    assert response.status_code == 500
    assert response.json() == {"error": "API request failed for all venues"}
