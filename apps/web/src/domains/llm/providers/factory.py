from typing import Dict, Type
from pydantic import BaseSettings
from .base import BaseLLMProvider, LLMError

class LLMProviderFactory:
    """Factory for creating LLM provider instances."""
    _providers: Dict[str, Type[BaseLLMProvider]] = {}
    
    @classmethod
    def register(cls, name: str, provider_class: Type[BaseLLMProvider]) -> None:
        """Register a provider implementation."""
        cls._providers[name.lower()] = provider_class
    
    @classmethod
    def create(cls, settings: BaseSettings) -> BaseLLMProvider:
        """Create provider instance based on settings."""
        provider_type = settings.llm_provider.lower()
        if provider_type not in cls._providers:
            raise LLMError(f"Unknown provider: {provider_type}")
            
        return cls._providers[provider_type](settings)