/**
 * Custom hook for archiving work items with optimistic updates and error handling.
 */

import { useState, useCallback } from 'react'
import { workItemService } from '../services/workItemService'
import { WorkItem, WorkItemStatus } from '../types/workItem.types'

export interface UseArchiveWorkItemReturn {
  archiveWorkItem: (workItemId: string) => Promise<void>
  isLoading: boolean
  error: string | null
  clearError: () => void
}

export interface UseArchiveWorkItemOptions {
  onOptimisticUpdate?: (workItemId: string, archivedWorkItem: WorkItem) => void
  onOptimisticRollback?: (
    workItemId: string,
    originalWorkItem: WorkItem
  ) => void
  onSuccess?: (archivedWorkItem: WorkItem) => void
  onError?: (error: string) => void
}

/**
 * Hook for archiving work items with optimistic updates.
 *
 * @param teamId - The team ID
 * @param options - Configuration options for callbacks
 * @returns Object with archive function, loading state, error, and clearError function
 */
export const useArchiveWorkItem = (
  teamId: string,
  options: UseArchiveWorkItemOptions = {}
): UseArchiveWorkItemReturn => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { onOptimisticUpdate, onOptimisticRollback, onSuccess, onError } =
    options

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const archiveWorkItem = useCallback(
    async (workItemId: string) => {
      if (isLoading) {
        return // Prevent concurrent requests
      }

      try {
        setIsLoading(true)
        setError(null)

        // Store original work item data for potential rollback
        let originalWorkItem: WorkItem | null = null

        try {
          originalWorkItem = await workItemService.getWorkItem(
            teamId,
            workItemId
          )
        } catch (fetchError) {
          console.warn(
            'Failed to fetch original work item for rollback:',
            fetchError
          )
        }

        // Perform optimistic update if callback provided
        if (onOptimisticUpdate && originalWorkItem) {
          const optimisticUpdate: WorkItem = {
            ...originalWorkItem,
            status: WorkItemStatus.ARCHIVED,
            updated_at: new Date().toISOString(),
          }
          onOptimisticUpdate(workItemId, optimisticUpdate)
        }

        // Make the actual API call
        const archivedWorkItem = await workItemService.archiveWorkItem(
          teamId,
          workItemId
        )

        // Call success callback
        if (onSuccess) {
          onSuccess(archivedWorkItem)
        }
      } catch (apiError: unknown) {
        // Handle error and rollback optimistic update
        const errorMessage =
          apiError instanceof Error
            ? apiError.message
            : 'Failed to archive work item'

        setError(errorMessage)

        // Rollback optimistic update if we have the original data
        if (onOptimisticRollback && originalWorkItem) {
          onOptimisticRollback(workItemId, originalWorkItem)
        }

        // Call error callback
        if (onError) {
          onError(errorMessage)
        }

        // Re-throw to allow component-level error handling
        throw apiError
      } finally {
        setIsLoading(false)
      }
    },
    [
      teamId,
      isLoading,
      onOptimisticUpdate,
      onOptimisticRollback,
      onSuccess,
      onError,
    ]
  )

  return {
    archiveWorkItem,
    isLoading,
    error,
    clearError,
  }
}

export default useArchiveWorkItem
