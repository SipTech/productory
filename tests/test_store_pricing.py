from decimal import Decimal

from productory_checkout.models import Cart
from productory_checkout.services import recompute_cart_totals, upsert_cart_item
from productory_core.models import Currency, StoreConfig


def test_store_defaults_seeded(db):
    config = StoreConfig.objects.select_related("default_currency", "default_tax_rate").get(
        slug="default"
    )

    assert config.default_currency.code == "ZAR"
    assert config.default_timezone == "Africa/Johannesburg"
    assert config.price_includes_vat is True
    assert config.default_tax_rate.rate_percent == Decimal("15.00")


def test_cart_totals_support_prices_excluding_vat(product):
    config = StoreConfig.objects.get(slug="default")
    config.price_includes_vat = False
    config.save(update_fields=["price_includes_vat", "updated_at"])

    cart = Cart.objects.create(email="exclusive-vat@example.com")
    upsert_cart_item(cart, product.id, 2)
    recompute_cart_totals(cart)
    cart.refresh_from_db()

    assert cart.price_includes_vat is False
    assert cart.vat_rate_percent == Decimal("15.00")
    assert cart.subtotal_excl_vat_amount == Decimal("25.00")
    assert cart.subtotal_incl_vat_amount == Decimal("28.75")
    assert cart.tax_amount == Decimal("3.75")
    assert cart.total_excl_vat_amount == Decimal("25.00")
    assert cart.total_incl_vat_amount == Decimal("28.75")
    assert cart.subtotal_amount == Decimal("28.75")
    assert cart.total_amount == Decimal("28.75")


def test_cart_pricing_snapshot_does_not_drift_after_store_changes(product):
    cart = Cart.objects.create(email="snapshot@example.com")
    assert cart.price_includes_vat is True
    assert cart.vat_rate_percent == Decimal("15.00")

    config = StoreConfig.objects.get(slug="default")
    config.price_includes_vat = False
    config.save(update_fields=["price_includes_vat", "updated_at"])

    upsert_cart_item(cart, product.id, 2)
    recompute_cart_totals(cart)
    cart.refresh_from_db()

    assert cart.price_includes_vat is True
    assert cart.vat_rate_percent == Decimal("15.00")
    assert cart.total_amount == Decimal("25.00")


def test_currency_defaults_follow_store_config(db):
    from productory_catalog.models import Category, Product
    from productory_checkout.models import Cart

    config = StoreConfig.objects.get(slug="default")
    config.default_currency = Currency.objects.get(code="USD")
    config.save(update_fields=["default_currency", "updated_at"])

    category = Category.objects.create(name="Config Category", slug="config-category")

    product = Product.objects.create(
        name="Config Product",
        slug="config-product",
        sku="CFG-001",
        category=category,
        price_amount=Decimal("12.50"),
    )
    cart = Cart.objects.create(email="config@example.com")

    assert product.currency == "USD"
    assert cart.currency == "USD"
