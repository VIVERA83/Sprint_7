import json
import uuid
from http.client import BAD_REQUEST, OK

import pytest  # noqa

from ..testdata.role_data import role


class TestRole:
    def test_set_role(
        self,
        base_url,
        admin_session,
    ):
        session, _ = admin_session
        # Добавить роль
        url = base_url + "set_role"
        resp = session.post(url, json.dumps(role))
        assert OK == resp.status_code
        # Добавить роль которая уже есть
        url = base_url + "set_role"
        resp = session.post(url, json.dumps(role))
        assert BAD_REQUEST == resp.status_code

    def test_role(self, base_url, admin_session):
        session, id_user = admin_session
        # Список ролей
        url = base_url + "get_roles"
        resp = session.get(url)

        assert OK == resp.status_code
        assert OK == resp.json().get("status")
        # Обновить роль
        role_id = resp.json().get("data")[-1].get("id")
        role_name = uuid.uuid4().hex[:10]
        role_data = {"id": role_id, "name": f"test_{role_name}"}
        url = base_url + "update_role"
        resp = session.put(url, data=json.dumps(role_data))
        assert OK == resp.status_code
        assert OK == resp.json().get("status")
        # Назначить роль пользователю
        new_user_role = {"id_user": id_user, "id_role": role_id}
        url = base_url + "assign_role"
        resp = session.post(url, data=json.dumps(new_user_role))
        assert OK == resp.status_code
        # забрать роль пользователю
        url = base_url + "del_user_role"
        role_g = {"id_role": role_id, "id_user": id_user}
        resp = session.delete(url, data=json.dumps(role_g))
        assert OK == resp.status_code
        # Удалить роль
        url = base_url + f"del_role?id={role_id}"
        resp = session.delete(url)
        assert OK == resp.status_code
