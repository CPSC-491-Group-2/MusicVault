from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.errors.handlers import register_error_handlers
from app.routes.health import health_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["FRONTEND_URL"]}},
    )

    app.register_blueprint(
        health_bp,
        url_prefix="/api",
    )

    register_error_handlers(app)

    return app
