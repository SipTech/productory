from rest_framework.routers import DefaultRouter

from productory_catalog.api.views import CategoryViewSet, CollectionViewSet, ProductViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="productory-category")
router.register("collections", CollectionViewSet, basename="productory-collection")
router.register("products", ProductViewSet, basename="productory-product")

urlpatterns = router.urls
