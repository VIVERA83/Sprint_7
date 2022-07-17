import datetime

from flasgger import Swagger
from flask import Flask, request
from flask_alembic import Alembic
from flask_opentracing import FlaskTracer
from jaeger_client import Config
from src.core.config import settings
from src.db.postgres import init_db
from src.middleware.middleware import init_middleware, init_rate_limit
from src.routes.route import init_route

alembic = Alembic()


def setup_jaeger():
    jaeger_config = {
        "sampler": {
            "type": settings.jaeger_type,
            "param": 1,
        },
        "local_agent": {
            "reporting_host": settings.reporting_host,
            "reporting_port": settings.reporting_port,
        },
        "logging": True,
    }
    config = Config(
        config=jaeger_config,
        service_name=settings.jaeger_service_name,
        validate=True,
    )
    return config.initialize_tracer()


def init_swagger(app: Flask):
    app.config.update({"SWAGGER": {"openapi": "3.0.2"}})
    swagger = Swagger(
        app,
        template=settings.swagger_template,
        parse=True,
    )
    swagger.template = settings.swagger_template


def init_trace(app: Flask):
    tracer = FlaskTracer(setup_jaeger, True, app=app)

    @app.before_request
    @tracer.trace()
    def before_request():
        request_id = request.headers.get("X-Request-Id")
        parent_span = tracer.get_span()
        parent_span.set_tag("http.request_id", request_id)


def create_app(app: Flask):
    with app.app_context():

        app.token = None
        app.refresh_token = None
        app.debug = settings.auth_debug
        app.secret_key = settings.auth_secret_key
        app.permanent_session_lifetime = datetime.timedelta(minutes=10)
        alembic.init_app(app)
        init_swagger(app)
        init_route(app)
        init_db(app)
        init_middleware(app)
        init_rate_limit(app)
        init_trace(app)

    return app


app = create_app(Flask(__name__))
