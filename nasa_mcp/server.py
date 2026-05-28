"""MCP server entry point. Registers tools and runs the stdio transport."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("nasa-mcp")


def main() -> None:
    """Run the nasa-mcp server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
