import json
import os

from dotenv import load_dotenv
from pydantic import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__name__)))
load_dotenv(BASE_DIR + "/.env")


class Settings(BaseSettings):
    swagger_template: dict = None
    auth_base_path: str
    # Настройки приложения
    auth_host: str
    auth_port: int
    auth_debug: bool
    auth_secret_key: str
    # Настройка Postgres
    postgres_dsn: str
    # Настройка Redis
    redis_host: str
    redis_port: int
    auth_redis_db: int
    auth_redis_expire: int
    # Супер пользователь
    auth_login: str
    auth_password: str

    jaeger_type: str = "const"
    reporting_host: str = "jaeger"
    reporting_port: int = 6831
    jaeger_service_name: str = "auth_app"

    rate_limit_period: int = 59
    rate_limit_max_calls: int = 20

    # Приложения в социальных сетях
    vk_client_id: str
    vk_client_secret: str

    yandex_client_id: str
    yandex_client_secret: str

    redirect_host: str

    def update_swagger(self, path_to_json: str):
        """Обновляем данные для Api"""
        with open(path_to_json) as file:
            self.swagger_template = json.load(file)
        self.swagger_template[
            "host"
        ] = f"{self.auth_host}:{self.auth_port}{self.auth_base_path}"
        self.swagger_template[
            "basePath"
        ] = f"{self.auth_host}:{self.auth_port}{self.auth_base_path}"
        return self


settings = Settings().update_swagger(
    BASE_DIR + "/auth/src/core/other/swagger_template.json"
)
