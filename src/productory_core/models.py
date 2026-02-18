from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Currency(TimeStampedModel):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=64)
    symbol = models.CharField(max_length=8, blank=True)
    decimal_places = models.PositiveSmallIntegerField(default=2)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(
                fields=["is_default"],
                condition=Q(is_default=True),
                name="productory_core_single_default_currency",
            )
        ]

    def __str__(self) -> str:
        return self.code


class TaxRate(TimeStampedModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=128)
    country_code = models.CharField(max_length=2, default="ZA")
    rate_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("100.00"))],
    )
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(
                fields=["is_default"],
                condition=Q(is_default=True),
                name="productory_core_single_default_tax_rate",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.rate_percent}%)"


class StoreConfig(TimeStampedModel):
    slug = models.SlugField(default="default", unique=True)
    default_currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="store_configs",
    )
    default_timezone = models.CharField(max_length=64, default="Africa/Johannesburg")
    price_includes_vat = models.BooleanField(default=True)
    default_tax_rate = models.ForeignKey(
        TaxRate,
        on_delete=models.PROTECT,
        related_name="store_configs",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Store configuration"
        verbose_name_plural = "Store configuration"

    def __str__(self) -> str:
        return f"StoreConfig<{self.default_currency.code}, {self.default_timezone}>"


class AuditEvent(models.Model):
    class Action(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"
        DELETED = "deleted", "Deleted"
        RELATION_UPDATED = "relation_updated", "Relation Updated"

    created_at = models.DateTimeField(auto_now_add=True)
    model_label = models.CharField(max_length=120)
    object_pk = models.CharField(max_length=64)
    action = models.CharField(max_length=20, choices=Action.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productory_audit_events",
    )
    actor_display = models.CharField(max_length=255, blank=True)
    changes = models.JSONField(default=dict)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(
                fields=["model_label", "object_pk", "-created_at"],
                name="prod_audit_lookup_idx",
            )
        ]

    def __str__(self) -> str:
        return f"AuditEvent<{self.model_label}:{self.object_pk}:{self.action}>"
