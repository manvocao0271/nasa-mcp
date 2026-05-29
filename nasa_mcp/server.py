"""MCP server entry point. Registers tools and runs the stdio transport."""

from datetime import date
import hashlib

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from nasa_mcp.config import load
from nasa_mcp.cache import Cache
from nasa_mcp.apis.apod import get_apod

mcp = FastMCP("nasa-mcp")
config = load()
cache = Cache(config.cache_path)


class GetApodInput(BaseModel):
    """Input validation for get_apod_tool."""

    target_date: date | None = Field(
        default=None,
        description="The date to look up ranging 1995-06-16 to present day. If omitted, return today's APOD.",
    )


@mcp.tool()
async def get_apod_tool(args: GetApodInput) -> dict:
    """Fetch NASA's Astronomy Picture of the Day (APOD) for a specific date, or today if no date is given.

    Returns a dict with `title`, `explanation`, `url`, `hdurl`, `date`,
    `media_type` (usually `"image"`, sometimes `"video"`), and `copyright`
    (when applicable).

    Use this for questions like "show me today's astronomy picture", "what
    was the APOD on July 14 1998", or "find the explanation for yesterday's
    NASA image of the day". Valid dates range from 1995-06-16 to today.
    """
    key = f"apod:get_apod:{hashlib.sha256(str(args.target_date).encode()).hexdigest()[:16]}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    response = await get_apod(config, args.target_date)

    ttl = 365 * 24 * 3600
    if args.target_date is None or args.target_date == date.today():
        ttl = 4 * 3600
    cache.set(key, response, ttl_seconds=ttl)

    return response


def main() -> None:
    """Run the nasa-mcp server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
