import datetime
from sqlalchemy import and_
from flasgger import swag_from
from flask import Flask, g, request, session, redirect
from marshmallow import ValidationError
from src.api.v1.helpers.jwt_token.jwt import make_jwt
from src.api.v1.helpers.jwt_token.jwt_dataclasses import JWT
from src.api.v1.helpers.tokens import create_tokens, save_tokens_to_cache
from src.api.v1.schema.requests_schema import LoginSchema, PaginateSchema, PathSchema
from src.api.v1.schema.users_schema import UserSignInSchema
from src.core.settings import settings
from src.db.models.db_models import User, UserSignIn, SocialAccounts, UserRole
from src.helpers.helpers import (
    CustomResponse,
    get_request_body,
    get_request_query,
    get_swagger_path,
    get_type_devices,
    validate_request,
)
from src.social_network.social_networks import SocialNetworks
from src.roles.roles import access_roles_list
from src.services.service_base import service
from werkzeug.security import check_password_hash, generate_password_hash

from uuid import uuid4

g.token: JWT  # noqa
g.refresh_token: JWT  # noqa


@validate_request(schema=LoginSchema, data=get_request_body)
@swag_from(get_swagger_path("auth/login.yaml"))
def user_login():
    """Авторизация пользователя"""
    login = LoginSchema(exclude=["id"]).load(get_request_body())
    if user := service.get_data_by_email(User, login.email):
        if check_password_hash(user.password, login.password):
            g.token, g.refresh_token = create_tokens(user.id)
            save_tokens_to_cache(g.token, g.refresh_token)
            service.set_data(
                UserSignIn(
                    user_id=user.id,
                    user_agent=request.headers.get("User-Agent"),
                    user_device_type=get_type_devices(
                        request.headers.get("User-Agent")
                    ),
                )
            )
            return CustomResponse()
    return CustomResponse(status=401, message="Логин либо пароль введены не верно ")


@swag_from(get_swagger_path("auth/logout.yaml"))
def user_logout():
    """Завершить сеанс"""
    if token := session.get("token"):
        jwt = make_jwt(token, settings.auth_secret_key)
        service.cache.delete(jwt.signature)
        session.pop("token", None)
        response = CustomResponse(status=200, message="log out is successful")
        response.set_cookie("refresh_token", "")
        return response
    return CustomResponse(status=401, message="Not authorized")


@validate_request(schema=PaginateSchema, data=get_request_query)
@swag_from(get_swagger_path("user/user_history.yaml"))
def user_history():
    paginate = PaginateSchema().dump(get_request_query())
    agents: list[UserSignIn] = (
        UserSignIn.query.filter(UserSignIn.user_id == g.token.payload.user_id)
        .paginate(**paginate, error_out=True)
        .items
    )
    data = UserSignInSchema(only=["user_agent", "logged_in_at"], many=True).dump(agents)
    return CustomResponse(data=data)


@swag_from(get_swagger_path("auth/refresh.yaml"))
def refresh():
    """Обновление токена, по refresh_token"""
    try:
        refresh_token = make_jwt(g.refresh_token.jwt, settings.auth_secret_key)
        cache_token = make_jwt(
            service.get_cache(refresh_token.signature)["jwt"], settings.auth_secret_key
        )
    except ValidationError as e:
        return CustomResponse(status=401, message=e.messages)
    except TypeError:
        return CustomResponse(status=401, message="the token is outdated")
    if (
            cache_token.payload.exp + cache_token.payload.iat
            > datetime.datetime.now().timestamp()
    ) and cache_token.payload.nonce:
        service.delete_cache(refresh_token.signature)
        token, refresh_token = create_tokens(refresh_token.payload.user_id)
        save_tokens_to_cache(token, refresh_token)
        return CustomResponse()
    return CustomResponse(status=401, message="Требуется авторизация")


@validate_request(schema=PathSchema, data=get_request_body)
@swag_from(get_swagger_path("auth/check_access.yaml"))
def check_access():
    path = PathSchema().load(get_request_body())
    response = CustomResponse()
    if g.token.payload.super_user:
        return response
    for role in g.token.payload.role.split(","):
        if path.path in access_roles_list.get(role, []):
            return response

    return CustomResponse(status=403)


@swag_from(get_swagger_path("auth/login_to_social_network.yaml"))
def login_to_social_network():
    """Авторизация с помощью социальных сетей"""
    network = SocialNetworks(get_request_query().get("social_network"))
    # если код есть, то проводим авторизацию или регистрацию
    if code := request.args.get('code', False):
        social_id, social_name, email, token, = network.get_user_data(code).values()
        # если пользователь с таким email нет, то создаем нового пользователя
        user = service.get_data_by_email(User, email)
        if not user or not SocialAccounts.query.filter(and_(SocialAccounts.user_id == user.id.hex,
                                                            SocialAccounts.social_name == social_name)).first():
            if not user:
                user = User(email=email, password=generate_password_hash(uuid4().hex[:8]))
            service.set_data(user)
            service.set_data(UserRole(id_user=user.id, id_role="97cd9d35-890c-4a2a-8321-08d9b1a83189"))
            service.set_data(UserRole(id_user=user.id, id_role="97cd9d35-890c-4a2a-8321-08d9b1a83182"))
            service.set_data(SocialAccounts(user_id=user.id, social_id=social_id, social_name=social_name))
        # производим авторизацию
        g.token, g.refresh_token = create_tokens(user.id)
        save_tokens_to_cache(g.token, g.refresh_token)
        service.set_data(
            UserSignIn(
                user_id=user.id,
                user_agent=request.headers.get("User-Agent"),
                user_device_type=get_type_devices(
                    request.headers.get("User-Agent")
                ),
            )
        )
    else:
        return redirect(network.auth_url)
    return CustomResponse(status=200, )


def init_auth_routes(app: Flask):
    """Пути к api auth"""
    app.add_url_rule(
        rule=settings.auth_base_path + "login/", view_func=user_login, methods=["POST"]
    )
    app.add_url_rule(
        rule=settings.auth_base_path + "logout/", view_func=user_logout, methods=["GET"]
    )
    app.add_url_rule(
        rule=settings.auth_base_path + "refresh/", view_func=refresh, methods=["GET"]
    )
    app.add_url_rule(
        rule=settings.auth_base_path + "check_access/",
        view_func=check_access,
        methods=["POST"],
    )
    app.add_url_rule(
        rule=settings.auth_base_path + "user_history/",
        view_func=user_history,
        methods=["GET"],
    )
    app.add_url_rule(
        rule=settings.auth_base_path + "login_to_social_network/",
        view_func=login_to_social_network,
        methods=["GET"],
    )
