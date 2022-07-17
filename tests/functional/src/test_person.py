import pytest

from ..conftest import get_test
from ..settings import settings
from ..testdata.person_data import db


class TestPerson:
    @pytest.mark.asyncio
    # проверка на консистентность индекса
    async def test_count_documents_in_person(
        self,
        session,
    ):
        name = "count_documents_in_person"
        params, expected = db[name]["quest"]
        uri = "films/?page[size]=" + params
        url = settings.api_url + uri
        async with session.get(url) as resp_api:
            count_doc = len(await resp_api.json())

        assert expected == count_doc

    @pytest.mark.asyncio
    # выемка по id - 2 попытки
    async def test_get_document(
        self,
        session,
    ):
        name = "get_document"
        uri = "person/<uuid:UUID>?person_id="
        await get_test(name, uri, session, db)

    @pytest.mark.asyncio
    # выемка по id - 2 попытки
    async def test_get_document_not_found(self, session):
        name = "get_document_not_found"
        uri = "person/<uuid:UUID>?person_id="
        await get_test(name, uri, session, db)

    @pytest.mark.asyncio
    # проверка на невалидный id
    async def test_no_valid_id(self, session):
        name = "no_valid_id"
        uri = "person/<uuid:UUID>?person_id="
        await get_test(name, uri, session, db)

    @pytest.mark.asyncio
    # поиск по имени
    async def test_search_by_name(self, session):
        name = "search_by_name"
        uri = "person/search/?captain="
        await get_test(name, uri, session, db)
