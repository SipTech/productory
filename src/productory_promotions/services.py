from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.db.models import Prefetch
from django.utils import timezone

from productory_checkout.models import Cart
from productory_promotions.models import Bundle, Promotion, PromotionType


@dataclass(frozen=True)
class PricingResolution:
    base_subtotal: Decimal
    discount_amount: Decimal
    final_total: Decimal
    rule: str


def _bundle_discount(cart: Cart) -> tuple[Decimal, str]:
    cart_items = {item.product_id: item for item in cart.items.select_related("product")}
    best_discount = Decimal("0.00")
    best_rule = ""

    bundles = Bundle.objects.filter(is_active=True).prefetch_related(
        Prefetch("items", to_attr="bundle_items")
    )

    for bundle in bundles:
        set_counts: list[int] = []
        regular_set_total = Decimal("0.00")
        for bundle_item in bundle.bundle_items:
            cart_item = cart_items.get(bundle_item.product_id)
            if not cart_item:
                set_counts = []
                break
            set_counts.append(cart_item.quantity // bundle_item.quantity)
            regular_set_total += cart_item.unit_price_snapshot * bundle_item.quantity

        if not set_counts:
            continue

        bundle_sets = min(set_counts)
        if bundle_sets < 1:
            continue

        standard_price = regular_set_total * bundle_sets
        bundle_price = bundle.bundle_price_amount * bundle_sets
        discount = standard_price - bundle_price

        if discount > best_discount:
            best_discount = discount
            best_rule = f"bundle:{bundle.slug}"

    return best_discount, best_rule


def _promotion_discount(cart: Cart) -> tuple[Decimal, str]:
    now = timezone.now()
    cart_items = {item.product_id: item for item in cart.items.select_related("product")}
    best_discount = Decimal("0.00")
    best_rule = ""

    promotions = Promotion.objects.filter(
        is_active=True,
        start_at__lte=now,
        end_at__gte=now,
    ).prefetch_related("products")

    for promo in promotions:
        eligible_subtotal = Decimal("0.00")
        for product in promo.products.all():
            item = cart_items.get(product.id)
            if not item:
                continue
            eligible_subtotal += item.quantity * item.unit_price_snapshot

        if eligible_subtotal <= Decimal("0.00"):
            continue

        if promo.promotion_type == PromotionType.PERCENTAGE:
            discount = (eligible_subtotal * promo.value / Decimal("100")).quantize(Decimal("0.01"))
        else:
            discount = min(promo.value, eligible_subtotal)

        if discount > best_discount:
            best_discount = discount
            best_rule = f"promotion:{promo.code}"

    return best_discount, best_rule


def resolve_cart_pricing(cart: Cart, *, base_subtotal: Decimal | None = None) -> PricingResolution:
    resolved_subtotal = base_subtotal if base_subtotal is not None else cart.subtotal_amount

    bundle_discount, bundle_rule = _bundle_discount(cart)
    promo_discount, promo_rule = _promotion_discount(cart)

    discount = bundle_discount
    rule = bundle_rule
    if promo_discount > bundle_discount:
        discount = promo_discount
        rule = promo_rule

    final_total = (resolved_subtotal - discount).quantize(Decimal("0.01"))
    if final_total < Decimal("0.00"):
        final_total = Decimal("0.00")

    return PricingResolution(
        base_subtotal=resolved_subtotal,
        discount_amount=discount,
        final_total=final_total,
        rule=rule or "none",
    )
