import pytest

from ..conftest import get_test
from ..testdata.movies_data import db


class TestFilms:
    @pytest.mark.asyncio
    async def test_get_film_by_id(self, session, create_db):
        # поиск по id
        name = "get_film_by_id"
        uri = "films/<uuid:UUID>?film_id="
        await get_test(name, uri, session, db)

    @pytest.mark.asyncio
    async def test_search_by_title(self, session, create_db):
        # поиск по названию фильма
        name = "search_by_title"
        uri = "films/search/?captain="
        await get_test(name, uri, session, db)

    @pytest.mark.asyncio
    async def test_filter_genre(self, session, create_db):
        # поиск по названию фильма
        name = "filter_genre"
        uri = "films/?filter_genre="
        await get_test(name, uri, session, db)

    @pytest.mark.asyncio
    async def test_filter_genre_page_2_size_3(self, session, create_db):
        # поиск по названию фильма, фильтр пагинация
        name = "filter_genre_page_2_size_3"
        uri = "films/?filter_genre="
        await get_test(name, uri, session, db)
