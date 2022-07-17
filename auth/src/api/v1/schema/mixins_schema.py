import datetime
import uuid
from typing import Any, Optional

from marshmallow import Schema, fields, post_load
from marshmallow_dataclass import dataclass


class DateMixin(Schema):
    created_at = fields.DateTime(
        dump_default=datetime.datetime.now, missing=datetime.datetime.now
    )
    updated_at = fields.DateTime(
        dump_default=datetime.datetime.now, missing=datetime.datetime.now
    )

    class Meta:
        dateformat = "%Y-%m-%dT%H:%M:%S.%f"


class BaseMixin(Schema):
    __model__: Optional[dataclass] = None

    id = fields.UUID(dump_default=uuid.uuid4, missing=uuid.uuid4)

    @post_load
    def make_object(self, data: dict[str, Any], **kwargs) -> dataclass:
        return self.__model__(**data)
