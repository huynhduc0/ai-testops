from abc import ABC, abstractmethod

class LLM(ABC):
    """
    Abstract base class for Large Language Model integrations.
    """
    @abstractmethod
    def generate_test_case(self, prompt: str) -> str:
        pass