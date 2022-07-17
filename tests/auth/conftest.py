import json
import os
from base64 import b64decode

import pytest
from requests import Session, request

from .settings import settings
from .testdata.auth_data import admin_user_data, test_user_data

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__name__)))


@pytest.fixture(scope="function")
def admin_session(base_url) -> [Session, str]:
    session = Session()
    url = base_url + "login"
    refresh_token = session.post(url, data=json.dumps(admin_user_data)).cookies.get(
        "refresh_token"
    )
    header, payload, signature = refresh_token.split(".")
    payload = json.loads(b64decode(payload.encode()))
    yield session, payload.get("user_id")
    session.close()


@pytest.fixture(scope="function")
def anonymous():
    return request


@pytest.fixture(scope="function")
def user_session(base_url) -> [Session, str]:
    session = Session()
    url = base_url + "login"
    refresh_token = session.post(url, data=json.dumps(test_user_data)).cookies.get(
        "refresh_token"
    )
    header, payload, signature = refresh_token.split(".")
    payload = json.loads(b64decode(payload.encode()))
    yield session, payload.get("user_id")
    session.close()


@pytest.fixture(scope="function")
def base_url() -> str:
    return settings.auth_base_url
