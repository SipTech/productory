from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'combos', views.ComboViewSet)
router.register(r'promotions', views.PromotionViewSet)
router.register(r'menus', views.MenuViewSet)
router.register(r'orders', views.OrderViewSet)

urlpatterns = [
	path('', include(router.urls)),
]
