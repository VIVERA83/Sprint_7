from dataclasses import dataclass
from typing import Union
from urllib.parse import urlencode
from requests import post
from src.core.config import settings


@dataclass
class Yandex:
    client_id: str = settings.yandex_client_id
    client_secret: str = settings.yandex_client_secret
    base_url: str = "https://oauth.yandex.ru/"
    network_name: str = "Yandex"
    redirect = f"http://{settings.redirect_host}:{settings.auth_port}{settings.auth_base_path}login_to_social_network/?social_network=Yandex"
    __uri = "authorize?response_type=code&client_id={}&redirect_uri={}".format(client_id, redirect)

    @property
    def auth_url(self) -> str:
        return self.base_url + self.__uri

    def _get_data(self, code: int) -> str:
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        return urlencode(data)

    def get_user_data(self, code: int) -> dict:
        resp = post(self.base_url + "token", data=self._get_data(code))
        token = resp.json().get('access_token')
        headers = {"Content-Type": "application/json",
                   "Accept": "application/json",
                   "Authorization": f"OAuth {token}"}
        url = "https://login.yandex.ru/info?format=json"
        resp = post(url, headers=headers).json()

        data = {
            "social_id": resp.get("id"),
            "social_name": self.network_name,
            "email": resp.get("default_email"),
            "token": token,
        }
        return data


@dataclass
class VK:
    client_id: str = "8218728"
    client_secret: str = "ryQmAFkoWlXBTnNYS6TH"
    base_url: str = "https://oauth.vk.com/"
    network_name: str = "VK"
    redirect = f"http://{settings.redirect_host}:{settings.auth_port}{settings.auth_base_path}login_to_social_network/?social_network=VK"
    __uri = "authorize?client_id={}&display=page&redirect_uri={}&scope=email&response_type=code".format(client_id,
                                                                                                        redirect)

    @property
    def auth_url(self) -> str:
        return self.base_url + self.__uri

    def _get_data(self, code: int) -> str:
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect,
            "code": code,
        }
        return urlencode(data)

    def get_user_data(self, code: int) -> dict:
        # получаем токен

        resp = post(self.base_url + "access_token", data=self._get_data(code)).json()
        data = {
            "social_id": resp.get("user_id"),
            "social_name": self.network_name,
            "email": resp.get("email"),
            "token": resp.get("token"),
        }

        return data


TYPE_NETWORKS = Union[Yandex, VK]
networks = {
    "Yandex": Yandex,
    "VK": VK
}
