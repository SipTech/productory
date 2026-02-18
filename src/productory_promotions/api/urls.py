from rest_framework.routers import DefaultRouter

from productory_promotions.api.views import BundleViewSet, PromotionViewSet

router = DefaultRouter()
router.register("bundles", BundleViewSet, basename="productory-bundle")
router.register("promotions", PromotionViewSet, basename="productory-promotion")

urlpatterns = router.urls
