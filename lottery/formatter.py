def print_lotto_result(item):
    """Prints the lottery result for a single round in a formatted manner."""
    print(f"\n--- Round {item['ltEpsd']} Results ---")
    print(f"Date: {item['ltRflYmd']}")
    numbers = [item['tm1WnNo'], item['tm2WnNo'], item['tm3WnNo'], 
               item['tm4WnNo'], item['tm5WnNo'], item['tm6WnNo']]
    print(f"Numbers: {', '.join(map(str, numbers))} + Bonus: {item['bnsWnNo']}")
    print(f"1st Prize Winners: {item['rnk1WnNope']} people")
    print(f"1st Prize Amount: {item['rnk1WnAmt']:,} KRW")
