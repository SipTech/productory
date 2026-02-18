from __future__ import annotations

from django.contrib import admin

from productory_core.models import AuditEvent, Currency, StoreConfig, TaxRate


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "symbol", "decimal_places", "is_active", "is_default")
    list_filter = ("is_active", "is_default")
    search_fields = ("code", "name", "symbol")
    ordering = ("code",)


@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "country_code", "rate_percent", "is_active", "is_default")
    list_filter = ("country_code", "is_active", "is_default")
    search_fields = ("code", "name")
    ordering = ("code",)


@admin.register(StoreConfig)
class StoreConfigAdmin(admin.ModelAdmin):
    list_display = (
        "slug",
        "default_currency",
        "default_timezone",
        "price_includes_vat",
        "default_tax_rate",
        "updated_at",
    )
    search_fields = ("slug", "default_timezone")
    autocomplete_fields = ("default_currency", "default_tax_rate")


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("created_at", "model_label", "object_pk", "action", "actor_display")
    list_filter = ("model_label", "action")
    search_fields = ("model_label", "object_pk", "actor_display")
    readonly_fields = (
        "created_at",
        "model_label",
        "object_pk",
        "action",
        "actor",
        "actor_display",
        "changes",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
