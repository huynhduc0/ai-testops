from django.test import SimpleTestCase
from django.core.asgi import get_asgi_application

class ASGITest(SimpleTestCase):
    def test_asgi_application(self):
        application = get_asgi_application()
        self.assertIsNotNone(application)
