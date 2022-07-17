import typing
from uuid import UUID

from fastapi import Request
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from src.api.v1.model.api_model import FilmSchema, GenreEnum, SortImdbRating
from src.api.v1.model.query import (
    QueryCaption,
    QueryGenre,
    QueryPageNumber,
    QueryPageSize,
    QuerySort,
)
from src.api.v1.search_params.search_params_films import FilmSearchParams
from src.models.film import Film

from .api_base import BaseAPI

film_router = InferringRouter()


@cbv(film_router)
class FilmAPI(BaseAPI, FilmSearchParams):
    @film_router.get(
        "/<uuid:UUID>/",
        description="Возвращает полное описание фильма по его id",
        summary="Описание фильма",
        tags=["Полнотекстовый поиск по id"],
        response_description="Название и рейтинг фильмы",
        response_model=Film,
    )
    async def get_film_details(self, request: Request, film_id: UUID) -> dict:
        return await self.get_data_by_id(
            index="movies",
            id_=str(film_id),
            url=str(request.url),
            err_msg="film not found",
        )

    @film_router.get(
        "/",
        description="Возвращает список фильмов согласно условию сортировки",
        summary="Список фильмов",
        response_description="Все данные о фильме",
        tags=["Получить список"],
        response_model=list[FilmSchema],
    )
    async def films(
        self,
        request: Request,
        sort: SortImdbRating = QuerySort,
        filter_genre: GenreEnum = QueryGenre,
        page_size: int = QueryPageSize,
        page_number: int = QueryPageNumber,
    ) -> list[dict]:
        return await self.get_data(
            url=str(request.url),
            query=self.get_search_parameters_by_top(
                sort=sort,
                genre_id=filter_genre.name if filter_genre else None,
                page_size=page_size,
                page_number=page_number,
            ),
            err_msg="movies not found",
        )

    @film_router.get(
        "/search/",
        description="Поиск фильмов по названию",
        summary="Поиск фильма по названию",
        response_description="Название и рейтинг фильма",
        tags=["Полнотекстовый поиск по ключевым словам"],
        response_model=list[FilmSchema],
    )
    async def film_search(
        self,
        request: Request,
        captain: str = QueryCaption,
        page_size: int = QueryPageSize,
        page_number: int = QueryPageNumber,
    ) -> list[dict]:
        return await self.get_data(
            url=str(request.url),
            query=self.get_search_parameters_by_title(
                title=captain, page_size=page_size, page_number=page_number
            ),
            err_msg="movies not found",
        )
