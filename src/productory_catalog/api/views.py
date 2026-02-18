from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny

from productory_catalog.api.serializers import (
    CategorySerializer,
    CollectionSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProductWriteSerializer,
)
from productory_catalog.models import Category, Collection, Product


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "slug"]


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "slug"]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").prefetch_related("collections", "images")
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "currency", "is_active"]
    search_fields = ["name", "sku", "slug"]
    ordering_fields = ["name", "price_amount", "created_at"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return ProductWriteSerializer
        if self.action == "list":
            return ProductListSerializer
        return ProductDetailSerializer
