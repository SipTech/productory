from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from productory_catalog.models import Product
from productory_core.currency import default_currency_code
from productory_core.models import TimeStampedModel
from productory_core.store import get_store_pricing_policy
from productory_core.validators import validate_active_currency_code


def generate_order_number() -> str:
    return uuid4().hex


class CartStatus(models.TextChoices):
    OPEN = "open", "Open"
    CONVERTED = "converted", "Converted"
    ABANDONED = "abandoned", "Abandoned"


class OrderStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    PAID = "paid", "Paid"
    FULFILLED = "fulfilled", "Fulfilled"
    CANCELED = "canceled", "Canceled"


class Address(TimeStampedModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=30)
    country_code = models.CharField(max_length=2)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}, {self.city}"


class Cart(TimeStampedModel):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productory_carts",
    )
    email = models.EmailField(blank=True)
    currency = models.CharField(
        max_length=3,
        default=default_currency_code,
        validators=[validate_active_currency_code],
    )
    price_includes_vat = models.BooleanField(default=True)
    vat_rate_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    status = models.CharField(max_length=20, choices=CartStatus.choices, default=CartStatus.OPEN)
    subtotal_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    subtotal_excl_vat_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    subtotal_incl_vat_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    total_excl_vat_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    total_incl_vat_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    class Meta:
        indexes = [models.Index(fields=["status", "-updated_at"], name="prod_cart_status_upd_idx")]

    def __str__(self) -> str:
        return f"Cart #{self.pk}"

    def save(self, *args, **kwargs):
        if self._state.adding:
            pricing_policy = get_store_pricing_policy()
            if not self.currency:
                self.currency = pricing_policy.currency_code
            self.price_includes_vat = pricing_policy.price_includes_vat
            self.vat_rate_percent = pricing_policy.vat_rate_percent

        self.currency = self.currency.upper()
        return super().save(*args, **kwargs)


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="cart_items")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    class Meta:
        unique_together = ("cart", "product")


class Order(TimeStampedModel):
    number = models.CharField(max_length=40, unique=True, default=generate_order_number)
    cart = models.ForeignKey(
        Cart,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productory_orders",
    )
    email = models.EmailField(blank=True)
    full_name = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.SUBMITTED,
    )
    currency = models.CharField(
        max_length=3,
        default=default_currency_code,
        validators=[validate_active_currency_code],
    )
    price_includes_vat = models.BooleanField(default=True)
    vat_rate_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    subtotal_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    subtotal_excl_vat_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    subtotal_incl_vat_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    total_excl_vat_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    total_incl_vat_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    shipping_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shipping_orders",
    )
    billing_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billing_orders",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "-created_at"], name="prod_order_status_cre_idx")]

    def __str__(self) -> str:
        return f"Order #{self.number}"

    def save(self, *args, **kwargs):
        self.currency = self.currency.upper()
        return super().save(*args, **kwargs)


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name_snapshot = models.CharField(max_length=255)
    sku_snapshot = models.CharField(max_length=64)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    line_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    class Meta:
        ordering = ["id"]
