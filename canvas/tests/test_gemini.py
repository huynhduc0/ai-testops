import unittest
from unittest.mock import patch, MagicMock
from api_tests.generators.gemini import GeminiLLM

class TestGeminiLLM(unittest.TestCase):
    @patch('google.generativeai.GenerativeModel.generate_content')
    def test_generate_test_case(self, mock_generate_content):
        llm = GeminiLLM(api_key="fake-api-key")
        prompt = "Generate a test case for an API endpoint"
        mock_generate_content.return_value.candidates = [MagicMock(content=MagicMock(parts=[MagicMock(text='Generated test case')]))]
        result = llm.generate_test_case(prompt)
        self.assertEqual(result, 'Generated test case')

if __name__ == '__main__':
    unittest.main()
