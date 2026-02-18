from django.contrib import admin

from productory_promotions.models import Bundle, BundleItem, Promotion


class BundleItemInline(admin.TabularInline):
    model = BundleItem
    extra = 0


@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "bundle_price_amount", "currency", "is_active")
    list_filter = ("is_active", "currency")
    search_fields = ("name", "slug")
    inlines = [BundleItemInline]


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "promotion_type", "value", "start_at", "end_at", "is_active")
    list_filter = ("promotion_type", "is_active")
    search_fields = ("name", "code")
    filter_horizontal = ("products", "bundles")
