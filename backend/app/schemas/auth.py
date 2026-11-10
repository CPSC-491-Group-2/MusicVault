from marshmallow import Schema, fields, validate


class RegisterRequestSchema(Schema):
    """Validate incoming MusicVault registration data."""

    email = fields.Email(
        required=True,
        validate=validate.Length(max=320),
    )

    password = fields.String(
        required=True,
        load_only=True,
        validate=validate.Length(min=8, max=128),
    )

    display_name = fields.String(
        load_default=None,
        allow_none=True,
        validate=validate.Length(max=255),
    )


class LoginRequestSchema(Schema):
    """Validate incoming MusicVault login data."""

    email = fields.Email(required=True)

    password = fields.String(
        required=True,
        load_only=True,
    )


class PasswordChangeSchema(Schema):
    # Required only when the user already has a password; the route checks.
    current_password = fields.String(load_only=True, load_default=None)
    # Checked against EmailSchema only when the account still needs an email.
    email = fields.String(load_default=None)
    new_password = fields.String(
        required=True,
        load_only=True,
        validate=validate.Length(min=8, max=128),
    )


class EmailSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=320))
