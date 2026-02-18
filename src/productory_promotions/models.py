from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from productory_catalog.models import Product
from productory_core.currency import DEFAULT_CURRENCY
from productory_core.models import TimeStampedModel


class Bundle(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    products = models.ManyToManyField(Product, through="BundleItem", related_name="bundles")
    bundle_price_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    currency = models.CharField(max_length=3, default=DEFAULT_CURRENCY)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]


class BundleItem(TimeStampedModel):
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="bundle_items")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("bundle", "product")


class PromotionType(models.TextChoices):
    PERCENTAGE = "percentage", "Percentage"
    FIXED = "fixed", "Fixed Amount"


class Promotion(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=64, unique=True)
    products = models.ManyToManyField(Product, related_name="promotions", blank=True)
    bundles = models.ManyToManyField(Bundle, related_name="promotions", blank=True)
    promotion_type = models.CharField(max_length=20, choices=PromotionType.choices)
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def is_current(self) -> bool:
        now = timezone.now()
        return self.is_active and self.start_at <= now <= self.end_at
