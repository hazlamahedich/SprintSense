import { render, waitFor, screen, cleanup } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import { QualityDashboard } from '../components/feature/recommendations/QualityDashboard'
import { recommendationsService } from '../services/recommendationsService'

// Mock the metrics service
vi.mock('../services/recommendationsService', () => ({
  recommendationsService: {
    getQualityMetrics: vi.fn(),
  },
}))

// Mock metrics response
const mockMetrics = {
  acceptanceRate: 0.75,
  recentAcceptanceCount: 15,
  avgConfidence: 0.85,
  totalRecommendations: 100,
  topFeedbackReason: 'too_complex',
  feedbackCount: 25,
  uiResponseTime: 250,
  backendResponseTime95th: 150,
  feedbackReasons: {
    too_complex: 10,
    not_relevant: 8,
    duplicate: 7,
  },
}

describe('QualityDashboard Performance', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(recommendationsService.getQualityMetrics as any).mockResolvedValue(
      mockMetrics
    )
  })

  afterEach(() => {
    cleanup()
  })

  it('should render within 500ms', async () => {
    const start = performance.now()

    render(<QualityDashboard teamId="test-team" />)

    // Wait until one of the expected metric texts appears
    await screen.findByText(/Recommendation Quality Metrics/i)

    const end = performance.now()
    const renderTime = end - start

    expect(renderTime).toBeLessThan(500)
  }, 10000)

  it('should handle concurrent metric requests efficiently', async () => {
    const concurrentRequests = 5 // render instances concurrently

    const start = performance.now()

    await Promise.all(
      Array.from({ length: concurrentRequests }).map(async () => {
        render(<QualityDashboard teamId="test-team" />)
        await screen.findByText(/Recommendation Quality Metrics/i)
      })
    )

    const end = performance.now()
    const avgTimePerRequest = (end - start) / concurrentRequests

    expect(avgTimePerRequest).toBeLessThan(500)
    expect(recommendationsService.getQualityMetrics).toHaveBeenCalledTimes(
      concurrentRequests
    )
  }, 15000)

  it('should maintain performance with large datasets', async () => {
    const largeMetrics = {
      ...mockMetrics,
      totalRecommendations: 10000,
      feedbackReasons: Object.fromEntries(
        Array.from({ length: 100 }).map((_, i) => [
          `reason_${i}`,
          // deterministic value for test stability
          (i * 7) % 100,
        ])
      ),
    }
    ;(recommendationsService.getQualityMetrics as any).mockResolvedValue(
      largeMetrics
    )

    const start = performance.now()

    render(<QualityDashboard teamId="test-team" />)
    await screen.findByText(/Recommendation Quality Metrics/i)

    const end = performance.now()
    const renderTime = end - start

    expect(renderTime).toBeLessThan(500)
  }, 10000)
})
