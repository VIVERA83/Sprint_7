import pytest

from ..utils.waiters import waiters_one


class TestConnectDB:
    @pytest.mark.asyncio
    async def test_connect_to_elastic(self, elastic_client):
        assert await waiters_one(elastic_client), "Elasticsearch connection failed"

    @pytest.mark.asyncio
    async def test_connect_to_redis(self, redis_client):
        assert await waiters_one(redis_client), "Redis connection failed"
