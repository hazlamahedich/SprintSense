import { WorkItemRecommendation } from '../types/recommendations.types'
import { QualityMetrics } from '../types/quality-metrics.types'

class RecommendationsService {
  private baseUrl: string
  private cache: Map<
    string,
    { data: WorkItemRecommendation[]; timestamp: number }
  >
  private readonly cacheTTL = 5 * 60 * 1000 // 5 minutes

  constructor() {
    this.baseUrl = process.env.API_BASE_URL || ''
    this.cache = new Map()
  }

  private getCacheKey(
    teamId: string,
    options: { minConfidence?: number; limit?: number }
  ): string {
    return `${teamId}-${JSON.stringify(options)}`
  }

  private isValidCache(key: string): boolean {
    const cached = this.cache.get(key)
    if (!cached) return false
    return Date.now() - cached.timestamp < this.cacheTTL
  }

  async getRecommendations(
    teamId: string,
    options: { minConfidence?: number; limit?: number } = {}
  ): Promise<WorkItemRecommendation[]> {
    const cacheKey = this.getCacheKey(teamId, options)

    if (this.isValidCache(cacheKey)) {
      return this.cache.get(cacheKey)!.data
    }

    const queryParams = new URLSearchParams({
      min_confidence: String(options.minConfidence || 0.7),
      limit: String(options.limit || 5),
    })

    try {
      const response = await fetch(
        `${this.baseUrl}/teams/${teamId}/work-items/recommendations?${queryParams}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        }
      )

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      this.cache.set(cacheKey, { data, timestamp: Date.now() })
      return data
    } catch (error) {
      console.error('Failed to fetch recommendations:', error)
      throw error
    }
  }

  async acceptRecommendation(id: string): Promise<void> {
    try {
      const response = await fetch(
        `${this.baseUrl}/work-items/recommendations/${id}/accept`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        }
      )

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
    } catch (error) {
      console.error('Failed to accept recommendation:', error)
      throw error
    }
  }

  async provideFeedback(
    id: string,
    type: string,
    reason: string
  ): Promise<void> {
    try {
      const response = await fetch(
        `${this.baseUrl}/work-items/recommendations/${id}/feedback`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ type, reason }),
          credentials: 'include',
        }
      )

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
    } catch (error) {
      console.error('Failed to provide feedback:', error)
      throw error
    }
  }

  async getQualityMetrics(teamId: string): Promise<QualityMetrics> {
    try {
      const response = await fetch(
        `${this.baseUrl}/teams/${teamId}/recommendations/quality-metrics`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        }
      )

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const raw = await response.json()
      const mapped: QualityMetrics = {
        acceptanceRate: raw.acceptance_rate ?? 0,
        recentAcceptanceCount: raw.recent_acceptance_count ?? 0,
        avgConfidence: raw.avg_confidence ?? 0,
        totalRecommendations: raw.total_recommendations ?? 0,
        topFeedbackReason: raw.top_feedback_reason ?? null,
        feedbackCount: raw.feedback_count ?? 0,
        uiResponseTime: raw.ui_response_time ?? 0,
        backendResponseTime95th: raw.backend_response_time_95th ?? 0,
        feedbackReasons: raw.feedback_reasons ?? {},
      }
      return mapped
    } catch (error) {
      console.error('Failed to fetch quality metrics:', error)
      throw error
    }
  }
}

export const recommendationsService = new RecommendationsService()
