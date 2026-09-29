from marshmallow import Schema, fields


class HealthResponseSchema(Schema):
    service = fields.String(
        required=True,
        metadata={"description": "Name of the backend service"},
    )

    status = fields.String(
        required=True,
        metadata={"description": "Current API health status"},
    )
