from abc import ABC, abstractmethod
import openai
from unittest.mock import patch, MagicMock

class LLM(ABC):
    """
    Abstract base class for Large Language Model integrations.
    """
    @abstractmethod
    def generate_test_case(self, prompt: str) -> str:
        pass

class OpenAILLM:
    def __init__(self, api_key):
        openai.api_key = api_key

    def generate_test_case(self, prompt):
        response = openai.Completion.create(engine="davinci-codex", prompt=prompt, max_tokens=150)
        return response.choices[0].text.strip()

def test_generate_test_case():
    llm = OpenAILLM(api_key="fake-api-key")
    prompt = "Generate a test case for an API endpoint"
    with patch('openai.Completion.create') as mock_create:
        mock_create.return_value.choices = [MagicMock(text='Generated test case')]
        result = llm.generate_test_case(prompt)
        assert result == 'Generated test case'