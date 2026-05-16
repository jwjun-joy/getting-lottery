import httpx
import re
import json
import sys

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

def main():
    if len(sys.argv) > 2:
        try:
            start_round = int(sys.argv[1])
            end_round = int(sys.argv[2])
            if start_round > end_round:
                start_round, end_round = end_round, start_round
            rounds_to_fetch = list(range(start_round, end_round + 1))
        except ValueError:
            print(f"Invalid round numbers: {sys.argv[1]}, {sys.argv[2]}")
            return
    elif len(sys.argv) > 1:
        try:
            target_round = int(sys.argv[1])
            rounds_to_fetch = [target_round]
        except ValueError:
            print(f"Invalid round number: {sys.argv[1]}")
            return
    else:
        latest_round = get_latest_round()
        if not latest_round:
            print("Could not find the latest round number.")
            return
        print(f"Latest round found: {latest_round}")
        rounds_to_fetch = [latest_round]
    
    for target_round in rounds_to_fetch:
        data = get_lotto_details(target_round)
        if data and "data" in data and "list" in data["data"] and data["data"]["list"]:
            # The API returns a list, find the one matching our round
            found = False
            for item in data["data"]["list"]:
                if item["ltEpsd"] == target_round:
                    print(f"\n--- Round {item['ltEpsd']} Results ---")
                    print(f"Date: {item['ltRflYmd']}")
                    numbers = [item['tm1WnNo'], item['tm2WnNo'], item['tm3WnNo'], 
                               item['tm4WnNo'], item['tm5WnNo'], item['tm6WnNo']]
                    print(f"Numbers: {', '.join(map(str, numbers))} + Bonus: {item['bnsWnNo']}")
                    print(f"1st Prize Winners: {item['rnk1WnNope']} people")
                    print(f"1st Prize Amount: {item['rnk1WnAmt']:,} KRW")
                    found = True
                    break
            if not found:
                print(f"Results for round {target_round} not found in the API response.")
        else:
            print(f"Failed to fetch lottery details for round {target_round}.")

if __name__ == "__main__":
    main()
