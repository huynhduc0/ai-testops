# api_tests/llm_offline.py
from .llm import LLM
from transformers import pipeline

class OfflineLLM(LLM):
    def __init__(self):
        self.generator = pipeline("text-generation", model="gpt2")

    def generate_test_case(self, prompt: str) -> str:
        result = self.generator(prompt, max_new_tokens=150, num_return_sequences=1)
        return result[0]["generated_text"]