from __future__ import annotations

import csv

from django.contrib import admin
from django.http import HttpResponse

from productory_checkout.models import Address, Cart, CartItem, Order, OrderItem


@admin.action(description="Export orders as CSV")
def export_orders_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="orders.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "id",
            "number",
            "status",
            "email",
            "currency",
            "subtotal_amount",
            "discount_amount",
            "tax_amount",
            "total_amount",
        ]
    )
    for order in queryset:
        writer.writerow(
            [
                order.id,
                order.number,
                order.status,
                order.email,
                order.currency,
                order.subtotal_amount,
                order.discount_amount,
                order.tax_amount,
                order.total_amount,
            ]
        )
    return response


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "city", "country_code", "updated_at")
    search_fields = ("first_name", "last_name", "line1", "postal_code")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "currency",
        "subtotal_amount",
        "discount_amount",
        "total_amount",
        "updated_at",
    )
    list_filter = ("status", "currency")
    inlines = [CartItemInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "status",
        "currency",
        "subtotal_amount",
        "discount_amount",
        "total_amount",
        "created_at",
    )
    list_filter = ("status", "currency")
    search_fields = ("number", "email", "full_name")
    inlines = [OrderItemInline]
    actions = [export_orders_csv]
