from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from home.models import Canvas

class CanvasViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.canvas = Canvas.objects.create(owner=self.user, name='Test Canvas')

    def test_get_queryset(self):
        response = self.client.get(reverse('canvas-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Canvas')

    def test_perform_create(self):
        data = {'name': 'New Canvas'}
        response = self.client.post(reverse('canvas-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Canvas.objects.count(), 2)
        self.assertEqual(Canvas.objects.get(id=response.data['id']).name, 'New Canvas')

    def test_retrieve_canvas(self):
        url = reverse('canvas-detail', args=[self.canvas.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Canvas')

    def test_update_canvas(self):
        url = reverse('canvas-detail', args=[self.canvas.id])
        data = {'name': 'Updated Canvas'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.canvas.refresh_from_db()
        self.assertEqual(self.canvas.name, 'Updated Canvas')

    def test_partial_update_canvas(self):
        url = reverse('canvas-detail', args=[self.canvas.id])
        data = {'name': 'Partially Updated Canvas'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.canvas.refresh_from_db()
        self.assertEqual(self.canvas.name, 'Partially Updated Canvas')

    def test_delete_canvas(self):
        url = reverse('canvas-detail', args=[self.canvas.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Canvas.objects.count(), 0)

    def test_create_canvas_without_name(self):
        data = {}
        response = self.client.post(reverse('canvas-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
