"""In-memory sliding-window rate limiter for chat endpoints."""

from __future__ import annotations

import time
from collections import defaultdict

_buckets: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(key: str, limit: int, window_seconds: int = 60) -> bool:
    """Return True if request is allowed, False if rate limit exceeded."""
    now = time.time()
    bucket = [t for t in _buckets[key] if now - t < window_seconds]
    if len(bucket) >= limit:
        _buckets[key] = bucket
        return False
    bucket.append(now)
    _buckets[key] = bucket
    return True


def reset_rate_limits() -> None:
    """Clear all buckets — for tests."""
    _buckets.clear()
