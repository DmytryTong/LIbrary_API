from datetime import datetime, timedelta

def calculate_fee_payment(start_date: datetime, end_date: datetime, daily_fee: int) -> int:
    end_date += timedelta(hours=1)
    day_count = (end_date - start_date).days
    return max(1, day_count) * daily_fee * 100
