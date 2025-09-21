import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import {
  Container,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Box,
  Alert,
  AlertTitle,
} from '@mui/material'
import { DatePicker } from '@mui/x-date-pickers'
import { SprintCreate } from '@/types/sprint'
import { SprintList } from '@/components/sprints/SprintList'
import { useSprintStore } from '@/stores/sprintStore'

export const SprintManagementView: React.FC = () => {
  const { teamId } = useParams<{ teamId: string }>()
  const { fetchTeamSprints, createSprint, error, clearError } = useSprintStore()

  // Dialog state
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [createData, setCreateData] = useState<Partial<SprintCreate>>({
    name: '',
    goal: '',
  })

  useEffect(() => {
    if (teamId) {
      fetchTeamSprints(teamId)
    }
  }, [teamId, fetchTeamSprints])

  const handleCreateClick = () => {
    setIsCreateOpen(true)
  }

  const handleClose = () => {
    setIsCreateOpen(false)
    setCreateData({
      name: '',
      goal: '',
    })
  }

  const handleSubmit = async () => {
    if (
      !createData.name ||
      !createData.startDate ||
      !createData.endDate ||
      !teamId
    ) {
      return // Form validation is handled by Material-UI
    }

    try {
      await createSprint(teamId, createData as SprintCreate)
      handleClose()
      fetchTeamSprints(teamId) // Refresh list after creation
    } catch (error) {
      console.error('Failed to create sprint:', error)
    }
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          Sprint Management
        </Typography>

        {error && (
          <Alert severity="error" onClose={clearError} sx={{ mb: 3 }}>
            <AlertTitle>Error</AlertTitle>
            {error}
          </Alert>
        )}

        {teamId && (
          <SprintList teamId={teamId} onCreateClick={handleCreateClick} />
        )}
      </Box>

      <Dialog open={isCreateOpen} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Sprint</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 3 }}>
            <TextField
              label="Sprint Name"
              required
              fullWidth
              value={createData.name}
              onChange={(e) =>
                setCreateData((prev) => ({ ...prev, name: e.target.value }))
              }
            />

            <TextField
              label="Sprint Goal"
              fullWidth
              multiline
              rows={3}
              value={createData.goal}
              onChange={(e) =>
                setCreateData((prev) => ({ ...prev, goal: e.target.value }))
              }
            />

            <DatePicker
              label="Start Date"
              value={
                createData.startDate ? new Date(createData.startDate) : null
              }
              onChange={(date) =>
                setCreateData((prev) => ({
                  ...prev,
                  startDate: date?.toISOString().split('T')[0] || '',
                }))
              }
              slotProps={{
                textField: { required: true, fullWidth: true },
              }}
            />

            <DatePicker
              label="End Date"
              value={createData.endDate ? new Date(createData.endDate) : null}
              onChange={(date) =>
                setCreateData((prev) => ({
                  ...prev,
                  endDate: date?.toISOString().split('T')[0] || '',
                }))
              }
              minDate={
                createData.startDate
                  ? new Date(createData.startDate)
                  : undefined
              }
              slotProps={{
                textField: { required: true, fullWidth: true },
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={
              !createData.name || !createData.startDate || !createData.endDate
            }
          >
            Create Sprint
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}
