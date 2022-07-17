import os

from dotenv import load_dotenv
from pydantic import BaseSettings

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__name__)))
load_dotenv()


class TestSettings(BaseSettings):
    auth_host: str
    auth_port: int
    auth_base_path: str
    auth_base_url: str = None
    auth_login: str
    auth_password: str


settings = TestSettings()
settings.auth_base_url = "http://{host}:{port}{auth}".format(
    host=settings.auth_host, port=settings.auth_port, auth=settings.auth_base_path
)
