import datetime
from uuid import uuid4

from marshmallow import fields
from marshmallow.validate import Length
from src.api.v1.schema.mixins_schema import BaseMixin, DateMixin
from src.db.models.db_models import Role, User, UserRole, UserSignIn, SocialAccounts


class UserSchema(BaseMixin, DateMixin):
    __model__ = User

    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=Length(min=8, max=20))  # noqa
    username = fields.Str(validate=Length(min=3, max=20))  # noqa
    role_id = fields.List(fields.Nested(lambda: RoleSchema()))  # noqa
    agents = fields.List(fields.Nested(lambda: UserSignInSchema()))  # noqa


class RoleSchema(BaseMixin):
    __model__ = Role
    name = fields.Str(missing="subscriber")


class UserRoleSchema(BaseMixin):
    __model__ = UserRole

    id_user = fields.UUID(dump_default=uuid4, missing=uuid4)
    id_role = fields.UUID(dump_default=uuid4, missing=uuid4)


class UserSignInSchema(BaseMixin):
    __model__ = UserSignIn

    user_agent = fields.Str()
    logged_in_at = fields.DateTime(
        dump_default=datetime.datetime.now, missing=datetime.datetime.now
    )
    user_device_type = fields.Str(required=True)


class SocialAccountsSchema(BaseMixin):
    __model__ = SocialAccounts
