import React from 'react'
import { Box, Tooltip, CircularProgress, Typography } from '@mui/material'

interface ConfidenceIndicatorProps {
  scores: Record<string, number>
  overallConfidence: number
}

export const ConfidenceIndicator: React.FC<ConfidenceIndicatorProps> = ({
  scores,
  overallConfidence,
}) => {
  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'success.main'
    if (score >= 0.6) return 'warning.main'
    return 'error.main'
  }

  return (
    <Tooltip
      title={
        <Box>
          <Typography variant="subtitle2">Confidence Scores:</Typography>
          {Object.entries(scores).map(([field, score]) => (
            <Box
              key={field}
              display="flex"
              justifyContent="space-between"
              gap={2}
            >
              <Typography variant="body2">
                {field
                  .replace(/_/g, ' ')
                  .replace(/\b\w/g, (l) => l.toUpperCase())}
                :
              </Typography>
              <Typography variant="body2" color={getConfidenceColor(score)}>
                {(score * 100).toFixed(0)}%
              </Typography>
            </Box>
          ))}
        </Box>
      }
      arrow
    >
      <Box position="relative" display="inline-flex">
        <CircularProgress
          variant="determinate"
          value={overallConfidence * 100}
          size={40}
          thickness={4}
          sx={{ color: getConfidenceColor(overallConfidence) }}
        />
        <Box
          position="absolute"
          top={0}
          left={0}
          bottom={0}
          right={0}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <Typography variant="caption" component="div" color="text.secondary">
            {(overallConfidence * 100).toFixed(0)}%
          </Typography>
        </Box>
      </Box>
    </Tooltip>
  )
}
