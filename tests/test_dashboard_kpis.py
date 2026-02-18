from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from productory_catalog.models import Category, Product, StockRecord
from productory_checkout.models import Cart, CartStatus, Order, OrderStatus
from productory_core.services.dashboard_kpis import get_store_kpis


@pytest.mark.django_db
def test_get_store_kpis_aggregates_expected_metrics():
    category = Category.objects.create(name="Dashboard Category", slug="dashboard-category")
    product_1 = Product.objects.create(
        name="Out Stock",
        slug="out-stock",
        sku="DB-001",
        category=category,
        price_amount=Decimal("12.50"),
    )
    product_2 = Product.objects.create(
        name="Low Stock",
        slug="low-stock",
        sku="DB-002",
        category=category,
        price_amount=Decimal("18.00"),
    )
    product_3 = Product.objects.create(
        name="Inactive Product",
        slug="inactive-product",
        sku="DB-003",
        category=category,
        price_amount=Decimal("9.99"),
        is_active=False,
    )
    StockRecord.objects.create(product=product_1, quantity=0, allow_backorder=False)
    StockRecord.objects.create(product=product_2, quantity=3, allow_backorder=False)
    StockRecord.objects.create(product=product_3, quantity=0, allow_backorder=False)

    open_cart = Cart.objects.create(email="open@example.com", status=CartStatus.OPEN)
    converted_cart = Cart.objects.create(email="converted@example.com", status=CartStatus.CONVERTED)
    abandoned_cart = Cart.objects.create(email="abandoned@example.com", status=CartStatus.ABANDONED)
    old_cart = Cart.objects.create(email="old@example.com", status=CartStatus.CONVERTED)
    old_timestamp = timezone.now() - timedelta(days=20)
    Cart.objects.filter(pk=old_cart.pk).update(created_at=old_timestamp, updated_at=old_timestamp)

    paid_order = Order.objects.create(
        cart=converted_cart,
        status=OrderStatus.PAID,
        subtotal_incl_vat_amount=Decimal("120.00"),
        total_incl_vat_amount=Decimal("100.00"),
        subtotal_amount=Decimal("120.00"),
        total_amount=Decimal("100.00"),
        discount_amount=Decimal("20.00"),
        tax_amount=Decimal("13.04"),
    )
    fulfilled_order = Order.objects.create(
        cart=abandoned_cart,
        status=OrderStatus.FULFILLED,
        subtotal_incl_vat_amount=Decimal("80.00"),
        total_incl_vat_amount=Decimal("70.00"),
        subtotal_amount=Decimal("80.00"),
        total_amount=Decimal("70.00"),
        discount_amount=Decimal("10.00"),
        tax_amount=Decimal("9.13"),
    )
    Order.objects.create(
        cart=open_cart,
        status=OrderStatus.SUBMITTED,
        subtotal_incl_vat_amount=Decimal("50.00"),
        total_incl_vat_amount=Decimal("50.00"),
        subtotal_amount=Decimal("50.00"),
        total_amount=Decimal("50.00"),
        discount_amount=Decimal("0.00"),
        tax_amount=Decimal("6.52"),
    )
    old_paid_order = Order.objects.create(
        cart=old_cart,
        status=OrderStatus.PAID,
        subtotal_incl_vat_amount=Decimal("999.00"),
        total_incl_vat_amount=Decimal("900.00"),
        subtotal_amount=Decimal("999.00"),
        total_amount=Decimal("900.00"),
        discount_amount=Decimal("99.00"),
        tax_amount=Decimal("117.39"),
    )
    Order.objects.filter(pk=old_paid_order.pk).update(
        created_at=old_timestamp, updated_at=old_timestamp
    )
    now = timezone.now()
    Order.objects.filter(pk=paid_order.pk).update(created_at=now, updated_at=now)
    Order.objects.filter(pk=fulfilled_order.pk).update(
        created_at=timezone.now(), updated_at=timezone.now()
    )

    local_today = timezone.localdate()
    payload = get_store_kpis(
        date_from=local_today - timedelta(days=1),
        date_to=local_today,
        low_stock_threshold=5,
    )

    assert payload["currency"] == "ZAR"
    assert payload["range"]["timezone"] == "Africa/Johannesburg"

    assert payload["revenue"]["gmv_incl_vat"] == Decimal("200.00")
    assert payload["revenue"]["net_sales"] == Decimal("170.00")
    assert payload["revenue"]["discount_total"] == Decimal("30.00")
    assert payload["revenue"]["aov_incl_vat"] == Decimal("85.00")

    assert payload["orders"]["total"] == 3
    assert payload["orders"]["paid"] == 2
    assert payload["orders"]["promo_usage_count"] == 2
    assert payload["orders"]["by_status"]["paid"] == 1
    assert payload["orders"]["by_status"]["fulfilled"] == 1
    assert payload["orders"]["by_status"]["submitted"] == 1
    assert payload["orders"]["by_status"]["draft"] == 0
    assert payload["orders"]["by_status"]["canceled"] == 0

    assert payload["carts"]["open"] == 1
    assert payload["carts"]["converted"] == 1
    assert payload["carts"]["abandoned"] == 1
    assert payload["carts"]["conversion_rate"] == 0.5

    assert payload["catalog"]["active_products"] == 2
    assert payload["catalog"]["out_of_stock"] == 1
    assert payload["catalog"]["low_stock"] == 1
    assert payload["catalog"]["low_stock_threshold"] == 5


@pytest.mark.django_db
def test_dashboard_kpi_endpoint_staff_only():
    client = APIClient()
    endpoint = "/api/internal/dashboard/kpis/"

    assert client.get(endpoint).status_code == 403

    user_model = get_user_model()
    non_staff = user_model.objects.create_user(username="member", password="pass")
    client.force_authenticate(user=non_staff)
    assert client.get(endpoint).status_code == 403

    staff = user_model.objects.create_user(username="staff", password="pass", is_staff=True)
    client.force_authenticate(user=staff)
    response = client.get(endpoint)

    assert response.status_code == 200
    assert response.data["revenue"]["gmv_incl_vat"] == Decimal("0.00")
    assert response.data["orders"]["total"] == 0
    assert response.data["carts"]["conversion_rate"] == 0.0


@pytest.mark.django_db
def test_dashboard_kpi_endpoint_validates_range_and_store():
    user_model = get_user_model()
    staff = user_model.objects.create_user(username="staff2", password="pass", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=staff)

    invalid_range = client.get(
        "/api/internal/dashboard/kpis/?date_from=2026-02-20&date_to=2026-02-10"
    )
    assert invalid_range.status_code == 400
    assert "from" in invalid_range.data

    unknown_store = client.get("/api/internal/dashboard/kpis/?store=other")
    assert unknown_store.status_code == 400
    assert "detail" in unknown_store.data
