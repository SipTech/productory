from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("productory_ecommerce.urls")),
]

if settings.DEMO_ENABLE_JWT:
    from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

    urlpatterns += [
        path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
        path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    ]
