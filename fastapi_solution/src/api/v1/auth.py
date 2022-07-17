from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError
from fastapi import Request
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from src.core.config import Settings
from src.models.auth import User

from .api_base import BaseAPI

auth_router = InferringRouter()


@cbv(auth_router)
class AuthAPI(BaseAPI):
    @auth_router.post(
        "/",
        description="Авторизация на сервисе",
        tags=["Авторизация"],
    )
    async def login(self, request: Request, user: User) -> dict:
        url = f"http://{Settings().auth_host}:{Settings().auth_port}/auth/api/v1/login"
        resp = {}
        try:
            resp = await ClientSession().post(url=url, data=user.json())
        except ClientConnectorError as e:
            return {"details": "Error "}
        request.session["token"] = resp.headers.get("token")
        request.cookies["refresh_token"] = resp.cookies.get("refresh_token").value
        return await resp.json()
