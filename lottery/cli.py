import sys
from .client import get_latest_round, get_lotto_details, get_lotto_range
from .formatter import print_lotto_result

def run():
    start_round = None
    end_round = None

    if len(sys.argv) > 2:
        try:
            start_round = int(sys.argv[1])
            end_round = int(sys.argv[2])
            if start_round > end_round:
                start_round, end_round = end_round, start_round
        except ValueError:
            print(f"Invalid round numbers: {sys.argv[1]}, {sys.argv[2]}")
            return
    elif len(sys.argv) > 1:
        try:
            start_round = end_round = int(sys.argv[1])
        except ValueError:
            print(f"Invalid round number: {sys.argv[1]}")
            return
    else:
        latest_round = get_latest_round()
        if not latest_round:
            print("Could not find the latest round number.")
            return
        print(f"Latest round found: {latest_round}")
        start_round = end_round = latest_round
    
    results = get_lotto_range(start_round, end_round)
    
    if not results:
        print(f"No results found for the requested range: {start_round} ~ {end_round}")
        return

    # Check for missing rounds if we expected more than what we got
    fetched_rounds = {item["ltEpsd"] for item in results}
    expected_rounds = set(range(start_round, end_round + 1))
    missing_rounds = sorted(list(expected_rounds - fetched_rounds))
    
    for item in results:
        print_lotto_result(item)
    
    if missing_rounds:
        print(f"\nNote: The following rounds could not be found: {', '.join(map(str, missing_rounds))}")

if __name__ == "__main__":
    run()
