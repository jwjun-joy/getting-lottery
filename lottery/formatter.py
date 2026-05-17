from datetime import datetime
from korean_lunar_calendar import KoreanLunarCalendar

def print_lotto_result(item):
    """Prints the lottery result for a single round in a formatted manner."""
    print(f"\n--- Round {item['ltEpsd']} Results ---")
    
    solar_date_str = item['ltRflYmd']
    print(f"Date: {solar_date_str}")
    
    try:
        # Convert Solar to Lunar
        solar_date = datetime.strptime(solar_date_str, "%Y%m%d")
        calendar = KoreanLunarCalendar()
        calendar.setSolarDate(solar_date.year, solar_date.month, solar_date.day)
        print(f"Lunar Date: {calendar.LunarIsoFormat()} (Leap: {calendar.isIntercalation})")
    except Exception:
        # Silently skip lunar date if there's any parsing error
        pass

    numbers = [item['tm1WnNo'], item['tm2WnNo'], item['tm3WnNo'], 
               item['tm4WnNo'], item['tm5WnNo'], item['tm6WnNo']]
    print(f"Numbers: {', '.join(map(str, numbers))} + Bonus: {item['bnsWnNo']}")
    print(f"1st Prize Winners: {item['rnk1WnNope']} people")
    print(f"1st Prize Amount: {item['rnk1WnAmt']:,} KRW")
