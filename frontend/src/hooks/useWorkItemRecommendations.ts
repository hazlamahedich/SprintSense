import { useState, useEffect, useCallback } from 'react'
import { WorkItemRecommendation } from '../types/recommendations.types'
import { recommendationsService } from '../services/recommendationsService'

interface UseWorkItemRecommendationsOptions {
  minConfidence?: number
  limit?: number
}

interface UseWorkItemRecommendationsReturn {
  recommendations: WorkItemRecommendation[]
  isLoading: boolean
  error: Error | null
  acceptRecommendation: (id: string) => Promise<void>
  modifyRecommendation: (id: string) => Promise<void>
  provideRecommendationFeedback: (
    id: string,
    type: string,
    reason: string
  ) => Promise<void>
}

export const useWorkItemRecommendations = (
  teamId: string,
  options: UseWorkItemRecommendationsOptions = {}
): UseWorkItemRecommendationsReturn => {
  const [recommendations, setRecommendations] = useState<
    WorkItemRecommendation[]
  >([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchRecommendations = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      const data = await recommendationsService.getRecommendations(
        teamId,
        options
      )
      setRecommendations(data)
    } catch (err) {
      setError(
        err instanceof Error
          ? err
          : new Error('Failed to fetch recommendations')
      )
    } finally {
      setIsLoading(false)
    }
  }, [teamId, options])

  useEffect(() => {
    fetchRecommendations()
  }, [fetchRecommendations])

  const acceptRecommendation = async (id: string) => {
    try {
      await recommendationsService.acceptRecommendation(id)
      setRecommendations((prev) => prev.filter((r) => r.id !== id))
    } catch (err) {
      setError(
        err instanceof Error
          ? err
          : new Error('Failed to accept recommendation')
      )
    }
  }

  const modifyRecommendation = async (id: string) => {
    try {
      const modifiedRecommendation = recommendations.find((r) => r.id === id)
      if (!modifiedRecommendation) throw new Error('Recommendation not found')
      // Store in global state for pre-filling the work item form
      // This will be handled by the work item creation modal
    } catch (err) {
      setError(
        err instanceof Error
          ? err
          : new Error('Failed to modify recommendation')
      )
    }
  }

  const provideRecommendationFeedback = async (
    id: string,
    type: string,
    reason: string
  ) => {
    try {
      await recommendationsService.provideFeedback(id, type, reason)
      setRecommendations((prev) => prev.filter((r) => r.id !== id))
    } catch (err) {
      setError(
        err instanceof Error ? err : new Error('Failed to provide feedback')
      )
    }
  }

  return {
    recommendations,
    isLoading,
    error,
    acceptRecommendation,
    modifyRecommendation,
    provideRecommendationFeedback,
  }
}
