from __future__ import annotations

from django.apps import apps
from django.db import OperationalError, ProgrammingError

from productory_core.conf import get_setting

SUPPORTED_CURRENCIES = {"ZAR", "USD", "EUR", "GBP"}
DEFAULT_CURRENCY = "ZAR"


def default_currency_code() -> str:
    fallback = str(get_setting("DEFAULT_CURRENCY", DEFAULT_CURRENCY) or DEFAULT_CURRENCY).upper()

    try:
        store_config_model = apps.get_model("productory_core", "StoreConfig")
        config = store_config_model.objects.select_related("default_currency").first()
        if config and config.default_currency_id:
            return config.default_currency.code
    except (LookupError, OperationalError, ProgrammingError):
        return fallback

    return fallback


def normalize_currency(value: str) -> str:
    code = (value or default_currency_code()).upper()
    if code not in SUPPORTED_CURRENCIES:
        raise ValueError(f"Unsupported currency: {code}")
    return code
