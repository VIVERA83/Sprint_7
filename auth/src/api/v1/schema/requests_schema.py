from dataclasses import dataclass
from uuid import UUID

from marshmallow import Schema, fields

from .mixins_schema import BaseMixin


@dataclass
class Id:
    id: UUID


@dataclass
class Login:
    email: str
    password: str
    id: UUID = None


@dataclass
class Path:
    path: str
    id: UUID = None


class IdSchema(BaseMixin):
    __model__ = Id


class LoginSchema(BaseMixin):
    __model__ = Login

    email = fields.Email(required=True)
    password = fields.Str(required=True)


class PathSchema(BaseMixin):
    __model__ = Path

    path = fields.Str(required=True)


class PaginateSchema(Schema):
    per_page = fields.Int(default=10)
    page = fields.Int(default=1)
