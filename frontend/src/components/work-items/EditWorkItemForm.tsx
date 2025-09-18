/**
 * EditWorkItemForm component for editing existing work items.
 *
 * Addresses Story 2.4 requirements:
 * - AC1: Form pre-population with existing values
 * - AC2: Comprehensive field validation
 * - AC3: Real-time save functionality
 * - AC4: Optimistic UI updates with rollback
 * - AC5: Structured error handling and user feedback
 * - AC6: Team membership authorization
 */

import React, { useState, useEffect, useCallback } from 'react'
import {
  WorkItem,
  UpdateWorkItemRequest,
  WorkItemType,
  WorkItemStatus,
} from '../../types/workItem.types'
import { workItemService } from '../../services/workItemService'

// Validation errors interface
interface ValidationErrors {
  title?: string
  description?: string
  priority?: string
  story_points?: string
  general?: string
}

// Form state interface
interface FormState {
  title: string
  description: string
  type: WorkItemType
  status: WorkItemStatus
  priority: number
  story_points: number | ''
  assignee_id: string
}

interface EditWorkItemFormProps {
  workItem: WorkItem
  teamId: string
  onSave: (updatedWorkItem: WorkItem) => void
  onCancel: () => void
  onError?: (error: string) => void
}

export const EditWorkItemForm: React.FC<EditWorkItemFormProps> = ({
  workItem,
  teamId,
  onSave,
  onCancel,
  onError,
}) => {
  // Form state with pre-populated values (AC1)
  const [formState, setFormState] = useState<FormState>({
    title: workItem.title,
    description: workItem.description || '',
    type: workItem.type,
    status: workItem.status,
    priority: workItem.priority,
    story_points: workItem.story_points || '',
    assignee_id: workItem.assignee_id || '',
  })

  // Validation and UI state
  const [errors, setErrors] = useState<ValidationErrors>({})
  const [isSaving, setIsSaving] = useState(false)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [optimisticUpdate, setOptimisticUpdate] = useState<WorkItem | null>(
    null
  )

  // Track form changes for unsaved changes indicator
  useEffect(() => {
    const hasChanges =
      formState.title !== workItem.title ||
      formState.description !== (workItem.description || '') ||
      formState.type !== workItem.type ||
      formState.status !== workItem.status ||
      formState.priority !== workItem.priority ||
      formState.story_points !== (workItem.story_points || '') ||
      formState.assignee_id !== (workItem.assignee_id || '')

    setHasUnsavedChanges(hasChanges)
  }, [formState, workItem])

  // Comprehensive form validation (AC2)
  const validateForm = useCallback((): ValidationErrors => {
    const newErrors: ValidationErrors = {}

    // Title validation
    if (!formState.title.trim()) {
      newErrors.title = 'Title is required'
    } else if (formState.title.trim().length > 200) {
      newErrors.title = 'Title cannot exceed 200 characters'
    }

    // Description validation
    if (formState.description.trim().length > 2000) {
      newErrors.description = 'Description cannot exceed 2000 characters'
    }

    // Priority validation
    if (formState.priority < 0) {
      newErrors.priority = 'Priority cannot be negative'
    }

    // Story points validation
    if (formState.story_points !== '' && formState.story_points < 0) {
      newErrors.story_points = 'Story points cannot be negative'
    }

    return newErrors
  }, [formState, workItem])

  // Real-time validation for save button state and error display
  const currentValidationErrors = React.useMemo(() => {
    return validateForm()
  }, [validateForm])

  const hasValidationErrors = Object.keys(currentValidationErrors).length > 0

  // Update errors state when validation changes
  React.useEffect(() => {
    // Only show errors if form has been modified (to avoid showing errors on initial load)
    if (hasUnsavedChanges && hasValidationErrors) {
      setErrors(currentValidationErrors)
    } else if (!hasValidationErrors) {
      setErrors({})
    }
  }, [currentValidationErrors, hasValidationErrors, hasUnsavedChanges])

  // Input change handler with validation (AC2)
  const handleInputChange = useCallback(
    (
      field: keyof FormState,
      value: string | number | WorkItemType | WorkItemStatus
    ) => {
      setFormState((prev) => ({ ...prev, [field]: value }))

      // Clear field-specific errors when user starts typing
      if (errors[field as keyof ValidationErrors]) {
        setErrors((prev) => ({ ...prev, [field]: undefined }))
      }
    },
    [errors]
  )

  // Real-time save with optimistic updates (AC3, AC4)
  const handleSave = useCallback(async () => {
    const validationErrors = validateForm()

    // Always set validation errors to state for display
    setErrors(validationErrors)

    if (Object.keys(validationErrors).length > 0) {
      return
    }

    setIsSaving(true)
    setErrors({})

    // Prepare update request with only changed fields
    const updateRequest: UpdateWorkItemRequest = {}

    if (formState.title !== workItem.title) {
      updateRequest.title = formState.title.trim()
    }

    if (formState.description !== (workItem.description || '')) {
      updateRequest.description = formState.description.trim() || undefined
    }

    if (formState.type !== workItem.type) {
      updateRequest.type = formState.type
    }

    if (formState.status !== workItem.status) {
      updateRequest.status = formState.status
    }

    if (formState.priority !== workItem.priority) {
      updateRequest.priority = formState.priority
    }

    if (formState.story_points !== (workItem.story_points || '')) {
      updateRequest.story_points =
        formState.story_points === ''
          ? undefined
          : Number(formState.story_points)
    }

    if (formState.assignee_id !== (workItem.assignee_id || '')) {
      updateRequest.assignee_id = formState.assignee_id || undefined
    }

    // Skip API call if no changes
    if (Object.keys(updateRequest).length === 0) {
      setIsSaving(false)
      onSave(workItem)
      return
    }

    // Optimistic update (AC4)
    const optimisticWorkItem: WorkItem = {
      ...workItem,
      title: formState.title.trim(),
      description: formState.description.trim() || undefined,
      type: formState.type,
      status: formState.status,
      priority: formState.priority,
      story_points:
        formState.story_points === ''
          ? undefined
          : Number(formState.story_points),
      assignee_id: formState.assignee_id || undefined,
      updated_at: new Date().toISOString(),
    }

    setOptimisticUpdate(optimisticWorkItem)
    onSave(optimisticWorkItem) // Immediate UI update

    try {
      // Make API call
      const updatedWorkItem = await workItemService.updateWorkItem(
        teamId,
        workItem.id,
        updateRequest
      )

      // Success: replace optimistic update with real data
      setOptimisticUpdate(null)
      onSave(updatedWorkItem)
    } catch (error: unknown) {
      // Rollback optimistic update (AC4)
      setOptimisticUpdate(null)
      onSave(workItem)

      // Handle structured error responses (AC5)
      let errorMessage = 'Failed to update work item'

      const apiError = error as {
        response?: {
          data?: {
            detail?: string | { message?: string }
          }
        }
        message?: string
      }

      if (apiError.response?.data?.detail) {
        const detail = apiError.response.data.detail
        if (typeof detail === 'string') {
          errorMessage = detail
        } else if (typeof detail === 'object' && detail.message) {
          errorMessage = detail.message
        }
      } else if (apiError.message) {
        errorMessage = apiError.message
      }

      setErrors({ general: errorMessage })
      onError?.(errorMessage)
    } finally {
      setIsSaving(false)
    }
  }, [formState, workItem, teamId, validateForm, onSave, onError])

  // Handle form submission
  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault()
      handleSave()
    },
    [handleSave]
  )

  // Warn user about unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault()
        e.returnValue =
          'You have unsaved changes. Are you sure you want to leave?'
      }
    }

    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [hasUnsavedChanges])

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* General error display */}
      {errors.general && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          <p className="text-sm">{errors.general}</p>
        </div>
      )}

      {/* Optimistic update indicator */}
      {optimisticUpdate && (
        <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-md">
          <p className="text-sm">Saving changes...</p>
        </div>
      )}

      {/* Title field */}
      <div>
        <label
          htmlFor="title"
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Title <span className="text-red-500">*</span>
        </label>
        <input
          id="title"
          type="text"
          value={formState.title}
          onChange={(e) => handleInputChange('title', e.target.value)}
          className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
            errors.title ? 'border-red-300' : 'border-gray-300'
          }`}
          placeholder="Enter work item title"
          required
        />
        {errors.title && (
          <p className="mt-1 text-sm text-red-600">{errors.title}</p>
        )}
        <p className="mt-1 text-sm text-gray-500">
          {formState.title.length}/200 characters
        </p>
      </div>

      {/* Description field */}
      <div>
        <label
          htmlFor="description"
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Description
        </label>
        <textarea
          id="description"
          value={formState.description}
          onChange={(e) => handleInputChange('description', e.target.value)}
          rows={4}
          className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
            errors.description ? 'border-red-300' : 'border-gray-300'
          }`}
          placeholder="Enter work item description (optional)"
        />
        {errors.description && (
          <p className="mt-1 text-sm text-red-600">{errors.description}</p>
        )}
        <p className="mt-1 text-sm text-gray-500">
          {formState.description.length}/2000 characters
        </p>
      </div>

      {/* Type and Status row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Type field */}
        <div>
          <label
            htmlFor="type"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Type
          </label>
          <select
            id="type"
            value={formState.type}
            onChange={(e) =>
              handleInputChange('type', e.target.value as WorkItemType)
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value={WorkItemType.STORY}>Story</option>
            <option value={WorkItemType.BUG}>Bug</option>
            <option value={WorkItemType.TASK}>Task</option>
          </select>
        </div>

        {/* Status field */}
        <div>
          <label
            htmlFor="status"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Status
          </label>
          <select
            id="status"
            value={formState.status}
            onChange={(e) =>
              handleInputChange('status', e.target.value as WorkItemStatus)
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value={WorkItemStatus.BACKLOG}>Backlog</option>
            <option value={WorkItemStatus.TODO}>Todo</option>
            <option value={WorkItemStatus.IN_PROGRESS}>In Progress</option>
            <option value={WorkItemStatus.DONE}>Done</option>
          </select>
        </div>
      </div>

      {/* Priority and Story Points row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Priority field */}
        <div>
          <label
            htmlFor="priority"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Priority
          </label>
          <input
            id="priority"
            type="number"
            step="0.1"
            value={formState.priority}
            onChange={(e) => {
              const value = e.target.value
              if (value === '') {
                handleInputChange('priority', 0)
              } else {
                const parsed = parseFloat(value)
                if (!isNaN(parsed)) {
                  handleInputChange('priority', parsed)
                }
              }
            }}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              errors.priority ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="0.0"
          />
          {errors.priority && (
            <p className="mt-1 text-sm text-red-600">{errors.priority}</p>
          )}
        </div>

        {/* Story Points field */}
        <div>
          <label
            htmlFor="story_points"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Story Points
          </label>
          <input
            id="story_points"
            type="number"
            value={formState.story_points}
            onChange={(e) =>
              handleInputChange(
                'story_points',
                e.target.value === '' ? '' : parseInt(e.target.value)
              )
            }
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              errors.story_points ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="Optional"
          />
          {errors.story_points && (
            <p className="mt-1 text-sm text-red-600">{errors.story_points}</p>
          )}
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          disabled={isSaving}
        >
          Cancel
        </button>

        <button
          type="submit"
          disabled={isSaving || hasValidationErrors}
          className={`px-4 py-2 text-sm font-medium text-white rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
            isSaving || hasValidationErrors
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {isSaving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      {/* Unsaved changes indicator */}
      {hasUnsavedChanges && !isSaving && (
        <div className="text-sm text-orange-600 flex items-center">
          <span className="w-2 h-2 bg-orange-400 rounded-full mr-2"></span>
          You have unsaved changes
        </div>
      )}
    </form>
  )
}

export default EditWorkItemForm
