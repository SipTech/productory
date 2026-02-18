from rest_framework import serializers

from productory_promotions.models import Bundle, BundleItem, Promotion


class BundleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BundleItem
        fields = ["id", "product", "quantity"]


class BundleSerializer(serializers.ModelSerializer):
    items = BundleItemSerializer(many=True, read_only=True)

    class Meta:
        model = Bundle
        fields = [
            "id",
            "name",
            "slug",
            "bundle_price_amount",
            "currency",
            "is_active",
            "items",
            "created_at",
            "updated_at",
        ]


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = [
            "id",
            "name",
            "code",
            "applies_to_all_products",
            "products",
            "bundles",
            "promotion_type",
            "value",
            "start_at",
            "end_at",
            "is_active",
            "created_at",
            "updated_at",
        ]
