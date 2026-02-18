from __future__ import annotations

from datetime import date, datetime, time, timedelta
from datetime import timezone as dt_timezone
from decimal import Decimal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.core.cache import cache
from django.db.models import Count, Q, Sum

from productory_catalog.models import Product, StockRecord
from productory_checkout.models import Cart, CartStatus, Order, OrderStatus
from productory_core.conf import get_setting
from productory_core.store import get_store_config, get_store_pricing_policy, store_now

_ZERO = Decimal("0.00")
_MONEY_PLACES = Decimal("0.01")
_REALIZED_ORDER_STATUSES = [OrderStatus.PAID, OrderStatus.FULFILLED]


def _money(value: Decimal | None) -> Decimal:
    return (value or _ZERO).quantize(_MONEY_PLACES)


def _safe_tz(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        return ZoneInfo("UTC")


def _resolve_range(date_from: date | None, date_to: date | None) -> tuple[date, date]:
    if date_from and date_to:
        return date_from, date_to

    today = store_now().date()
    if date_to is None:
        date_to = today
    if date_from is None:
        date_from = date_to - timedelta(days=6)
    return date_from, date_to


def _cache_key(
    store_slug: str,
    date_from: date,
    date_to: date,
    timezone_name: str,
    low_stock_threshold: int,
) -> str:
    return (
        "productory:kpis:v1:"
        f"{store_slug}:{date_from.isoformat()}:{date_to.isoformat()}:"
        f"{timezone_name}:{low_stock_threshold}"
    )


def get_store_kpis(
    *,
    store_slug: str = "default",
    date_from: date | None = None,
    date_to: date | None = None,
    low_stock_threshold: int = 5,
) -> dict:
    if low_stock_threshold < 0:
        raise ValueError("low_stock_threshold must be >= 0")

    store_config = get_store_config()
    if store_config and store_slug != store_config.slug:
        raise ValueError(f"Unknown store slug: {store_slug}")
    if store_config is None and store_slug != "default":
        raise ValueError(f"Unknown store slug: {store_slug}")

    policy = get_store_pricing_policy()
    tz_name = policy.timezone_name
    range_from, range_to = _resolve_range(date_from, date_to)
    if range_from > range_to:
        raise ValueError("`from` date must be before or equal to `to` date")

    cache_key = _cache_key(store_slug, range_from, range_to, tz_name, low_stock_threshold)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    tz = _safe_tz(tz_name)
    start_local = datetime.combine(range_from, time.min, tzinfo=tz)
    end_local_exclusive = datetime.combine(range_to + timedelta(days=1), time.min, tzinfo=tz)
    start_utc = start_local.astimezone(dt_timezone.utc)
    end_utc_exclusive = end_local_exclusive.astimezone(dt_timezone.utc)

    orders = Order.objects.filter(created_at__gte=start_utc, created_at__lt=end_utc_exclusive)
    realized_orders = orders.filter(status__in=_REALIZED_ORDER_STATUSES)

    realized_agg = realized_orders.aggregate(
        gmv_incl_vat=Sum("subtotal_incl_vat_amount"),
        net_sales=Sum("total_incl_vat_amount"),
        discount_total=Sum("discount_amount"),
        paid_count=Count("id"),
    )
    gmv_incl_vat = _money(realized_agg["gmv_incl_vat"])
    net_sales = _money(realized_agg["net_sales"])
    discount_total = _money(realized_agg["discount_total"])
    paid_orders_count = int(realized_agg["paid_count"] or 0)
    aov_incl_vat = _money(net_sales / paid_orders_count) if paid_orders_count else _ZERO

    status_counts = {
        row["status"]: row["total"] for row in orders.values("status").annotate(total=Count("id"))
    }
    orders_by_status = {
        status: int(status_counts.get(status, 0)) for status, _ in OrderStatus.choices
    }

    carts = Cart.objects.filter(created_at__gte=start_utc, created_at__lt=end_utc_exclusive)
    cart_counts = carts.aggregate(
        open=Count("id", filter=Q(status=CartStatus.OPEN)),
        converted=Count("id", filter=Q(status=CartStatus.CONVERTED)),
        abandoned=Count("id", filter=Q(status=CartStatus.ABANDONED)),
    )
    open_count = int(cart_counts["open"] or 0)
    converted_count = int(cart_counts["converted"] or 0)
    abandoned_count = int(cart_counts["abandoned"] or 0)
    conversion_denominator = converted_count + abandoned_count
    conversion_rate = (
        round(converted_count / conversion_denominator, 4) if conversion_denominator else 0.0
    )

    active_products = Product.objects.filter(is_active=True).count()
    out_of_stock = StockRecord.objects.filter(
        product__is_active=True,
        quantity__lte=0,
        allow_backorder=False,
    ).count()
    low_stock = StockRecord.objects.filter(
        product__is_active=True,
        quantity__gt=0,
        quantity__lte=low_stock_threshold,
        allow_backorder=False,
    ).count()

    payload = {
        "range": {
            "from": range_from.isoformat(),
            "to": range_to.isoformat(),
            "timezone": tz_name,
        },
        "currency": policy.currency_code,
        "revenue": {
            "gmv_incl_vat": gmv_incl_vat,
            "net_sales": net_sales,
            "discount_total": discount_total,
            "aov_incl_vat": aov_incl_vat,
        },
        "orders": {
            "total": orders.count(),
            "paid": paid_orders_count,
            "by_status": orders_by_status,
            "promo_usage_count": realized_orders.filter(discount_amount__gt=_ZERO).count(),
        },
        "carts": {
            "open": open_count,
            "converted": converted_count,
            "abandoned": abandoned_count,
            "conversion_rate": conversion_rate,
        },
        "catalog": {
            "active_products": active_products,
            "out_of_stock": out_of_stock,
            "low_stock": low_stock,
            "low_stock_threshold": low_stock_threshold,
        },
    }

    cache_ttl = int(get_setting("DASHBOARD_KPI_CACHE_TTL_SECONDS", 120) or 120)
    cache.set(cache_key, payload, cache_ttl)
    return payload
