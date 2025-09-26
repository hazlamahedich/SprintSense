import React from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Grid,
  Alert,
} from '@mui/material'
import { useQualityMetrics } from '../../../hooks/useQualityMetrics'

interface QualityDashboardProps {
  teamId: string
}

export const QualityDashboard: React.FC<QualityDashboardProps> = ({
  teamId,
}) => {
  const { metrics, isLoading, error } = useQualityMetrics(teamId)

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={2}>
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Failed to load quality metrics: {error.message}
      </Alert>
    )
  }

  if (!metrics) {
    return (
      <Alert severity="info" sx={{ m: 2 }}>
        No quality metrics available yet.
      </Alert>
    )
  }

  return (
    <Card sx={{ m: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Recommendation Quality Metrics
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Acceptance Rate
                </Typography>
                <Typography variant="h4">
                  {(metrics.acceptanceRate * 100).toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Last 7 days: {metrics.recentAcceptanceCount} accepted
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Average Confidence
                </Typography>
                <Typography variant="h4">
                  {(metrics.avgConfidence * 100).toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Based on {metrics.totalRecommendations} recommendations
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Top Feedback Reason
                </Typography>
                <Typography variant="h6">
                  {metrics.topFeedbackReason || 'N/A'}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {metrics.feedbackCount} total feedback items
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  )
}
