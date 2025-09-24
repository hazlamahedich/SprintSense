import React, { useEffect, useState } from 'react'
import { WorkItem } from '../types/workItem.types'
import { WorkItemSprintService } from '../services/workItemSprintService'
import { useToast } from '../hooks/useToast'

interface Props {
  workItem: WorkItem
  onAssign: (workItem: WorkItem) => void
  sprints: Array<{ id: string; name: string; status: string }>
}

export const WorkItemSprintAssignment: React.FC<Props> = ({
  workItem,
  onAssign,
  sprints,
}) => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { showToast } = useToast()

  // Filter to only show Future sprints
  const availableSprints = sprints.filter(
    (sprint) => sprint.status === 'Future'
  )

  // Effect for real-time updates
  useEffect(() => {
    const unsubscribe = WorkItemSprintService.subscribeToWorkItemUpdates(
      (updatedWorkItem) => {
        if (updatedWorkItem.id === workItem.id) {
          onAssign(updatedWorkItem)
        }
      }
    )
    return () => unsubscribe()
  }, [workItem.id, onAssign])

  const handleSprintAssignment = async (sprintId: string | null) => {
    setLoading(true)
    setError(null)

    try {
      const result = await WorkItemSprintService.assignToSprint(
        workItem.id,
        sprintId,
        workItem.version
      )

      const updatedWorkItem: WorkItem = {
        ...workItem,
        sprintId: result.sprintId,
        version: result.version,
      }

      onAssign(updatedWorkItem)
      showToast({
        title: 'Success',
        description: sprintId
          ? 'Work item assigned to sprint'
          : 'Work item removed from sprint',
        status: 'success',
      })
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to assign sprint'
      setError(message)
      showToast({
        title: 'Error',
        description: message,
        status: 'error',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="work-item-sprint-assignment">
      <label
        htmlFor="sprint-select"
        className="block text-sm font-medium text-gray-700"
      >
        Sprint Assignment
      </label>
      <div className="mt-1">
        <select
          id="sprint-select"
          value={workItem.sprintId || ''}
          onChange={(e) => handleSprintAssignment(e.target.value || null)}
          disabled={loading}
          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
        >
          <option value="">No Sprint</option>
          {availableSprints.map((sprint) => (
            <option key={sprint.id} value={sprint.id}>
              {sprint.name}
            </option>
          ))}
        </select>
      </div>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      {loading && (
        <div className="mt-2 text-sm text-gray-500">
          Updating sprint assignment...
        </div>
      )}
    </div>
  )
}
