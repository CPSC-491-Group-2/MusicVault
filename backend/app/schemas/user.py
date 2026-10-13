from marshmallow import Schema, fields


class UserResponseSchema(Schema):
    id = fields.UUID(
        required=True,
        metadata={"description": "User ID"},
    )

    email = fields.String(
        allow_none=True,
        metadata={"description": "User email, null for Spotify-only accounts"},
    )

    display_name = fields.String(
        allow_none=True,
        metadata={"description": "User display name"},
    )

    created_at = fields.DateTime(
        required=True,
        metadata={"description": "Account creation timestamp"},
    )

    updated_at = fields.DateTime(
        required=True,
        metadata={"description": "Last update timestamp"},
    )
