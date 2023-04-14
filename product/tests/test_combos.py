from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from ..models import Combo, Product, Category


class ComboViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(name="Test Product", price=9.99, category=self.category)
        self.combo = Combo.objects.create(name="Test Combo", price=19.99, start_date="2022-01-01T00:00:00Z", end_date="2022-01-31T23:59:59Z")
        self.combo.products.add(self.product)
        self.url = reverse('combo-list')

        # Set up authentication token for the client
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_list_combos(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_combo(self):
        data = {
            "name": "New Combo",
            "price": 24.99,
            "products": [self.product.id],
            "start_date": "2022-02-01T00:00:00Z",
            "end_date": "2022-02-28T23:59:59Z"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Combo.objects.count(), 2)

    def test_retrieve_combo(self):
        combo_url = reverse('combo-detail', args=[self.combo.id])
        response = self.client.get(combo_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.combo.name)

    def test_update_combo(self):
        combo_url = reverse('combo-detail', args=[self.combo.id])
        data = {
            "name": "Updated Combo",
            "price": 29.99,
            "products": [self.product.id],
            "start_date": "2022-02-01T00:00:00Z",
            "end_date": "2022-02-28T23:59:59Z"
        }
        response = self.client.put(combo_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['price'], data['price'])

    def test_delete_combo(self):
        combo_url = reverse('combo-detail', args=[self.combo.id])
        response = self.client.delete(combo_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Combo.objects.count(), 0)
