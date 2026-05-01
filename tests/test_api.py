from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_returns_html():
    # Verify if the root route (/) returns HTML successfully (status 200)
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_search_returns_html():
    # Verify if the search route (/search/{region}/{riot_id}) returns HTML correctly
    response = client.get("/search/br1/Faker-T1")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
