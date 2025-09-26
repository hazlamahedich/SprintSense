import { useState, useCallback } from 'react';
import { TitleGenerationRequest, TitleGenerationResponse } from '../domains/llm/title/types';
import { useLLMClient } from './useLLMClient';
import { useRedisCache } from './useRedisCache';

export function useTitleGeneration() {
  const [isLoading, setIsLoading] = useState(false);
  const { client: llmClient } = useLLMClient();
  const { cache } = useRedisCache();

  const generateTitle = useCallback(async (
    request: TitleGenerationRequest
  ): Promise<TitleGenerationResponse> => {
    setIsLoading(true);
    try {
      // TODO: Implement using TitleGenerationService
      const response = await llmClient.generateTitle(request);
      return response;
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [llmClient]);

  return {
    generateTitle,
    isLoading
  };
}
