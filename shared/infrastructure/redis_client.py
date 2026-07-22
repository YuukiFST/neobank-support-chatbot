"""Async Redis client wrapper."""

import redis.asyncio as redis

from shared.infrastructure.config import settings

redis_pool = redis.ConnectionPool.from_url(settings.redis_url, decode_responses=True)


async def get_redis() -> redis.Redis:  # type: ignore[type-arg]
    return redis.Redis(connection_pool=redis_pool)
