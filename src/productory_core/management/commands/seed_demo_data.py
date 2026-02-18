from __future__ import annotations

import calendar
from decimal import Decimal
from random import Random

from django.core.management.base import BaseCommand
from django.db import transaction

from productory_catalog.models import Category, Collection, Product, StockRecord
from productory_checkout.models import Address, Cart, CartItem, Order, OrderItem
from productory_core.store import get_store_pricing_policy, store_now
from productory_promotions.models import Bundle, BundleItem, Promotion, PromotionType

RNG_SEED = 20260218

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

    @staticmethod
    def _slug(value: str) -> str:
        return value.lower().replace(" ", "-").replace("/", "-")
