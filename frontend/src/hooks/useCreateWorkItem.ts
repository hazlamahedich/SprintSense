import { useState, useCallback } from 'react'
import { CreateWorkItemRequest, WorkItem } from '../types/workItem.types'
import { workItemService } from '../services/workItemService'

interface UseCreateWorkItemReturn {
  createWorkItem: (
    teamId: string,
    data: CreateWorkItemRequest
  ) => Promise<WorkItem>
  isSubmitting: boolean
  error: string | null
  successMessage: string | null
  clearMessages: () => void
  reset: () => void
}

interface CreateWorkItemError {
  message: string
  details?: {
    field?: string
    code?: string
  }
}

const parseErrorMessage = (error: any): string => {
  // Handle different error response formats
  if (error?.response?.data) {
    const data = error.response.data

    // Handle validation errors
    if (data.detail && Array.isArray(data.detail)) {
      const messages = data.detail.map((err: any) => {
        if (err.msg && err.loc) {
          const field = err.loc[err.loc.length - 1]
          return `${field}: ${err.msg}`
        }
        return err.msg || 'Validation error'
      })
      return messages.join(', ')
    }

    // Handle single error message
    if (data.detail && typeof data.detail === 'string') {
      return data.detail
    }

    // Handle custom error format
    if (data.message) {
      return data.message
    }
  }

  // Handle HTTP status codes
  if (error?.response?.status) {
    switch (error.response.status) {
      case 401:
        return 'You need to be logged in to create work items'
      case 403:
        return "You don't have permission to create work items for this team"
      case 409:
        return 'A work item with similar details already exists'
      case 422:
        return 'Please check your input and try again'
      case 500:
        return 'Server error occurred. Please try again later'
      default:
        return `Request failed with status ${error.response.status}`
    }
  }

  // Handle network errors
  if (
    error?.code === 'NETWORK_ERROR' ||
    error?.message?.includes('Network Error')
  ) {
    return 'Network error. Please check your connection and try again'
  }

  // Fallback
  return (
    error?.message ||
    'An unexpected error occurred while creating the work item'
  )
}

export const useCreateWorkItem = (): UseCreateWorkItemReturn => {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const clearMessages = useCallback(() => {
    setError(null)
    setSuccessMessage(null)
  }, [])

  const reset = useCallback(() => {
    setIsSubmitting(false)
    clearMessages()
  }, [clearMessages])

  const createWorkItem = useCallback(
    async (teamId: string, data: CreateWorkItemRequest): Promise<WorkItem> => {
      // Clear any previous messages
      clearMessages()
      setIsSubmitting(true)

      try {
        // Validate required fields on client side
        if (!data.title?.trim()) {
          throw new Error('Title is required')
        }

        if (data.title.length > 200) {
          throw new Error('Title cannot exceed 200 characters')
        }

        if (data.description && data.description.length > 2000) {
          throw new Error('Description cannot exceed 2000 characters')
        }

        // Call the API service
        const workItem = await workItemService.createWorkItem(teamId, data)

        // Set success message
        setSuccessMessage(
          `Work item "${data.title}" has been created successfully and added to your backlog!`
        )

        return workItem
      } catch (err: any) {
        const errorMessage = parseErrorMessage(err)
        setError(errorMessage)

        // Re-throw the error so the caller can handle it if needed
        throw new Error(errorMessage)
      } finally {
        setIsSubmitting(false)
      }
    },
    [clearMessages]
  )

  return {
    createWorkItem,
    isSubmitting,
    error,
    successMessage,
    clearMessages,
    reset,
  }
}

export default useCreateWorkItem
