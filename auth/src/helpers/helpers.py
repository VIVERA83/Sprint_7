import json
import re
from functools import wraps
from json import JSONDecodeError
from typing import Any, Callable, Literal, Type, Union

from flask import Response, request
from marshmallow import Schema, ValidationError
from user_agents import parse

DEVICE_TYPE = Literal["pc", "mobile", "tablet", "other"]

SchemaType = Type[Schema]

STATUS_MESSAGE = {
    200: "Ok",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Access Denied",
    404: "Not Found",
}


class CustomResponse(Response):
    def __init__(
        self,
        data: Union[list[dict], dict, tuple[dict]] = None,
        message: Union[list[dict], dict, str] = None,
        status: int = 200,
        content_type: str = "application/json",
        headers=None,
    ):
        response = {
            "data": data,
            "message": message if message else STATUS_MESSAGE[status],
            "status": status,
        }
        super(Response, self).__init__(
            content_type=content_type,
            status=status,
            response=json.dumps(response),
            headers=headers,
        )


def get_swagger_path(file_name: str, path: str = "/src/api/v1/api_doc/") -> str:
    """Вспомогательная функция которая возвращает относительный путь до swagger файла"""
    return path + file_name


def get_request_query() -> dict[str, str]:
    """Вспомогательная функция возвратит, аргументы запроса, для получения из GET запроса"""
    return request.args.to_dict()


def get_request_body() -> dict[str, str]:
    """Вспомогательная функция возвратит, аргументы запроса, для получения из POST запроса"""
    try:
        return json.loads(request.data)
    except JSONDecodeError:
        return request.json


def validate_request(
    schema: SchemaType,
    data: Union[get_request_query, get_request_body],
    only: list[str] = None,
    mock: dict[str, Any] = None,
) -> Union[Callable, dict]:
    """Валидация входящих параметров запроса, на соответствие схемы"""

    def func_wrapper(func: Callable):
        @wraps(func)
        def inner(*args, **kwargs):
            check_data: dict = data()
            if mock:
                check_data.update(mock)
                only.extend(mock.keys())
            try:
                schema(only=only).load(check_data)
            except ValidationError as er:
                args: Union[list, tuple] = er.args
                return CustomResponse(message=args, status=400)
            return func(*args, **kwargs)

        return inner

    return func_wrapper


def get_error_dict(e: Exception) -> dict:
    """Вытаскивает из Exception имя переменно и сообщение об ошибке связанной с данной переменно"""
    if isinstance(e, KeyError):
        return {key: "Not Found" for key in e.args}
    try:
        result = re.findall(pattern=r"\(.*?\)", string=str(e))
        return {result[1][1:-1]: "problems"}
    except Exception:
        return {"error": "Bad data"}


def get_type_devices(user_agent_string=str) -> DEVICE_TYPE:
    """Функция определят тип устройства с которого пришел запрос,
    на текущий момент определено 3 устройства:
    pc, mobile, tablet все остальное заносим в other"""
    ua = parse(user_agent_string)
    return {
        ua.is_pc: "pc",
        ua.is_mobile: "mobile",
        ua.is_tablet: "tablet",
    }.get(True, "other")
