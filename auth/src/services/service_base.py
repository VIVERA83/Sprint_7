import json
from abc import ABC
from typing import Any, Optional

from flask_sqlalchemy import Model, SQLAlchemy
from redis import Redis
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from src.core.config import settings
from src.db.models.db_models import UserSignIn
from src.db.postgres import db_postgres
from src.db.redis import db_redis

from .abstract_class import AbstractCache, AbstractStorage


class Service(AbstractStorage, AbstractCache, ABC):
    def __init__(self, storage: SQLAlchemy, cache: Redis, expire: int):
        self.storage = storage
        self.cache = cache
        self.expire = expire

    def set_cache(self, key: str, value: bytes, expire: int):
        """Метод, который заносит данные в кэш key - выполняет роль ключа"""
        return self.cache.set(key, value, expire, get=True)

    def get_cache(self, key: str) -> bytes:
        """Метод, который возвращает данные по ключу - выполняет роль ключа"""
        if data := service.cache.get(key):
            return json.loads(data)

    def delete_cache(self, key: str):
        self.cache.delete(key)

    def del_cache(self, keys: str):
        """Метод, который уделяет данные по ключу"""
        return self.cache.delete(keys)

    def get_by_id(self, id_: str, model: db_postgres.Model) -> db_postgres.Model:
        """Метод возвращает запись по id записи"""
        return self.storage.session.query(model).get(id_)

    def get_history(
        self, id_: str, model: db_postgres.Model
    ) -> Optional[list[UserSignIn]]:
        """Метод возвращает запись"""
        return (
            self.storage.session.query(model)
            .filter(
                model.user_id == id_,
            )
            .all()
        )

    def get_data(
        self,
        model: Model,
    ) -> Optional[list[dict]]:
        """Метод возвращает запись"""
        result = []
        for item in model.query.all():
            result.append(item)
        return result

    def get_data_user_roles(
        self, model: db_postgres.Model, user_role: db_postgres.Model
    ) -> Optional[Model]:
        """Получить данные по фильтру"""
        return (
            self.storage.session.query(model)
            .filter(
                and_(
                    model.id_role == user_role.id_role.hex,
                    model.id_user == user_role.id_user.hex,
                )
            )
            .first()
        )

    def get_data_by_email(
        self, model: db_postgres.Model, email: str
    ) -> Optional[Model]:
        """Получить данные по фильтру"""
        return self.storage.session.query(model).filter(model.email == email).first()

    def set_data(self, model: db_postgres.Model) -> db_postgres.Model:
        """Метод добавляет запись"""
        self.storage.session.add(model)
        try:
            self.storage.session.commit()
        except IntegrityError as e:
            # вставка не удалась из-за того что данный ключ не уникален
            self.storage.session.rollback()
            raise e

    def update_data(
        self, id_: str, model: db_postgres.Model, data: dict[str, Any]
    ) -> bool:
        """Метод обновляет записи по id"""
        return self.storage.session.query(model).filter(model.id == id_).update(data)

    def delete(self, id_: str, model: Model) -> bool:
        if obj := self.storage.session.query(model).get(id_):
            self.storage.session.delete(obj)
            self.storage.session.commit()
            return True


service = Service(db_postgres, db_redis, settings.auth_redis_expire)
