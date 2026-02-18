from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.apps import apps
from django.db import OperationalError, ProgrammingError
from django.utils import timezone

from productory_core.conf import get_setting
from productory_core.currency import DEFAULT_CURRENCY

DEFAULT_TIMEZONE = "Africa/Johannesburg"
DEFAULT_VAT_RATE_PERCENT = Decimal("15.00")
_MONEY_PLACES = Decimal("0.01")


@dataclass(frozen=True)
class StorePricingPolicy:
    currency_code: str
    timezone_name: str
    vat_rate_percent: Decimal
    price_includes_vat: bool


@dataclass(frozen=True)
class TaxBreakdown:
    amount_excl_vat: Decimal
    amount_incl_vat: Decimal
    vat_amount: Decimal


def _as_percent(value: Decimal | str | None) -> Decimal:
    if value is None:
        return DEFAULT_VAT_RATE_PERCENT
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return DEFAULT_VAT_RATE_PERCENT


def _quantize_money(value: Decimal) -> Decimal:
    return value.quantize(_MONEY_PLACES)


def get_store_config():
    try:
        store_config_model = apps.get_model("productory_core", "StoreConfig")
        return (
            store_config_model.objects.select_related("default_currency", "default_tax_rate")
            .order_by("id")
            .first()
        )
    except (LookupError, OperationalError, ProgrammingError):
        return None


def get_store_pricing_policy() -> StorePricingPolicy:
    config = get_store_config()
    if config:
        tax_rate = (
            config.default_tax_rate.rate_percent
            if config.default_tax_rate_id and config.default_tax_rate.is_active
            else Decimal("0.00")
        )
        return StorePricingPolicy(
            currency_code=config.default_currency.code,
            timezone_name=config.default_timezone or DEFAULT_TIMEZONE,
            vat_rate_percent=_as_percent(tax_rate),
            price_includes_vat=config.price_includes_vat,
        )

    return StorePricingPolicy(
        currency_code=str(
            get_setting("DEFAULT_CURRENCY", DEFAULT_CURRENCY) or DEFAULT_CURRENCY
        ).upper(),
        timezone_name=str(get_setting("DEFAULT_TIMEZONE", DEFAULT_TIMEZONE) or DEFAULT_TIMEZONE),
        vat_rate_percent=_as_percent(get_setting("DEFAULT_TAX_RATE_PERCENT", "15.00")),
        price_includes_vat=bool(get_setting("PRICE_INCLUDES_VAT", True)),
    )


def store_now():
    now = timezone.now()
    policy = get_store_pricing_policy()
    try:
        return now.astimezone(ZoneInfo(policy.timezone_name))
    except ZoneInfoNotFoundError:
        return now


def compute_tax_breakdown(
    amount: Decimal,
    *,
    vat_rate_percent: Decimal,
    price_includes_vat: bool,
) -> TaxBreakdown:
    normalized_amount = _quantize_money(amount if amount >= Decimal("0.00") else Decimal("0.00"))
    if vat_rate_percent <= Decimal("0.00"):
        return TaxBreakdown(
            amount_excl_vat=normalized_amount,
            amount_incl_vat=normalized_amount,
            vat_amount=Decimal("0.00"),
        )

    multiplier = Decimal("1.00") + (vat_rate_percent / Decimal("100.00"))
    if price_includes_vat:
        amount_incl = normalized_amount
        amount_excl = _quantize_money(normalized_amount / multiplier)
    else:
        amount_excl = normalized_amount
        amount_incl = _quantize_money(normalized_amount * multiplier)

    vat_amount = _quantize_money(amount_incl - amount_excl)
    return TaxBreakdown(
        amount_excl_vat=amount_excl,
        amount_incl_vat=amount_incl,
        vat_amount=vat_amount,
    )
