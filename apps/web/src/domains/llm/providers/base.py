from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class LLMResponse(BaseModel):
    """Response from an LLM provider."""
    content: str = Field(..., description="The generated text content")
    tokens_used: int = Field(..., description="Total tokens used for request/response")
    model: str = Field(..., description="Model used for generation")
    provider: str = Field(..., description="Provider name")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class LLMError(Exception):
    """Base exception for LLM provider errors."""
    pass

class RateLimitError(LLMError):
    """Rate limit exceeded."""
    pass

class AuthenticationError(LLMError):
    """Authentication failed."""
    pass

class BaseLLMProvider(ABC):
    """Base class for all LLM providers."""

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        params: Dict[str, Any]
    ) -> LLMResponse:
        """Generate completion for given prompt."""
        pass

    @abstractmethod
    async def validate_key(self) -> bool:
        """Validate API key is active and has required permissions."""
        pass

    @abstractmethod
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        pass

    @abstractmethod
    def calculate_tokens(self, text: str) -> int:
        """Calculate number of tokens in text."""
        pass