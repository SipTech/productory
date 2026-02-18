from __future__ import annotations

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import OperationalError, ProgrammingError


def validate_active_currency_code(value: str) -> None:
    code = (value or "").upper()
    if not code:
        raise ValidationError("Currency code is required.")

    try:
        currency_model = apps.get_model("productory_core", "Currency")
        exists = currency_model.objects.filter(code=code, is_active=True).exists()
    except (LookupError, OperationalError, ProgrammingError):
        return

    if not exists:
        raise ValidationError(f"Currency '{code}' is not active.")
