from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.utils.timezone import now
from ..models import Category, Product, Combo, Promotion, Menu
from ..serializers import ProductSerializer

class ProductViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(name='Test Product', price=10.0, category=self.category)
        self.menu = Menu.objects.create()
        self.menu.products.add(self.product)
        self.url = reverse('product-list')
        self.data = {
            'name': 'New Test Product',
            'price': 20.0,
            'category': self.category.id,
        }
        self.serializer_data = ProductSerializer(self.product).data

    def test_list_products(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [self.serializer_data])

    def test_retrieve_product(self):
        response = self.client.get(reverse('product-detail', args=[self.product.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.serializer_data)

    def test_create_product(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.data['name'])
        self.assertEqual(response.data['price'], self.data['price'])
        self.assertEqual(response.data['category'], self.data['category'])

    def test_update_product(self):
        self.client.force_authenticate(user=None)
        response = self.client.put(reverse('product-detail', args=[self.product.id]), self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('product-detail', args=[self.product.id]), self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, self.data['name'])
        self.assertEqual(self.product.price, self.data['price'])
        self.assertEqual(self.product.category_id, self.data['category'])

    def test_delete_product(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(reverse('product-detail', args=[self.product.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('product-detail', args=[self.product.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())
