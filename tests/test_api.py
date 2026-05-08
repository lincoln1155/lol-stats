from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_openapi_schema_is_served():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")


def test_registered_routes_are_exposed_in_schema():
    response = client.get("/openapi.json")
    paths = response.json()["paths"]

    assert "/matches/{region}/{riot_id}" in paths
    assert "get" in paths["/matches/{region}/{riot_id}"]

    assert "/chat/{region}/{riot_id}" in paths
    assert "post" in paths["/chat/{region}/{riot_id}"]


def test_unknown_route_returns_404():
    response = client.get("/this-route-does-not-exist")
    assert response.status_code == 404
