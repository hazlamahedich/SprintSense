import React, { useState, useCallback } from 'react'
import { CreateWorkItemButton } from './CreateWorkItemButton'
import { CreateWorkItemModal } from './CreateWorkItemModal'
import { useCreateWorkItem } from '../../../hooks/useCreateWorkItem'
import { CreateWorkItemRequest, WorkItem } from '../../../types/workItem.types'

interface CreateWorkItemDemoProps {
  teamId: string
  onWorkItemCreated?: (workItem: WorkItem) => void
  showFloatingButton?: boolean
  showHeaderButton?: boolean
}

/**
 * Complete demo component showing how to integrate work item creation
 * This component demonstrates the full workflow from button click to successful creation
 */
export const CreateWorkItemDemo: React.FC<CreateWorkItemDemoProps> = ({
  teamId,
  onWorkItemCreated,
  showFloatingButton = true,
  showHeaderButton = true,
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const {
    createWorkItem,
    isSubmitting,
    error,
    successMessage,
    clearMessages,
    reset,
  } = useCreateWorkItem()

  const handleOpenModal = useCallback(() => {
    // Clear any previous messages when opening modal
    clearMessages()
    setIsModalOpen(true)
  }, [clearMessages])

  const handleCloseModal = useCallback(() => {
    setIsModalOpen(false)
    // Reset the hook state when closing modal
    setTimeout(() => reset(), 300) // Delay to avoid flash during modal closing animation
  }, [reset])

  const handleSubmit = useCallback(
    async (data: CreateWorkItemRequest) => {
      try {
        const workItem = await createWorkItem(teamId, data)

        // Notify parent component about successful creation
        if (onWorkItemCreated) {
          onWorkItemCreated(workItem)
        }

        // Close modal after successful creation (with delay to show success message)
        setTimeout(() => {
          handleCloseModal()
        }, 2000)
      } catch (error) {
        // Error is handled by the hook, no need to do anything here
        console.error('Work item creation failed:', error)
      }
    },
    [createWorkItem, teamId, onWorkItemCreated, handleCloseModal]
  )

  return (
    <div className="create-work-item-demo">
      {/* Header Button */}
      {showHeaderButton && (
        <div className="flex justify-end mb-4">
          <CreateWorkItemButton
            onClick={handleOpenModal}
            variant="header"
            disabled={isSubmitting}
          />
        </div>
      )}

      {/* Floating Action Button */}
      {showFloatingButton && (
        <CreateWorkItemButton
          onClick={handleOpenModal}
          variant="floating"
          disabled={isSubmitting}
        />
      )}

      {/* Modal */}
      <CreateWorkItemModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSubmit={handleSubmit}
        isSubmitting={isSubmitting}
        error={error}
        successMessage={successMessage}
      />
    </div>
  )
}

export default CreateWorkItemDemo
