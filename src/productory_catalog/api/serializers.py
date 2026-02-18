from __future__ import annotations

from rest_framework import serializers

from productory_catalog.models import Category, Collection, Product, ProductImage, StockRecord


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["id", "name", "slug", "description", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image_url", "alt_text", "position"]


class StockRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockRecord
        fields = ["id", "quantity", "allow_backorder", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "sku",
            "category_name",
            "price_amount",
            "currency",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    collections = CollectionSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    stock_record = StockRecordSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "sku",
            "description",
            "category",
            "collections",
            "price_amount",
            "currency",
            "is_active",
            "images",
            "stock_record",
            "created_at",
            "updated_at",
        ]


class ProductWriteSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.all(),
    )
    collection_ids = serializers.PrimaryKeyRelatedField(
        source="collections",
        many=True,
        queryset=Collection.objects.all(),
        required=False,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "sku",
            "description",
            "category_id",
            "collection_ids",
            "price_amount",
            "currency",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
