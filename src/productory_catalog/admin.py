from __future__ import annotations

import csv

from django.contrib import admin
from django.http import HttpResponse

from productory_catalog.models import Category, Collection, Product, ProductImage, StockRecord


@admin.action(description="Export categories as CSV")
def export_categories_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="categories.csv"'

    writer = csv.writer(response)
    writer.writerow(["id", "name", "slug", "description"])
    for category in queryset:
        writer.writerow([category.id, category.name, category.slug, category.description])
    return response


@admin.action(description="Export products as CSV")
def export_products_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="products.csv"'

    writer = csv.writer(response)
    writer.writerow(["id", "name", "sku", "category", "price_amount", "currency", "is_active"])
    for product in queryset.select_related("category"):
        writer.writerow(
            [
                product.id,
                product.name,
                product.sku,
                product.category.name,
                product.price_amount,
                product.currency,
                product.is_active,
            ]
        )
    return response


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug")
    actions = [export_categories_csv]


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "price_amount", "currency", "is_active")
    list_filter = ("is_active", "currency", "category")
    search_fields = ("name", "sku", "slug")
    inlines = [ProductImageInline]
    actions = [export_products_csv]


@admin.register(StockRecord)
class StockRecordAdmin(admin.ModelAdmin):
    list_display = ("product", "quantity", "allow_backorder", "updated_at")
    list_filter = ("allow_backorder",)
    search_fields = ("product__name", "product__sku")
