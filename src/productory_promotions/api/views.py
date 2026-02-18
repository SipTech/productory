from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from productory_promotions.api.serializers import BundleSerializer, PromotionSerializer
from productory_promotions.models import Bundle, Promotion


class BundleViewSet(viewsets.ModelViewSet):
    queryset = Bundle.objects.prefetch_related("items")
    serializer_class = BundleSerializer
    permission_classes = [AllowAny]


class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.prefetch_related("products", "bundles")
    serializer_class = PromotionSerializer
    permission_classes = [AllowAny]
