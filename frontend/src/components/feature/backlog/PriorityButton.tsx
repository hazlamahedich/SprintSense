/**
 * PriorityButton component for individual priority action buttons.
 * Implements Story 2.6 requirements for accessible priority controls.
 */

import React from 'react'
import {
  IconButton,
  Tooltip,
  CircularProgress,
  useTheme,
  alpha,
} from '@mui/material'
import {
  KeyboardArrowUp,
  KeyboardArrowDown,
  KeyboardDoubleArrowUp,
  KeyboardDoubleArrowDown,
} from '@mui/icons-material'
import { PriorityAction } from '../../../types/workItem.types'

interface PriorityButtonProps {
  action: PriorityAction
  disabled?: boolean
  loading?: boolean
  onClick: () => void
  'aria-label': string
  workItemTitle?: string
  currentPosition?: number
  totalItems?: number
}

const getButtonIcon = (action: PriorityAction) => {
  switch (action) {
    case PriorityAction.MOVE_TO_TOP:
      return <KeyboardDoubleArrowUp />
    case PriorityAction.MOVE_UP:
      return <KeyboardArrowUp />
    case PriorityAction.MOVE_DOWN:
      return <KeyboardArrowDown />
    case PriorityAction.MOVE_TO_BOTTOM:
      return <KeyboardDoubleArrowDown />
    default:
      return <KeyboardArrowUp />
  }
}

const getTooltipText = (
  action: PriorityAction,
  workItemTitle?: string,
  currentPosition?: number,
  totalItems?: number
) => {
  const itemName = workItemTitle ? `"${workItemTitle}"` : 'work item'

  switch (action) {
    case PriorityAction.MOVE_TO_TOP:
      return `Move ${itemName} to top of backlog`
    case PriorityAction.MOVE_UP:
      return currentPosition === 1
        ? `${itemName} is already at the top`
        : `Move ${itemName} up one position`
    case PriorityAction.MOVE_DOWN:
      return currentPosition === totalItems
        ? `${itemName} is already at the bottom`
        : `Move ${itemName} down one position`
    case PriorityAction.MOVE_TO_BOTTOM:
      return `Move ${itemName} to bottom of backlog`
    default:
      return `Move ${itemName}`
  }
}

export const PriorityButton: React.FC<PriorityButtonProps> = ({
  action,
  disabled = false,
  loading = false,
  onClick,
  'aria-label': ariaLabel,
  workItemTitle,
  currentPosition,
  totalItems,
}) => {
  const theme = useTheme()

  const handleClick = () => {
    if (!disabled && !loading) {
      onClick()
    }
  }

  const handleKeyDown = (event: React.KeyboardEvent) => {
    // Support Enter and Space key activation
    if ((event.key === 'Enter' || event.key === ' ') && !disabled && !loading) {
      event.preventDefault()
      onClick()
    }
  }

  const tooltipText = getTooltipText(
    action,
    workItemTitle,
    currentPosition,
    totalItems
  )

  return (
    <Tooltip title={tooltipText} arrow>
      <span>
        <IconButton
          onClick={handleClick}
          onKeyDown={handleKeyDown}
          disabled={disabled || loading}
          aria-label={ariaLabel}
          aria-describedby={
            workItemTitle ? `priority-${action}-${workItemTitle}` : undefined
          }
          size="small"
          sx={{
            color: theme.palette.primary.main,
            '&:hover': {
              backgroundColor: alpha(theme.palette.primary.main, 0.04),
              color: theme.palette.primary.dark,
              transform: 'translateY(-1px)',
            },
            '&:focus': {
              outline: `2px solid ${theme.palette.primary.main}`,
              outlineOffset: 2,
            },
            '&:disabled': {
              color: theme.palette.action.disabled,
            },
            transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
            minWidth: 40,
            minHeight: 40,
          }}
        >
          {loading ? (
            <CircularProgress size={16} color="inherit" />
          ) : (
            getButtonIcon(action)
          )}
        </IconButton>
      </span>
    </Tooltip>
  )
}

export default PriorityButton
