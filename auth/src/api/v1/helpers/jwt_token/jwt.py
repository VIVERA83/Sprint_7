import hmac
from base64 import b64decode, b64encode
from hashlib import sha256
from typing import Union

from marshmallow import ValidationError

from .jwt_dataclasses import JWT


def make_jwt(token: str, secret_key: str) -> JWT:
    """
    Create a JWT instance from a token.
    :param token: The token to authenticate.
    :param secret_key: The secret key to authenticate.
    :return: An instance of the JWT class.
    """
    from .jwt_schema import HeaderSchema, PayloadSchema

    header, payload, signature = token.split(".")
    expected_key = hmac.new(
        key=secret_key.encode(),
        msg="{header}.{payload}".format(header=header, payload=payload).encode(),
        digestmod=sha256,
    ).hexdigest()
    if expected_key == signature:
        return JWT(
            header=HeaderSchema().loads(b64decode(header.encode()).decode()),
            payload=PayloadSchema().loads(b64decode(payload.encode()).decode()),
            jwt=token,
        )

    raise ValidationError(
        message="The integrity of the token has been violated",
    )


def create_token(schema: Union[JWT, dict]) -> str:
    """Create a jwt token"""
    from .jwt_schema import HeaderSchema, PayloadSchema

    if isinstance(schema, JWT):
        return schema.jwt
    header = HeaderSchema().dumps(schema.get("header")).encode()
    payload = PayloadSchema().dumps(schema.get("payload")).encode()
    hp = b64encode(header).decode() + "." + b64encode(payload).decode()
    signature = hmac.new(
        key=schema["secret_key"].encode(), msg=hp.encode(), digestmod=sha256
    )
    jwt = hp + "." + signature.hexdigest()
    return jwt
