/**
 * Hook for managing work item priority updates.
 * Implements Story 2.6 requirements for accessible priority management
 * with optimistic updates, error handling, and loading states.
 */

import { useState, useCallback } from 'react'
import { workItemService } from '../services/workItemService'
import {
  WorkItem,
  PriorityUpdateRequest,
  PriorityAction,
} from '../types/workItem.types'

interface PriorityUpdateParams {
  workItemId: string
  teamId: string
  action: PriorityAction
  currentPriority: number
}

interface UsePriorityUpdateOptions {
  onSuccess?: (updatedItem: WorkItem) => void
  onError?: (error: string) => void
  onConflict?: (conflictMessage: string) => void
}

interface UsePriorityUpdateReturn {
  loading: boolean
  error: string | null
  updatePriority: (params: PriorityUpdateParams) => Promise<WorkItem | null>
}

export const usePriorityUpdate = (
  options: UsePriorityUpdateOptions = {}
): UsePriorityUpdateReturn => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { onSuccess, onError, onConflict } = options

  const updatePriority = useCallback(
    async (params: PriorityUpdateParams): Promise<WorkItem | null> => {
      const { workItemId, teamId, action, currentPriority } = params
      setLoading(true)
      setError(null)

      try {
        const priorityData: PriorityUpdateRequest = {
          action,
          current_priority: currentPriority,
        }

        const updatedItem = await workItemService.updateWorkItemPriority(
          teamId,
          workItemId,
          priorityData
        )

        if (onSuccess) {
          onSuccess(updatedItem)
        }

        return updatedItem
      } catch (error: unknown) {
        const errorMessage =
          err.response?.data?.detail || err.message || 'Priority update failed'
        setError(errorMessage)

        // Handle 409 conflict specifically
        if (err.response?.status === 409) {
          if (onConflict) {
            onConflict(errorMessage)
          }
        } else if (onError) {
          onError(errorMessage)
        }

        return null
      } finally {
        setLoading(false)
      }
    },
    [onSuccess, onError, onConflict]
  )

  return {
    loading,
    error,
    updatePriority,
  }
}

export default usePriorityUpdate
