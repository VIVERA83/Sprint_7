import asyncio
from typing import Optional, Union

import orjson
from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from src.models.search_args import SearchARGS
from src.utils.backoff import before_execution

from .abstract_class import AbstractCache, AbstractStorage

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 500  # 5 минут !


class Service(AbstractStorage, AbstractCache):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.elastic = elastic
        self.redis = redis

    @staticmethod
    def cache(func):
        """Декоратор, который перед обращением пытается найти данные по ключе. Если
        данные не найдены передает управление декорированному методу, и если результат
        положительны ответ кладет к себе, далее возвращает результат запроса"""

        async def inner(cache: AbstractCache, key: str, *args, **kwargs):
            if data := await before_execution()(cache.get_cache)(key):
                return data
            if data := await before_execution()(func)(cache, key, *args, **kwargs):
                # запускаем задачу на добавление данных в кэш, не ждем ее выполнения
                asyncio.create_task(
                    before_execution()(cache.set_cache)(
                        key=key, value=orjson.dumps(data)
                    )
                )
                return data

        return inner

    @cache
    async def get_by_id(self, key: str, index: str, id_: str) -> Optional[dict]:
        """Метод возвращает данные из хранилища по id записи"""
        try:
            d = (await self.elastic.get(index=index, id=id_)).raw["_source"]
            return d
        except NotFoundError:
            return

    @cache
    async def get_data(
        self,
        url: str,
        search: SearchARGS = None,
    ) -> Optional[list[dict]]:
        """Метод возвращает данные по переданным параметрам поиска"""
        try:
            resp = await self.elastic.search(
                index=search.index,
                from_=search.from_,
                size=search.size,
                query=search.query,
                source=search.source,
                sort=search.sort,
            )
            return [el["_source"] for el in resp.get("hits").get("hits")]
        except NotFoundError:
            pass

    async def set_cache(self, key: str, value: bytes):
        """Метод, который заносит данные, key - выполняет роль ключа"""
        await self.redis.set(key, value, FILM_CACHE_EXPIRE_IN_SECONDS)

    async def get_cache(self, key: str) -> Union[dict, list[dict]]:
        """Метод, который возвращает данные по ключу"""
        if cache := await self.redis.get(key):
            return orjson.loads(cache)
