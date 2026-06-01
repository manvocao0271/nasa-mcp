"""MCP tool registration for Mars rovers."""

import hashlib

from mcp.server.fastmcp import FastMCP

from nasa_mcp.cache import Cache
from nasa_mcp.config import Config
from nasa_mcp.features.mars_rovers.api import get_rover_manifest, get_rover_photos
from nasa_mcp.features.mars_rovers.inputs import (
    GetRoverManifestInput,
    GetRoverPhotosInput,
)

LONG_TTL = 365 * 24 * 3600


def register_mars_rover_tools(mcp: FastMCP, config: Config, cache: Cache) -> None:
    """Register Mars rover MCP tools."""

    @mcp.tool()
    async def get_rover_photos_tool(args: GetRoverPhotosInput) -> dict:
        """Fetch Mars rover photos by sol or Earth date, optionally filtered by camera."""

        if args.sol is not None:
            date_key = f"sol:{args.sol}"
        else:
            assert args.earth_date is not None
            date_key = f"earth_date:{args.earth_date.isoformat()}"

        camera_key = args.camera or "all"
        key_input = f"{args.rover}|{date_key}|{camera_key}"
        key = f"mars_rover_photos:{hashlib.sha256(key_input.encode()).hexdigest()[:16]}"

        cached = cache.get(key)
        if cached is not None:
            return cached

        response = await get_rover_photos(
            config,
            rover_name=args.rover,
            sol=args.sol,
            earth_date=args.earth_date,
            camera=args.camera,
        )
        cache.set(key, response, ttl_seconds=LONG_TTL)
        return response

    @mcp.tool()
    async def get_rover_manifest_tool(args: GetRoverManifestInput) -> dict:
        """Fetch the mission manifest for a specific Mars rover."""

        key = f"mars_rover_manifest:{args.rover}"
        cached = cache.get(key)
        if cached is not None:
            return cached

        response = await get_rover_manifest(config, args.rover)
        cache.set(key, response, ttl_seconds=LONG_TTL)
        return response
