from __future__ import annotations

import calendar
from decimal import Decimal

from django.core.management import call_command
from django.utils import timezone

from productory_catalog.models import Category, Collection, Product, StockRecord
from productory_checkout.models import Address, Cart, CartStatus, Order, OrderStatus
from productory_promotions.models import Bundle, Promotion, PromotionType


def test_seed_demo_data_creates_expected_dataset(db):
    call_command("seed_demo_data", reset=True)

    assert Category.objects.count() == 10
    assert Collection.objects.count() == 10
    assert Product.objects.count() == 50
    assert StockRecord.objects.count() == 50
    assert Bundle.objects.count() == 6
    assert Promotion.objects.count() == 5
    assert Address.objects.count() == 10
    assert Cart.objects.count() == 32
    assert Order.objects.count() == 18

    quantities = list(StockRecord.objects.values_list("quantity", flat=True))
    assert all(5 <= qty <= 10 for qty in quantities)
    assert set(Product.objects.values_list("currency", flat=True)) == {"ZAR"}
    assert set(Bundle.objects.values_list("currency", flat=True)) == {"ZAR"}

    promo_types = set(Promotion.objects.values_list("promotion_type", flat=True))
    assert promo_types == {PromotionType.FIXED, PromotionType.PERCENTAGE}
    assert Promotion.objects.filter(applies_to_all_products=True).count() == 1
    assert set(Cart.objects.values_list("status", flat=True)) == {
        CartStatus.OPEN,
        CartStatus.CONVERTED,
        CartStatus.ABANDONED,
    }
    assert set(Order.objects.values_list("status", flat=True)) == {
        OrderStatus.SUBMITTED,
        OrderStatus.PAID,
        OrderStatus.FULFILLED,
        OrderStatus.CANCELED,
    }

    now = timezone.now()
    last_day = calendar.monthrange(now.year, now.month)[1]
    for promo in Promotion.objects.all():
        assert promo.start_at <= now
        localized_end_at = timezone.localtime(promo.end_at)
        assert localized_end_at.day == last_day
        assert localized_end_at.hour == 23
        assert localized_end_at.minute == 59
        assert localized_end_at.second == 59
        assert promo.value > Decimal("0.00")


def test_seed_demo_data_is_idempotent_with_reset(db):
    call_command("seed_demo_data", reset=True)
    call_command("seed_demo_data", reset=True)

    assert Category.objects.count() == 10
    assert Collection.objects.count() == 10
    assert Product.objects.count() == 50
    assert StockRecord.objects.count() == 50
    assert Bundle.objects.count() == 6
    assert Promotion.objects.count() == 5
    assert Address.objects.count() == 10
    assert Cart.objects.count() == 32
    assert Order.objects.count() == 18
