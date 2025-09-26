import { TitleGenerationService } from '../TitleGenerationService';
import { PromptBuilder } from '../PromptBuilder';
import { TitleCache, TitleGenerationRequest, TitleGenerationResponse } from '../types';
import { LLMClient } from '../../core/LLMClient';

describe('TitleGenerationService', () => {
  let service: TitleGenerationService;
  let mockPromptBuilder: jest.Mocked<PromptBuilder>;
  let mockCache: jest.Mocked<TitleCache>;
  let mockLLMClient: jest.Mocked<LLMClient>;

  beforeEach(() => {
    mockPromptBuilder = {
      buildTitlePrompt: jest.fn()
    } as any;

    mockCache = {
      get: jest.fn(),
      set: jest.fn(),
      warmup: jest.fn()
    };

    mockLLMClient = {
      complete: jest.fn()
    } as any;

    service = new TitleGenerationService(
      mockPromptBuilder,
      mockCache,
      mockLLMClient
    );
  });

  const sampleRequest: TitleGenerationRequest = {
    description: 'Sample description for testing',
    context: {
      teamId: 'team1',
      category: 'test'
    },
    options: {
      style: 'concise',
      maxLength: 100
    }
  };

  const sampleResponse: TitleGenerationResponse = {
    title: 'Generated Title',
    confidence: 0.9,
    alternatives: ['Alt 1', 'Alt 2'],
    metadata: {
      tokensUsed: 50,
      model: 'test-model',
      cacheHit: false
    }
  };

  describe('generateTitle', () => {
    it('should return cached response when available', async () => {
      mockCache.get.mockResolvedValue(sampleResponse);

      const result = await service.generateTitle(sampleRequest);

      expect(result).toEqual({
        ...sampleResponse,
        metadata: { ...sampleResponse.metadata, cacheHit: true }
      });
      expect(mockLLMClient.complete).not.toHaveBeenCalled();
    });

    it('should generate new title when cache misses', async () => {
      mockCache.get.mockResolvedValue(null);
      mockPromptBuilder.buildTitlePrompt.mockResolvedValue('test prompt');
      mockLLMClient.complete.mockResolvedValue({
        choices: [{
          text: 'Generated Title',
          confidence: 0.9
        }],
        usage: { total_tokens: 50 },
        model: 'test-model'
      });

      const result = await service.generateTitle(sampleRequest);

      expect(result.title).toBe('Generated Title');
      expect(mockCache.set).toHaveBeenCalled();
    });

    it('should validate request description length', async () => {
      const invalidRequest = {
        ...sampleRequest,
        description: 'short'
      };

      await expect(service.generateTitle(invalidRequest))
        .rejects
        .toThrow('Description must be at least 10 characters long');
    });

    it('should validate maxLength option', async () => {
      const invalidRequest = {
        ...sampleRequest,
        options: {
          ...sampleRequest.options,
          maxLength: 250
        }
      };

      await expect(service.generateTitle(invalidRequest))
        .rejects
        .toThrow('Maximum title length cannot exceed 200 characters');
    });
  });
});
