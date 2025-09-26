import { ExampleStore, TitleGenerationRequest, TemplateEngine } from './types';

export class PromptBuilder {
  private readonly exampleStore: ExampleStore;
  private readonly templateEngine: TemplateEngine;

  constructor(exampleStore: ExampleStore, templateEngine: TemplateEngine) {
    this.exampleStore = exampleStore;
    this.templateEngine = templateEngine;
  }

  async buildTitlePrompt(request: TitleGenerationRequest): Promise<string> {
    const context = await this.buildContext(request);
    const examples = await this.exampleStore.getRelevantExamples(
      request.context?.category
    );

    return this.templateEngine.render('title_generation', {
      description: request.description,
      context,
      examples,
      style: request.options?.style || 'concise',
      maxLength: request.options?.maxLength || 100
    });
  }

  private async buildContext(request: TitleGenerationRequest): Promise<string> {
    const teamContext = await this.getTeamContext(request.context?.teamId);
    return `
      Category: ${request.context?.category || 'General'}
      Team Context: ${teamContext}
      Style: ${request.options?.style || 'concise'}
    `;
  }

  private async getTeamContext(teamId?: string): Promise<string> {
    // TODO: Implement team context fetching
    return teamId ? `Team ${teamId}` : 'General';
  }
}
