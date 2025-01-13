from django.test import SimpleTestCase
from django.core.wsgi import get_wsgi_application

class WSGITest(SimpleTestCase):
    def test_wsgi_application(self):
        application = get_wsgi_application()
        self.assertIsNotNone(application)
