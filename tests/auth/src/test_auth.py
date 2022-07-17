import json
from http.client import FORBIDDEN, OK

import pytest  # noqa

from ..testdata.auth_data import admin_user_data


class TestAuth:
    def test_check_access(self, base_url, admin_session, anonymous):
        url = base_url + "check_token"
        path = {"path": "/auth/api/v1/assign_role"}
        session, _ = admin_session
        resp = session.post(url, json.dumps(path))
        # проверка доступа к методу к которому есть доступ
        assert OK == resp.status_code
        assert OK == resp.json().get("status")
        # проверка доступа к методу к которому доступ нет
        resp = anonymous(method="post", url=url, data=json.dumps(path))
        assert FORBIDDEN == resp.status_code
        assert FORBIDDEN == resp.json().get("status")

    def test_refresh(self, base_url, admin_session):
        url = base_url + "login"
        session, _ = admin_session
        resp = session.post(url, data=json.dumps(admin_user_data))
        assert OK == resp.status_code
        assert OK == resp.json().get("status")
