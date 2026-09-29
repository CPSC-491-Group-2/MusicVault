from flask import jsonify


def register_error_handlers(app):

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify(
                {
                    "error": "Not Found",
                    "message": "The requested resource was not found.",
                }
            ),
            404,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "Something went wrong on the server.",
                }
            ),
            500,
        )
