import redis
from src.core.config import settings

db_redis = redis.Redis(
    host=settings.redis_host, port=settings.redis_port, db=settings.auth_redis_db
)
