# Getting Lottery (Lotto 6/45)

A powerful and robust Python CLI tool for fetching South Korean Lotto 6/45 winning numbers and detailed prize information directly from the official DongHang Lottery website.

## 🚀 Features

- **Latest Result:** Automatically detects and fetches the most recent lottery round.
- **Specific Round Search:** Retrieve historical data for any specific round number.
- **Range Support:** Fetch multiple rounds at once by providing a start and end range.
- **`last` Keyword:** Use `last` as a round argument to automatically resolve the most recent round number.
- **Date Search:** Find the lottery round that occurred on or before a specific date.
- **Detailed Data:** Provides winning numbers, bonus numbers, 1st prize winner counts, and total prize amounts.
- **Robustness:** Includes 30-second timeouts and detailed error handling to manage slow server responses or network issues.

## 🛠 Tech Stack

- **Python:** >= 3.13
- **HTTP Client:** [httpx](https://www.python-httpx.org/) for fast and reliable HTTP requests.
- **Package Manager:** [uv](https://github.com/astral-sh/uv) for lightning-fast dependency management and execution.

## 📦 Installation

Ensure you have [uv](https://github.com/astral-sh/uv) installed. Then, clone the repository and sync dependencies:

```bash
uv sync
```

## 📖 Usage

### 1. Fetch the Latest Round
If no arguments are provided, the script identifies and displays the most recent result.

```bash
uv run main.py
```

### 2. Fetch a Specific Round
Provide a single round number to get results for that specific draw.

```bash
uv run main.py 1100
```

### 3. Fetch a Range of Rounds
Provide two round numbers (start and end) to fetch all results in that range (inclusive).

```bash
uv run main.py 1220 1223
```
*Note: The script automatically sorts the range from smallest to largest.*

### 4. Fetch from a Round to the Latest (`last` keyword)
Use the special keyword `last` as either argument to automatically resolve it to the most recent round number.

```bash
# Fetch all rounds from 1000 up to the latest
uv run main.py 1000 last
```

*Note: `last` can be used in either position — the range is always sorted automatically.*

### 5. Fetch by Date
Provide a date (in `YYYY-MM-DD` or `YYYYMMDD` format) to retrieve the last round that occurred on or before that date.

```bash
uv run main.py 2026-05-10
uv run main.py 20260510
```

## 🤖 MCP Server

This tool also provides a Model Context Protocol (MCP) server, allowing AI models to directly query lottery data.

### 1. Local Development (Inspector)
To test the server locally with the MCP Inspector:
```bash
uv run mcp dev lottery/server.py
```
This launches the MCP Inspector in your browser at `http://localhost:6274`, where you can interactively call each tool.

### 2. Integration with Claude Desktop
Add the following to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "korean-lottery": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/getting-lottery",
        "run",
        "lottery/server.py"
      ]
    }
  }
}
```

### 3. Running as an SSE Server (Remote)
To run the server over HTTP (SSE):
```bash
uv run lottery/server.py --transport sse --port 8000
```

### 4. Running as a Streamable HTTP Server
```bash
uv run lottery/server.py --transport streamable-http --port 8000
```

### Available MCP Tools

| Tool | Description | Parameters |
|---|---|---|
| `get_latest_draw_round` | Returns the most recent round number | None |
| `get_lottery_results` | Fetches results for a round or range | `start_round`, `end_round` (optional) |
| `get_lottery_by_date` | Finds the round for a given date | `date_str` (YYYY-MM-DD or YYYYMMDD) |

## 📄 Output Format Example

```text
--- Round 1223 Results ---
Date: 20260509
Lunar Date: 2026-04-12 (Leap: False)
Numbers: 16, 18, 20, 32, 33, 39 + Bonus: 26
1st Prize Winners: 16 people
1st Prize Amount: 1,857,554,133 KRW
```
