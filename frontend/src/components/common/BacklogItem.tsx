import React, { useState } from 'react'
import {
  WorkItem,
  WorkItemType,
  WorkItemStatus,
} from '../../types/workItem.types'
import { Card, CardHeader, CardContent, CardFooter } from '../ui/card'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import {
  UserIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  MinusIcon,
  PencilIcon,
  TrashIcon,
} from '@heroicons/react/24/outline'
import EditWorkItemModal from '../work-items/EditWorkItemModal'

interface BacklogItemProps {
  workItem: WorkItem
  teamId: string
  onEdit?: (workItem: WorkItem) => void
  onDelete: (id: string) => void
  onMove?: (id: string, direction: 'up' | 'down') => void
  showMoveButtons?: boolean
  className?: string
}

const TYPE_COLORS: Record<WorkItemType, string> = {
  [WorkItemType.STORY]: 'bg-green-100 text-green-800',
  [WorkItemType.TASK]: 'bg-yellow-100 text-yellow-800',
  [WorkItemType.BUG]: 'bg-red-100 text-red-800',
}

const STATUS_COLORS: Record<WorkItemStatus, string> = {
  [WorkItemStatus.BACKLOG]: 'bg-slate-100 text-slate-800',
  [WorkItemStatus.TODO]: 'bg-blue-100 text-blue-800',
  [WorkItemStatus.IN_PROGRESS]: 'bg-orange-100 text-orange-800',
  [WorkItemStatus.DONE]: 'bg-green-100 text-green-800',
  [WorkItemStatus.ARCHIVED]: 'bg-gray-100 text-gray-800',
}

// Priority is a numeric value from backend, we'll create utility functions for display
const getPriorityColor = (priority: number): string => {
  if (priority >= 7) return 'bg-red-100 text-red-600' // Critical
  if (priority >= 5) return 'bg-orange-100 text-orange-600' // High
  if (priority >= 3) return 'bg-yellow-100 text-yellow-600' // Medium
  return 'bg-gray-100 text-gray-600' // Low
}

const getPriorityIcon = (priority: number) => {
  if (priority >= 5) return ArrowUpIcon // High/Critical
  return MinusIcon // Low/Medium
}

const getPriorityLabel = (priority: number): string => {
  if (priority >= 7) return 'Critical'
  if (priority >= 5) return 'High'
  if (priority >= 3) return 'Medium'
  return 'Low'
}

export const BacklogItem: React.FC<BacklogItemProps> = ({
  workItem,
  teamId,
  onEdit,
  onDelete,
  onMove,
  showMoveButtons = false,
  className = '',
}) => {
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const PriorityIcon = getPriorityIcon(workItem.priority)

  const handleEdit = () => {
    if (onEdit) {
      // Use external handler if provided
      onEdit(workItem)
    } else {
      // Use internal modal by default
      setIsEditModalOpen(true)
    }
  }

  const handleEditModalClose = () => {
    setIsEditModalOpen(false)
  }

  const handleEditModalSave = (updatedWorkItem: WorkItem) => {
    // Update would be handled by the parent component through state management
    // For now, just close the modal
    setIsEditModalOpen(false)

    // Optionally call the onEdit callback with updated item
    onEdit?.(updatedWorkItem)
  }

  const handleDelete = () => {
    onDelete(workItem.id)
  }

  const handleMoveUp = () => {
    onMove?.(workItem.id, 'up')
  }

  const handleMoveDown = () => {
    onMove?.(workItem.id, 'down')
  }

  return (
    <>
      <Card className={`hover:shadow-md transition-shadow ${className}`}>
        <CardHeader className="pb-2">
          <div className="flex justify-between items-start">
            <div className="flex items-center gap-2 flex-1">
              <Badge className={TYPE_COLORS[workItem.type]}>
                {workItem.type.replace('_', ' ')}
              </Badge>
              <Badge className={STATUS_COLORS[workItem.status]}>
                {workItem.status.replace('_', ' ')}
              </Badge>
              <Badge
                className={`${getPriorityColor(workItem.priority)} flex items-center gap-1`}
              >
                <PriorityIcon className="w-3 h-3" />
                {getPriorityLabel(workItem.priority)}
              </Badge>
            </div>
            <div className="flex items-center gap-1">
              {showMoveButtons && onMove && (
                <>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleMoveUp}
                    className="p-1 h-8 w-8"
                    title="Move up"
                  >
                    <ArrowUpIcon className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleMoveDown}
                    className="p-1 h-8 w-8"
                    title="Move down"
                  >
                    <ArrowDownIcon className="w-4 h-4" />
                  </Button>
                </>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={handleEdit}
                className="p-1 h-8 w-8"
                title="Edit"
              >
                <PencilIcon className="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleDelete}
                className="p-1 h-8 w-8 text-red-600 hover:text-red-800"
                title="Delete"
              >
                <TrashIcon className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent className="pb-2">
          <h3 className="font-semibold text-lg mb-2 line-clamp-2">
            {workItem.title}
          </h3>
          {workItem.description && (
            <p className="text-gray-600 text-sm line-clamp-3 mb-3">
              {workItem.description}
            </p>
          )}
          <div className="flex items-center gap-4 text-sm text-gray-500">
            {workItem.assignee_id && (
              <div className="flex items-center gap-1">
                <UserIcon className="w-4 h-4" />
                <span>Assignee: {workItem.assignee_id}</span>
              </div>
            )}
          </div>
        </CardContent>

        <CardFooter className="pt-2 border-t">
          <div className="flex justify-between items-center w-full text-xs text-gray-500">
            <span>ID: {workItem.id.slice(0, 8)}</span>
            <div className="flex items-center gap-4">
              {workItem.story_points && (
                <span>Story Points: {workItem.story_points}</span>
              )}
              <span>
                Created: {new Date(workItem.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </CardFooter>
      </Card>

      {/* Edit Modal */}
      <EditWorkItemModal
        isOpen={isEditModalOpen}
        workItem={workItem}
        teamId={teamId}
        onClose={handleEditModalClose}
        onSave={handleEditModalSave}
      />
    </>
  )
}

export default BacklogItem
