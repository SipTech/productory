from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Promotion, Combo, Product

class PromotionViewSetTestCase(APITestCase):
    def setUp(self):
        # Create test data
        self.combo = Combo.objects.create(
            name='Test Combo',
            price=10.0,
            start_date='2023-04-01 00:00:00',
            end_date='2023-04-30 23:59:59'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=5.0
        )
        self.promotion = Promotion.objects.create(
            name='Test Promotion',
            price=10.0,
            start_date='2023-04-01 00:00:00',
            end_date='2023-04-30 23:59:59'
        )
        self.promotion.combos.add(self.combo)
        self.promotion.products.add(self.product)

        # Set up test client with authentication
        self.client.credentials(HTTP_AUTHORIZATION='Bearer <test_token>')

    def test_list_promotions(self):
        # Test list promotions API endpoint
        url = reverse('promotion-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_promotion(self):
        # Test create promotion API endpoint
        url = reverse('promotion-list')
        data = {
            'name': 'New Promotion',
            'price': 15.0,
            'combos': [self.combo.id],
            'products': [self.product.id],
            'start_date': '2023-05-01 00:00:00',
            'end_date': '2023-05-31 23:59:59'
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Promotion.objects.count(), 2)

    def test_update_promotion(self):
        # Test update promotion API endpoint
        url = reverse('promotion-detail', args=[self.promotion.id])
        data = {
            'name': 'Updated Promotion',
            'price': 12.0,
            'combos': [self.combo.id],
            'products': [self.product.id],
            'start_date': '2023-05-01 00:00:00',
            'end_date': '2023-05-31 23:59:59'
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.promotion.refresh_from_db()
        self.assertEqual(self.promotion.name, 'Updated Promotion')
        self.assertEqual(self.promotion.price, 12.0)

    def test_delete_promotion(self):
        # Test delete promotion API endpoint
        url = reverse('promotion-detail', args=[self.promotion.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Promotion.objects.filter(id=self.promotion.id).exists())
