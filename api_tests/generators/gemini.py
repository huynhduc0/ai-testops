from .llm import LLM
import requests
import google.generativeai as genai

class GeminiLLM(LLM):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_test_case(self, prompt: str) -> str:
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        model.fi
        return response.text