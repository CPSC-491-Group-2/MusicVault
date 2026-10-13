def test_health_contract_matches_frontend(client):
    response = client.get("/api/v1/health")
    body = response.get_json()

    assert response.status_code == 200
    assert set(body.keys()) == {"status", "service"}
    assert isinstance(body["status"], str)
    assert isinstance(body["service"], str)


def test_health_allows_frontend_origin(client):
    response = client.get(
        "/api/v1/health",
        headers={"Origin": "http://localhost:3000"},
    )

    assert response.status_code == 200
    assert response.headers.get("Access-Control-Allow-Origin") == "http://localhost:3000"


def test_health_preflight_allows_frontend(client):
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.headers.get("Access-Control-Allow-Origin") == "http://localhost:3000"

