from uuid import UUID

from fastapi import Request
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from src.api.v1.model.api_model import GenreSchema
from src.api.v1.search_params.search_params_genres import GenreSearchParams

from .api_base import BaseAPI

genre_router = InferringRouter()


@cbv(genre_router)
class GenreAPI(BaseAPI, GenreSearchParams):
    @genre_router.get(
        "/<uuid:UUID>/",
        description="Получить описание жанра по его id",
        summary="Описание жанра",
        response_description="Жанр и его описание",
        tags=["Полнотекстовый поиск по id"],
        response_model=GenreSchema,
    )
    async def get_genre_details(self, request: Request, genre_id: UUID) -> dict:
        return await self.get_data_by_id(
            index="genre",
            id_=str(genre_id),
            url=str(request.url),
            err_msg="genre not found",
        )

    @genre_router.get(
        "/",
        description="Получить список жанров",
        summary="Список жанров",
        response_description="Список жанров и их описания",
        tags=["Получить список"],
        response_model=list[GenreSchema],
    )
    async def get_genres(self, request: Request) -> list[dict]:
        result = await self.get_data(
            url=str(request.url),
            query=self.get_search_parameters_by_genres(),
            err_msg="genres not found",
        )

        return result
