import os


class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"

    FRONTEND_URL = os.getenv(
        "FRONTEND_URL",
        "http://localhost:3000",
    )

    API_TITLE = "MusicVault API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"

    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
