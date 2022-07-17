from functools import lru_cache
from http import HTTPStatus
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends, HTTPException
from icecream import ic
from src.api.v1.model.search_args import SearchARGS
from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.services.service_base import Service


@lru_cache()
def get_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> Service:
    return Service(redis, elastic)


class BaseAPI:
    service: Optional[Service] = Depends(get_service)

    async def get_data(
        self, url: str, query: SearchARGS, err_msg: str
    ) -> Optional[list[dict]]:
        if data := await self.service.get_data(
            key=url,
            search=query,
        ):
            return data
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=err_msg)

    async def get_data_by_id(
        self, index: str, id_: str, url: str, err_msg
    ) -> Optional[dict]:
        if data := await self.service.get_by_id(index=index, id_=id_, key=url):
            return data
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=err_msg)
