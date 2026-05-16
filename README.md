# Getting Lottery (Lotto 6/45)

A powerful and robust Python CLI tool for fetching South Korean Lotto 6/45 winning numbers and detailed prize information directly from the official DongHang Lottery website.

## 🚀 Features

- **Latest Result:** Automatically detects and fetches the most recent lottery round.
- **Specific Round Search:** Retrieve historical data for any specific round number.
- **Range Support:** Fetch multiple rounds at once by providing a start and end range.
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

## 📄 Output Format Example

```text
--- Round 1223 Results ---
Date: 20260509
Numbers: 16, 18, 20, 32, 33, 39 + Bonus: 26
1st Prize Winners: 16 people
1st Prize Amount: 1,857,554,133 KRW
```
