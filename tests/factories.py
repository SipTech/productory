from __future__ import annotations

import factory

from productory_catalog.models import Category, Product
from productory_checkout.models import Cart


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"Product {n}")
    slug = factory.Sequence(lambda n: f"product-{n}")
    sku = factory.Sequence(lambda n: f"SKU-{n:04d}")
    category = factory.SubFactory(CategoryFactory)
    price_amount = "12.50"
    currency = "USD"


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    email = factory.Sequence(lambda n: f"buyer{n}@example.com")
    currency = "USD"
