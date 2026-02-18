from django.urls import include, path

urlpatterns = [
    path("catalog/", include("productory_catalog.api.urls")),
    path("checkout/", include("productory_checkout.api.urls")),
    path("promotions/", include("productory_promotions.api.urls")),
    path("internal/", include("productory_core.api.urls")),
]
