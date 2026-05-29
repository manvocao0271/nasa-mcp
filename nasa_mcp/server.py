"""MCP server entry point. Registers tools and runs the stdio transport."""

from datetime import date

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


def main() -> None:
    """Run the nasa-mcp server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
