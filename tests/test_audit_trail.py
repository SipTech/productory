from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from productory_catalog.models import Category, Product, StockRecord
from productory_checkout.models import Cart, Order
from productory_core.audit_context import clear_current_actor, set_current_actor
from productory_core.models import AuditEvent, Currency, StoreConfig, TaxRate
from productory_promotions.models import Bundle, BundleItem, Promotion, PromotionType


@pytest.mark.django_db
def test_audit_events_are_created_for_tracked_models_with_actor():
    user = get_user_model().objects.create_user(username="auditor", password="pass", is_staff=True)
    set_current_actor(user)
    try:
        currency = Currency.objects.create(
            code="NAD",
            name="Namibian Dollar",
            symbol="N$",
            is_active=True,
            is_default=False,
        )
        currency.name = "Namibian Dollar Updated"
        currency.save()

        tax_rate = TaxRate.objects.create(
            code="NA_VAT_STANDARD",
            name="Namibia VAT Standard",
            country_code="NA",
            rate_percent=Decimal("15.00"),
            is_active=True,
            is_default=False,
        )
        tax_rate.rate_percent = Decimal("16.00")
        tax_rate.save()

        store = StoreConfig.objects.get(slug="default")
        store.default_currency = currency
        store.default_tax_rate = tax_rate
        store.save()

        category = Category.objects.create(name="Audit Category", slug="audit-category")
        product = Product.objects.create(
            name="Audit Product",
            slug="audit-product",
            sku="AUD-001",
            category=category,
            price_amount=Decimal("10.00"),
            currency=currency.code,
        )
        stock = StockRecord.objects.create(product=product, quantity=5, allow_backorder=False)
        stock.quantity = 3
        stock.save()

        cart = Cart.objects.create(email="audit@example.com", currency=currency.code)
        order = Order.objects.create(
            cart=cart,
            status="submitted",
            currency=currency.code,
            subtotal_amount=Decimal("100.00"),
            subtotal_excl_vat_amount=Decimal("86.96"),
            subtotal_incl_vat_amount=Decimal("100.00"),
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("13.04"),
            total_amount=Decimal("100.00"),
            total_excl_vat_amount=Decimal("86.96"),
            total_incl_vat_amount=Decimal("100.00"),
        )
        order.status = "paid"
        order.save()

        bundle = Bundle.objects.create(
            name="Audit Bundle",
            slug="audit-bundle",
            bundle_price_amount=Decimal("18.00"),
            currency=currency.code,
            is_active=True,
        )
        BundleItem.objects.create(bundle=bundle, product=product, quantity=2)
        bundle.bundle_price_amount = Decimal("17.50")
        bundle.save()

        promotion = Promotion.objects.create(
            name="Audit Promo",
            code="AUDIT10",
            promotion_type=PromotionType.PERCENTAGE,
            value=Decimal("10.00"),
            applies_to_all_products=False,
            start_at=timezone.now() - timedelta(days=1),
            end_at=timezone.now() + timedelta(days=1),
            is_active=True,
        )
        promotion.products.add(product)
        promotion.bundles.add(bundle)
        promotion.value = Decimal("12.50")
        promotion.save()

    finally:
        clear_current_actor()

    labels = set(
        AuditEvent.objects.values_list("model_label", flat=True).distinct()
    )
    assert "productory_core.Currency" in labels
    assert "productory_core.TaxRate" in labels
    assert "productory_core.StoreConfig" in labels
    assert "productory_checkout.Order" in labels
    assert "productory_catalog.StockRecord" in labels
    assert "productory_promotions.Bundle" in labels
    assert "productory_promotions.Promotion" in labels

    # Ensure "who" is captured for actor-driven changes.
    assert AuditEvent.objects.filter(actor=user).exists()
    assert AuditEvent.objects.filter(actor_display="auditor").exists()

    order_update = AuditEvent.objects.filter(
        model_label="productory_checkout.Order",
        action="updated",
    ).first()
    assert order_update is not None
    assert "status" in order_update.changes
    assert order_update.changes["status"]["before"] == "submitted"
    assert order_update.changes["status"]["after"] == "paid"
