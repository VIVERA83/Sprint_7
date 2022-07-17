from uuid import UUID

import orjson
from aenum import Enum

# Используем pydantic для упрощения работы при перегонке данных из json в объекты
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class Config(BaseModel):
    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class BaseMixin(Config):
    id: UUID


class RoleEnum(str, Enum):
    actor = "actor"
    writer = "writer"
    director = "director"


class BaseRoleMixin(BaseMixin):
    name: str
