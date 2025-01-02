# api_tests/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from .models import TestExecution

class TestExecutionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.test_execution = TestExecution.objects.create(
            user=self.user,
            execute_info='Test execution info',
            report_pass_fail=True,
            log='Test log'
        )

    def test_test_execution_creation(self):
        self.assertEqual(self.test_execution.user.username, 'testuser')
        self.assertEqual(self.test_execution.execute_info, 'Test execution info')
        self.assertTrue(self.test_execution.report_pass_fail)
        self.assertEqual(self.test_execution.log, 'Test log')

    def test_test_execution_str(self):
        self.assertEqual(str(self.test_execution), f"TestExecution by {self.user.username} at {self.test_execution.created_at}")