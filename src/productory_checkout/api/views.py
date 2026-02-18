from __future__ import annotations

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from productory_checkout.api.serializers import (
    AddressSerializer,
    CartDetailSerializer,
    CartItemWriteSerializer,
    CartListSerializer,
    CheckoutSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
    OrderStatusTransitionSerializer,
)
from productory_checkout.models import Address, Cart, CartItem, Order


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [AllowAny]


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.prefetch_related("items__product")
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "list":
            return CartListSerializer
        return CartDetailSerializer


class CartItemViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemWriteSerializer
    permission_classes = [AllowAny]


class CheckoutViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = CheckoutSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        read_serializer = OrderDetailSerializer(order)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


class OrderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Order.objects.prefetch_related("items", "items__product")
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "transition":
            return OrderStatusTransitionSerializer
        return OrderDetailSerializer

    @action(detail=True, methods=["post"])
    def transition(self, request, pk=None):
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            updated = serializer.save()
        except ValueError as exc:
            raise ValidationError({"status": str(exc)}) from exc
        return Response(OrderDetailSerializer(updated).data, status=status.HTTP_200_OK)
