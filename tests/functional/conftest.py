import json
import os

import aiohttp
import pytest
from aioredis import Redis
from elasticsearch import AsyncElasticsearch, helpers
from elasticsearch.exceptions import BadRequestError, ConnectionError, NotFoundError

from .settings import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__name__)))


@pytest.fixture(scope="function")
async def elastic_client():
    client = AsyncElasticsearch(settings.elastic_dns)
    yield client
    await client.close()


@pytest.fixture(scope="function")
async def redis_client():
    client = Redis(host=settings.redis_host, port=settings.redis_port)
    yield client
    await client.close()


@pytest.fixture(scope="function")
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope="function")
async def clear_cache(redis_client):
    await redis_client.flushall(asynchronous=True)


@pytest.fixture(scope="function")
async def create_db(elastic_client):
    prefix = "/functional/testdata/"
    paths = [
        "person.json",
        "genre.json",
        "movies.json",
    ]
    indexs = ["person", "genre", "movies"]

    for index in indexs:
        try:
            await elastic_client.indices.delete(index=index)
            await elastic_client.indices.create(index=index)
        except BadRequestError:
            pass
        except ConnectionError:
            pass
        except NotFoundError:
            pass

    for path, index in zip(paths, indexs):
        with open(BASE_DIR + prefix + path) as file:
            data = json.loads(file.read())
            data = add_id(data)
            await helpers.async_bulk(
                client=elastic_client, actions=data, index=index, refresh="true"
            )


async def get_test(name: str, uri: str, session: aiohttp.ClientSession, db: dict):
    for key, expected in db[name]["quest"].items():
        url = settings.api_url + uri + key
        async with session.get(url) as resp:
            assert expected == await resp.json()


def add_id(data: list[dict]) -> list[dict]:
    for index, item in enumerate(data.copy()):
        data[index].update({"_id": data[index]["_source"]["id"]})
    return data
