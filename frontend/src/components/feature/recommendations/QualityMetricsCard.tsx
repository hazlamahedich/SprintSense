import React from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Stack,
  LinearProgress,
  Divider,
} from '@mui/material'
import { useQualityMetrics } from '../../../hooks/useQualityMetrics'

interface QualityMetricsCardProps {
  teamId: string
}

export const QualityMetricsCard: React.FC<QualityMetricsCardProps> = ({
  teamId,
}) => {
  const { metrics, isLoading, error } = useQualityMetrics(teamId)

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error.message || 'Failed to load metrics'}
      </Alert>
    )
  }

  if (!metrics) {
    return (
      <Alert severity="info">
        No metrics available yet. Start using recommendations to see insights
        here.
      </Alert>
    )
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Recommendation Metrics
        </Typography>

        <Stack spacing={2}>
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Acceptance Rate
            </Typography>
            <LinearProgress
              variant="determinate"
              value={metrics.acceptanceRate * 100}
              sx={{ mb: 1, height: 8, borderRadius: 1 }}
            />
            <Typography variant="caption" color="text.secondary">
              {(metrics.acceptanceRate * 100).toFixed(1)}% recommendations
              accepted
            </Typography>
          </Box>

          <Divider />

          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Average Confidence
            </Typography>
            <LinearProgress
              variant="determinate"
              value={metrics.avgConfidence * 100}
              sx={{ mb: 1, height: 8, borderRadius: 1 }}
            />
            <Typography variant="caption" color="text.secondary">
              {(metrics.avgConfidence * 100).toFixed(1)}% confidence average
            </Typography>
          </Box>

          <Divider />

          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Feedback Distribution
            </Typography>
            {Object.entries(metrics.feedbackReasons).map(([reason, count]) => (
              <Box
                key={reason}
                display="flex"
                alignItems="center"
                justifyContent="space-between"
                mb={1}
              >
                <Typography variant="body2">
                  {reason
                    .replace(/_/g, ' ')
                    .replace(/\\b\\w/g, (l) => l.toUpperCase())}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {count} reports
                </Typography>
              </Box>
            ))}
          </Box>

          <Divider />

          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Performance
            </Typography>
            <Box display="flex" justifyContent="space-between" mb={1}>
              <Typography variant="body2">UI Response Time</Typography>
              <Typography
                variant="body2"
                color={
                  metrics.uiResponseTime < 500 ? 'success.main' : 'warning.main'
                }
              >
                {metrics.uiResponseTime.toFixed(0)}ms
              </Typography>
            </Box>
            <Box display="flex" justifyContent="space-between">
              <Typography variant="body2">
                Backend Response Time (95th)
              </Typography>
              <Typography
                variant="body2"
                color={
                  metrics.backendResponseTime95th < 200
                    ? 'success.main'
                    : 'warning.main'
                }
              >
                {metrics.backendResponseTime95th.toFixed(0)}ms
              </Typography>
            </Box>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  )
}
