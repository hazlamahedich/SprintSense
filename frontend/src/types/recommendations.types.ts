export type WorkItemType = 'story' | 'bug' | 'task'

export interface WorkItemRecommendation {
  id: string
  title: string
  description: string
  type: WorkItemType
  suggested_priority: number
  confidence_scores: Record<string, number>
  reasoning: string
  patterns_identified: string[]
  team_velocity_factor: number
}

export interface RecommendationFeedback {
  type: 'not_useful' | 'accepted' | 'modified'
  reason?: string
  timestamp: string
}
