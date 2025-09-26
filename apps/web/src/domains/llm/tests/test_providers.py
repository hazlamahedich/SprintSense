import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any

from ..providers.base import BaseLLMProvider, LLMResponse, LLMError
from ..providers.factory import LLMProviderFactory
from ..providers.openai_provider import OpenAIProvider, OpenAISettings

@pytest.fixture
def openai_settings():
    return OpenAISettings(
        api_key="test_key",
        model="gpt-4",
        organization_id="test_org"
    )

@pytest.fixture
def mock_openai_client():
    client = AsyncMock()
    response = MagicMock()
    response.choices = [
        MagicMock(
            message=MagicMock(content="Test response"),
            finish_reason="stop"
        )
    ]
    response.usage = MagicMock(total_tokens=10)
    response.model = "gpt-4"
    response.created = 123456789
    client.chat.completions.create.return_value = response
    return client

@pytest.fixture
def openai_provider(openai_settings, mock_openai_client, monkeypatch):
    monkeypatch.setattr(
        "openai.AsyncOpenAI",
        lambda **kwargs: mock_openai_client
    )
    return OpenAIProvider(openai_settings)

@pytest.mark.asyncio
async def test_openai_provider_complete(openai_provider, mock_openai_client):
    response = await openai_provider.complete(
        "Test prompt",
        {"temperature": 0.7}
    )
    
    assert isinstance(response, LLMResponse)
    assert response.content == "Test response"
    assert response.tokens_used == 10
    assert response.provider == "openai"
    assert response.model == "gpt-4"
    
    mock_openai_client.chat.completions.create.assert_called_once_with(
        model="gpt-4",
        messages=[{"role": "user", "content": "Test prompt"}],
        temperature=0.7,
        max_tokens=2000
    )

@pytest.mark.asyncio
async def test_openai_provider_error_handling(openai_provider, mock_openai_client):
    mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
    
    with pytest.raises(LLMError) as exc:
        await openai_provider.complete("Test prompt", {})
    
    assert str(exc.value) == "API Error"

@pytest.mark.asyncio
async def test_provider_factory():
    class TestProvider(BaseLLMProvider):
        async def complete(self, prompt: str, params: Dict[str, Any]) -> LLMResponse:
            return LLMResponse(
                content="test",
                tokens_used=1,
                model="test",
                provider="test"
            )
        
        async def validate_key(self) -> bool:
            return True
            
        async def get_model_info(self) -> Dict[str, Any]:
            return {"id": "test"}
            
        def calculate_tokens(self, text: str) -> int:
            return len(text.split())
    
    # Register provider
    LLMProviderFactory.register("test", TestProvider)
    
    # Create settings with test provider
    settings = MagicMock()
    settings.llm_provider = "test"
    
    # Create provider
    provider = LLMProviderFactory.create(settings)
    assert isinstance(provider, TestProvider)
    
    # Test unknown provider
    settings.llm_provider = "unknown"
    with pytest.raises(LLMError):
        LLMProviderFactory.create(settings)