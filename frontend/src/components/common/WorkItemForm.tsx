import React, { useCallback, useEffect, useState } from 'react'
import {
  WorkItem,
  CreateWorkItemRequest,
  UpdateWorkItemRequest,
  WorkItemType,
  WorkItemStatus,
} from '../../types/workItem.types'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Label } from '../ui/label'
import { Textarea } from '../ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog'
import { XMarkIcon } from '@heroicons/react/24/outline/index.js'

interface WorkItemFormProps {
  workItem?: WorkItem | null
  isOpen: boolean
  onClose: () => void
  onSubmit: (
    data: CreateWorkItemRequest | UpdateWorkItemRequest
  ) => Promise<void>
  isSubmitting?: boolean
  teamId: string
}

const TYPE_OPTIONS = [
  { value: WorkItemType.STORY, label: 'Story' },
  { value: WorkItemType.TASK, label: 'Task' },
  { value: WorkItemType.BUG, label: 'Bug' },
]

const STATUS_OPTIONS = [
  { value: WorkItemStatus.BACKLOG, label: 'Backlog' },
  { value: WorkItemStatus.TODO, label: 'Todo' },
  { value: WorkItemStatus.IN_PROGRESS, label: 'In Progress' },
  { value: WorkItemStatus.DONE, label: 'Done' },
  { value: WorkItemStatus.ARCHIVED, label: 'Archived' },
]

const PRIORITY_OPTIONS = [
  { value: '1', label: 'Low' },
  { value: '3', label: 'Medium' },
  { value: '5', label: 'High' },
  { value: '7', label: 'Critical' },
]

interface FormData {
  title: string
  description: string
  type: WorkItemType
  status: WorkItemStatus
  priority: string
  assigneeId: string
  dueDate: string
  storyPoints: string
  acceptanceCriteria: string
  tags: string
}

const initialFormData: FormData = {
  title: '',
  description: '',
  type: WorkItemType.TASK,
  status: WorkItemStatus.BACKLOG,
  priority: '3',
  assigneeId: '',
  dueDate: '',
  storyPoints: '',
  acceptanceCriteria: '',
  tags: '',
}

export const WorkItemForm: React.FC<WorkItemFormProps> = ({
  workItem,
  isOpen,
  onClose,
  onSubmit,
  isSubmitting = false,
  teamId, // eslint-disable-line @typescript-eslint/no-unused-vars -- Required for API calls by parent
}) => {
  const [formData, setFormData] = useState<FormData>(initialFormData)
  const [errors, setErrors] = useState<Partial<FormData>>({})

  const isEditing = !!workItem

  // Reset form when dialog opens/closes or workItem changes
  useEffect(() => {
    if (isOpen) {
      if (workItem) {
        // Pre-fill form with existing work item data
        setFormData({
          title: workItem.title,
          description: workItem.description || '',
          type: workItem.type,
          status: workItem.status,
          priority: workItem.priority.toString(),
          assigneeId: workItem.assigneeId || '',
          dueDate: workItem.dueDate
            ? new Date(workItem.dueDate).toISOString().split('T')[0]
            : '',
          storyPoints: workItem.storyPoints?.toString() || '',
          acceptanceCriteria: workItem.acceptanceCriteria || '',
          tags: workItem.tags?.join(', ') || '',
        })
      } else {
        setFormData(initialFormData)
      }
      setErrors({})
    }
  }, [isOpen, workItem])

  const validateForm = useCallback((): boolean => {
    const newErrors: Partial<FormData> = {}

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required'
    } else if (formData.title.length > 200) {
      newErrors.title = 'Title must be 200 characters or less'
    }

    if (formData.description && formData.description.length > 2000) {
      newErrors.description = 'Description must be 2000 characters or less'
    }

    if (formData.storyPoints) {
      const points = parseInt(formData.storyPoints, 10)
      if (isNaN(points) || points < 0) {
        newErrors.storyPoints = 'Story points must be a positive number'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }, [formData])

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault()

      if (!validateForm()) {
        return
      }

      try {
        const submitData: CreateWorkItemRequest | UpdateWorkItemRequest = {
          title: formData.title.trim(),
          description: formData.description.trim() || undefined,
          type: formData.type,
          status: formData.status,
          priority: parseFloat(formData.priority),
          assigneeId: formData.assigneeId.trim() || undefined,
          dueDate: formData.dueDate
            ? new Date(formData.dueDate).toISOString()
            : undefined,
          storyPoints: formData.storyPoints
            ? parseInt(formData.storyPoints, 10)
            : undefined,
          acceptanceCriteria: formData.acceptanceCriteria.trim() || undefined,
          tags: formData.tags
            ? formData.tags
                .split(',')
                .map((tag) => tag.trim())
                .filter(Boolean)
            : undefined,
        }

        await onSubmit(submitData)
        onClose()
      } catch (error) {
        console.error('Form submission error:', error)
      }
    },
    [formData, validateForm, onSubmit, onClose]
  )

  const handleFieldChange = useCallback(
    (field: keyof FormData, value: string) => {
      setFormData((prev) => ({
        ...prev,
        [field]: value,
      }))

      // Clear error for this field when user starts typing
      if (errors[field]) {
        setErrors((prev) => ({
          ...prev,
          [field]: undefined,
        }))
      }
    },
    [errors]
  )

  const handleClose = useCallback(() => {
    if (!isSubmitting) {
      onClose()
    }
  }, [isSubmitting, onClose])

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle>
              {isEditing ? 'Edit Work Item' : 'Create Work Item'}
            </DialogTitle>
            <Button
              onClick={handleClose}
              variant="ghost"
              size="sm"
              className="p-1 h-8 w-8"
              disabled={isSubmitting}
            >
              <XMarkIcon className="w-4 h-4" />
            </Button>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="title">Title *</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => handleFieldChange('title', e.target.value)}
              placeholder="Enter work item title"
              disabled={isSubmitting}
              className={errors.title ? 'border-red-500' : ''}
            />
            {errors.title && (
              <p className="text-sm text-red-600">{errors.title}</p>
            )}
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => handleFieldChange('description', e.target.value)}
              placeholder="Describe the work item..."
              rows={4}
              disabled={isSubmitting}
              className={errors.description ? 'border-red-500' : ''}
            />
            {errors.description && (
              <p className="text-sm text-red-600">{errors.description}</p>
            )}
          </div>

          {/* Type, Status, Priority Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="type">Type *</Label>
              <Select
                value={formData.type}
                onValueChange={(value) => handleFieldChange('type', value)}
                disabled={isSubmitting}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {TYPE_OPTIONS.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="status">Status *</Label>
              <Select
                value={formData.status}
                onValueChange={(value) => handleFieldChange('status', value)}
                disabled={isSubmitting}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {STATUS_OPTIONS.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="priority">Priority *</Label>
              <Select
                value={formData.priority}
                onValueChange={(value) => handleFieldChange('priority', value)}
                disabled={isSubmitting}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {PRIORITY_OPTIONS.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Assignee and Story Points Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="assigneeId">Assignee ID</Label>
              <Input
                id="assigneeId"
                value={formData.assigneeId}
                onChange={(e) =>
                  handleFieldChange('assigneeId', e.target.value)
                }
                placeholder="Enter assignee ID"
                disabled={isSubmitting}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="storyPoints">Story Points</Label>
              <Input
                id="storyPoints"
                type="number"
                min="0"
                value={formData.storyPoints}
                onChange={(e) =>
                  handleFieldChange('storyPoints', e.target.value)
                }
                placeholder="Enter story points"
                disabled={isSubmitting}
                className={errors.storyPoints ? 'border-red-500' : ''}
              />
              {errors.storyPoints && (
                <p className="text-sm text-red-600">{errors.storyPoints}</p>
              )}
            </div>
          </div>

          {/* Due Date */}
          <div className="space-y-2">
            <Label htmlFor="dueDate">Due Date</Label>
            <Input
              id="dueDate"
              type="date"
              value={formData.dueDate}
              onChange={(e) => handleFieldChange('dueDate', e.target.value)}
              disabled={isSubmitting}
            />
          </div>

          {/* Acceptance Criteria */}
          <div className="space-y-2">
            <Label htmlFor="acceptanceCriteria">Acceptance Criteria</Label>
            <Textarea
              id="acceptanceCriteria"
              value={formData.acceptanceCriteria}
              onChange={(e) =>
                handleFieldChange('acceptanceCriteria', e.target.value)
              }
              placeholder="Define acceptance criteria..."
              rows={3}
              disabled={isSubmitting}
            />
          </div>

          {/* Tags */}
          <div className="space-y-2">
            <Label htmlFor="tags">Tags</Label>
            <Input
              id="tags"
              value={formData.tags}
              onChange={(e) => handleFieldChange('tags', e.target.value)}
              placeholder="Enter tags separated by commas"
              disabled={isSubmitting}
            />
            <p className="text-sm text-gray-500">
              Separate multiple tags with commas (e.g., "frontend, bug, urgent")
            </p>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  {isEditing ? 'Updating...' : 'Creating...'}
                </div>
              ) : isEditing ? (
                'Update Work Item'
              ) : (
                'Create Work Item'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export default WorkItemForm
