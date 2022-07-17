from datetime import date
from typing import Optional
from uuid import UUID

from .base import BaseMixin


class Person(BaseMixin):
    full_name: str
    birth_date: Optional[date] = None
    film_ids: Optional[list[UUID]] = None
