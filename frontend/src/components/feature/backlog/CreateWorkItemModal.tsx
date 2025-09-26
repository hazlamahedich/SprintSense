import React from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '../../ui/dialog'
import { CreateWorkItemForm } from './CreateWorkItemForm'
import { CreateWorkItemRequest } from '../../../types/workItem.types'
import { X } from 'lucide-react'
import { Button } from '../../ui/button'

interface CreateWorkItemModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: CreateWorkItemRequest) => Promise<void>
  isSubmitting?: boolean
  error?: string | null
  successMessage?: string | null
}

export const CreateWorkItemModal: React.FC<CreateWorkItemModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  isSubmitting = false,
  error = null,
  successMessage = null,
}) => {
  const handleClose = () => {
    if (!isSubmitting) {
      onClose()
    }
  }

  const handleBackdropClick = (e: React.MouseEvent) => {
    // Prevent closing when clicking inside the modal content
    e.stopPropagation()
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent
        className="max-w-4xl max-h-[95vh] overflow-hidden flex flex-col"
        onClick={handleBackdropClick}
      >
        <DialogHeader className="flex-shrink-0 border-b border-gray-200 pb-4">
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle className="text-xl font-semibold text-gray-900">
                Create New Work Item
              </DialogTitle>
              <p className="text-sm text-gray-600 mt-1">
                Add a new item to your team's backlog. It will be automatically
                prioritized and ready for planning.
              </p>
            </div>
            <Button
              onClick={handleClose}
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0 hover:bg-gray-100 rounded-full"
              disabled={isSubmitting}
              aria-label="Close modal"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto px-1 py-4">
          <CreateWorkItemForm
            onSubmit={onSubmit}
            onCancel={handleClose}
            isSubmitting={isSubmitting}
            error={error}
            successMessage={successMessage}
          />
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default CreateWorkItemModal
