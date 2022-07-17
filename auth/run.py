from flask import Flask
from src.core.config import settings
from src.core.settings import create_app

if __name__ == "__main__":
    create_app(Flask(__name__)).run(host=settings.auth_host, port=settings.auth_port)
