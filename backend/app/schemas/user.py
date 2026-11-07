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


class SpotifyConnectionSchema(Schema):
    """Describe a user's Spotify connection."""

    connected = fields.Boolean(required=True)

    display_name = fields.String(
        allow_none=True,
        metadata={"description": "Connected Spotify display name"},
    )


class CurrentUserResponseSchema(UserResponseSchema):
    """Current user information and authentication methods."""

    has_password = fields.Boolean(
        required=True,
        metadata={"description": "Whether local password credentials exist"},
    )

    spotify = fields.Nested(
        SpotifyConnectionSchema,
        required=True,
    )
