"""SQLite-backed response cache with per-resource TTLs.

Cache key format: ``{api_name}:{tool_name}:{hash_of_params}``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class Cache:
    """TTL-aware SQLite cache for NASA API responses."""

    def __init__(self, path: Path) -> None:
        raise NotImplementedError

    def get(self, key: str) -> Any | None:
        """Return the cached value for ``key`` if present and unexpired."""
        raise NotImplementedError

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Store ``value`` under ``key`` with a TTL."""
        raise NotImplementedError

    def stats(self) -> dict[str, Any]:
        """Return hit rate, entry count, and on-disk size."""
        raise NotImplementedError
