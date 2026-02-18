from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from productory_catalog.models import Category, Product
from productory_checkout.models import Cart
from productory_core.models import Currency


@pytest.mark.django_db
def test_currency_code_must_be_active_for_product_and_cart():
    usd = Currency.objects.get(code="USD")
    usd.is_active = False
    usd.save(update_fields=["is_active", "updated_at"])

    category = Category.objects.create(name="Validation Category", slug="validation-category")

    product = Product(
        name="Validation Product",
        slug="validation-product",
        sku="VAL-001",
        category=category,
        price_amount=Decimal("12.50"),
        currency="USD",
    )
    cart = Cart(email="validator@example.com", currency="USD")

    with pytest.raises(ValidationError):
        product.full_clean()
    with pytest.raises(ValidationError):
        cart.full_clean()


@pytest.mark.django_db
def test_currency_codes_are_normalized_to_uppercase_on_save():
    category = Category.objects.create(name="Upper Category", slug="upper-category")
    product = Product.objects.create(
        name="Upper Product",
        slug="upper-product",
        sku="UP-001",
        category=category,
        price_amount=Decimal("12.50"),
        currency="zar",
    )
    cart = Cart.objects.create(email="upper@example.com", currency="zar")

    assert product.currency == "ZAR"
    assert cart.currency == "ZAR"
