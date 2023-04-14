from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from ..models import Menu, Category, Product, Combo, Promotion
from ..serializers import MenuSerializer
from ..views import MenuViewSet
from datetime import datetime, timedelta

class MenuViewSetTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='test category')
        self.product = Product.objects.create(name='test product', price=10.0, category=self.category)
        self.combo = Combo.objects.create(name='test combo', price=20.0, start_date=datetime.now(), end_date=datetime.now() + timedelta(days=1))
        self.combo.products.add(self.product)
        self.promotion = Promotion.objects.create(name='test promotion', price=30.0, start_date=datetime.now(), end_date=datetime.now() + timedelta(days=1))
        self.promotion.combos.add(self.combo)
        self.promotion.products.add(self.product)
        self.menu = Menu.objects.create()
        self.menu.combos.add(self.combo)
        self.menu.products.add(self.product)
        self.menu.promotions.add(self.promotion)
        self.menu.categories.add(self.category)

    def test_get_menu_list(self):
        view = MenuViewSet.as_view({'get': 'list'})
        request = self.factory.get('/menu/')
        force_authenticate(request, user=self.user, authentication=JSONWebTokenAuthentication())
        response = view(request)
        serialized_data = MenuSerializer(self.menu).data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [serialized_data])
