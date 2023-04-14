from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Category
from ..serializers import CategorySerializer

class CategoryViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

        self.category1 = Category.objects.create(name='Category 1')
        self.category2 = Category.objects.create(name='Category 2')

    def test_get_all_categories(self):
        response = self.client.get(reverse('category-list'))
        categories = Category.objects.all()
        serializer_data = CategorySerializer(categories, many=True).data
        self.assertEqual(response.data, serializer_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_category_by_id(self):
        response = self.client.get(reverse('category-detail', args=[self.category1.id]))
        category = Category.objects.get(id=self.category1.id)
        serializer_data = CategorySerializer(category).data
        self.assertEqual(response.data, serializer_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_category(self):
        new_category = {
            'name': 'New Category'
        }
        response = self.client.post(reverse('category-list'), data=new_category)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 3)

    def test_update_category(self):
        updated_category = {
            'name': 'Updated Category'
        }
        response = self.client.put(reverse('category-detail', args=[self.category1.id]), data=updated_category)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Category.objects.get(id=self.category1.id).name, 'Updated Category')

    def test_delete_category(self):
        response = self.client.delete(reverse('category-detail', args=[self.category1.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 1)
