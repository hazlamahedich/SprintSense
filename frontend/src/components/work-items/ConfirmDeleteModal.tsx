import React, { useEffect, useRef } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '../ui/dialog'
import { Button } from '../ui/button'
import { Alert, AlertDescription } from '../ui/alert'
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline'

interface ConfirmDeleteModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => Promise<void>
  workItemTitle: string
  isLoading?: boolean
}

/**
 * ConfirmDeleteModal component
 *
 * Provides an accessible confirmation dialog for archiving work items.
 * Includes proper focus management, keyboard navigation, and screen reader support.
 */
export const ConfirmDeleteModal: React.FC<ConfirmDeleteModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  workItemTitle,
  isLoading = false,
}) => {
  const cancelButtonRef = useRef<HTMLButtonElement>(null)
  const confirmButtonRef = useRef<HTMLButtonElement>(null)

  // Focus management - focus confirm button when modal opens
  useEffect(() => {
    if (isOpen && confirmButtonRef.current) {
      confirmButtonRef.current.focus()
    }
  }, [isOpen])

  const handleClose = () => {
    if (!isLoading) {
      onClose()
    }
  }

  const handleConfirm = async () => {
    if (!isLoading) {
      await onConfirm()
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Handle escape key
    if (e.key === 'Escape' && !isLoading) {
      onClose()
    }

    // Handle tab navigation between buttons
    if (e.key === 'Tab') {
      const currentElement = e.target as HTMLElement
      if (currentElement === cancelButtonRef.current && !e.shiftKey) {
        e.preventDefault()
        confirmButtonRef.current?.focus()
      } else if (currentElement === confirmButtonRef.current && e.shiftKey) {
        e.preventDefault()
        cancelButtonRef.current?.focus()
      }
    }
  }

  // Prevent closing modal when clicking inside the content
  const handleBackdropClick = (e: React.MouseEvent) => {
    e.stopPropagation()
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent
        className="max-w-md"
        onClick={handleBackdropClick}
        onKeyDown={handleKeyDown}
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirm-delete-title"
        aria-describedby="confirm-delete-description"
      >
        <DialogHeader className="text-center pb-4">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-100 mb-4">
            <ExclamationTriangleIcon
              className="h-6 w-6 text-red-600"
              aria-hidden="true"
            />
          </div>
          <DialogTitle
            id="confirm-delete-title"
            className="text-lg font-semibold text-gray-900"
          >
            Archive Work Item
          </DialogTitle>
        </DialogHeader>

        <div className="text-center pb-6">
          <Alert className="mb-4 bg-amber-50 border-amber-200">
            <AlertDescription id="confirm-delete-description">
              <p className="text-sm text-gray-700 mb-2">
                Are you sure you want to archive{' '}
                <strong className="font-semibold">"{workItemTitle}"</strong>?
              </p>
              <p className="text-xs text-gray-600">
                This work item will be moved to the archived state and hidden
                from regular views. This action can be undone by updating the
                work item's status.
              </p>
            </AlertDescription>
          </Alert>
        </div>

        <DialogFooter className="flex justify-center gap-3">
          <Button
            ref={cancelButtonRef}
            variant="outline"
            onClick={handleClose}
            disabled={isLoading}
            className="min-w-24"
          >
            Cancel
          </Button>
          <Button
            ref={confirmButtonRef}
            variant="destructive"
            onClick={handleConfirm}
            disabled={isLoading}
            className="min-w-24"
            aria-describedby="confirm-delete-description"
          >
            {isLoading ? 'Archiving...' : 'Archive'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default ConfirmDeleteModal
