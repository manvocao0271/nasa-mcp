"""MCP server entry point. Registers tools and runs the stdio transport."""

from datetime import date, timedelta
import hashlib

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from nasa_mcp.config import load
from nasa_mcp.cache import Cache
from nasa_mcp.apis.apod import get_apod, search_apod
from nasa_mcp.apis.mars_rovers import get_rover_photos, get_rover_manifest

mcp = FastMCP("nasa-mcp")
config = load()
cache = Cache(config.cache_path)

LONG_TTL = 365 * 24 * 3600
SHORT_TTL = 4 * 3600


class GetApodInput(BaseModel):
    """Input validation for get_apod_tool."""

    target_date: date | None = Field(
        default=None,
        description="The date to look up ranging 1995-06-16 to present day. If omitted, return today's APOD.",
    )


@mcp.tool()
async def get_apod_tool(args: GetApodInput) -> dict:
    """Fetch NASA's Astronomy Picture of the Day (APOD) for a specific date, or today if no date is given.

    Returns a dict with `title`, `explanation`, `url`, `hdurl`, `date`, `media_type` (usually `"image"`, sometimes `"video"`), and `copyright` (when applicable).

    Use this for questions like "show me today's astronomy picture", "what was the APOD on July 14 1998", or "find the explanation for yesterday's NASA image of the day". Valid dates range from 1995-06-16 to today.
    """

    key = f"apod:get_apod:{hashlib.sha256(str(args.target_date).encode()).hexdigest()[:16]}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    response = await get_apod(config, args.target_date)

    ttl_seconds = (
        SHORT_TTL
        if args.target_date is None or args.target_date == date.today()
        else LONG_TTL
    )

    cache.set(key, response, ttl_seconds=ttl_seconds)
    return response


class SearchApodInput(BaseModel):
    """Input validation for search_apod_tool."""

    query: str = Field(
        description="The search input to match case-insensitively with title and/or explanation."
    )
    start_date: date | None = Field(
        default=None,
        description="The date to start for a ranged search (inclusive).",
    )
    end_date: date | None = Field(
        default=None,
        description="The date to end for a ranged search (inclusive).",
    )


@mcp.tool()
async def search_apod_tool(args: SearchApodInput) -> list[dict]:
    """Search NASA's Astronomy Picture of the Day (APOD) archive for entries whose title or explanation matches a keyword, within a date range.

    Matches `query` case-insensitively against each entry's `title` and `explanation`. Returns a list of dicts, each containing `title`, `explanation`, `url`, `hdurl`, `date`, `media_type` (usually `"image"`, sometimes `"video"`), and `copyright` (when applicable). The list is empty if nothing matches.

    If `start_date` and `end_date` are omitted, defaults to the last 30 days. Valid dates range from 1995-06-16 to today.

    Use this for questions like "find APODs about black holes from 2024", "show me Mars photos from June 2023", or "any APODs mentioning Hubble in the last month?".
    """

    start_date = args.start_date or (date.today() - timedelta(days=30))
    end_date = args.end_date or date.today()

    key_input = f"{args.query}|{start_date}|{end_date}"
    key = f"apod:search_apod:{hashlib.sha256(key_input.encode()).hexdigest()[:16]}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    response = await search_apod(config, args.query, start_date, end_date)

    ttl = 365 * 24 * 3600
    if end_date == date.today():
        ttl = 4 * 3600
    cache.set(key, response, ttl_seconds=ttl)

    return response


@mcp.tool()
async def get_rover_photos_tool(
    rover_name: str,
    sol: int | None = None,
    earth_date: date | None = None,
    camera: str | None = None,
) -> dict:
    """Fetch Mars rover photos by sol or Earth date, optionally filtered by camera."""
    if (sol is None) == (earth_date is None):
        raise ValueError("Provide exactly one of sol or earth_date.")

    if sol is not None and sol < 0:
        raise ValueError("sol must be greater than or equal to 0.")

    rover = rover_name.strip().lower()
    camera_name = camera.strip().lower() if camera else None

    date_key = f"sol:{sol}" if sol is not None else f"earth_date:{earth_date.isoformat()}"
    camera_key = camera_name or "all"
    key = f"mars_rover_photos:{rover}:{date_key}:camera:{camera_key}"

    cached = cache.get(key)
    if cached is not None:
        return cached
    response = await get_rover_photos(
        config,
        rover_name=rover,
        sol=sol,
        earth_date=earth_date,
        camera=camera_name,
    )

    cache.set(key, response, ttl_seconds=LONG_TTL)
    return response


@mcp.tool()
async def get_rover_manifest_tool(rover_name: str) -> dict:
    """Fetch the mission manifest for a specific Mars rover, including landing date, launch date, status, and total photos taken."""
    rover = rover_name.strip().lower()
    key = f"mars_rover_manifest:{rover}"

    cached = cache.get(key)
    if cached is not None:
        return cached
    response = await get_rover_manifest(config, rover)

    cache.set(key, response, ttl_seconds=LONG_TTL)
    return response


def main() -> None:
    """Run the nasa-mcp server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
