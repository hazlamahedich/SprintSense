import React from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Divider,
} from '@mui/material'
import { SprintStatus, Sprint } from '@/types/sprint'
import { SprintStatusButton } from './SprintStatusButton'

// Helper function to format date nicely
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

interface SprintCardProps {
  sprint: Sprint
  isStartDisabled: boolean
  onStartSprint: () => void
  onCloseSprint: () => void
}

import { IncompleteWorkDialog } from './IncompleteWorkDialog'
import { completeSprint, getIncompleteItems } from '@/api/sprint'
import { CompleteSprintRequest } from '@/types/sprint'

export const SprintCard: React.FC<SprintCardProps> = ({
  sprint,
  isStartDisabled,
  onStartSprint,
  onCloseSprint,
}) => {
  const [dialogOpen, setDialogOpen] = React.useState(false)

  const handleCloseClick = async () => {
    // Before closing, check if there are incomplete items
    // Open dialog to handle move choice
    setDialogOpen(true)
  }

  const handleDialogCompleted = async () => {
    setDialogOpen(false)
    // After items are handled, proceed to set sprint to CLOSED
    await onCloseSprint()
  }

  return (
    <Card
      sx={{
        position: 'relative',
        overflow: 'visible',
        transition: 'transform 0.2s',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: (theme) => theme.shadows[4],
        },
      }}
    >
      <Box sx={{ position: 'absolute', top: 16, right: 16 }}>
        <SprintStatusButton
          disabled={isStartDisabled}
          currentStatus={sprint.status}
          onStart={onStartSprint}
          onClose={handleCloseClick}
        />
      </Box>

      <CardContent>
        <Box mb={3}>
          <Typography variant="h5" gutterBottom>
            {sprint.name}
          </Typography>

          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <Chip
              label={
                sprint.status.charAt(0).toUpperCase() + sprint.status.slice(1)
              }
              color={
                sprint.status === SprintStatus.ACTIVE
                  ? 'success'
                  : sprint.status === SprintStatus.FUTURE
                    ? 'primary'
                    : 'default'
              }
              size="small"
            />
          </Box>

          {sprint.goal && (
            <Typography color="text.secondary" variant="body2" mb={2}>
              {sprint.goal}
            </Typography>
          )}
        </Box>

        <Divider sx={{ my: 2 }} />

        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography
              variant="overline"
              display="block"
              color="text.secondary"
            >
              Start Date
            </Typography>
            <Typography variant="body2">
              {formatDate(sprint.startDate)}
            </Typography>
          </Box>
          <Box>
            <Typography
              variant="overline"
              display="block"
              color="text.secondary"
            >
              End Date
            </Typography>
            <Typography variant="body2">
              {formatDate(sprint.endDate)}
            </Typography>
          </Box>
        </Box>
      </CardContent>

      <IncompleteWorkDialog
        open={dialogOpen}
        sprintId={sprint.id}
        onClose={() => setDialogOpen(false)}
        onCompleted={() => handleDialogCompleted()}
      />
    </Card>
  )
}

