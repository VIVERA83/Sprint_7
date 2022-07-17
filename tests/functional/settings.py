import os

from dotenv import load_dotenv
from pydantic import BaseSettings

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__name__)))
load_dotenv()


class TestSettings(BaseSettings):
    redis_host: str
    redis_port: int

    elastic_host: str
    elastic_port: int
    elastic_dns: str
    api_key: str

    api_url: str = None

    timeout: int  # Время ожидания отклика от БД, сек

    class Config:
        # env_file = ".env"
        # enf_file_encoding = "utf-8"
        case_sensitive = False


settings = TestSettings()
