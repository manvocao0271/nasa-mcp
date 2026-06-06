"""Pydantic input models for NeoWs MCP tools."""

from datetime import date

from pydantic import BaseModel, Field

class GetNeoFeedInput(BaseModel):
    """Input validation for get_neo_feed_tool."""

    start_date: date = Field(
        description="The beginning date to start for a ranged search, inclusive."
    )
    end_date: date | None = Field(
        default=None,
        description="The final date to start for a ranged search, inclusive. If omitted, the final search date range is seven days after the starting date."
    )


class GetNeoLookupInput(BaseModel):
    """Input validation for get_neo_lookup_tool."""

    asteroid_id: str = Field(
        description="The SPK-ID of the asteroid to look up. For example '3542519'."
    )