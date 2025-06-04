from __future__ import annotations

from abc import ABC, abstractmethod
from dynamicprompts.prompt_cleaning import clean_prompt


class PromptGenerator(ABC):
    @abstractmethod
    def generate(self, *args, **kwargs) -> list[str]:
        pass
    
    def clean_prompts(self, prompts: list[str]):
        return [clean_prompt(p) for p in prompts]

class GeneratorException(Exception):
    pass
