import React from 'react'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from '@/components/ui/select-radix'
import {
  WorkItem as WorkItemType,
  WorkItemStatus,
} from '@/types/workItem.types'
import { useWorkItemStatus } from '@/hooks/useWorkItemStatus'
import { ConfirmStatusChangeModal } from './ConfirmStatusChangeModal'

interface WorkItemProps {
  workItem: WorkItemType
  teamId: string
}

export const WorkItem: React.FC<WorkItemProps> = ({ workItem, teamId }) => {
  const {
    isConfirmOpen,
    isLoading,
    targetStatus,
    handleStatusChange,
    handleConfirm,
    handleClose,
  } = useWorkItemStatus({ workItem, teamId })

  const getStatusColor = (status: WorkItemStatus) => {
    switch (status) {
      case WorkItemStatus.DONE:
        return 'bg-green-100 text-green-700'
      case WorkItemStatus.IN_PROGRESS:
        return 'bg-blue-100 text-blue-700'
      case WorkItemStatus.TODO:
        return 'bg-yellow-100 text-yellow-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  return (
    <>
      <div className="w-full p-6 bg-white rounded-lg shadow-sm">
        <div className="flex flex-row items-center justify-between space-y-0 pb-4">
          <div className="flex items-center space-x-2">
            <Badge
              className={getStatusColor(workItem.status)}
              aria-label={`Status: ${workItem.status}`}
            >
              {workItem.status}
            </Badge>
            {workItem.story_points && (
              <Badge
                className="bg-purple-100 text-purple-700"
                aria-label={`Story Points: ${workItem.story_points}`}
              >
                {workItem.story_points} pts
              </Badge>
            )}
          </div>
          <div className="w-[140px]">
            <Select value={workItem.status} onValueChange={handleStatusChange}>
              <SelectTrigger
                className="w-full"
                aria-label="Change work item status"
              >
                <SelectValue placeholder="Change status" />
              </SelectTrigger>
              <SelectContent>
                {Object.values(WorkItemStatus).map((status) => (
                  <SelectItem
                    key={status}
                    value={status}
                    disabled={workItem.status === status}
                    onClick={() => handleStatusChange(status)}
                  >
                    {status}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="py-4">
          <h3 className="text-lg font-semibold mb-2">{workItem.title}</h3>
          {workItem.description && (
            <p className="text-sm text-gray-600">{workItem.description}</p>
          )}
        </div>

        <div className="pt-4 text-sm text-gray-500 flex justify-between border-t">
          <div>Created: {formatDate(workItem.created_at)}</div>
          {workItem.completed_at && (
            <div>Completed: {formatDate(workItem.completed_at)}</div>
          )}
        </div>
      </div>

      {isConfirmOpen && targetStatus && (
        <ConfirmStatusChangeModal
          isOpen={isConfirmOpen}
          onClose={handleClose}
          onConfirm={handleConfirm}
          title={`Update Status: ${workItem.title}`}
          targetStatus={targetStatus}
          isLoading={isLoading}
        />
      )}
    </>
  )
}

export default WorkItem
