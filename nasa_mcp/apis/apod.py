"""Astronomy Picture of the Day (APOD) client.

Endpoints: https://api.nasa.gov/planetary/apod
"""

import httpx
from datetime import date
from nasa_mcp.config import Config
from nasa_mcp.errors import NasaApiError, NotFoundError, RateLimitError


async def get_apod(config: Config, target_date: date | None = None) -> dict:
    """Fetch the Astronomy Picture of the Day for the given date (or today if omitted)."""

    params: dict[str, str] = {"api_key": config.nasa_api_key}
    if target_date is not None:
        params["date"] = target_date.isoformat()

    async with httpx.AsyncClient(timeout=config.request_timeout) as client:
        response = await client.get(
            "https://api.nasa.gov/planetary/apod",
            params=params,
        )

    match response.status_code:
        case status if 200 <= status < 300:
            return response.json()
        case 429:
            raise RateLimitError(response.text)
        case 404:
            raise NotFoundError(response.text)
        case _:
            raise NasaApiError(f"APOD returned {response.status_code}: {response.text}")
