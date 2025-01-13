# api_tests/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from .models import TestExecution
from .generators.openai import OpenAILLM
from .generators.llm_offline import OfflineLLM
from .generators.gemini import GeminiLLM
from unittest.mock import patch, MagicMock
from django.urls import reverse
from django.test import Client
from .models import TestCase as TestCaseModel, TestResult
import json

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

class OpenAILLMTest(TestCase):
    def setUp(self):
        self.llm = OpenAILLM(api_key='fake-api-key')

    @patch('openai.Completion.create')
    def test_generate_test_case(self, mock_create):
        mock_create.return_value.choices = [MagicMock(text='Generated test case')]
        result = self.llm.generate_test_case('Test prompt')
        self.assertEqual(result, 'Generated test case')

# class OfflineLLMTest(TestCase):
#     @patch('transformers.pipeline')
#     def setUp(self, mock_pipeline):
#         # Mock pipeline once for the entire test class
#         self.mock_pipeline = mock_pipeline
#         self.mock_generator = MagicMock()
#         self.mock_pipeline.return_value = self.mock_generator
#         self.llm = OfflineLLM()

#     def test_generate_test_case(self):
#         self.mock_generator.return_value = [{'generated_text': 'Generated test case'}]
#         result = self.llm.generate_test_case('Test prompt')
#         self.assertEqual(result, 'Generated test case')
#         self.mock_pipeline.assert_called_once_with(task='text-generation', model=None)
#         self.mock_generator.assert_called_once_with('Test prompt')

#     def test_generate_test_case_empty_prompt(self):
#         self.mock_generator.return_value = [{'generated_text': ''}]
#         result = self.llm.generate_test_case('')
#         self.assertEqual(result, '')

#     def test_generate_test_case_pipeline_error(self):
#         self.mock_pipeline.side_effect = RuntimeError('Pipeline error')
#         with self.assertRaises(RuntimeError):
#             self.llm.generate_test_case('Test prompt')

class GeminiLLMTest(TestCase):
    def setUp(self):
        self.llm = GeminiLLM(api_key='fake-api-key')

    @patch('google.generativeai.GenerativeModel.generate_content')
    def test_generate_test_case(self, mock_generate_content):
        mock_generate_content.return_value.candidates = [MagicMock(content=MagicMock(parts=[MagicMock(text='Generated test case')]), finish_reason=0)]
        result = self.llm.generate_test_case('Test prompt')
        self.assertEqual(result, 'Generated test case')

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.test_execution = TestExecution.objects.create(
            user=self.user,
            execute_info='Test execution info',
            report_pass_fail=True,
            log='Test log'
        )
        self.test_case = TestCaseModel.objects.create(
            test_execution=self.test_execution,
            url='/test/url',
            method='GET',
            body={},
            parameters=[],
            content=''
        )

    def test_parse_and_test_view(self):
        response = self.client.get(reverse('parse_and_test'))
        self.assertEqual(response.status_code, 200)

    @patch('api_tests.views.parse_swagger_from_url')
    @patch('api_tests.views.get_base_url')
    def test_parse_and_test_post(self, mock_get_base_url, mock_parse_swagger_from_url):
        mock_get_base_url.return_value = 'http://example.com'
        mock_parse_swagger_from_url.return_value = {'paths': {'/test/url': {'get': {}}}}
        response = self.client.post(reverse('parse_and_test'), {'swagger_url': 'http://example.com/swagger.yaml'})
        self.assertEqual(response.status_code, 302)

    def test_test_api_view(self):
        response = self.client.get(reverse('test_api'))
        self.assertEqual(response.status_code, 200)

    def test_list_test_executions(self):
        response = self.client.get(reverse('list_test_executions'))
        self.assertEqual(response.status_code, 200)

    def test_test_execution_detail(self):
        response = self.client.get(reverse('test_execution_detail', args=[self.test_execution.id]))
        self.assertEqual(response.status_code, 200)

    def test_test_result_detail(self):
        test_result = TestResult.objects.create(test_case=self.test_case, status='passed', log='')
        response = self.client.get(reverse('test_result_detail', args=[test_result.id]))
        self.assertEqual(response.status_code, 200)

    @patch('api_tests.views.GeminiLLM')
    @patch('api_tests.views.generate_test_case')
    def test_generate_test_case_content(self, mock_generate_test_case, mock_GeminiLLM):
        mock_generate_test_case.return_value = self.test_case
        response = self.client.get(reverse('generate_test_case_content', args=[self.test_case.id]))
        self.assertEqual(response.status_code, 200)

    @patch('api_tests.views.request_run_test_case')
    def test_execute_test_case(self, mock_request_run_test_case):
        response = self.client.get(reverse('execute_test_case', args=[self.test_case.id]))
        self.assertEqual(response.status_code, 200)

    @patch('api_tests.views.generate_report')
    @patch('api_tests.views.request_run_test_case')
    @patch('api_tests.views.generate_test_case')
    def test_execute_tests(self, mock_generate_test_case, mock_request_run_test_case, mock_generate_report):
        mock_generate_test_case.return_value = self.test_case
        mock_generate_report.return_value = 'Test report'
        response = self.client.get(reverse('execute_tests', args=[self.test_execution.id]))
        self.assertEqual(response.status_code, 200)

    def test_save_test_result(self):
        response = self.client.post(reverse('save_test_result', args=[self.test_case.id]), json.dumps({'status': 'passed', 'log': ''}), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_save_test_case_content(self):
        response = self.client.post(reverse('save_test_case_content', args=[self.test_case.id]), json.dumps({'content': 'new content'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_test_case_detail_api(self):
        response = self.client.get(reverse('test_case_detail_api', args=[self.test_case.id]))
        self.assertEqual(response.status_code, 200)

    def test_update_base_url(self):
        response = self.client.post(reverse('update_base_url'), json.dumps({'base_url': 'http://new-url.com', 'test_execution_id': self.test_execution.id}), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_update_test_summary(self):
        response = self.client.get(reverse('update_test_summary'), {'test_execution_id': self.test_execution.id})
        self.assertEqual(response.status_code, 200)