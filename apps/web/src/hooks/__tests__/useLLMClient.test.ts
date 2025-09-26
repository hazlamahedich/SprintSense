import { renderHook } from '@testing-library/react';
import { useLLMClient } from '../useLLMClient';

describe('useLLMClient', () => {
  it('provides an LLM client interface', () => {
    const { result } = renderHook(() => useLLMClient());

    expect(result.current.client).toBeDefined();
    expect(result.current.client.complete).toBeDefined();
    expect(result.current.client.validateKey).toBeDefined();
    expect(result.current.error).toBeNull();
    expect(result.current.isInitialized).toBeDefined();
  });

  it('returns a working complete method', async () => {
    const { result } = renderHook(() => useLLMClient());

    const response = await result.current.client.complete('test prompt');

    expect(response).toEqual({
      choices: [
        {
          text: 'Generated response',
          confidence: 0.9,
          index: 0
        }
      ],
      usage: {
        prompt_tokens: 100,
        completion_tokens: 50,
        total_tokens: 150
      },
      model: 'test-model'
    });
  });

  it('returns a working validateKey method', async () => {
    const { result } = renderHook(() => useLLMClient());

    const isValid = await result.current.client.validateKey();

    expect(isValid).toBe(true);
  });
});
