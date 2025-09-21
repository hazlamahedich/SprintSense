export interface QualityMetrics {
  acceptanceRate: number
  recentAcceptanceCount: number
  avgConfidence: number
  totalRecommendations: number
  topFeedbackReason: string | null
  feedbackCount: number
  uiResponseTime: number
  backendResponseTime95th: number
  feedbackReasons: Record<string, number>
}
