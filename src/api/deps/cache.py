from typing import Annotated
from src.core.cache_service import CacheService
from fastapi import Depends
from redis.asyncio import Redis
from src.core.cache import get_redis


RedisDep = Annotated[Redis, Depends(get_redis)]


def get_cache_service(redis_client: RedisDep) -> CacheService:
    return CacheService(redis_client)


CacheServiceDep = Annotated[CacheService, Depends(get_cache_service)]
