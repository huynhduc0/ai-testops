from django.urls import reverse, resolve
from django.test import SimpleTestCase
from canvas.views import CanvasViewSet

class TestUrls(SimpleTestCase):
    def test_canvas_list_url_resolves(self):
        url = reverse('canvas-list')
        self.assertEqual(resolve(url).func.cls, CanvasViewSet)
