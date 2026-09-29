from flask.views import MethodView
from flask_smorest import Blueprint

from app.schemas.health import HealthResponseSchema

health_bp = Blueprint(
    "health",
    __name__,
    description="API health endpoints",
)


@health_bp.route("/health")
class HealthResource(MethodView):

    @health_bp.response(
        200,
        HealthResponseSchema,
    )
    def get(self):
        return {
            "status": "ok",
            "service": "MusicVault API",
        }
