import json
from http.client import BAD_REQUEST, FORBIDDEN, NOT_FOUND, OK

import pytest  # noqa

from ..testdata.auth_data import expected, test_not_valid_user_data, test_user_data


class TestAuth:
    def test_get_user(self, admin_session, base_url, anonymous):
        session, user_id = admin_session
        url = base_url + "get_user?id=6f71b32b-e74d-4803-aab6-dc915dec01a0"
        # запрос ны выдачу не существующего пользователя
        assert NOT_FOUND == session.get(url).status_code
        assert NOT_FOUND == session.get(url).json().get("status")
        # запрос ны выдачу на реального пользователя
        url = base_url + "get_user?id=" + user_id
        assert OK == session.get(url).status_code
        assert OK == session.get(url).json().get("status")
        # запрос без прав доступа
        assert FORBIDDEN == anonymous("GET", url).status_code
        assert FORBIDDEN == anonymous("GET", url).json().get("status")

    def test_get_users(self, admin_session, base_url, anonymous):
        session, user_id = admin_session
        url = base_url + "get_users"
        # запрос на выдачу списка  с правами
        assert OK == session.get(url).status_code
        assert OK == session.get(url).json().get("status")
        # запрос на выдачу списка  без прав
        assert FORBIDDEN == anonymous("GET", url).status_code
        assert FORBIDDEN == anonymous("GET", url).json().get("status")

    def test_set_user(self, base_url, anonymous):
        url = base_url + "set_user"
        # запрос на регистрацию, невалидными полями
        resp = anonymous("POST", url, data=json.dumps(test_not_valid_user_data))
        assert BAD_REQUEST == resp.status_code
        assert expected == resp.json().get("message")
        # запрос на регистрацию пользователя
        resp = anonymous("POST", url, data=json.dumps(test_user_data))
        assert OK == resp.status_code
        assert OK == resp.json().get("status")
        # Попытка зарегистрироваться по данным которые уже есть в системе
        resp = anonymous("POST", url, data=json.dumps(test_user_data))
        assert BAD_REQUEST == resp.status_code
        assert BAD_REQUEST == resp.json().get("status")

    def test_login_password_update(self, base_url, anonymous, user_session):
        url = base_url + "login"
        # корректная авторизация
        session, _ = user_session
        resp = session.post(url, data=json.dumps(test_user_data))
        assert OK == resp.status_code
        assert OK == resp.json().get("status")
        # запрос на изменения пароля без прав
        url = base_url + "password_update"
        user_data = {"password": "test_password"}
        resp = anonymous("PUT", url, data=json.dumps(test_user_data))
        assert FORBIDDEN == resp.status_code
        assert FORBIDDEN == resp.json().get("status")
        # запрос на изменения обладая правами
        resp = session.put(url, json.dumps(user_data))
        assert OK == resp.status_code
        assert OK == resp.json().get("status")

    def test_user_history(self, base_url, admin_session):
        url = base_url + "user_history"
        # получить историю посещений
        session, _ = admin_session
        resp = session.get(url)
        assert OK == resp.status_code
        assert resp.json().get("data")
