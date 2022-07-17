import datetime
import http

from flask import Flask, Response, g, request, session
from marshmallow import ValidationError
from src.api.v1.helpers.jwt_token.jwt import JWT, make_jwt
from src.api.v1.helpers.jwt_token.jwt_schema import JWTSchema
from src.api.v1.views.auth import refresh
from src.core.config import settings
from src.db.redis import db_redis
from src.helpers.helpers import CustomResponse
from src.roles.roles import access_roles_list

g.token: JWT  # noqa
g.refresh_token: JWT  # noqa


def init_middleware(app: Flask):
    @app.before_request
    def check_url_role():
        """Проверяем корректность URL"""
        if not request.url_rule:
            return CustomResponse(message="Api not Found", status=404)

    @app.before_request
    def create_token():
        """Создаем токен доступа, в глобальной переменной g"""
        token = JWTSchema(only=["jwt"]).dump({"secret_key": settings.auth_secret_key})[
            "jwt"
        ]
        g.token = make_jwt(token, settings.auth_secret_key)
        if token := session.get("token"):
            try:
                # если токен не корректен выбрасываем ошибку о том что токен не валиден
                g.token = make_jwt(token, settings.auth_secret_key)
                return
            except ValidationError as e:
                return CustomResponse(message=e.messages, status=400)
        # если пользователь только вошел создавать ему анонимный token c ролью 'anonymous'
        if auth := request.headers.get("Authorization"):
            try:
                g.token = make_jwt(auth.split()[1], settings.auth_secret_key)
                return
            except ValidationError as e:
                return CustomResponse(message=e.messages, status=400)
            except IndexError:
                pass

    @app.before_request
    def create_refresh_token():
        """Создаем токен обновления, в глобальной переменной g"""
        g.refresh_token = make_jwt(g.token.jwt, settings.auth_secret_key)
        try:
            # если токен не корректен выбрасываем ошибку о том что токен не валиден
            g.refresh_token = make_jwt(
                request.cookies.get("refresh_token"), settings.auth_secret_key
            )
        except ValidationError as e:
            return CustomResponse(message=e.messages, status=400)
        except ValueError:
            pass
        except AttributeError:
            pass

    @app.before_request
    def check_refresh():
        """Обновляем token если срок действия вышел, и есть корректный refresh_token"""
        if (
                g.token.payload.exp + g.token.payload.iat
        ) < datetime.datetime.now().timestamp():
            if g.refresh_token.payload.nonce:
                refresh()

    @app.before_request
    def check_access():
        """Проверка доступа к запрашиваемым ресурсам"""
        if g.token.payload.super_user:
            return
        for role in g.token.payload.role.split(","):
            if request.url_rule.rule in access_roles_list.get(role, []):
                return
        return CustomResponse(message="Access denied", status=403)

    @app.after_request
    def after_request(response: Response):
        if getattr(g, "token", None):
            session["token"] = g.token.jwt
            response.set_cookie("refresh_token", g.refresh_token.jwt)
            response.headers.set("token", g.token.jwt)
            session.modified = True
            session.permanent = True

        return response


def init_rate_limit(app: Flask):
    @app.before_request
    def rate_limit(*args, **kwargs):  # noqa
        pipe = db_redis.pipeline()
        now = datetime.datetime.now()
        key = f"{request.remote_addr}:{now.minute}"

        pipe.incr(key, 1)
        pipe.expire(key, settings.rate_limit_period)

        result = pipe.execute()
        request_number = result[0]

        if request_number > settings.rate_limit_max_calls:
            return http.HTTPStatus(429)
