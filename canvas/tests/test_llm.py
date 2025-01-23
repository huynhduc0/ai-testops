import unittest
from unittest.mock import patch, MagicMock
from api_tests.generators.llm import OpenAILLM

class TestOpenAILLM(unittest.TestCase):
    @patch('openai.Completion.create')
    def test_generate_test_case(self, mock_create):
        llm = OpenAILLM(api_key="fake-api-key")
        prompt = "Generate a test case for an API endpoint"
        mock_create.return_value.choices = [MagicMock(text='Generated test case')]
        result = llm.generate_test_case(prompt)
        self.assertEqual(result, 'Generated test case')

if __name__ == '__main__':
    unittest.main()
