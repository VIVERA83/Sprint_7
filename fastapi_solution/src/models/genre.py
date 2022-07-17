from uuid import UUID

from .base import BaseRoleMixin, Config


class Genre(Config):
    id: UUID = None
    name: str = None
    description: str = None


class GenreShort(BaseRoleMixin):
    pass
