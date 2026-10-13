from __future__ import annotations

import importlib
import logging

import pytest

import app as app_package
from app import config as config_module
from app import create_app

# Every value the Spotify login needs. Listed here rather than imported from
# the app, so dropping one from the app's own check makes these tests fail.
REQUIRED_SETTINGS = [
    "SECRET_KEY",
    "SPOTIFY_CLIENT_ID",
    "SPOTIFY_CLIENT_SECRET",
    "SPOTIFY_REDIRECT_URI",
]
OPTIONAL_SETTINGS = ["FRONTEND_URL", "SESSION_COOKIE_SECURE", "SPOTIFY_SCOPES"]

FULL_ENV = {
    "SECRET_KEY": "env-secret-key",
    "SPOTIFY_CLIENT_ID": "env-client-id",
    "SPOTIFY_CLIENT_SECRET": "env-client-secret",
    "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:3000/api/auth/spotify/callback",
}


@pytest.fixture
def load_config(monkeypatch):
    """Re-read Config from a controlled environment.

    Config reads os.environ when its module is imported, so each call clears
    the relevant variables, applies the given ones, and reloads the module.
    The original Config is restored afterwards for the other tests.
    """

    def _load(**env):
        for key in REQUIRED_SETTINGS + OPTIONAL_SETTINGS:
            monkeypatch.delenv(key, raising=False)
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        config = importlib.reload(config_module).Config
        # create_app() uses the Config it imported, so point it at this one.
        monkeypatch.setattr(app_package, "Config", config)
        return config

    yield _load
    monkeypatch.undo()
    importlib.reload(config_module)


def app_from_env(load_config, **env):
    load_config(**env)
    app = create_app()
    app.testing = True
    return app


# --- secrets come from the environment ------------------------------------


def test_secrets_are_read_from_environment(load_config):
    config = load_config(**FULL_ENV)

    for key, value in FULL_ENV.items():
        assert getattr(config, key) == value


@pytest.mark.parametrize("key", REQUIRED_SETTINGS)
def test_secrets_have_no_hardcoded_fallback(load_config, key):
    # If a default were baked into the code, a deployment with a missing
    # variable would silently run on a value that's public in the repo.
    config = load_config()

    assert getattr(config, key) is None


def test_session_cookie_is_hardened(load_config):
    config = load_config()

    assert config.SESSION_COOKIE_HTTPONLY is True
    assert config.SESSION_COOKIE_SAMESITE == "Lax"
    assert config.SESSION_COOKIE_SECURE is False


def test_session_cookie_secure_can_be_enabled(load_config):
    assert load_config(SESSION_COOKIE_SECURE="True").SESSION_COOKIE_SECURE is True


# --- missing configuration -------------------------------------------------


def test_app_starts_without_any_secrets(load_config):
    # Health checks and non-login routes must keep working on a fresh
    # checkout with no .env.
    app = app_from_env(load_config)

    assert app.test_client().get("/api/v1/health").status_code == 200


@pytest.mark.parametrize("path", ["/login", "/callback"])
@pytest.mark.parametrize("missing", REQUIRED_SETTINGS)
def test_login_refuses_to_run_when_env_var_missing(load_config, missing, path):
    env = {key: value for key, value in FULL_ENV.items() if key != missing}
    app = app_from_env(load_config, **env)

    response = app.test_client().get(f"/api/auth/spotify{path}")

    assert response.status_code == 503
    assert response.get_json() == {
        "error": "Service Unavailable",
        "message": "Spotify login is not configured.",
    }


@pytest.mark.parametrize("empty", REQUIRED_SETTINGS)
def test_empty_env_var_counts_as_missing(load_config, empty):
    # compose.yml passes unset variables through as empty strings.
    app = app_from_env(load_config, **{**FULL_ENV, empty: ""})

    assert app.test_client().get("/api/auth/spotify/login").status_code == 503


def test_missing_config_is_logged_by_name_only(load_config, caplog):
    env = {k: v for k, v in FULL_ENV.items() if k != "SPOTIFY_CLIENT_SECRET"}
    app = app_from_env(load_config, **env)

    with caplog.at_level(logging.ERROR):
        app.test_client().get("/api/auth/spotify/login")

    assert "SPOTIFY_CLIENT_SECRET" in caplog.text
    # Names of what's missing, never the values that are set.
    for value in env.values():
        assert value not in caplog.text


def test_login_works_with_full_env(load_config):
    app = app_from_env(load_config, **FULL_ENV)

    response = app.test_client().get("/api/auth/spotify/login")

    assert response.status_code == 302
    assert "env-client-id" in response.location
    assert "env-client-secret" not in response.location
