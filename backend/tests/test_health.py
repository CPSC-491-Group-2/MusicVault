def test_health_returns_200(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200


def test_health_returns_json(client):
    response = client.get("/api/v1/health")

    assert response.is_json


def test_health_returns_expected_body(client):
    response = client.get("/api/v1/health")
    body = response.get_json()

    assert body["status"] == "ok"
    assert body["service"] == "MusicVault API"


def test_missing_route_returns_json_404(client):
    response = client.get("/api/v1/does-not-exist")
    body = response.get_json()

    assert response.status_code == 404
    assert response.is_json
    assert body["error"] == "Not Found"
    assert body["message"] == "The requested resource was not found."
