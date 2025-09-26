import React from 'react'
import { Box, Typography, Grid, IconButton } from '@mui/material'
import { Add as AddIcon } from '@mui/icons-material'
import { SprintStatus } from '@/types/sprint'
import { SprintCard } from './SprintCard'
import { useSprintStore } from '@/stores/sprintStore'

interface SprintListProps {
  onCreateClick: () => void
}

export const SprintList: React.FC<SprintListProps> = ({ onCreateClick }) => {
  const { sprints, activeSprintId, updateSprintStatus } = useSprintStore()

  const handleStartSprint = async (sprintId: string) => {
    await updateSprintStatus(sprintId, SprintStatus.ACTIVE)
  }

  const handleCloseSprint = async (sprintId: string) => {
    await updateSprintStatus(sprintId, SprintStatus.CLOSED)
  }

  const renderSprintSection = (status: SprintStatus, title: string) => {
    const filteredSprints = sprints.filter((sprint) => sprint.status === status)

    if (filteredSprints.length === 0) {
      return null
    }

    return (
      <Box sx={{ mt: 4 }}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 2,
          }}
        >
          <Typography variant="h6">{title}</Typography>
          {status === SprintStatus.FUTURE && (
            <IconButton
              onClick={onCreateClick}
              color="primary"
              aria-label="Add Sprint"
            >
              <AddIcon />
            </IconButton>
          )}
        </Box>
        <Grid container spacing={3}>
          {filteredSprints.map((sprint) => (
            <Grid item xs={12} sm={6} md={4} key={sprint.id}>
              <SprintCard
                sprint={sprint}
                isStartDisabled={
                  !!activeSprintId && sprint.status === SprintStatus.FUTURE
                }
                onStartSprint={() => handleStartSprint(sprint.id)}
                onCloseSprint={() => handleCloseSprint(sprint.id)}
              />
            </Grid>
          ))}
        </Grid>
      </Box>
    )
  }

  return (
    <Box>
      {renderSprintSection(SprintStatus.ACTIVE, 'Active Sprint')}
      {renderSprintSection(SprintStatus.FUTURE, 'Future Sprints')}
      {renderSprintSection(SprintStatus.CLOSED, 'Closed Sprints')}

      {sprints.length === 0 && (
        <Box
          sx={{
            textAlign: 'center',
            p: 4,
            backgroundColor: 'background.paper',
            borderRadius: 1,
            mt: 4,
          }}
        >
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No sprints found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Click the + button to create your first sprint
          </Typography>
        </Box>
      )}
    </Box>
  )
}
