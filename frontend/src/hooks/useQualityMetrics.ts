import { useState, useEffect } from 'react'
import { QualityMetrics } from '../types/quality-metrics.types'
import { recommendationsService } from '../services/recommendationsService'

export function useQualityMetrics(teamId: string) {
  const [metrics, setMetrics] = useState<QualityMetrics | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data = await recommendationsService.getQualityMetrics(teamId)
        setMetrics(data)
      } catch (err) {
        setError(
          err instanceof Error
            ? err
            : new Error('Failed to fetch quality metrics')
        )
      } finally {
        setIsLoading(false)
      }
    }

    fetchMetrics()

    // Refresh metrics every 5 minutes (skip in test to avoid infinite fake timers)
    let interval: number | undefined
    if (process.env.NODE_ENV !== 'test') {
      interval = window.setInterval(fetchMetrics, 5 * 60 * 1000)
    }
    return () => {
      if (interval) window.clearInterval(interval)
    }
  }, [teamId])

  return { metrics, isLoading, error }
}
