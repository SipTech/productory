from __future__ import annotations

from random import Random

import pytest
from django.core.management import call_command

from productory_checkout.models import Cart, OrderStatus
from productory_checkout.services import (
    create_order_from_cart,
    recompute_cart_totals,
    transition_order_status,
    upsert_cart_item,
)
from productory_promotions.models import Promotion


@pytest.mark.django_db
def test_chaos_monkey_cart_total_invariants_hold():
    call_command("seed_demo_data", reset=True)
    rng = Random(2026)

    products = list(Promotion.objects.first().products.all()[:8])
    cart = Cart.objects.create(email="chaos@example.com")

    for _ in range(120):
        product = rng.choice(products)
        quantity = rng.randint(1, 6)
        upsert_cart_item(cart, product.id, quantity)
        recompute_cart_totals(cart)

        cart.refresh_from_db()
        calculated_subtotal = sum(
            item.quantity * item.unit_price_snapshot for item in cart.items.all()
        )

        assert cart.subtotal_amount == calculated_subtotal
        assert cart.discount_amount >= 0
        assert cart.total_amount >= 0
        assert cart.total_amount <= cart.subtotal_amount


@pytest.mark.django_db
def test_chaos_monkey_order_transitions_reject_invalid_paths():
    call_command("seed_demo_data", reset=True)
    rng = Random(42)

    product = Promotion.objects.first().products.first()
    cart = Cart.objects.create(email="chaos-order@example.com")
    upsert_cart_item(cart, product.id, 2)

    order = create_order_from_cart(cart, email="chaos-order@example.com")

    valid_sequence = [OrderStatus.PAID, OrderStatus.FULFILLED]
    for status in valid_sequence:
        transition_order_status(order, status)
        order.refresh_from_db()
        assert order.status == status

    invalid_targets = [OrderStatus.SUBMITTED, OrderStatus.PAID, OrderStatus.CANCELED]
    rng.shuffle(invalid_targets)
    for invalid_status in invalid_targets:
        with pytest.raises(ValueError):
            transition_order_status(order, invalid_status)
