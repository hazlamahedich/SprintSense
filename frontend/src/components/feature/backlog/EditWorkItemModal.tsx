import React from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '../../ui/dialog'
import { WorkItem, UpdateWorkItemRequest } from '../../../types/workItem.types'
import EditWorkItemForm from './EditWorkItemForm'

interface EditWorkItemModalProps {
  isOpen: boolean
  onClose: () => void
  workItem: WorkItem
  onSubmit: (data: UpdateWorkItemRequest) => Promise<void>
  isSubmitting?: boolean
  error?: string | null
  successMessage?: string | null
  isEditingIndicator?: {
    isEditing: boolean
    editingUser?: string
  }
}

export const EditWorkItemModal: React.FC<EditWorkItemModalProps> = ({
  isOpen,
  onClose,
  workItem,
  onSubmit,
  isSubmitting = false,
  error = null,
  successMessage = null,
  isEditingIndicator,
}) => {
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'story':
        return '📚'
      case 'bug':
        return '🐛'
      case 'task':
        return '✅'
      default:
        return '📚'
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent
        className="sm:max-w-3xl max-h-[90vh] overflow-y-auto"
        aria-describedby="edit-work-item-description"
      >
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl font-semibold text-gray-900">
            <span>{getTypeIcon(workItem.type)}</span>
            <span>Edit Work Item</span>
          </DialogTitle>
          <DialogDescription
            id="edit-work-item-description"
            className="text-gray-600"
          >
            Make changes to your work item. All fields are optional except
            title. Changes will be saved immediately and synchronized with your
            team.
          </DialogDescription>
        </DialogHeader>

        <div className="mt-6">
          <EditWorkItemForm
            workItem={workItem}
            onSubmit={onSubmit}
            onCancel={onClose}
            isSubmitting={isSubmitting}
            error={error}
            successMessage={successMessage}
            isEditingIndicator={isEditingIndicator}
          />
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default EditWorkItemModal
