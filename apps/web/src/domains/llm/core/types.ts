export interface LLMChoice {
  text: string;
  confidence: number;
  index: number;
}

export interface LLMUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface LLMResponse {
  choices: LLMChoice[];
  usage: LLMUsage;
  model: string;
}

export interface LLMClient {
  complete(
    prompt: string,
    params?: Record<string, unknown>
  ): Promise<LLMResponse>;
  validateKey(): Promise<boolean>;
}
