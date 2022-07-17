import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from marshmallow import INCLUDE, Schema, fields, post_load

from .jwt import create_token
from .jwt_dataclasses import JWT, Header, Payload


class BaseMixin(Schema):
    __model__: Optional[dataclass] = None

    @post_load
    def make_object(self, data: dict[str, Any], **kwargs) -> dataclass:
        return self.__model__(**data)


class HeaderSchema(BaseMixin):
    __model__ = Header

    alg = fields.Str(dump_default="H256")


class PayloadSchema(BaseMixin):
    __model__ = Payload

    user_id = fields.UUID(default=uuid.uuid4())
    iat = fields.Int(default=datetime.now().timestamp())
    exp = fields.Int(default=900)
    role = fields.Str(dump_default="anonymous")
    nonce = fields.Bool(dump_default=False)
    super_user = fields.Bool(dump_default=False)


class JWTSchema(BaseMixin):
    __model__ = JWT

    header = fields.Nested(HeaderSchema())
    payload = fields.Nested(PayloadSchema())
    jwt: str = fields.Function(create_token)  # noqa

    secret_key = fields.String(required=True)

    class Meta:
        unknown = INCLUDE

    @post_load
    def make_object(self, data: dict[str, Any], **kwargs) -> JWT:
        """Create a JWT"""
        data["jwt"] = create_token(data)
        data.pop("secret_key")
        return self.__model__(**data)
