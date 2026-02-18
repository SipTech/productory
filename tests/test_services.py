from decimal import Decimal

import pytest

from productory_checkout.models import CartStatus, OrderStatus
from productory_checkout.services import (
    create_order_from_cart,
    transition_order_status,
    upsert_cart_item,
)
from productory_core.models import StoreConfig


def test_create_order_snapshots_prices(cart, product):
    upsert_cart_item(cart, product.id, 2)

    order = create_order_from_cart(cart, email="shopper@example.com", full_name="Shopper")

    item = order.items.get()
    assert order.currency == "ZAR"
    assert str(order.total_amount) == "25.00"
    assert str(order.total_excl_vat_amount) == "21.74"
    assert str(order.tax_amount) == "3.26"
    assert item.product_name_snapshot == product.name
    assert str(item.unit_price_snapshot) == "12.50"
    assert cart.status == CartStatus.CONVERTED


def test_order_status_transitions(cart, product):
    upsert_cart_item(cart, product.id, 1)
    order = create_order_from_cart(cart)

    assert order.status == OrderStatus.SUBMITTED
    transition_order_status(order, OrderStatus.PAID)
    order.refresh_from_db()
    assert order.status == OrderStatus.PAID

    transition_order_status(order, OrderStatus.FULFILLED)
    order.refresh_from_db()
    assert order.status == OrderStatus.FULFILLED


@pytest.mark.parametrize(
    ("from_status", "to_status"),
    [
        (OrderStatus.SUBMITTED, OrderStatus.FULFILLED),
        (OrderStatus.CANCELED, OrderStatus.PAID),
    ],
)
def test_invalid_status_transitions_raise(cart, product, from_status, to_status):
    upsert_cart_item(cart, product.id, 1)
    order = create_order_from_cart(cart)
    if from_status != OrderStatus.SUBMITTED:
        order.status = from_status
        order.save(update_fields=["status"])

    with pytest.raises(ValueError):
        transition_order_status(order, to_status)


def test_discount_never_exceeds_subtotal(cart, product):
    upsert_cart_item(cart, product.id, 1)
    cart.refresh_from_db()
    assert cart.total_amount <= cart.subtotal_amount
    assert cart.discount_amount >= Decimal("0.00")


def test_create_order_supports_exclusive_vat_mode(cart, product):
    config = StoreConfig.objects.get(slug="default")
    config.price_includes_vat = False
    config.save(update_fields=["price_includes_vat", "updated_at"])

    upsert_cart_item(cart, product.id, 2)
    order = create_order_from_cart(cart)

    assert order.price_includes_vat is False
    assert order.subtotal_excl_vat_amount == Decimal("25.00")
    assert order.subtotal_incl_vat_amount == Decimal("28.75")
    assert order.tax_amount == Decimal("3.75")
    assert order.total_excl_vat_amount == Decimal("25.00")
    assert order.total_incl_vat_amount == Decimal("28.75")
    assert order.total_amount == Decimal("28.75")
