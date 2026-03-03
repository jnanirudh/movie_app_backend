import redis
import json
from typing import Optional, Any
from app.config import settings

# Connect to Redis
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

# Cache TTLs in seconds
TTL_POPULAR_MOVIES = 3600       # 1 hour
TTL_MOVIE_DETAILS = 86400       # 24 hours
TTL_SEARCH_RESULTS = 600        # 10 minutes
TTL_REVIEWS = 300               # 5 minutes


def cache_get(key: str) -> Optional[Any]:
    """Get a value from cache. Returns None if missing or expired."""
    try:
        value = redis_client.get(key)
        return json.loads(value) if value else None
    except Exception:
        # If Redis is down, don't crash the app — just miss the cache
        return None


def cache_set(key: str, value: Any, ttl: int) -> None:
    """Store a value in cache with TTL (seconds)."""
    try:
        redis_client.setex(key, ttl, json.dumps(value))
    except Exception:
        pass  # Silent fail — app works without cache, just slower


def cache_delete(key: str) -> None:
    """Delete a cache key (use when data changes)."""
    try:
        redis_client.delete(key)
    except Exception:
        pass


def cache_delete_pattern(pattern: str) -> None:
    """Delete all keys matching a pattern. e.g. 'movie:*'"""
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    except Exception:
        pass