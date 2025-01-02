# api_tests/llm_openai.py
import openai
from .llm import LLM

class OpenAILLM(LLM):
    def __init__(self, api_key: str):
        openai.api_key = api_key

    def generate_test_case(self, prompt: str) -> str:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()