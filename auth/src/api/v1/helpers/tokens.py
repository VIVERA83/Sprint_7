from src.api.v1.helpers.jwt_token.jwt_dataclasses import JWT
from src.api.v1.helpers.jwt_token.jwt_schema import (
    HeaderSchema,
    JWTSchema,
    PayloadSchema,
)
from src.core.settings import settings
from src.db.models.db_models import User
from src.services.service_base import service


def create_tokens(user_id) -> [JWT, JWT]:
    """Создание токенов"""
    user = service.get_by_id(user_id, User)
    roles = ",".join([role.name for role in user.roles])
    token: JWT = JWTSchema().load(
        {
            "secret_key": settings.auth_secret_key,
            "header": HeaderSchema().dump({}),
            "payload": PayloadSchema().dump(
                {
                    "user_id": user.id,
                    "role": roles,
                    "super_user": user.super_user or False,
                }
            ),
        }
    )
    refresh_token: JWT = JWTSchema().load(
        {
            "secret_key": settings.auth_secret_key,
            "header": HeaderSchema().dump({}),
            "payload": PayloadSchema().dump(
                {
                    "user_id": user.id,
                    "nonce": True,
                    "role": roles,
                    "exp": settings.auth_redis_expire,
                    "super_user": user.super_user or False,
                }
            ),
        }
    )
    return token, refresh_token


def save_tokens_to_cache(token: JWT, refresh_token: JWT):
    """Сохранение токенов в Кэш"""
    service.set_cache(token.signature, JWTSchema().dumps(token), token.payload.exp)
    service.set_cache(
        refresh_token.signature,
        JWTSchema().dumps(refresh_token),
        refresh_token.payload.exp,
    )
