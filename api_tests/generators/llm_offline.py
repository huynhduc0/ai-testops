# api_tests/llm_offline.py
from .llm import LLM
from transformers import pipeline

class OfflineLLM(LLM):
    def __init__(self):
        self.generator = pipeline("text-generation", model="gpt2")

    def generate_test_case(self, prompt: str) -> str:
        result = self.generator(prompt, max_new_tokens=150, num_return_sequences=1)
        return result[0]["generated_text"]

def test_generate_test_case():
    llm = OfflineLLM()
    prompt = "Generate a test case for an API endpoint"
    result = llm.generate_test_case(prompt)
    assert isinstance(result, str)
    assert len(result) > 0