from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from productory_checkout.services import recompute_cart_totals, upsert_cart_item
from productory_promotions.models import Bundle, BundleItem, Promotion, PromotionType


def test_percentage_promotion_applies_best_discount(cart, product):
    Promotion.objects.create(
        name="Launch",
        code="LAUNCH10",
        promotion_type=PromotionType.PERCENTAGE,
        value=Decimal("10.00"),
        start_at=timezone.now() - timedelta(days=1),
        end_at=timezone.now() + timedelta(days=1),
        is_active=True,
    ).products.add(product)

    upsert_cart_item(cart, product.id, 2)
    recompute_cart_totals(cart)
    cart.refresh_from_db()

    assert cart.subtotal_amount == Decimal("25.00")
    assert cart.discount_amount == Decimal("2.50")
    assert cart.total_amount == Decimal("22.50")


def test_bundle_discount_is_applied(cart, product):
    bundle = Bundle.objects.create(
        name="Coffee Pair",
        slug="coffee-pair",
        bundle_price_amount=Decimal("20.00"),
        is_active=True,
    )
    BundleItem.objects.create(bundle=bundle, product=product, quantity=2)

    upsert_cart_item(cart, product.id, 2)
    recompute_cart_totals(cart)
    cart.refresh_from_db()

    assert cart.subtotal_amount == Decimal("25.00")
    assert cart.discount_amount == Decimal("5.00")
    assert cart.total_amount == Decimal("20.00")


def test_applies_to_all_products_promotion_uses_cart_subtotal(cart, product):
    Promotion.objects.create(
        name="Storewide 10",
        code="STORE10",
        promotion_type=PromotionType.PERCENTAGE,
        value=Decimal("10.00"),
        applies_to_all_products=True,
        start_at=timezone.now() - timedelta(days=1),
        end_at=timezone.now() + timedelta(days=1),
        is_active=True,
    )

    upsert_cart_item(cart, product.id, 2)
    recompute_cart_totals(cart)
    cart.refresh_from_db()

    assert cart.subtotal_amount == Decimal("25.00")
    assert cart.discount_amount == Decimal("2.50")
    assert cart.total_amount == Decimal("22.50")
