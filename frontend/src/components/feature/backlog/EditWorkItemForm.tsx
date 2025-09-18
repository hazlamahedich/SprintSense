import React, { useCallback, useState, useEffect } from 'react'
import {
  WorkItem,
  WorkItemType,
  UpdateWorkItemRequest,
} from '../../../types/workItem.types'
import { Button } from '../../ui/button'
import { Input } from '../../ui/input'
import { Label } from '../../ui/label'
import { Textarea } from '../../ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../ui/select'
import { Alert, AlertDescription } from '../../ui/alert'
import { AlertCircle, CheckCircle, Edit } from 'lucide-react'

interface EditWorkItemFormProps {
  workItem: WorkItem
  onSubmit: (data: UpdateWorkItemRequest) => Promise<void>
  onCancel: () => void
  isSubmitting?: boolean
  error?: string | null
  successMessage?: string | null
  isEditingIndicator?: {
    isEditing: boolean
    editingUser?: string
  }
}

interface FormData {
  title: string
  description: string
  type: WorkItemType
  story_points: string
}

const TYPE_OPTIONS = [
  { value: WorkItemType.STORY, label: '📚 Story', icon: '📚' },
  { value: WorkItemType.BUG, label: '🐛 Bug', icon: '🐛' },
  { value: WorkItemType.TASK, label: '✅ Task', icon: '✅' },
]

export const EditWorkItemForm: React.FC<EditWorkItemFormProps> = ({
  workItem,
  onSubmit,
  onCancel,
  isSubmitting = false,
  error = null,
  successMessage = null,
  isEditingIndicator = { isEditing: false },
}) => {
  // Initialize form with existing work item data
  const [formData, setFormData] = useState<FormData>({
    title: workItem.title || '',
    description: workItem.description || '',
    type: workItem.type || WorkItemType.STORY,
    story_points: workItem.story_points?.toString() || '',
  })

  const [validationErrors, setValidationErrors] = useState<Partial<FormData>>(
    {}
  )
  const [titleCharCount, setTitleCharCount] = useState(0)
  const [descCharCount, setDescCharCount] = useState(0)
  const [hasChanges, setHasChanges] = useState(false)

  // Update character counts on mount and when form data changes
  useEffect(() => {
    setTitleCharCount(formData.title.length)
    setDescCharCount(formData.description.length)

    // Check if form has changes compared to original work item
    const hasModifications =
      formData.title.trim() !== (workItem.title || '').trim() ||
      formData.description.trim() !== (workItem.description || '').trim() ||
      formData.type !== workItem.type ||
      (formData.story_points
        ? parseInt(formData.story_points, 10)
        : undefined) !== workItem.story_points

    setHasChanges(hasModifications)
  }, [formData, workItem])

  const validateForm = useCallback((): boolean => {
    const errors: Partial<FormData> = {}

    // Title validation (required, max 200 chars)
    if (!formData.title.trim()) {
      errors.title = 'Title is required'
    } else if (formData.title.length > 200) {
      errors.title = 'Title cannot exceed 200 characters'
    }

    // Description validation (optional, max 2000 chars)
    if (formData.description && formData.description.length > 2000) {
      errors.description = 'Description cannot exceed 2000 characters'
    }

    // Story points validation (optional, positive number)
    if (formData.story_points) {
      const points = parseInt(formData.story_points, 10)
      if (isNaN(points) || points < 0) {
        errors.story_points = 'Story points must be a positive number'
      } else if (points > 100) {
        errors.story_points = 'Story points cannot exceed 100'
      }
    }

    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }, [formData])

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault()

      if (!validateForm()) {
        return
      }

      if (!hasChanges) {
        // No changes, just close the form
        onCancel()
        return
      }

      try {
        const submitData: UpdateWorkItemRequest = {}

        // Only include fields that have changed
        if (formData.title.trim() !== (workItem.title || '').trim()) {
          submitData.title = formData.title.trim()
        }

        const newDescription = formData.description.trim() || undefined
        const originalDescription = workItem.description || undefined
        if (newDescription !== originalDescription) {
          submitData.description = newDescription
        }

        if (formData.type !== workItem.type) {
          submitData.type = formData.type
        }

        const newStoryPoints = formData.story_points
          ? parseInt(formData.story_points, 10)
          : undefined
        if (newStoryPoints !== workItem.story_points) {
          submitData.story_points = newStoryPoints
        }

        await onSubmit(submitData)
      } catch (error) {
        console.error('Form submission error:', error)
      }
    },
    [formData, workItem, validateForm, hasChanges, onSubmit, onCancel]
  )

  const handleFieldChange = useCallback(
    (field: keyof FormData, value: string) => {
      setFormData((prev) => ({
        ...prev,
        [field]: value,
      }))

      // Clear validation error for this field
      if (validationErrors[field]) {
        setValidationErrors((prev) => ({
          ...prev,
          [field]: undefined,
        }))
      }
    },
    [validationErrors]
  )

  const getSelectedTypeIcon = () => {
    const selectedType = TYPE_OPTIONS.find(
      (option) => option.value === formData.type
    )
    return selectedType?.icon || '📚'
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Editing Indicator */}
      {isEditingIndicator.isEditing && isEditingIndicator.editingUser && (
        <Alert className="mb-6 border-orange-200 bg-orange-50">
          <Edit className="h-4 w-4 text-orange-600" />
          <AlertDescription className="text-orange-700">
            <span className="font-medium">
              {isEditingIndicator.editingUser}
            </span>{' '}
            is also editing this work item. Your changes will use the "last
            writer wins" approach.
          </AlertDescription>
        </Alert>
      )}

      {/* Success Message */}
      {successMessage && (
        <Alert className="mb-6 border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-700">
            {successMessage}
          </AlertDescription>
        </Alert>
      )}

      {/* Error Message */}
      {error && (
        <Alert className="mb-6 border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-700">{error}</AlertDescription>
        </Alert>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Title Field */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <Label
              htmlFor="title"
              className="text-sm font-medium text-gray-700"
            >
              Title <span className="text-red-500">*</span>
            </Label>
            <span
              className={`text-xs ${titleCharCount > 200 ? 'text-red-500' : 'text-gray-500'}`}
            >
              {titleCharCount}/200
            </span>
          </div>
          <Input
            id="title"
            value={formData.title}
            onChange={(e) => handleFieldChange('title', e.target.value)}
            placeholder="Enter a clear, concise title for your work item"
            disabled={isSubmitting}
            className={`transition-colors ${
              validationErrors.title
                ? 'border-red-500 focus:border-red-500 focus:ring-red-200'
                : 'focus:border-blue-500 focus:ring-blue-200'
            }`}
            maxLength={200}
          />
          {validationErrors.title && (
            <p className="text-sm text-red-600 flex items-center gap-1">
              <AlertCircle className="h-3 w-3" />
              {validationErrors.title}
            </p>
          )}
        </div>

        {/* Description Field */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <Label
              htmlFor="description"
              className="text-sm font-medium text-gray-700"
            >
              Description <span className="text-gray-400">(optional)</span>
            </Label>
            <span
              className={`text-xs ${descCharCount > 2000 ? 'text-red-500' : 'text-gray-500'}`}
            >
              {descCharCount}/2000
            </span>
          </div>
          <Textarea
            id="description"
            value={formData.description}
            onChange={(e) => handleFieldChange('description', e.target.value)}
            placeholder="Describe the work item in detail. Include context, requirements, and any additional information..."
            rows={4}
            disabled={isSubmitting}
            className={`transition-colors resize-vertical ${
              validationErrors.description
                ? 'border-red-500 focus:border-red-500 focus:ring-red-200'
                : 'focus:border-blue-500 focus:ring-blue-200'
            }`}
            maxLength={2000}
          />
          {validationErrors.description && (
            <p className="text-sm text-red-600 flex items-center gap-1">
              <AlertCircle className="h-3 w-3" />
              {validationErrors.description}
            </p>
          )}
        </div>

        {/* Type and Story Points Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Work Item Type */}
          <div className="space-y-2">
            <Label htmlFor="type" className="text-sm font-medium text-gray-700">
              Type <span className="text-red-500">*</span>
            </Label>
            <Select
              value={formData.type}
              onValueChange={(value) => handleFieldChange('type', value)}
              disabled={isSubmitting}
            >
              <SelectTrigger className="w-full">
                <SelectValue>
                  <span className="flex items-center gap-2">
                    <span>{getSelectedTypeIcon()}</span>
                    <span>
                      {TYPE_OPTIONS.find(
                        (opt) => opt.value === formData.type
                      )?.label.split(' ')[1] || 'Story'}
                    </span>
                  </span>
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                {TYPE_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    <span className="flex items-center gap-2">
                      <span>{option.icon}</span>
                      <span>{option.label.split(' ')[1]}</span>
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Story Points */}
          <div className="space-y-2">
            <Label
              htmlFor="story_points"
              className="text-sm font-medium text-gray-700"
            >
              Story Points <span className="text-gray-400">(optional)</span>
            </Label>
            <Input
              id="story_points"
              type="number"
              min="0"
              max="100"
              value={formData.story_points}
              onChange={(e) =>
                handleFieldChange('story_points', e.target.value)
              }
              placeholder="e.g., 3, 5, 8"
              disabled={isSubmitting}
              className={`transition-colors ${
                validationErrors.story_points
                  ? 'border-red-500 focus:border-red-500 focus:ring-red-200'
                  : 'focus:border-blue-500 focus:ring-blue-200'
              }`}
            />
            {validationErrors.story_points && (
              <p className="text-sm text-red-600 flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />
                {validationErrors.story_points}
              </p>
            )}
          </div>
        </div>

        {/* Work Item Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-blue-900 mb-2">
            📝 Work Item Info
          </h4>
          <div className="text-xs text-blue-800 space-y-1">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="font-medium">Created:</span>{' '}
                {new Date(workItem.created_at).toLocaleDateString()}
              </div>
              <div>
                <span className="font-medium">Status:</span> {workItem.status}
              </div>
              {workItem.updated_at && (
                <div>
                  <span className="font-medium">Last Updated:</span>{' '}
                  {new Date(workItem.updated_at).toLocaleDateString()}
                </div>
              )}
              <div>
                <span className="font-medium">Priority:</span>{' '}
                {workItem.priority}
              </div>
            </div>
            {hasChanges && (
              <div className="mt-2 pt-2 border-t border-blue-200">
                <p className="text-blue-700 font-medium">
                  ✨ You have unsaved changes
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t border-gray-200">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isSubmitting}
            className="sm:w-auto flex-1 sm:flex-initial"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={isSubmitting || !formData.title.trim() || !hasChanges}
            className={`sm:w-auto flex-1 sm:flex-initial font-medium ${
              hasChanges
                ? 'bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {isSubmitting ? (
              <div className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                Saving Changes...
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <span>{getSelectedTypeIcon()}</span>
                <span>{hasChanges ? 'Save Changes' : 'No Changes'}</span>
              </div>
            )}
          </Button>
        </div>
      </form>
    </div>
  )
}

export default EditWorkItemForm
