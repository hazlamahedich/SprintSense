export interface TitleGenerationRequest {
  description: string;
  context?: {
    category?: string;
    teamId: string;
    examples?: string[];
  };
  options?: {
    maxLength?: number;
    style?: 'concise' | 'detailed';
  };
}

export interface TitleGenerationResponse {
  title: string;
  confidence: number;
  alternatives?: string[];
  metadata: {
    tokensUsed: number;
    model: string;
    cacheHit: boolean;
  };
}

export interface TitleCache {
  get(key: string): Promise<TitleGenerationResponse | null>;
  set(key: string, value: TitleGenerationResponse): Promise<void>;
  warmup(category: string): Promise<void>;
}

export interface ExampleStore {
  getRelevantExamples(category?: string): Promise<string[]>;
}

export interface TemplateEngine {
  render(
    template: string,
    context: Record<string, unknown>
  ): string;
}
