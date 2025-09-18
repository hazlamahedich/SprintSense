import { useState, useCallback } from 'react'
import { UpdateWorkItemRequest, WorkItem } from '../types/workItem.types'
import { workItemService } from '../services/workItemService'

interface UseEditWorkItemResult {
  updateWorkItem: (
    teamId: string,
    workItemId: string,
    data: UpdateWorkItemRequest
  ) => Promise<WorkItem>
  isLoading: boolean
  error: string | null
  clearError: () => void
}

export const useEditWorkItem = (): UseEditWorkItemResult => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const updateWorkItem = useCallback(
    async (
      teamId: string,
      workItemId: string,
      data: UpdateWorkItemRequest
    ): Promise<WorkItem> => {
      setIsLoading(true)
      setError(null)

      try {
        const updatedWorkItem = await workItemService.updateWorkItem(
          teamId,
          workItemId,
          data
        )
        return updatedWorkItem
      } catch (err) {
        let errorMessage = 'Failed to update work item'

        if (err instanceof Error) {
          errorMessage = err.message
        } else if (typeof err === 'object' && err !== null) {
          // Handle axios errors
          const axiosError = err as any
          if (axiosError.response?.data?.detail) {
            errorMessage = axiosError.response.data.detail
          } else if (axiosError.response?.data?.message) {
            errorMessage = axiosError.response.data.message
          } else if (axiosError.message) {
            errorMessage = axiosError.message
          }
        }

        setError(errorMessage)
        throw new Error(errorMessage)
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  return {
    updateWorkItem,
    isLoading,
    error,
    clearError,
  }
}

export default useEditWorkItem
