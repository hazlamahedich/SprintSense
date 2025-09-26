import { LLMClient, LLMResponse } from '../core/types';
import {
  TitleGenerationRequest,
  TitleGenerationResponse,
  TitleCache
} from './types';
import { PromptBuilder } from './PromptBuilder';
import { createHash } from 'crypto';

export class TitleGenerationService {
  private readonly promptBuilder: PromptBuilder;
  private readonly cache: TitleCache;
  private readonly llmClient: LLMClient;

  constructor(
    promptBuilder: PromptBuilder,
    cache: TitleCache,
    llmClient: LLMClient
  ) {
    this.promptBuilder = promptBuilder;
    this.cache = cache;
    this.llmClient = llmClient;
  }

  async generateTitle(
    request: TitleGenerationRequest
  ): Promise<TitleGenerationResponse> {
    this.validateRequest(request);

    const cacheKey = this.generateCacheKey(request);
    const cached = await this.cache.get(cacheKey);

    if (cached) {
      return {
        ...cached,
        metadata: { ...cached.metadata, cacheHit: true }
      };
    }

    const prompt = await this.promptBuilder.buildTitlePrompt(request);
    const llmResponse = await this.llmClient.complete(prompt, {
      max_tokens: request.options?.maxLength || 100,
      temperature: 0.7,
      top_p: 1,
      frequency_penalty: 0.5,
      presence_penalty: 0.5
    });

    const result = this.processLLMResponse(llmResponse);
    await this.cache.set(cacheKey, result);

    return result;
  }

  private validateRequest(request: TitleGenerationRequest): void {
    if (!request.description || request.description.trim().length < 10) {
      throw new Error('Description must be at least 10 characters long');
    }

    if (request.options?.maxLength && request.options.maxLength > 200) {
      throw new Error('Maximum title length cannot exceed 200 characters');
    }
  }

  private generateCacheKey(request: TitleGenerationRequest): string {
    const content = JSON.stringify({
      description: request.description,
      category: request.context?.category,
      style: request.options?.style,
      maxLength: request.options?.maxLength
    });

    return createHash('sha256').update(content).digest('hex');
  }

  private processLLMResponse(response: LLMResponse): TitleGenerationResponse {
    // TODO: Implement proper response processing
    return {
      title: response.choices?.[0]?.text?.trim() || '',
      confidence: response.choices?.[0]?.confidence || 0.8,
      alternatives: response.choices?.slice(1)?.map(c => c.text?.trim()),
      metadata: {
        tokensUsed: response.usage?.total_tokens || 0,
        model: response.model || 'unknown',
        cacheHit: false
      }
    };
  }
}
