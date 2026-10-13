from app import create_app


def test_method_not_allowed_returns_json_405(client):
    response = client.post("/api/v1/health")
    body = response.get_json()

    assert response.status_code == 405
    assert response.is_json
    assert body["error"] == "Method Not Allowed"
    assert (
        body["message"]
        == "The requested method is not allowed for this resource."
    )


def test_internal_server_error_returns_json_500():
    app = create_app()

    # Flask normally propagates exceptions while testing. Disable propagation
    # here so the request goes through the application's real 500 handler.
    app.config.update(
        TESTING=False,
        PROPAGATE_EXCEPTIONS=False,
    )

    @app.get("/api/v1/test-force-500")
    def force_internal_server_error():
        raise RuntimeError("forced error for contract test")

    client = app.test_client()
    response = client.get("/api/v1/test-force-500")
    body = response.get_json()

    assert response.status_code == 500
    assert response.is_json
    assert body["error"] == "Internal Server Error"
    assert body["message"] == "Something went wrong on the server."