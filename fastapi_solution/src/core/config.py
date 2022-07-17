import os
from logging import config as logging_config

from pydantic import BaseSettings
from src.core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__name__)))


class Settings(BaseSettings):
    project_name: str

    redis_host: str
    redis_port: int
    redis_db_number: int

    elastic_host: str
    elastic_port: int

    auth_host: str
    auth_port: int

    class Config:
        env_file = BASE_DIR + ".env_local"
        enf_file_encoding = "utf-8"
