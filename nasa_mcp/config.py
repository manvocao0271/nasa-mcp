"""Runtime configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_CACHE_PATH = Path.home() / ".cache" / "nasa-mcp" / "cache.sqlite3"


@dataclass(frozen=True)
class Config:
    """Resolved server configuration."""

    nasa_api_key: str
    cache_path: Path
    request_timeout_seconds: float


def load() -> Config:
    """Read config from the environment, applying defaults."""
    raise NotImplementedError
