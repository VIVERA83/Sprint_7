from uuid import UUID

from fastapi import Request
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from src.api.v1.model.api_model import FilmSchema, PersonSchema
from src.api.v1.model.query import QueryPageNumber, QueryPageSize, QueryPerson
from src.api.v1.search_params.search_params_person import PersonSearchParams

from .api_base import BaseAPI

person_router = InferringRouter()


@cbv(person_router)
class PersonAPI(BaseAPI, PersonSearchParams):
    @person_router.get(
        "/<uuid:UUID>/",
        description="Получить информацию о персону по id",
        summary="Данные о Персоне",
        response_description="Имя персоны, роль и в каких фильма принимал участие",
        tags=["Полнотекстовый поиск по id"],
        response_model=PersonSchema,
    )
    async def get_person_details(self, request: Request, person_id: UUID) -> dict:
        return await self.get_data_by_id(
            index="person",
            id_=str(person_id),
            url=str(request.url),
            err_msg="person not found",
        )

    @person_router.get(
        "/<uuid:UUID>/film/",
        description="Получить фильмы по id персоны",
        summary="Фильмы по персоне",
        response_description="Список фильмов по персоне",
        tags=["Полнотекстовый поиск по id"],
        response_model=list[FilmSchema],
    )
    async def get_movies_by_person_id(
        self, request: Request, person_id: UUID
    ) -> list[dict]:
        return await self.get_data(
            url=str(request.url),
            query=self.get_search_parameters_by_id(person_id=str(person_id)),
            err_msg="movies not found",
        )

    @person_router.get(
        "/search/",
        description="Поиск персонажа",
        summary="Поиск информации о персонаже по его имени",
        response_description="Список о персоне",
        tags=["Полнотекстовый поиск по ключевым словам"],
        response_model=list[PersonSchema],
    )
    async def get_persons_by_name(
        self,
        request: Request,
        captain: str = QueryPerson,
        page_size: int = QueryPageSize,
        page_number: int = QueryPageNumber,
    ) -> list[dict]:
        return await self.get_data(
            url=str(request.url),
            query=self.get_search_parameters_by_name(
                title=captain, page_size=page_size, page_number=page_number
            ),
            err_msg="person not found",
        )
