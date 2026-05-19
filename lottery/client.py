import httpx
import re
from datetime import datetime, date

FIRST_ROUND_DATE = date(2002, 12, 7)

def get_latest_round():
    url = "https://www.dhlottery.co.kr/lt645/result"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        with httpx.Client(follow_redirects=True, timeout=30.0) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            
            # Look for something like "1223회"
            match = re.search(r"(\d+)회", response.text)
            if match:
                return int(match.group(1))
    except (httpx.HTTPError, ValueError, TypeError) as e:
        print(f"Error fetching latest round: {e}")
    return None

def get_lotto_details(round_number):
    """Fetches details for a single lottery round."""
    return get_lotto_range(round_number, round_number)

def get_lotto_range(start_round, end_round):
    """
    Fetches lottery results for a range of rounds in a single request.
    Uses the srchStrLtEpsd and srchEndLtEpsd parameters.
    """
    url = f"https://www.dhlottery.co.kr/lt645/selectPstLt645Info.do?srchStrLtEpsd={start_round}&srchEndLtEpsd={end_round}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.dhlottery.co.kr/lt645/result"
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data and "data" in data and "list" in data["data"] and data["data"]["list"]:
                # Return the list of items, sorted by round number ascending
                return sorted(data["data"]["list"], key=lambda x: x["ltEpsd"])
            return []
    except (httpx.HTTPError, KeyError, ValueError, TypeError) as e:
        print(f"Error fetching lotto range {start_round}~{end_round}: {e}")
        return []

def get_round_by_date(date_str):
    """
    Calculates the last lottery round number on or before the given date.
    Supports YYYY-MM-DD and YYYYMMDD formats.
    """
    try:
        if "-" in date_str:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            target_date = datetime.strptime(date_str, "%Y%m%d").date()
    except ValueError:
        return None

    if target_date < FIRST_ROUND_DATE:
        return 0

    delta = target_date - FIRST_ROUND_DATE
    calculated_round = (delta.days // 7) + 1
    
    latest_round = get_latest_round()
    if latest_round and calculated_round > latest_round:
        return latest_round
        
    return calculated_round
