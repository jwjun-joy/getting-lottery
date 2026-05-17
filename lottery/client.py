import httpx
import re

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
    except httpx.HTTPError as e:
        print(f"Error fetching latest round: {e}")
    return None

def get_lotto_details(round_number):
    url = f"https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do?srchDir=center&srchLtEpsd={round_number}"
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
            return response.json()
    except httpx.HTTPError as e:
        print(f"Error fetching lotto details for round {round_number}: {e}")
        return None

def get_lotto_range(start_round, end_round):
    """
    Fetches lottery results for a range of rounds using the API's implicit batching behavior.
    Each query returns about 10 rounds.
    """
    all_results = {}
    current_end = end_round
    
    while current_end >= start_round:
        # The API returns rounds from (query_round + 4) down to (query_round - 5).
        # To get current_end as the highest, we query for current_end - 4.
        query_round = max(1, current_end - 4)
        data = get_lotto_details(query_round)
        
        if not data or "data" not in data or "list" not in data["data"] or not data["data"]["list"]:
            # If we fail to fetch a chunk, we might need to skip or handle it.
            # For now, if we can't get any data, we stop to avoid infinite loop.
            break
            
        found_in_chunk = False
        min_round_in_chunk = current_end
        
        for item in data["data"]["list"]:
            round_no = item["ltEpsd"]
            if start_round <= round_no <= end_round:
                all_results[round_no] = item
                found_in_chunk = True
                min_round_in_chunk = min(min_round_in_chunk, round_no)
        
        if not found_in_chunk:
            # If the chunk didn't contain anything we need, we still need to move back.
            # This could happen if there's a gap in rounds.
            current_end -= 10
        else:
            current_end = min_round_in_chunk - 1
            
    # Return sorted list of results
    return [all_results[r] for r in sorted(all_results.keys())]
