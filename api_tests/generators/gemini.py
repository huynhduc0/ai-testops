from .llm import LLM
import requests
import google.generativeai as genai
import google.api_core.exceptions
from unittest.mock import patch, MagicMock

class GeminiLLM(LLM):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_test_case(self, prompt: str) -> str:
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel("gemini-flash-latest")
        try:
            response = model.generate_content(prompt)
        except google.api_core.exceptions.ResourceExhausted as e:
            raise RuntimeError("Resource has been exhausted (e.g. check quota).") from e
        
        # print(response)
        
        if response.candidates[0].finish_reason == 4:
            raise ValueError("Invalid operation: The response contains copyrighted material.")
        
        if not response.candidates[0].content.parts:
            raise ValueError("Invalid response: No content parts found.")
        
        return response.candidates[0].content.parts[0].text

def test_generate_test_case():
    llm = GeminiLLM(api_key="fake-api-key")
    prompt = "Generate a test case for an API endpoint"
    with patch('google.generativeai.GenerativeModel.generate_content') as mock_generate_content:
        mock_generate_content.return_value.candidates = [MagicMock(content=MagicMock(parts=[MagicMock(text='Generated test case')]))]
        result = llm.generate_test_case(prompt)
        assert result == 'Generated test case'