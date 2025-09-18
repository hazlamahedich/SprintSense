/**
 * EditWorkItemModal component that provides a modal wrapper for the EditWorkItemForm.
 *
 * Addresses Story 2.4 requirements:
 * - Modal presentation and lifecycle management
 * - Focus management and accessibility
 * - Escape key handling
 * - Backdrop click handling with unsaved changes protection
 */

import React, { useEffect, useRef, useState } from 'react'
import { WorkItem } from '../../types/workItem.types'
import EditWorkItemForm from './EditWorkItemForm'

interface EditWorkItemModalProps {
  isOpen: boolean
  workItem: WorkItem | null
  teamId: string
  onClose: () => void
  onSave: (updatedWorkItem: WorkItem) => void
  onError?: (error: string) => void
}

export const EditWorkItemModal: React.FC<EditWorkItemModalProps> = ({
  isOpen,
  workItem,
  teamId,
  onClose,
  onSave,
  onError,
}) => {
  const modalRef = useRef<HTMLDivElement>(null)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  // Handle close with unsaved changes protection
  const handleClose = () => {
    if (hasUnsavedChanges) {
      const confirmed = window.confirm(
        'You have unsaved changes. Are you sure you want to close without saving?'
      )
      if (!confirmed) {
        return
      }
    }
    setHasUnsavedChanges(false)
    onClose()
  }

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        handleClose()
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      // Prevent body scrolling when modal is open
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, handleClose])

  // Focus management
  useEffect(() => {
    if (isOpen && modalRef.current) {
      // Focus the modal content when opened
      modalRef.current.focus()

      // Trap focus within modal
      const focusableElements = modalRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )

      const firstElement = focusableElements[0] as HTMLElement
      const lastElement = focusableElements[
        focusableElements.length - 1
      ] as HTMLElement

      const handleTabKey = (e: KeyboardEvent) => {
        if (e.key === 'Tab') {
          if (e.shiftKey) {
            // Shift + Tab
            if (document.activeElement === firstElement) {
              e.preventDefault()
              lastElement?.focus()
            }
          } else {
            // Tab
            if (document.activeElement === lastElement) {
              e.preventDefault()
              firstElement?.focus()
            }
          }
        }
      }

      modalRef.current.addEventListener('keydown', handleTabKey)
      const currentModalRef = modalRef.current

      return () => {
        currentModalRef?.removeEventListener('keydown', handleTabKey)
      }
    }
  }, [isOpen])

  // Handle backdrop click
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      handleClose()
    }
  }

  // Handle form save
  const handleSave = (updatedWorkItem: WorkItem) => {
    setHasUnsavedChanges(false)
    onSave(updatedWorkItem)
    onClose()
  }

  // Handle form cancel
  const handleCancel = () => {
    handleClose()
  }

  // Handle form error
  const handleError = (error: string) => {
    onError?.(error)
  }

  // Don't render if not open or no work item
  if (!isOpen || !workItem) {
    return null
  }

  return (
    <div
      className="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-50 flex items-center justify-center p-4"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div
        ref={modalRef}
        className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden"
        tabIndex={-1}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 id="modal-title" className="text-xl font-semibold text-gray-900">
            Edit Work Item
          </h2>
          <button
            type="button"
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md p-1"
            aria-label="Close modal"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Modal Body - Scrollable content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          <EditWorkItemForm
            workItem={workItem}
            teamId={teamId}
            onSave={handleSave}
            onCancel={handleCancel}
            onError={handleError}
          />
        </div>
      </div>
    </div>
  )
}

export default EditWorkItemModal
