from flasgger import swag_from
from flask import Flask, g
from src.api.v1.helpers.jwt_token.jwt_dataclasses import JWT
from src.api.v1.schema.requests_schema import IdSchema
from src.api.v1.schema.users_schema import UserSchema
from src.core.settings import settings
from src.db.models.db_models import User, UserRole
from src.helpers.helpers import (
    CustomResponse,
    get_error_dict,
    get_request_body,
    get_request_query,
    get_swagger_path,
    validate_request,
)
from src.services.service_base import service
from werkzeug.security import generate_password_hash

g.token: JWT  # noqa


@swag_from(get_swagger_path("user/get_users.yaml"))
def get_users():
    """Получить список пользователей"""
    data = UserSchema(only=["id", "email"]).dump(service.get_data(User), many=True)
    return CustomResponse(data)


@validate_request(schema=IdSchema, data=get_request_query)
@swag_from(get_swagger_path("user/get_user.yaml"))
def get_user():
    """Получить подробную информацию"""
    if user := service.get_by_id(get_request_query().get("id"), User):
        return CustomResponse(data=UserSchema(exclude=["password"]).dump(user))
    return CustomResponse(status=404)


@validate_request(schema=UserSchema, data=get_request_body)
@swag_from(get_swagger_path("user/set_user.yaml"))
def set_user():
    """Создать пользователя, назначить роль по умолчанию"""
    try:
        user: User = UserSchema().load(get_request_body())
        user.password = generate_password_hash(user.password)
        service.set_data(user)
        service.set_data(
            UserRole(id_user=user.id, id_role="97cd9d35-890c-4a2a-8321-08d9b1a83189")
        )
        service.set_data(
            UserRole(id_user=user.id, id_role="97cd9d35-890c-4a2a-8321-08d9b1a83182")
        )
    except Exception as e:
        return CustomResponse(message=get_error_dict(e), status=400)
    return CustomResponse()


@validate_request(schema=UserSchema, data=get_request_body, only=["password"])
@swag_from(get_swagger_path("user/update_password.yaml"))
def password_update():
    """Обновить пароль"""
    password = {"password": generate_password_hash(get_request_body().get("password"))}
    if service.update_data(
        g.token.payload.user_id,
        User,
        UserSchema(only=["password", "updated_at"]).dump(password),
    ):
        return CustomResponse()
    return CustomResponse(message="Not Found", status=400)


def init_user_routes(app: Flask):
    """Пути к api user"""
    app.add_url_rule(
        rule=settings.auth_base_path + "get_users", view_func=get_users, methods=["GET"]
    ),
    app.add_url_rule(
        rule=settings.auth_base_path + "get_user", view_func=get_user, methods=["GET"]
    ),
    app.add_url_rule(
        rule=settings.auth_base_path + "set_user", view_func=set_user, methods=["POST"]
    )
    app.add_url_rule(
        rule=settings.auth_base_path + "password_update",
        view_func=password_update,
        methods=["PUT"],
    )
