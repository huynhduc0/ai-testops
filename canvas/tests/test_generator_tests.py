import unittest
from unittest.mock import patch, MagicMock
from api_tests.test_generator import generate_test_case, generate_test_cases, create_test_case_file, request_run_test_case, generate_report

class TestGenerator(unittest.TestCase):
    @patch('api_tests.test_generator.GeminiLLM')
    def test_generate_test_case(self, MockLLM):
        mock_llm = MockLLM.return_value
        mock_llm.generate_test_case.return_value = "def test_case(): pass"
        test_case = MagicMock()
        test_case.method = 'GET'
        test_case.url = '/api/test'
        test_case.body = None
        test_case.parameters = None
        test_case.content = ''
        base_url = 'http://localhost'
        
        result = generate_test_case(mock_llm, test_case, base_url)
        
        self.assertEqual(result.content, "def test_case(): pass")
        test_case.save.assert_called_once()

    @patch('api_tests.test_generator.GeminiLLM')
    def test_generate_test_cases(self, MockLLM):
        mock_llm = MockLLM.return_value
        mock_llm.generate_test_case.return_value = "def test_case(): pass"
        swagger_data = {
            'servers': [{'url': 'http://localhost'}],
            'paths': {
                '/api/test': {
                    'get': {
                        'requestBody': None,
                        'parameters': [],
                        'description': 'Test endpoint'
                    }
                }
            }
        }
        
        result = generate_test_cases(mock_llm, swagger_data)
        
        self.assertEqual(len(result), 1)
        self.assertIn('content', result[0])
        self.assertEqual(result[0]['content'], "def test_case(): pass")

    @patch('api_tests.test_generator.Producer')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_create_test_case_file(self, mock_open, MockProducer):
        test_case_content = "def test_case(): pass"
        test_case_id = 1
        
        result = create_test_case_file(test_case_content, test_case_id)
        
        mock_open.assert_called_once_with('/test_cases/test_case_1.py', 'w')
        mock_open().write.assert_called_once_with(test_case_content)
        MockProducer.return_value.produce.assert_called_once()
        self.assertEqual(result, '/test_cases/test_case_1.py')

    @patch('api_tests.test_generator.Producer')
    @patch('api_tests.test_generator.TestCase')
    def test_request_run_test_case(self, MockTestCase, MockProducer):
        mock_test_case = MockTestCase.objects.get.return_value
        mock_test_case.content = "def test_case(): pass"
        test_case_id = 1
        
        result = request_run_test_case(test_case_id, "def test_case(): pass")
        
        self.assertEqual(result['status'], 'executed')
        mock_test_case.save.assert_called_once()
        MockProducer.return_value.produce.assert_called_once()

    def test_generate_report(self):
        results = [
            {
                'test_case': 1,
                'status': 'passed',
                'summary': 'All tests passed',
                'log': 'Test log'
            }
        ]
        
        result = generate_report(results)
        
        expected_report = (
            "Test Execution Report\n"
            "Test Case ID: 1\n"
            "Status: passed\n"
            "Summary: All tests passed\n"
            "Log: Test log\n\n"
        )
        self.assertEqual(result, expected_report)

if __name__ == '__main__':
    unittest.main()