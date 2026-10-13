import os


class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"

    FRONTEND_URL = os.getenv(
        "FRONTEND_URL",
        "http://localhost:3000",
    )

    # Signs the session cookie that carries the OAuth state and logged-in
    # user. Never commit a real value; see .env.example.
    SECRET_KEY = os.getenv("SECRET_KEY")

    SESSION_COOKIE_HTTPONLY = True
    # Lax still sends the cookie on Spotify's top-level redirect back to the
    # callback, but not on cross-site POSTs or embedded requests.
    SESSION_COOKIE_SAMESITE = "Lax"
    # Turn on wherever the site is served over HTTPS.
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False") == "True"

    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    # Must exactly match a redirect URI registered in the Spotify dashboard.
    SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
    SPOTIFY_SCOPES = os.getenv(
        "SPOTIFY_SCOPES",
        "user-read-email user-read-private user-top-read",
    )

    API_TITLE = "MusicVault API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"

    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
