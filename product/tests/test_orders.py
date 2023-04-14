from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Order, Menu
from ..serializers import OrderSerializer
from ..views import OrderViewSet


class OrderViewSetTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.order = Order.objects.create(
            menu=Menu.objects.create(name='Test menu', price=10),
            customer_name='Test customer'
        )

    def test_list_orders(self):
        url = reverse('order-list')
        request = self.factory.get(url)
        request.user = self.user
        view = OrderViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_order(self):
        url = reverse('order-list')
        data = {
            'menu': self.order.menu.id,
            'customer_name': 'New customer'
        }
        request = self.factory.post(url, data)
        request.user = self.user
        view = OrderViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)

    def test_retrieve_order(self):
        url = reverse('order-detail', args=[self.order.id])
        request = self.factory.get(url)
        request.user = self.user
        view = OrderViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=self.order.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = OrderSerializer(self.order).data
        self.assertEqual(response.data, expected_data)

    def test_update_order(self):
        url = reverse('order-detail', args=[self.order.id])
        data = {
            'menu': self.order.menu.id,
            'customer_name': 'Updated customer'
        }
        request = self.factory.put(url, data)
        request.user = self.user
        view = OrderViewSet.as_view({'put': 'update'})
        response = view(request, pk=self.order.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.customer_name, 'Updated customer')

    def test_delete_order(self):
        url = reverse('order-detail', args=[self.order.id])
        request = self.factory.delete(url)
        request.user = self.user
        view = OrderViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=self.order.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 0)
