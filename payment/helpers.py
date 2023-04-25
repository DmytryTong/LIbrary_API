def calculate_fine_payment(expected_return_date, actual_return_date, daily_fee):
    if actual_return_date > expected_return_date:
        return (actual_return_date.day - expected_return_date.day) * daily_fee * 200
    return False


def calculate_fee_payment(expected_return_date, borrow_date, daily_fee):
    calculation = ((expected_return_date.day - borrow_date.day) * daily_fee) * 100
    if calculation < daily_fee:
        return daily_fee * 100
    return calculation
