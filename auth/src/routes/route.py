from flask import Flask
from src.api.v1.views.auth import init_auth_routes
from src.api.v1.views.role import init_role_routes
from src.api.v1.views.user import init_user_routes


def init_route(app: Flask):
    init_user_routes(app)
    init_auth_routes(app)
    init_role_routes(app)
