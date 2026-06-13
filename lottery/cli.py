import sys
from .client import get_latest_round, get_lotto_details, get_lotto_range, get_round_by_date
from .formatter import print_lotto_result

_LAST_KEYWORD = "last"

def _resolve_round_arg(arg: str, latest_round_cache: list) -> int | None:
    """
    문자열 인자를 회차 번호(int)로 변환합니다.
    - 숫자 문자열이면 그대로 int 반환
    - "last" 키워드면 최신 회차 번호 반환 (캐시 활용)
    - 그 외는 None 반환
    """
    if arg.lower() == _LAST_KEYWORD:
        if not latest_round_cache:
            latest = get_latest_round()
            if not latest:
                return None
            latest_round_cache.append(latest)
        return latest_round_cache[0]
    try:
        return int(arg)
    except ValueError:
        return None

def run():
    start_round = None
    end_round = None
    latest_round_cache = []  # get_latest_round() 중복 호출 방지용 캐시

    if len(sys.argv) > 2:
        arg1, arg2 = sys.argv[1], sys.argv[2]

        start_round = _resolve_round_arg(arg1, latest_round_cache)
        end_round   = _resolve_round_arg(arg2, latest_round_cache)

        if start_round is None or end_round is None:
            print(f"Invalid round numbers: {arg1}, {arg2}")
            print(f'Tip: Use a round number or the keyword "{_LAST_KEYWORD}" (e.g. uv run main.py 1000 last)')
            return

        if start_round > end_round:
            start_round, end_round = end_round, start_round

        # "last" 키워드 사용 시 실제 조회된 최신 회차를 출력
        if arg1.lower() == _LAST_KEYWORD or arg2.lower() == _LAST_KEYWORD:
            print(f"Latest round resolved: {latest_round_cache[0]}")

    elif len(sys.argv) > 1:
        arg = sys.argv[1]
        try:
            start_round = end_round = int(arg)
        except ValueError:
            # Not an integer, check if it's a date
            calc_round = get_round_by_date(arg)
            if calc_round is None:
                print(f"Invalid input (not a round number or date): {arg}")
                return
            elif calc_round == 0:
                print(f"No rounds exist before the first draw on 2002-12-07.")
                return
            else:
                print(f"Finding last round for date {arg}: Round {calc_round}")
                start_round = end_round = calc_round
    else:
        latest_round = get_latest_round()
        if not latest_round:
            print("Could not find the latest round number.")
            return
        print(f"Latest round found: {latest_round}")
        start_round = end_round = latest_round

    # Security/Robustness: Limit the range to prevent excessive memory usage
    MAX_RANGE_SIZE = 3000
    if abs(end_round - start_round) >= MAX_RANGE_SIZE:
        print(f"Requested range is too large (max {MAX_RANGE_SIZE} rounds).")
        return

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

