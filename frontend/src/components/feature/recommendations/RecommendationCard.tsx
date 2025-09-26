import React, { useState } from 'react'
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Box,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
} from '@mui/material'
import { WorkItemRecommendation } from '../../../types/recommendations.types'
import { ConfidenceIndicator } from './ConfidenceIndicator'

interface RecommendationCardProps {
  recommendation: WorkItemRecommendation
  onAccept: () => void
  onModify: () => void
  onNotUseful: (reason: string) => void
}

const notUsefulReasons = [
  'irrelevant_to_current_goals',
  'incorrect_priority',
  'unclear_description',
  'duplicate_work',
  'other',
]

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  recommendation,
  onAccept,
  onModify,
  onNotUseful,
}) => {
  const [feedbackDialogOpen, setFeedbackDialogOpen] = useState(false)
  const [feedbackReason, setFeedbackReason] = useState('')
  const [customReason, setCustomReason] = useState('')

  const handleNotUseful = () => {
    if (feedbackReason === 'other' && customReason) {
      onNotUseful(customReason)
    } else {
      onNotUseful(feedbackReason)
    }
    setFeedbackDialogOpen(false)
    setFeedbackReason('')
    setCustomReason('')
  }

  return (
    <>
      <Card sx={{ mb: 2, position: 'relative' }}>
        <CardContent>
          <Box
            display="flex"
            alignItems="center"
            justifyContent="space-between"
            mb={1}
          >
            <Typography variant="h6">{recommendation.title}</Typography>
            <ConfidenceIndicator
              scores={recommendation.confidence_scores}
              overallConfidence={
                Object.values(recommendation.confidence_scores).reduce(
                  (a, b) => a + b,
                  0
                ) / Object.keys(recommendation.confidence_scores).length
              }
            />
          </Box>

          <Typography color="textSecondary" gutterBottom>
            Type: {recommendation.type}
          </Typography>

          <Typography variant="body2" paragraph>
            {recommendation.description}
          </Typography>

          <Box display="flex" gap={1} mb={2}>
            <Chip
              label={`Priority: ${recommendation.suggested_priority.toFixed(2)}`}
              color="primary"
              variant="outlined"
              size="small"
            />
            <Chip
              label={`Team Velocity Impact: ${(recommendation.team_velocity_factor * 100).toFixed(0)}%`}
              color="secondary"
              variant="outlined"
              size="small"
            />
          </Box>

          <Typography variant="subtitle2" gutterBottom>
            Reasoning:
          </Typography>
          <Typography variant="body2" color="textSecondary">
            {recommendation.reasoning}
          </Typography>

          <Box mt={2}>
            <Typography variant="subtitle2" gutterBottom>
              Patterns Identified:
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              {recommendation.patterns_identified.map((pattern, index) => (
                <Chip
                  key={index}
                  label={pattern}
                  size="small"
                  variant="outlined"
                />
              ))}
            </Box>
          </Box>
        </CardContent>

        <CardActions>
          <Button color="primary" variant="contained" onClick={onAccept}>
            Accept
          </Button>
          <Button color="secondary" variant="outlined" onClick={onModify}>
            Modify
          </Button>
          <Button
            color="error"
            variant="outlined"
            onClick={() => setFeedbackDialogOpen(true)}
          >
            Not Useful
          </Button>
        </CardActions>
      </Card>

      <Dialog
        open={feedbackDialogOpen}
        onClose={() => setFeedbackDialogOpen(false)}
      >
        <DialogTitle>Why is this recommendation not useful?</DialogTitle>
        <DialogContent>
          <TextField
            select
            fullWidth
            value={feedbackReason}
            onChange={(e) => setFeedbackReason(e.target.value)}
            margin="normal"
          >
            {notUsefulReasons.map((reason) => (
              <MenuItem key={reason} value={reason}>
                {reason
                  .replace(/_/g, ' ')
                  .replace(/\b\w/g, (l) => l.toUpperCase())}
              </MenuItem>
            ))}
          </TextField>
          {feedbackReason === 'other' && (
            <TextField
              fullWidth
              multiline
              rows={3}
              value={customReason}
              onChange={(e) => setCustomReason(e.target.value)}
              margin="normal"
              placeholder="Please provide more details..."
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFeedbackDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleNotUseful}
            disabled={
              !feedbackReason || (feedbackReason === 'other' && !customReason)
            }
            color="primary"
          >
            Submit
          </Button>
        </DialogActions>
      </Dialog>
    </>
  )
}
