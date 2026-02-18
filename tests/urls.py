from django.urls import include, path

urlpatterns = [
    path("api/", include("productory_ecommerce.urls")),
]
