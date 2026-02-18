from __future__ import annotations

from typing import Any

from django.conf import settings

DEFAULTS: dict[str, Any] = {
    "DEFAULT_CURRENCY": "ZAR",
    "DEFAULT_TIMEZONE": "Africa/Johannesburg",
    "DEFAULT_TAX_RATE_PERCENT": "15.00",
    "PRICE_INCLUDES_VAT": True,
    "DEFAULT_PAGE_SIZE": 20,
    "ENABLE_PROMOTIONS": True,
    "ENABLE_WEBHOOKS": False,
    "WEBHOOK_URL": "",
}


def get_setting(name: str, default: Any | None = None) -> Any:
    config = getattr(settings, "PRODUCTORY", {})
    if name in config:
        return config[name]
    if default is not None:
        return default
    return DEFAULTS.get(name)
