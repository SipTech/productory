SUPPORTED_CURRENCIES = {"USD", "EUR", "GBP", "ZAR"}
DEFAULT_CURRENCY = "USD"


def normalize_currency(value: str) -> str:
    code = (value or DEFAULT_CURRENCY).upper()
    if code not in SUPPORTED_CURRENCIES:
        raise ValueError(f"Unsupported currency: {code}")
    return code
