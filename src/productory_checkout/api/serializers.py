from __future__ import annotations

from rest_framework import serializers

from productory_catalog.api.serializers import ProductDetailSerializer, ProductListSerializer
from productory_catalog.models import Product
from productory_checkout.models import Address, Cart, CartItem, Order, OrderItem, OrderStatus
from productory_checkout.services import (
    create_order_from_cart,
    transition_order_status,
    upsert_cart_item,
)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "first_name",
            "last_name",
            "line1",
            "line2",
            "city",
            "state",
            "postal_code",
            "country_code",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class CartItemReadSerializer(serializers.ModelSerializer):
    product = ProductDetailSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "unit_price_snapshot", "created_at", "updated_at"]


class CartItemWriteSerializer(serializers.Serializer):
    cart_id = serializers.PrimaryKeyRelatedField(queryset=Cart.objects.all(), source="cart")
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
    )
    quantity = serializers.IntegerField(min_value=1)

    def create(self, validated_data):
        return upsert_cart_item(
            cart=validated_data["cart"],
            product_id=validated_data["product"].id,
            quantity=validated_data["quantity"],
        )


class CartListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = [
            "id",
            "email",
            "currency",
            "status",
            "subtotal_amount",
            "discount_amount",
            "total_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "subtotal_amount", "discount_amount", "total_amount"]


class CartDetailSerializer(CartListSerializer):
    items = CartItemReadSerializer(many=True, read_only=True)

    class Meta(CartListSerializer.Meta):
        fields = CartListSerializer.Meta.fields + ["items"]


class OrderItemReadSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name_snapshot",
            "sku_snapshot",
            "quantity",
            "unit_price_snapshot",
            "line_total",
        ]


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "number",
            "status",
            "currency",
            "email",
            "full_name",
            "subtotal_amount",
            "discount_amount",
            "tax_amount",
            "total_amount",
            "created_at",
            "updated_at",
        ]


class OrderDetailSerializer(OrderListSerializer):
    items = OrderItemReadSerializer(many=True, read_only=True)

    class Meta(OrderListSerializer.Meta):
        fields = OrderListSerializer.Meta.fields + ["items"]


class CheckoutSerializer(serializers.Serializer):
    cart_id = serializers.PrimaryKeyRelatedField(queryset=Cart.objects.all(), source="cart")
    email = serializers.EmailField(required=False, allow_blank=True)
    full_name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    shipping_address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source="shipping_address",
        required=False,
        allow_null=True,
    )
    billing_address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source="billing_address",
        required=False,
        allow_null=True,
    )

    def create(self, validated_data):
        return create_order_from_cart(
            cart=validated_data["cart"],
            email=validated_data.get("email", ""),
            full_name=validated_data.get("full_name", ""),
            shipping_address_id=getattr(validated_data.get("shipping_address"), "id", None),
            billing_address_id=getattr(validated_data.get("billing_address"), "id", None),
        )


class OrderStatusTransitionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=OrderStatus.choices)

    def update(self, instance: Order, validated_data):
        return transition_order_status(instance, validated_data["status"])
