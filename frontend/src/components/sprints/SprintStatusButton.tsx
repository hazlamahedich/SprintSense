import React, { useMemo } from 'react'
import { Button } from '@mui/material'
import { SprintStatus } from '@/types/sprint'

interface SprintStatusButtonProps {
  disabled: boolean
  currentStatus: SprintStatus
  onStart: () => void
  onClose: () => void
}

export const SprintStatusButton: React.FC<SprintStatusButtonProps> = ({
  disabled,
  currentStatus,
  onStart,
  onClose,
}) => {
  const { label, action, isDisabled } = useMemo(() => {
    if (currentStatus === SprintStatus.FUTURE) {
      return { label: 'Start Sprint', action: onStart, isDisabled: disabled }
    }
    if (currentStatus === SprintStatus.ACTIVE) {
      return { label: 'Close Sprint', action: onClose, isDisabled: false }
    }
    return { label: 'Closed', action: () => {}, isDisabled: true }
  }, [currentStatus, disabled, onStart, onClose])

  return (
    <Button variant="contained" disabled={isDisabled} onClick={action}>
      {label}
    </Button>
  )
}
