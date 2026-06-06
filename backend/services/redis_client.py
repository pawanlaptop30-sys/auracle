import redis.asyncio as aioredis
from config import settings
import json
import logging

logger = logging.getLogger(__name__)
redis_client = None


async def init_redis():
    global redis_client
    try:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        await redis_client.ping()
        logger.info("Redis connected")
    except Exception as e:
        logger.warning(f"Redis unavailable (caching disabled): {e}")
        redis_client = None


async def cache_get(key: str):
    if not redis_client:
        return None
    try:
        val = await redis_client.get(key)
        return json.loads(val) if val else None
    except Exception:
        return None


async def cache_set(key: str, data, ttl: int = 300):
    if not redis_client:
        return
    try:
        await redis_client.setex(key, ttl, json.dumps(data))
    except Exception:
        pass


async def cache_delete(key: str):
    if not redis_client:
        return
    try:
        await redis_client.delete(key)
    except Exception:
        pass
