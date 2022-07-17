import abc
from typing import Optional, Union

import orjson
from src.models.search_args import SearchARGS


class AbstractCache(abc.ABC):
    @abc.abstractmethod
    async def set_cache(self, key: str, value: bytes):
        """Метод, который заносит данные в кэш key - выполняет роль ключа"""
        pass

    @abc.abstractmethod
    async def get_cache(self, key: str) -> Union[dict, list[dict]]:
        """Метод, который возвращает данные по ключу - выполняет роль ключа"""
        pass

    # @staticmethod
    # def cache(func):
    #     """Декоратор, который перед обращением пытается найти данные по ключе. Если
    #     данные не найдены передает управление декорированному методу, и если результат
    #     положительны ответ кладет к себе, далее возвращает результат запроса"""
    #
    #     async def inner(cache: AbstractCache, key: str, *args, **kwargs):
    #         if data := await cache.get_cache(key):
    #             return data
    #         if data := await func(cache, key, *args, **kwargs):
    #             await cache.set_cache(key=key, value=orjson.dumps(data))
    #             return data
    #
    #     return inner


class AbstractStorage(abc.ABC):
    @abc.abstractmethod
    async def get_by_id(self, index: str, id_: str) -> Optional[dict]:
        """Метод возвращает данные из хранилища по id записи"""
        pass

    @abc.abstractmethod
    async def get_data(
        self,
        search: SearchARGS = None,
    ) -> Optional[list[dict]]:
        """Метод возвращает данные по переданным параметрам поиска"""
        pass
