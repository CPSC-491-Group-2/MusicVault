from flask import Flask
from flask_cors import CORS
from flask_smorest import Api

from app.config import Config
from app.errors.handlers import register_error_handlers
from app.routes.health import health_bp
from app.routes.user import user_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["FRONTEND_URL"]}},
    )

    api = Api(app)

    api.register_blueprint(
        health_bp,
        url_prefix="/api/v1",
    )

    api.register_blueprint(
        user_bp,
        url_prefix="/api/v1",
    )

    register_error_handlers(app)

    return app
