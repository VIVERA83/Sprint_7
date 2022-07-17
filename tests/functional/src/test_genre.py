import random

import pytest

from ..settings import settings
from ..testdata.data_genre import expected_drama, expected_not_valid_id


class TestGenre:
    URL = settings.api_url
    index = "genre"

    @pytest.mark.asyncio
    # проверка на консистентность индекса
    async def test_count_documents_in_genres(self, session, elastic_client, create_db):
        url = settings.api_url + "genres/"
        async with session.get(url) as resp_api, elastic_client as resp_el:
            count_api = len(await resp_api.json())
            count_el = (await resp_el.count(index=self.index)).raw.get("count")
        assert count_el == count_api

    @pytest.mark.asyncio
    # выемка по случайному id - 5 попыток
    async def test_get_document(self, session, elastic_client, create_db):
        count = (await elastic_client.count(index=self.index)).raw.get("count")
        for i in range(5):
            async with elastic_client as resp_el:
                if (
                    data := (
                        await resp_el.search(
                            index="genre",
                            from_=random.randint(0, count),
                            size=1,
                            query={"match_all": {}},
                        )
                    )
                    .raw.get("hits")
                    .get("hits")
                ):
                    id_ = data[0].get("_source").get("id")
                    url = self.URL + f"genres/%3Cuuid:UUID%3E?genre_id={id_}"

                    async with session.get(url) as resp_api:
                        data = await resp_api.json()
                        assert data["id"] == id_

    # поиск конкретного жанра;
    @pytest.mark.asyncio
    async def test_search_drama(self, session, elastic_client, create_db):
        url = self.URL + f"genres/%3Cuuid:UUID%3E?genre_id={expected_drama['id']}"
        async with session.get(url) as resp_api:
            data = await resp_api.json()
            assert expected_drama == data
        return data

    # поиск конкретного жанра отрицательный ответ;
    @pytest.mark.asyncio
    async def test_search_not_found(self, session, elastic_client):
        expected_not_found = {"detail": "genre not found"}
        url = (
            self.URL + f"genres/%3Cuuid:UUID%3E?genre_id={expected_drama['id'][:-1]}F"
        )  # неверный id
        async with session.get(url) as resp_api:
            data = await resp_api.json()
            assert expected_drama != data
            assert expected_not_found == data

    # проверка на невалидный id
    @pytest.mark.asyncio
    async def test_no_valid_id(self, session, elastic_client, create_db):
        fail_id = "invalid data"
        url = self.URL + f"genres/%3Cuuid:UUID%3E?genre_id={fail_id}"
        async with session.get(url) as resp_api:
            data = await resp_api.json()
            assert expected_not_valid_id == data

    # проверка кэша наличие данных
    @pytest.mark.asyncio
    async def test_cache(
        self, clear_cache, redis_client, session, elastic_client, create_db
    ):
        data_elastic = await self.test_search_drama(session, elastic_client, create_db)
        data_redis = await self.test_search_drama(session, elastic_client, create_db)
        info: dict = await redis_client.info()
        assert info.get("db1")  # есть записи
        assert 1 == info.get("db1").get("keys")  # кол-во записей
        assert data_redis == data_elastic  # проверка консистентность
