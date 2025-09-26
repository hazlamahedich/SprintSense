import pytest
from unittest.mock import AsyncMock, MagicMock
import json

from ..cache import LLMCache, LLMCacheSettings
from ..providers.base import LLMResponse

@pytest.fixture
def cache_settings():
    return LLMCacheSettings(
        ttl=3600,
        prefix="test:cache:",
        max_items=1000
    )

@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.get.return_value = None
    redis.setex.return_value = True
    redis.delete.return_value = 1
    redis.keys.return_value = ["test:cache:key1", "test:cache:key2"]
    redis.scan.return_value = (0, ["test:cache:key1"])
    redis.ttl.return_value = 100
    return redis

@pytest.fixture
def llm_cache(mock_redis, cache_settings):
    return LLMCache(mock_redis, cache_settings)

@pytest.fixture
def sample_response():
    return LLMResponse(
        content="Test response",
        tokens_used=10,
        model="test-model",
        provider="test-provider"
    )

def test_generate_cache_key(llm_cache):
    prompt = "Test prompt"
    params = {"max_tokens": 100, "temperature": 0.7}
    key = llm_cache.generate_cache_key(prompt, params)
    
    # Key should include prefix and be deterministic
    assert key.startswith("test:cache:")
    assert llm_cache.generate_cache_key(prompt, params) == key
    
    # Temperature should be excluded from key
    params2 = {"max_tokens": 100, "temperature": 0.8}
    assert llm_cache.generate_cache_key(prompt, params2) == key

@pytest.mark.asyncio
async def test_cache_get_miss(llm_cache, mock_redis):
    mock_redis.get.return_value = None
    result = await llm_cache.get_cached_response("test:key", "test-provider")
    assert result is None
    mock_redis.get.assert_called_once_with("test:key")

@pytest.mark.asyncio
async def test_cache_get_hit(llm_cache, mock_redis, sample_response):
    mock_redis.get.return_value = sample_response.json()
    result = await llm_cache.get_cached_response("test:key", "test-provider")
    
    assert isinstance(result, LLMResponse)
    assert result.content == sample_response.content
    assert result.tokens_used == sample_response.tokens_used
    assert result.model == sample_response.model
    assert result.provider == sample_response.provider

@pytest.mark.asyncio
async def test_cache_set(llm_cache, mock_redis, sample_response):
    await llm_cache.cache_response("test:key", sample_response)
    
    mock_redis.setex.assert_called_once_with(
        "test:key",
        3600,  # Default TTL
        sample_response.json()
    )

@pytest.mark.asyncio
async def test_cache_set_custom_ttl(llm_cache, mock_redis, sample_response):
    await llm_cache.cache_response("test:key", sample_response, ttl=1800)
    
    mock_redis.setex.assert_called_once_with(
        "test:key",
        1800,
        sample_response.json()
    )

@pytest.mark.asyncio
async def test_cache_invalidate(llm_cache, mock_redis):
    # Set up mock to return some keys
    mock_redis.keys.return_value = ["test:cache:key1", "test:cache:key2"]
    
    count = await llm_cache.invalidate("key*")
    
    assert count == 1  # Mock redis.delete returns 1
    mock_redis.keys.assert_called_once_with("test:cache:key*")
    mock_redis.delete.assert_called_once_with("test:cache:key1", "test:cache:key2")

@pytest.mark.asyncio
async def test_cache_cleanup_expired(llm_cache, mock_redis):
    # First scan returns some keys
    mock_redis.scan.side_effect = [(1, ["key1", "key2"]), (0, ["key3"])]
    mock_redis.ttl.side_effect = [0, 100, 0]  # key1 and key3 are expired
    
    await llm_cache.cleanup_expired()
    
    # Should have checked TTL for all keys
    assert mock_redis.ttl.call_count == 3
    
    # Should have deleted expired keys
    assert mock_redis.delete.call_count == 2
    mock_redis.delete.assert_any_call("key1")
    mock_redis.delete.assert_any_call("key3")