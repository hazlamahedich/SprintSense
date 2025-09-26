from typing import Dict, Any, Optional
import openai
from openai import AsyncOpenAI
import tiktoken
from pydantic import BaseSettings, Field

from .base import BaseLLMProvider, LLMResponse, LLMError, RateLimitError, AuthenticationError

class OpenAISettings(BaseSettings):
    """OpenAI-specific settings."""
    api_key: str = Field(..., env='OPENAI_API_KEY')
    model: str = Field('gpt-4', env='OPENAI_MODEL')
    organization_id: Optional[str] = Field(None, env='OPENAI_ORG_ID')
    timeout: int = Field(30, env='OPENAI_TIMEOUT')
    max_retries: int = Field(3, env='OPENAI_MAX_RETRIES')

    class Config:
        env_file = '.env'

class OpenAIProvider(BaseLLMProvider):
    """OpenAI implementation of LLM provider."""

    def __init__(self, settings: OpenAISettings):
        self.settings = settings
        self.client = AsyncOpenAI(
            api_key=settings.api_key,
            organization=settings.organization_id,
            timeout=settings.timeout
        )
        self._encoding = tiktoken.encoding_for_model(settings.model)

    async def complete(
        self,
        prompt: str,
        params: Dict[str, Any]
    ) -> LLMResponse:
        """Generate completion using OpenAI API."""
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=params.get("temperature", 0.7),
                max_tokens=params.get("max_tokens", 2000)
            )
            return LLMResponse(
                content=response.choices[0].message.content,
                tokens_used=response.usage.total_tokens,
                model=response.model,
                provider="openai",
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "created": response.created
                }
            )
        except openai.RateLimitError as e:
            raise RateLimitError(str(e))
        except openai.AuthenticationError as e:
            raise AuthenticationError(str(e))
        except Exception as e:
            raise LLMError(str(e))

    async def validate_key(self) -> bool:
        """Validate OpenAI API key."""
        try:
            await self.client.models.list()
            return True
        except:
            return False

    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        try:
            model = await self.client.models.retrieve(self.settings.model)
            return {
                "id": model.id,
                "owned_by": model.owned_by,
                "created": model.created
            }
        except Exception as e:
            raise LLMError(f"Failed to get model info: {str(e)}")

    def calculate_tokens(self, text: str) -> int:
        """Calculate tokens using tiktoken."""
        return len(self._encoding.encode(text))
