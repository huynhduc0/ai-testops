import unittest
from api_tests.generators.llm_offline import OfflineLLM

class TestOfflineLLM(unittest.TestCase):
    def test_generate_test_case(self):
        llm = OfflineLLM()
        prompt = "Generate a test case for an API endpoint"
        result = llm.generate_test_case(prompt)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

if __name__ == '__main__':
    unittest.main()
