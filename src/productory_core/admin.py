from __future__ import annotations

from django.contrib import admin

from productory_core.models import Currency, StoreConfig, TaxRate


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
