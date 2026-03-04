import time
import threading
from typing import Any, Optional

class InMemoryCache:

    def __init__(self):
        self._store: dict[str, dict] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get a value. Returns None if missing or expired."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None

            # Check if expired
            if time.time() > entry["expires_at"]:
                del self._store[key]
                return None

            return entry["value"]

    def set(self, key: str, value: Any, ttl: int) -> None:
        """Store a value with TTL in seconds."""
        with self._lock:
            self._store[key] = {
                "value": value,
                "expires_at": time.time() + ttl,
            }

    def delete(self, key: str) -> None:
        """Delete a specific key."""
        with self._lock:
            self._store.pop(key, None)

    def delete_pattern(self, prefix: str) -> None:
        """Delete all keys starting with a prefix."""
        with self._lock:
            keys_to_delete = [k for k in self._store if k.startswith(prefix)]
            for key in keys_to_delete:
                del self._store[key]

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries. Call this periodically.
        Returns number of entries removed.
        """
        with self._lock:
            now = time.time()
            expired = [k for k, v in self._store.items() if now > v["expires_at"]]
            for key in expired:
                del self._store[key]
            return len(expired)

    def stats(self) -> dict:
        """How many entries are cached — useful for debugging."""
        with self._lock:
            now = time.time()
            total = len(self._store)
            active = sum(1 for v in self._store.values() if now <= v["expires_at"])
            return {"total_entries": total, "active_entries": active}


# Single instance used everywhere — like a singleton bean in Spring
cache = InMemoryCache()

# ── TTL Constants ──────────────────────────────────────────────────────
# All in seconds. Defined once here so you change them in one place.

TTL_POPULAR_MOVIES = 3600       # 1 hour  — changes rarely
TTL_MOVIE_DETAILS  = 86400      # 24 hours — almost never changes
TTL_SEARCH_RESULTS = 600        # 10 min  — user expects fresh results
TTL_REVIEWS        = 300        # 5 min   — can be slightly stale
TTL_WATCHLIST      = 60         # 1 min   — user expects near-real-time


# ── Convenience functions ──────────────────────────────────────────────
# These match the exact same function signatures as the Redis version.
# When you switch to Redis later, only this section changes.

def cache_get(key: str) -> Optional[Any]:
    return cache.get(key)

def cache_set(key: str, value: Any, ttl: int) -> None:
    cache.set(key, value, ttl)

def cache_delete(key: str) -> None:
    cache.delete(key)

def cache_delete_pattern(pattern: str) -> None:
    cache.delete_pattern(pattern)