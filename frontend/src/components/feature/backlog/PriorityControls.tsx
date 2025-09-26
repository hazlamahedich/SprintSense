/**
 * PriorityControls component for managing work item priority actions.
 * Implements Story 2.6 requirements for priority management with accessibility.
 */

import React, { useState, useCallback } from 'react'
import {
  Box,
  ButtonGroup,
  Alert,
  Snackbar,
  useTheme,
  alpha,
} from '@mui/material'
import PriorityButton from './PriorityButton'
import { usePriorityUpdate } from '../../../hooks/usePriorityUpdate'
import { PriorityAction, WorkItem } from '../../../types/workItem.types'

interface PriorityControlsProps {
  workItem: WorkItem
  teamId: string
  currentPosition?: number
  totalItems?: number
  onSuccess?: (updatedWorkItem: WorkItem) => void
  onError?: (error: string) => void
  onConflict?: (conflictMessage: string) => void
  disabled?: boolean
  compact?: boolean
}

interface SnackbarState {
  open: boolean
  message: string
  severity: 'success' | 'error' | 'warning'
}

export const PriorityControls: React.FC<PriorityControlsProps> = ({
  workItem,
  teamId,
  currentPosition = 1,
  totalItems = 1,
  onSuccess,
  onError,
  onConflict,
  disabled = false,
  compact = false,
}) => {
  const theme = useTheme()
  const [snackbar, setSnackbar] = useState<SnackbarState>({
    open: false,
    message: '',
    severity: 'success',
  })

  const { updatePriority, loading, error } = usePriorityUpdate({
    onSuccess: (updatedItem) => {
      setSnackbar({
        open: true,
        message: `Priority updated successfully for "${updatedItem.title}"`,
        severity: 'success',
      })
      onSuccess?.(updatedItem)
    },
    onError: (_error) => {
      setSnackbar({
        open: true,
        message: error?.message || 'Failed to update priority',
        severity: 'error',
      })
      onError?.(
        error instanceof Error ? error.message : 'Failed to update priority'
      )
    },
    onConflict: (conflictMessage) => {
      setSnackbar({
        open: true,
        message: conflictMessage,
        severity: 'warning',
      })
      onConflict?.(conflictMessage)
    },
  })

  const handlePriorityUpdate = useCallback(
    async (action: PriorityAction) => {
      if (disabled || loading) return

      await updatePriority({
        workItemId: workItem.id,
        teamId,
        action,
        currentPriority: workItem.priority,
      })
    },
    [workItem.id, workItem.priority, teamId, disabled, loading, updatePriority]
  )

  const handleSnackbarClose = () => {
    setSnackbar((prev) => ({ ...prev, open: false }))
  }

  // Determine which buttons should be disabled based on position
  const isAtTop = currentPosition === 1
  const isAtBottom = currentPosition === totalItems
  const isSingleItem = totalItems === 1

  const getAriaLabel = (action: PriorityAction) => {
    const position = `Position ${currentPosition} of ${totalItems}`
    switch (action) {
      case PriorityAction.MOVE_TO_TOP:
        return `Move "${workItem.title}" to top of backlog. ${position}`
      case PriorityAction.MOVE_UP:
        return `Move "${workItem.title}" up one position. ${position}`
      case PriorityAction.MOVE_DOWN:
        return `Move "${workItem.title}" down one position. ${position}`
      case PriorityAction.MOVE_TO_BOTTOM:
        return `Move "${workItem.title}" to bottom of backlog. ${position}`
      default:
        return `Move "${workItem.title}"`
    }
  }

  const buttonSpacing = compact ? 0.5 : 1

  return (
    <Box
      role="group"
      aria-label={`Priority controls for ${workItem.title}`}
      sx={{
        display: 'flex',
        alignItems: 'center',
      }}
    >
      <ButtonGroup
        variant="text"
        size="small"
        orientation={compact ? 'horizontal' : 'horizontal'}
        sx={{
          '& .MuiButtonGroup-grouped': {
            margin: theme.spacing(0, buttonSpacing / 2),
            borderRadius: 1,
            '&:not(:first-of-type)': {
              borderLeft: 'none',
            },
          },
          backgroundColor: alpha(theme.palette.background.paper, 0.8),
          borderRadius: 1,
          boxShadow: theme.shadows[1],
          padding: theme.spacing(0.25),
        }}
      >
        <PriorityButton
          action={PriorityAction.MOVE_TO_TOP}
          disabled={disabled || isAtTop || isSingleItem}
          loading={loading}
          onClick={() => handlePriorityUpdate(PriorityAction.MOVE_TO_TOP)}
          aria-label={getAriaLabel(PriorityAction.MOVE_TO_TOP)}
          workItemTitle={workItem.title}
          currentPosition={currentPosition}
          totalItems={totalItems}
        />

        <PriorityButton
          action={PriorityAction.MOVE_UP}
          disabled={disabled || isAtTop || isSingleItem}
          loading={loading}
          onClick={() => handlePriorityUpdate(PriorityAction.MOVE_UP)}
          aria-label={getAriaLabel(PriorityAction.MOVE_UP)}
          workItemTitle={workItem.title}
          currentPosition={currentPosition}
          totalItems={totalItems}
        />

        <PriorityButton
          action={PriorityAction.MOVE_DOWN}
          disabled={disabled || isAtBottom || isSingleItem}
          loading={loading}
          onClick={() => handlePriorityUpdate(PriorityAction.MOVE_DOWN)}
          aria-label={getAriaLabel(PriorityAction.MOVE_DOWN)}
          workItemTitle={workItem.title}
          currentPosition={currentPosition}
          totalItems={totalItems}
        />

        <PriorityButton
          action={PriorityAction.MOVE_TO_BOTTOM}
          disabled={disabled || isAtBottom || isSingleItem}
          loading={loading}
          onClick={() => handlePriorityUpdate(PriorityAction.MOVE_TO_BOTTOM)}
          aria-label={getAriaLabel(PriorityAction.MOVE_TO_BOTTOM)}
          workItemTitle={workItem.title}
          currentPosition={currentPosition}
          totalItems={totalItems}
        />
      </ButtonGroup>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default PriorityControls

