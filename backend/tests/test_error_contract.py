from app import create_app


SENSITIVE_TERMS = [
    "traceback",
    "runtimeerror",
    "forced error for contract test",
    "sqlalchemy",
    "database_url",
    "client_secret",
    "access_token",
    "refresh_token",
]


def assert_controlled_error_response(
    response,
    expected_status,
    expected_error,
    expected_message,
):
    body = response.get_json()

    assert response.status_code == expected_status
    assert response.is_json
    assert body == {
        "error": expected_error,
        "message": expected_message,
    }

    response_text = response.get_data(as_text=True).lower()

    for term in SENSITIVE_TERMS:
        assert term not in response_text


def test_not_found_returns_json_404(client):
    response = client.get("/api/v1/does-not-exist")

    assert_controlled_error_response(
        response,
        404,
        "Not Found",
        "The requested resource was not found.",
    )


def test_method_not_allowed_returns_json_405(client):
    response = client.post("/api/v1/health")

    assert_controlled_error_response(
        response,
        405,
        "Method Not Allowed",
        "The requested method is not allowed for this resource.",
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

    assert_controlled_error_response(
        response,
        500,
        "Internal Server Error",
        "Something went wrong on the server.",
    )