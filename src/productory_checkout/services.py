from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from productory_checkout.models import Cart, CartItem, CartStatus, Order, OrderItem, OrderStatus
from productory_core.conf import get_setting
from productory_core.hooks import emit_webhook_event, order_created, order_status_changed
from productory_core.store import compute_tax_breakdown

_ALLOWED_TRANSITIONS = {
    OrderStatus.DRAFT: {OrderStatus.SUBMITTED, OrderStatus.CANCELED},
    OrderStatus.SUBMITTED: {OrderStatus.PAID, OrderStatus.CANCELED},
    OrderStatus.PAID: {OrderStatus.FULFILLED, OrderStatus.CANCELED},
    OrderStatus.FULFILLED: set(),
    OrderStatus.CANCELED: set(),
}


def _resolve_promotional_total(cart: Cart, base_subtotal: Decimal) -> tuple[Decimal, Decimal]:
    if not get_setting("ENABLE_PROMOTIONS", True):
        return Decimal("0.00"), base_subtotal

    try:
        from productory_promotions.services import resolve_cart_pricing
    except ImportError:
        return Decimal("0.00"), base_subtotal

    resolution = resolve_cart_pricing(cart, base_subtotal=base_subtotal)
    return resolution.discount_amount, resolution.final_total


@transaction.atomic
def recompute_cart_totals(cart: Cart) -> Cart:
    subtotal_base = Decimal("0.00")
    items = cart.items.select_related("product")

    for item in items:
        item.unit_price_snapshot = item.product.price_amount
        item.save(update_fields=["unit_price_snapshot", "updated_at"])
        subtotal_base += item.unit_price_snapshot * item.quantity

    subtotal_base = subtotal_base.quantize(Decimal("0.01"))
    discount_base, total_base = _resolve_promotional_total(cart, subtotal_base)
    if discount_base > subtotal_base:
        discount_base = subtotal_base
        total_base = Decimal("0.00")

    subtotal_breakdown = compute_tax_breakdown(
        subtotal_base,
        vat_rate_percent=cart.vat_rate_percent,
        price_includes_vat=cart.price_includes_vat,
    )
    total_breakdown = compute_tax_breakdown(
        total_base,
        vat_rate_percent=cart.vat_rate_percent,
        price_includes_vat=cart.price_includes_vat,
    )
    cart.subtotal_excl_vat_amount = subtotal_breakdown.amount_excl_vat
    cart.subtotal_incl_vat_amount = subtotal_breakdown.amount_incl_vat
    cart.total_excl_vat_amount = total_breakdown.amount_excl_vat
    cart.total_incl_vat_amount = total_breakdown.amount_incl_vat
    cart.tax_amount = total_breakdown.vat_amount

    # Keep canonical totals in VAT-inclusive terms.
    cart.subtotal_amount = cart.subtotal_incl_vat_amount
    cart.total_amount = cart.total_incl_vat_amount
    cart.discount_amount = (cart.subtotal_amount - cart.total_amount).quantize(Decimal("0.01"))

    cart.save(
        update_fields=[
            "price_includes_vat",
            "vat_rate_percent",
            "subtotal_amount",
            "subtotal_excl_vat_amount",
            "subtotal_incl_vat_amount",
            "discount_amount",
            "tax_amount",
            "total_amount",
            "total_excl_vat_amount",
            "total_incl_vat_amount",
            "updated_at",
        ]
    )
    return cart


@transaction.atomic
def upsert_cart_item(cart: Cart, product_id: int, quantity: int) -> CartItem:
    item, _ = CartItem.objects.get_or_create(
        cart=cart,
        product_id=product_id,
        defaults={"quantity": 0},
    )
    item.quantity = quantity
    item.unit_price_snapshot = item.product.price_amount
    item.save()
    recompute_cart_totals(cart)
    return item


@transaction.atomic
def transition_order_status(order: Order, new_status: str) -> Order:
    if new_status not in OrderStatus.values:
        raise ValueError(f"Unknown status: {new_status}")

    current_status = order.status
    if new_status == current_status:
        return order

    allowed = _ALLOWED_TRANSITIONS.get(current_status, set())
    if new_status not in allowed:
        raise ValueError(f"Invalid transition: {current_status} -> {new_status}")

    order.status = new_status
    order.save(update_fields=["status", "updated_at"])

    payload = {"order_id": order.id, "from": current_status, "to": new_status}
    order_status_changed.send(sender=Order, order=order, payload=payload)
    emit_webhook_event("order.status_changed", payload)
    return order


@transaction.atomic
def create_order_from_cart(
    cart: Cart,
    *,
    email: str = "",
    full_name: str = "",
    shipping_address_id: int | None = None,
    billing_address_id: int | None = None,
) -> Order:
    if cart.status != CartStatus.OPEN:
        raise ValueError("Only open carts can be checked out")

    recompute_cart_totals(cart)

    order = Order.objects.create(
        cart=cart,
        customer=cart.customer,
        email=email or cart.email,
        full_name=full_name,
        currency=cart.currency,
        price_includes_vat=cart.price_includes_vat,
        vat_rate_percent=cart.vat_rate_percent,
        subtotal_amount=cart.subtotal_amount,
        subtotal_excl_vat_amount=cart.subtotal_excl_vat_amount,
        subtotal_incl_vat_amount=cart.subtotal_incl_vat_amount,
        discount_amount=cart.discount_amount,
        tax_amount=cart.tax_amount,
        total_amount=cart.total_amount,
        total_excl_vat_amount=cart.total_excl_vat_amount,
        total_incl_vat_amount=cart.total_incl_vat_amount,
        shipping_address_id=shipping_address_id,
        billing_address_id=billing_address_id,
    )

    for item in cart.items.select_related("product"):
        line_total = item.quantity * item.unit_price_snapshot
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name_snapshot=item.product.name,
            sku_snapshot=item.product.sku,
            quantity=item.quantity,
            unit_price_snapshot=item.unit_price_snapshot,
            line_total=line_total,
        )

    cart.status = CartStatus.CONVERTED
    cart.save(update_fields=["status", "updated_at"])

    payload = {
        "order_id": order.id,
        "number": order.number,
        "total_amount": str(order.total_amount),
        "currency": order.currency,
    }
    order_created.send(sender=Order, order=order, payload=payload)
    emit_webhook_event("order.created", payload)
    return order
