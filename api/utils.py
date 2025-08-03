def calculate_approved_limit(monthly_income: int) -> int:
    limit = 36 * monthly_income
    # Round to nearest lakh
    return round(limit, -5)
