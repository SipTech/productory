from rest_framework.routers import DefaultRouter

from productory_checkout.api.views import (
    AddressViewSet,
    CartItemViewSet,
    CartViewSet,
    CheckoutViewSet,
    OrderViewSet,
)

router = DefaultRouter()
router.register("addresses", AddressViewSet, basename="productory-address")
router.register("carts", CartViewSet, basename="productory-cart")
router.register("cart-items", CartItemViewSet, basename="productory-cart-item")
router.register("checkout", CheckoutViewSet, basename="productory-checkout")
router.register("orders", OrderViewSet, basename="productory-order")

urlpatterns = router.urls
