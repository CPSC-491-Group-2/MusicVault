import os


class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"

    FRONTEND_URL = os.getenv(
        "FRONTEND_URL",
        "http://localhost:3000",
    )
