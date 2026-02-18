from __future__ import annotations

import calendar
from datetime import timedelta
from decimal import Decimal
from random import Random

from django.core.management.base import BaseCommand
from django.db import transaction

from productory_catalog.models import Category, Collection, Product, StockRecord
from productory_checkout.models import (
    Address,
    Cart,
    CartItem,
    Order,
    OrderItem,
)
from productory_checkout.services import (
    create_order_from_cart,
    transition_order_status,
    upsert_cart_item,
)
from productory_core.store import get_store_pricing_policy, store_now
from productory_promotions.models import Bundle, BundleItem, Promotion, PromotionType

RNG_SEED = 20260218
ADDRESS_COUNT = 10
ORDER_COUNT = 18
OPEN_CART_COUNT = 8
ABANDONED_CART_COUNT = 6

FIRST_NAMES = [
    "Sipho",
    "Lebo",
    "Aisha",
    "Michael",
    "Tariro",
    "Nokuthula",
    "Amira",
    "Daniel",
    "Zanele",
    "Thabo",
]

LAST_NAMES = [
    "Mkhize",
    "Ndlovu",
    "Patel",
    "Smith",
    "Chikore",
    "Dlamini",
    "Khan",
    "Miller",
    "Naidoo",
    "Mokoena",
]

STREET_NAMES = [
    "Main Road",
    "Long Street",
    "Bree Street",
    "Oxford Road",
    "Nelson Mandela Drive",
    "Umhlanga Ridge Blvd",
    "Florida Road",
    "Jan Smuts Avenue",
    "Loop Street",
    "Rivonia Road",
]

CATEGORY_NAMES = [
    "Coffee Beans",
    "Tea",
    "Brewing Gear",
    "Espresso Tools",
    "Grinders",
    "Mugs",
    "Flavors",
    "Snacks",
    "Cold Brew",
    "Subscriptions",
]

COLLECTION_NAMES = [
    "Best Sellers",
    "New Arrivals",
    "Barista Picks",
    "Office Setup",
    "Home Brew",
    "Limited Edition",
    "Budget Friendly",
    "Premium Reserve",
    "Gift Ready",
    "Weekend Specials",
]

ADJECTIVES = [
    "Single Origin",
    "Classic",
    "Sunrise",
    "Midnight",
    "Velvet",
    "Roasted",
    "Craft",
    "Pure",
    "Wild",
    "Urban",
]

NOUNS = [
    "Blend",
    "Roast",
    "Sampler",
    "Infusion",
    "Drip Kit",
    "Mug",
    "Filter",
    "Shot",
    "Pack",
    "Box",
]


class Command(BaseCommand):
    help = "Seed deterministic demo data for Productory apps."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing ecommerce records before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self._reset_all()

        pricing_policy = get_store_pricing_policy()
        randomizer = Random(RNG_SEED)
        categories = self._seed_categories()
        collections = self._seed_collections()
        products = self._seed_products(
            categories, collections, randomizer, currency_code=pricing_policy.currency_code
        )
        self._seed_stock(products, randomizer)
        bundles = self._seed_bundles(products, currency_code=pricing_policy.currency_code)
        self._seed_promotions(products, bundles)
        addresses = self._seed_addresses()
        self._seed_sales(products, addresses, randomizer)

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))

    def _reset_all(self) -> None:
        CartItem.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Cart.objects.all().delete()
        Address.objects.all().delete()

        Promotion.objects.all().delete()
        BundleItem.objects.all().delete()
        Bundle.objects.all().delete()

        StockRecord.objects.all().delete()
        Product.objects.all().delete()
        Collection.objects.all().delete()
        Category.objects.all().delete()

    def _seed_categories(self) -> list[Category]:
        created = []
        for name in CATEGORY_NAMES:
            slug = self._slug(name)
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "description": f"Products for {name.lower()}."},
            )
            created.append(category)
        return created

    def _seed_collections(self) -> list[Collection]:
        created = []
        for name in COLLECTION_NAMES:
            slug = self._slug(name)
            collection, _ = Collection.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "description": f"{name} collection."},
            )
            created.append(collection)
        return created

    def _seed_products(
        self,
        categories: list[Category],
        collections: list[Collection],
        randomizer: Random,
        *,
        currency_code: str,
    ) -> list[Product]:
        created: list[Product] = []

        for idx in range(50):
            adjective = ADJECTIVES[idx % len(ADJECTIVES)]
            noun = NOUNS[(idx // len(ADJECTIVES)) % len(NOUNS)]
            name = f"{adjective} {noun} {idx + 1}"
            slug = self._slug(name)
            sku = f"PRD-{idx + 1:03d}"
            category = categories[idx % len(categories)]

            price_amount = Decimal(randomizer.randrange(750, 6500)) / Decimal("100")
            product, _ = Product.objects.update_or_create(
                sku=sku,
                defaults={
                    "name": name,
                    "slug": slug,
                    "description": f"{name} prepared for demo usage.",
                    "category": category,
                    "price_amount": price_amount.quantize(Decimal("0.01")),
                    "currency": currency_code,
                    "is_active": True,
                },
            )

            product.collections.set(
                {
                    collections[idx % len(collections)],
                    collections[(idx + 3) % len(collections)],
                }
            )
            created.append(product)

        return created

    def _seed_stock(self, products: list[Product], randomizer: Random) -> None:
        for product in products:
            quantity = randomizer.randint(5, 10)
            StockRecord.objects.update_or_create(
                product=product,
                defaults={"quantity": quantity, "allow_backorder": False},
            )

    def _seed_bundles(self, products: list[Product], *, currency_code: str) -> list[Bundle]:
        bundles: list[Bundle] = []

        for idx in range(6):
            name = f"Bundle {idx + 1}"
            slug = f"bundle-{idx + 1}"
            bundle_price = Decimal(18 + idx * 3).quantize(Decimal("0.01"))
            bundle, _ = Bundle.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "bundle_price_amount": bundle_price,
                    "currency": currency_code,
                    "is_active": True,
                },
            )

            BundleItem.objects.filter(bundle=bundle).delete()
            start = idx * 4
            selected = products[start : start + 4]
            for offset, product in enumerate(selected, start=1):
                BundleItem.objects.create(bundle=bundle, product=product, quantity=1 + (offset % 2))

            bundles.append(bundle)

        return bundles

    def _seed_promotions(self, products: list[Product], bundles: list[Bundle]) -> None:
        now = store_now()
        last_day = calendar.monthrange(now.year, now.month)[1]
        month_end = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=0)

        promo_specs = [
            ("launch-10", "Launch 10", PromotionType.PERCENTAGE, Decimal("10.00")),
            ("gear-15", "Gear 15", PromotionType.PERCENTAGE, Decimal("15.00")),
            ("weekend-20", "Weekend 20", PromotionType.PERCENTAGE, Decimal("20.00")),
            ("save-5", "Save 5", PromotionType.FIXED, Decimal("5.00")),
            ("save-8", "Save 8", PromotionType.FIXED, Decimal("8.00")),
        ]

        for idx, (code, name, promo_type, value) in enumerate(promo_specs):
            applies_to_all_products = idx == 0
            promo, _ = Promotion.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "promotion_type": promo_type,
                    "value": value,
                    "applies_to_all_products": applies_to_all_products,
                    "start_at": now,
                    "end_at": month_end,
                    "is_active": True,
                },
            )

            if applies_to_all_products:
                promo.products.clear()
            else:
                product_slice = products[idx * 6 : (idx * 6) + 10]
                promo.products.set(product_slice)
            promo.bundles.set(bundles[idx % len(bundles) : (idx % len(bundles)) + 2])

    def _seed_addresses(self) -> list[Address]:
        addresses: list[Address] = []
        for idx in range(ADDRESS_COUNT):
            address, _ = Address.objects.update_or_create(
                line1=f"{100 + idx} {STREET_NAMES[idx]}",
                postal_code=f"{2000 + idx}",
                defaults={
                    "first_name": FIRST_NAMES[idx],
                    "last_name": LAST_NAMES[idx],
                    "line2": "",
                    "city": "Johannesburg" if idx % 2 == 0 else "Cape Town",
                    "state": "Gauteng" if idx % 2 == 0 else "Western Cape",
                    "country_code": "ZA",
                },
            )
            addresses.append(address)
        return addresses

    def _seed_sales(
        self,
        products: list[Product],
        addresses: list[Address],
        randomizer: Random,
    ) -> None:
        now = store_now()
        status_cycle: list[str] = ["fulfilled", "paid", "submitted", "canceled"]

        for idx in range(ORDER_COUNT):
            cart = Cart.objects.create(email=f"buyer{idx + 1}@example.com")
            for product, quantity in self._cart_line_items(products, randomizer):
                upsert_cart_item(cart, product.id, quantity)

            shipping_address = addresses[idx % len(addresses)]
            billing_address = addresses[(idx + 3) % len(addresses)]
            order = create_order_from_cart(
                cart,
                email=cart.email,
                full_name=f"{shipping_address.first_name} {shipping_address.last_name}",
                shipping_address_id=shipping_address.id,
                billing_address_id=billing_address.id,
            )
            self._set_order_status(order, status_cycle[idx % len(status_cycle)])

            placed_at = now - timedelta(
                days=idx * 2,
                hours=randomizer.randint(0, 23),
                minutes=randomizer.randint(0, 59),
            )
            cart_opened_at = placed_at - timedelta(hours=randomizer.randint(1, 6))
            self._stamp_cart_and_items(cart, cart_opened_at, placed_at)
            self._stamp_order_and_items(order, placed_at)

        self._seed_non_converted_carts(
            products,
            randomizer,
            now,
            prefix="open",
            status="open",
            count=OPEN_CART_COUNT,
        )
        self._seed_non_converted_carts(
            products,
            randomizer,
            now,
            prefix="abandoned",
            status="abandoned",
            count=ABANDONED_CART_COUNT,
        )

    def _seed_non_converted_carts(
        self,
        products: list[Product],
        randomizer: Random,
        now,
        *,
        prefix: str,
        status: str,
        count: int,
    ) -> None:
        for idx in range(count):
            cart = Cart.objects.create(email=f"{prefix}{idx + 1}@example.com")
            for product, quantity in self._cart_line_items(products, randomizer):
                upsert_cart_item(cart, product.id, quantity)

            captured_at = now - timedelta(
                days=randomizer.randint(0, 21),
                hours=randomizer.randint(0, 23),
                minutes=randomizer.randint(0, 59),
            )
            if status != "open":
                Cart.objects.filter(pk=cart.pk).update(status=status)
            self._stamp_cart_and_items(cart, captured_at, captured_at)

    @staticmethod
    def _cart_line_items(products: list[Product], randomizer: Random) -> list[tuple[Product, int]]:
        line_count = randomizer.randint(1, 4)
        selected = randomizer.sample(products, line_count)
        return [(product, randomizer.randint(1, 3)) for product in selected]

    @staticmethod
    def _set_order_status(order: Order, target_status: str) -> None:
        if target_status == "paid":
            transition_order_status(order, "paid")
        elif target_status == "fulfilled":
            transition_order_status(order, "paid")
            transition_order_status(order, "fulfilled")
        elif target_status == "canceled":
            transition_order_status(order, "canceled")

    @staticmethod
    def _stamp_cart_and_items(cart: Cart, created_at, updated_at) -> None:
        Cart.objects.filter(pk=cart.pk).update(created_at=created_at, updated_at=updated_at)
        CartItem.objects.filter(cart=cart).update(created_at=created_at, updated_at=updated_at)

    @staticmethod
    def _stamp_order_and_items(order: Order, timestamp) -> None:
        Order.objects.filter(pk=order.pk).update(created_at=timestamp, updated_at=timestamp)
        OrderItem.objects.filter(order=order).update(created_at=timestamp, updated_at=timestamp)

    @staticmethod
    def _slug(value: str) -> str:
        return value.lower().replace(" ", "-").replace("/", "-")
