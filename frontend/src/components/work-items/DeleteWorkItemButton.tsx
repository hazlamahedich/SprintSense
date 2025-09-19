import React, { useState } from 'react'
import { Button } from '../ui/button'
import { TrashIcon } from '@heroicons/react/24/outline'
import { ConfirmDeleteModal } from './ConfirmDeleteModal'

interface DeleteWorkItemButtonProps {
  workItemId: string
  workItemTitle: string
  teamId: string
  onArchive: (workItemId: string) => Promise<void>
  disabled?: boolean
  className?: string
  size?: 'default' | 'sm' | 'lg' | 'icon'
}

/**
 * DeleteWorkItemButton component
 *
 * Provides an accessible delete button that opens a confirmation modal
 * before archiving (soft-deleting) a work item.
 */
export const DeleteWorkItemButton: React.FC<DeleteWorkItemButtonProps> = ({
  workItemId,
  workItemTitle,
  teamId: _teamId,
  onArchive,
  disabled = false,
  className = '',
  size = 'sm',
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleButtonClick = () => {
    setIsModalOpen(true)
  }

  const handleModalClose = () => {
    if (!isLoading) {
      setIsModalOpen(false)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      setIsLoading(true)
      await onArchive(workItemId)
      setIsModalOpen(false)
    } catch (error) {
      // Error handling is managed by the parent component through the onArchive callback
      console.error('Failed to archive work item:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <>
      <Button
        variant="ghost"
        size={size}
        onClick={handleButtonClick}
        disabled={disabled}
        className={`text-red-600 hover:text-red-800 hover:bg-red-50 ${className}`}
        title="Delete work item"
        aria-label={`Delete work item: ${workItemTitle}`}
      >
        <TrashIcon className="w-4 h-4" />
      </Button>

      <ConfirmDeleteModal
        isOpen={isModalOpen}
        onClose={handleModalClose}
        onConfirm={handleConfirmDelete}
        workItemTitle={workItemTitle}
        isLoading={isLoading}
      />
    </>
  )
}

export default DeleteWorkItemButton
