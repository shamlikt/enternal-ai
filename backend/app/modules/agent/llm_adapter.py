from abc import ABC, abstractmethod

from langchain_core.language_models import BaseChatModel


class LLMProviderAdapter(ABC):
    @abstractmethod
    def get_chat_model(self) -> BaseChatModel: ...
