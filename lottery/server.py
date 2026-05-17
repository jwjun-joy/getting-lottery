import re
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from mcp.server.fastmcp import FastMCP

from lottery.client import get_latest_round, get_lotto_range, get_round_by_date
from lottery.formatter import format_lotto_result

# Initialize the MCP server
mcp = FastMCP("korean_lottery_mcp")

# Pydantic Models for Input Validation
class RangeSearchInput(BaseModel):
    """Input model for fetching lottery results within a range of rounds."""
    model_config = ConfigDict(validate_assignment=True)

    start_round: int = Field(..., description="The starting round number (e.g., 1100)", ge=1)
    end_round: Optional[int] = Field(None, description="The ending round number. If omitted, only start_round is fetched.", ge=1)

class DateSearchInput(BaseModel):
    """Input model for finding the last lottery round by date."""
    model_config = ConfigDict(str_strip_whitespace=True)

    date_str: str = Field(..., description="The target date in YYYY-MM-DD or YYYYMMDD format (e.g., '2024-05-18')")

    @field_validator('date_str')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', v) and not re.match(r'^\d{8}$', v):
            raise ValueError("Date must be in YYYY-MM-DD or YYYYMMDD format")
        return v

# Tool definitions
@mcp.tool(
    name="get_latest_draw_round",
    annotations={
        "title": "Get Latest Lottery Round",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def get_latest_draw_round() -> int:
    """
    Fetches the number of the most recent South Korean Lotto 6/45 draw.
    
    Returns:
        int: The latest round number (e.g., 1224).
    """
    latest = get_latest_round()
    return latest if latest else 0

@mcp.tool(
    name="get_lottery_results",
    annotations={
        "title": "Get Lottery Results by Range",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def get_lottery_results(params: RangeSearchInput) -> str:
    """
    Fetches winning numbers and prize details for a specific range of lottery rounds.
    
    Args:
        params (RangeSearchInput): Start and end round numbers.
        
    Returns:
        str: A formatted Markdown string containing results for each round in the range.
    """
    start = params.start_round
    end = params.end_round if params.end_round is not None else start
    
    # Ensure start is less than or equal to end
    if start > end:
        start, end = end, start
        
    results = get_lotto_range(start, end)
    
    if not results:
        return f"No results found for rounds {start} ~ {end}."
        
    formatted_outputs = [format_lotto_result(item) for item in results]
    return "\n\n".join(formatted_outputs)

@mcp.tool(
    name="get_lottery_by_date",
    annotations={
        "title": "Find Lottery Round by Date",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def get_lottery_by_date(params: DateSearchInput) -> str:
    """
    Finds and returns the details of the last lottery round that occurred on or before a given date.
    
    Args:
        params (DateSearchInput): Target date string (YYYY-MM-DD or YYYYMMDD).
        
    Returns:
        str: A formatted Markdown string for the calculated round, or an informative error message.
    """
    date_str = params.date_str
    calc_round = get_round_by_date(date_str)
    
    if calc_round is None:
        return f"Error: Could not calculate a round for the provided date format: {date_str}"
    elif calc_round == 0:
        return f"No rounds exist before the first draw on 2002-12-07."
        
    results = get_lotto_range(calc_round, calc_round)
    if not results:
        return f"Found round {calc_round} for date {date_str}, but failed to fetch its details."
        
    return f"Calculated last round for {date_str} is **Round {calc_round}**:\n\n" + format_lotto_result(results[0])

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Korean Lottery MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse", "streamable-http"], default="stdio", help="Transport protocol")
    parser.add_argument("--port", type=int, default=8000, help="Port for SSE transport")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host for SSE transport")
    
    args, unknown = parser.parse_known_args()

    if args.transport == "sse":
        import uvicorn
        print(f"Starting MCP server with SSE transport on {args.host}:{args.port}...")
        uvicorn.run(mcp.app, host=args.host, port=args.port)
    else:
        mcp.run(transport="stdio")
