import abc
from typing import Optional, Union


class AbstractCache(abc.ABC):
    @abc.abstractmethod
    def set_cache(self, key: str, value: bytes, expire: int):
        """Метод, который заносит данные в кэш key - выполняет роль ключа"""
        pass

    @abc.abstractmethod
    def get_cache(self, key: str) -> Union[dict, list[dict]]:
        """Метод, который возвращает данные по ключу - выполняет роль ключа"""
        pass


class AbstractStorage(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, *args, **kwargs) -> Optional[dict]:
        """Метод возвращает запись по id записи"""
        pass

    @abc.abstractmethod
    def get_data(self, *args, **kwargs) -> Optional[list[dict]]:
        """Метод возвращает запись"""
        pass

    @abc.abstractmethod
    def set_data(self, *args, **kwargs):
        """Метод добавляет запись"""
        pass

    @abc.abstractmethod
    def update_data(self, *args, **kwargs):
        """Метод обновляет запись"""
