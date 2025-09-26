import React from 'react'
import { Box, Typography, CircularProgress } from '@mui/material'
import { useWorkItemRecommendations } from '../../../hooks/useWorkItemRecommendations'
import { RecommendationCard } from './RecommendationCard'

interface RecommendationsPanelProps {
  teamId: string
  minConfidence?: number
  limit?: number
}

export const RecommendationsPanel: React.FC<RecommendationsPanelProps> = ({
  teamId,
  minConfidence = 0.7,
  limit = 5,
}) => {
  const {
    recommendations,
    isLoading,
    error,
    acceptRecommendation,
    modifyRecommendation,
    provideRecommendationFeedback,
  } = useWorkItemRecommendations(teamId, { minConfidence, limit })

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Box sx={{ p: 2, color: 'error.main' }}>
        <Typography variant="body1">
          {error.message || 'Failed to load recommendations'}
        </Typography>
      </Box>
    )
  }

  if (!recommendations?.length) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="body1" color="textSecondary">
          No recommendations available at this time
        </Typography>
      </Box>
    )
  }

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Recommended Work Items
      </Typography>
      {recommendations.map((recommendation) => (
        <RecommendationCard
          key={recommendation.id}
          recommendation={recommendation}
          onAccept={() => acceptRecommendation(recommendation.id)}
          onModify={() => modifyRecommendation(recommendation.id)}
          onNotUseful={(reason) =>
            provideRecommendationFeedback(
              recommendation.id,
              'not_useful',
              reason
            )
          }
        />
      ))}
    </Box>
  )
}

