from typing import Type

from aenum import Enum, extend_enum
from pydantic import Field
from src.api.v1.search_params.search_params_genres import GenreSearchParams
from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.base import BaseMixin
from src.services.service_base import Service


class FilmSchema(BaseMixin):
    title: str
    imdb_rating: float = Field(default=None)


class GenreSchema(BaseMixin):
    name: str
    description: str = None


class PersonSchema(BaseMixin):
    full_name: str
    film_ids: list = Field(default=None)


class SortImdbRating(str, Enum):
    a = "-imdb_rating"
    b = "imdb_rating"


class GenreEnum(str, Enum):
    @classmethod
    async def update_genre(cls) -> Type["GenreEnum"]:
        for genre in await get_all_genres():
            try:
                extend_enum(GenreEnum, genre.get("id"), genre.get("name"))
            except TypeError:
                pass
        return GenreEnum


async def get_all_genres() -> list[dict]:
    """Возвращает Список жанров"""
    service = Service(redis=await get_redis(), elastic=await get_elastic())
    if data := await service.get_data(
        "", GenreSearchParams().get_search_parameters_by_genres(page_size=200)
    ):
        return data
    return []
