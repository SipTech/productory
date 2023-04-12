from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Category, Product, Combo, Promotion, Menu
from .serializers import CategorySerializer, ProductSerializer, ComboSerializer, PromotionSerializer, MenuSerializer


class CategoryViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='TestCategory')

    def test_list_categories(self):
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_category(self):
        url = reverse('category-list')
        data = {'name': 'TestCategory2'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)


class ProductViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='TestCategory')
        self.product = Product.objects.create(name='TestProduct', price=10.0, category=self.category)

    def test_list_products(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_product(self):
        url = reverse('product-list')
        data = {'name': 'TestProduct2', 'price': 15.0, 'category': self.category.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

class ComboViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

        self.product1 = Product.objects.create(name='TestProduct1', price=10.0)
        self.product2 = Product.objects.create(name='TestProduct2', price=15.0)
        self.combo = Combo.objects.create(name='TestCombo', price=20.0)

        self.combo.products.add(self.product1)
        self.combo.products.add(self.product2)

    def test_list_combos(self):
        url = reverse('combo-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_combo(self):
        url = reverse('combo-list')
        data = {'name': 'TestCombo2', 'price': 25.0, 'products': [self.product1.id, self.product2.id]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Combo.objects.count(), 2)


class PromotionViewSetTestCase(APITestCase):
    def setUp(self):
        self.promotion1 = Promotion.objects.create(
            name='Promotion 1',
            price=10.99,
            start_date='2023-04-12 00:00:00',
            end_date='2023-04-18 23:59:59'
        )
        self.promotion2 = Promotion.objects.create(
            name='Promotion 2',
            price=20.99,
            start_date='2023-04-19 00:00:00',
            end_date='2023-04-25 23:59:59'
        )
        self.url = reverse('promotion-list')
        self.serializer = PromotionSerializer(instance=[self.promotion1, self.promotion2], many=True)
        self.token = AccessToken.for_user(self.user)

    def test_list_promotions(self):
        response = self.client.get(self.url, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.serializer.data)

    def test_create_promotion(self):
        data = {
            'name': 'New Promotion',
            'price': 15.99,
            'start_date': '2023-05-01 00:00:00',
            'end_date': '2023-05-31 23:59:59',
        }
        response = self.client.post(self.url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        promotion = Promotion.objects.last()
        self.assertEqual(promotion.name, data['name'])
        self.assertEqual(promotion.price, data['price'])
        self.assertEqual(promotion.start_date, data['start_date'])
        self.assertEqual(promotion.end_date, data['end_date'])

    def test_update_promotion(self):
        data = {
            'name': 'Updated Promotion',
            'price': 25.99,
            'start_date': '2023-06-01 00:00:00',
            'end_date': '2023-06-30 23:59:59',
        }
        url = reverse('promotion-detail', args=[self.promotion1.id])
        response = self.client.put(url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        promotion = Promotion.objects.get(id=self.promotion1.id)
        self.assertEqual(promotion.name, data['name'])
        self.assertEqual(promotion.price, data['price'])
        self.assertEqual(promotion.start_date, data['start_date'])
        self.assertEqual(promotion.end_date, data['end_date'])

    def test_delete_promotion(self):
        url = reverse('promotion-detail', args=[self.promotion1.id])
        response = self.client.delete(url, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Promotion.objects.filter(id=self.promotion1.id).exists())

    
class MenuViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(
            name='Test Category'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=10.0,
            category=self.category
        )
        self.combo = Combo.objects.create(
            name='Test Combo',
            price=15.0,
            start_date='2022-01-01 00:00:00',
            end_date='2022-01-31 23:59:59'
        )
        self.combo.products.add(self.product)
        self.promotion = Promotion.objects.create(
            name='Test Promotion',
            price=5.0,
            start_date='2022-01-01 00:00:00',
            end_date='2022-01-31 23:59:59'
        )
        self.promotion.products.add(self.product)
        self.promotion.combos.add(self.combo)
        self.menu = Menu.objects.create()
        self.menu.products.add(self.product)
        self.menu.combos.add(self.combo)
        self.menu.promotions.add(self.promotion)
        self.menu.categories.add(self.category)

    def test_list_menus(self):
        url = reverse('menu-list')
        response = self.client.get(url)
        menus = Menu.objects.all()
        serializer = MenuSerializer(menus, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_menu(self):
        url = reverse('menu-list')
        data = {
            'products': [self.product.id],
            'combos': [self.combo.id],
            'promotions': [self.promotion.id],
            'categories': [self.category.id]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Menu.objects.count(), 2)

    def test_retrieve_menu(self):
        url = reverse('menu-detail', args=[self.menu.id])
        response = self.client.get(url)
        serializer = MenuSerializer(self.menu)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_menu(self):
        url = reverse('menu-detail', args=[self.menu.id])
        data = {
            'products': [],
            'combos': [],
            'promotions': [],
            'categories': []
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Menu.objects.get(id=self.menu.id).products.count(), 0)

    def test_delete_menu(self):
        url = reverse('menu-detail', args=[self.menu.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Menu.objects.count(), 0)
