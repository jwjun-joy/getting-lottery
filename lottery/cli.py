import sys
from .client import get_latest_round, get_lotto_details
from .formatter import print_lotto_result

def run():
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
                    print_lotto_result(item)
                    found = True
                    break
            if not found:
                print(f"Results for round {target_round} not found in the API response.")
        else:
            print(f"Failed to fetch lottery details for round {target_round}.")

if __name__ == "__main__":
    run()
