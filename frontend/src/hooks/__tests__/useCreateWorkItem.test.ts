import { renderHook, act, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useCreateWorkItem } from '../useCreateWorkItem'
import { workItemService } from '../../services/workItemService'
import { WorkItemType, WorkItem } from '../../types/workItem.types'

// Mock the work item service
vi.mock('../../services/workItemService', () => ({
  workItemService: {
    createWorkItem: vi.fn(),
  },
}))

interface MockWorkItemService {
  createWorkItem: ReturnType<typeof vi.fn>
}

const mockWorkItemService = workItemService as MockWorkItemService

describe('useCreateWorkItem', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should initialize with correct default state', () => {
    const { result } = renderHook(() => useCreateWorkItem())

    expect(result.current.isSubmitting).toBe(false)
    expect(result.current.error).toBe(null)
    expect(result.current.successMessage).toBe(null)
    expect(typeof result.current.createWorkItem).toBe('function')
    expect(typeof result.current.clearMessages).toBe('function')
    expect(typeof result.current.reset).toBe('function')
  })

  it('should clear messages when clearMessages is called', () => {
    const { result } = renderHook(() => useCreateWorkItem())

    // Set some initial state
    act(() => {
      // Simulate error state
      result.current.createWorkItem('team-1', { title: '' }).catch(() => {})
    })

    // Clear messages
    act(() => {
      result.current.clearMessages()
    })

    expect(result.current.error).toBe(null)
    expect(result.current.successMessage).toBe(null)
  })

  it('should reset all state when reset is called', () => {
    const { result } = renderHook(() => useCreateWorkItem())

    // Clear messages and reset submitting state
    act(() => {
      result.current.reset()
    })

    expect(result.current.isSubmitting).toBe(false)
    expect(result.current.error).toBe(null)
    expect(result.current.successMessage).toBe(null)
  })

  it('should validate title is required', async () => {
    const { result } = renderHook(() => useCreateWorkItem())

    await act(async () => {
      try {
        await result.current.createWorkItem('team-1', { title: '' })
      } catch {
        // Expected to throw
      }
    })

    expect(result.current.error).toBe('Title is required')
    expect(result.current.isSubmitting).toBe(false)
  })

  it('should validate title length (max 200 characters)', async () => {
    const { result } = renderHook(() => useCreateWorkItem())

    const longTitle = 'x'.repeat(201)

    await act(async () => {
      try {
        await result.current.createWorkItem('team-1', { title: longTitle })
      } catch {
        // Expected to throw
      }
    })

    expect(result.current.error).toBe('Title cannot exceed 200 characters')
    expect(result.current.isSubmitting).toBe(false)
  })

  it('should validate description length (max 2000 characters)', async () => {
    const { result } = renderHook(() => useCreateWorkItem())

    const longDescription = 'x'.repeat(2001)

    await act(async () => {
      try {
        await result.current.createWorkItem('team-1', {
          title: 'Valid title',
          description: longDescription,
        })
      } catch {
        // Expected to throw
      }
    })

    expect(result.current.error).toBe(
      'Description cannot exceed 2000 characters'
    )
    expect(result.current.isSubmitting).toBe(false)
  })

  it('should successfully create work item with valid data', async () => {
    const mockWorkItem = {
      id: 'work-item-1',
      team_id: 'team-1',
      title: 'Test Work Item',
      description: 'Test description',
      type: WorkItemType.STORY,
      status: 'backlog',
      priority: 1.0,
      author_id: 'user-1',
      created_at: new Date().toISOString(),
    }

    mockWorkItemService.createWorkItem.mockResolvedValue(mockWorkItem)

    const { result } = renderHook(() => useCreateWorkItem())

    let returnedWorkItem: WorkItem

    await act(async () => {
      returnedWorkItem = await result.current.createWorkItem('team-1', {
        title: 'Test Work Item',
        description: 'Test description',
        type: WorkItemType.STORY,
      })
    })

    expect(mockWorkItemService.createWorkItem).toHaveBeenCalledWith('team-1', {
      title: 'Test Work Item',
      description: 'Test description',
      type: WorkItemType.STORY,
    })

    expect(returnedWorkItem).toEqual(mockWorkItem)
    expect(result.current.isSubmitting).toBe(false)
    expect(result.current.error).toBe(null)
    expect(result.current.successMessage).toContain('Test Work Item')
    expect(result.current.successMessage).toContain('created successfully')
  })

  it('should set isSubmitting to true during API call', async () => {
    // Mock a delayed response
    mockWorkItemService.createWorkItem.mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    )

    const { result } = renderHook(() => useCreateWorkItem())

    act(() => {
      result.current.createWorkItem('team-1', {
        title: 'Test Work Item',
      })
    })

    expect(result.current.isSubmitting).toBe(true)

    await waitFor(() => {
      expect(result.current.isSubmitting).toBe(false)
    })
  })

  it('should handle API error responses correctly', async () => {
    const apiError = {
      response: {
        status: 403,
        data: {
          detail:
            "You don't have permission to create work items for this team",
        },
      },
    }

    mockWorkItemService.createWorkItem.mockRejectedValue(apiError)

    const { result } = renderHook(() => useCreateWorkItem())

    await act(async () => {
      try {
        await result.current.createWorkItem('team-1', {
          title: 'Test Work Item',
        })
      } catch {
        // Expected to throw
      }
    })

    expect(result.current.error).toBe(
      "You don't have permission to create work items for this team"
    )
    expect(result.current.isSubmitting).toBe(false)
    expect(result.current.successMessage).toBe(null)
  })

  it('should handle validation error responses', async () => {
    const validationError = {
      response: {
        status: 422,
        data: {
          detail: [
            {
              msg: 'Title cannot be empty',
              loc: ['body', 'title'],
            },
            {
              msg: 'Invalid type',
              loc: ['body', 'type'],
            },
          ],
        },
      },
    }

    mockWorkItemService.createWorkItem.mockRejectedValue(validationError)

    const { result } = renderHook(() => useCreateWorkItem())

    await act(async () => {
      try {
        await result.current.createWorkItem('team-1', {
          title: 'Test Work Item',
        })
      } catch {
        // Expected to throw
      }
    })

    expect(result.current.error).toBe(
      'title: Title cannot be empty, type: Invalid type'
    )
    expect(result.current.isSubmitting).toBe(false)
  })

  it('should handle network errors', async () => {
    const networkError = {
      message: 'Network Error',
      code: 'NETWORK_ERROR',
    }

    mockWorkItemService.createWorkItem.mockRejectedValue(networkError)

    const { result } = renderHook(() => useCreateWorkItem())

    await act(async () => {
      try {
        await result.current.createWorkItem('team-1', {
          title: 'Test Work Item',
        })
      } catch {
        // Expected to throw
      }
    })

    expect(result.current.error).toBe(
      'Network error. Please check your connection and try again'
    )
    expect(result.current.isSubmitting).toBe(false)
  })

  it('should handle different HTTP status codes', async () => {
    const testCases = [
      {
        status: 401,
        expectedMessage: 'You need to be logged in to create work items',
      },
      {
        status: 409,
        expectedMessage: 'A work item with similar details already exists',
      },
      {
        status: 500,
        expectedMessage: 'Server error occurred. Please try again later',
      },
    ]

    for (const testCase of testCases) {
      mockWorkItemService.createWorkItem.mockRejectedValue({
        response: { status: testCase.status },
      })

      const { result } = renderHook(() => useCreateWorkItem())

      await act(async () => {
        try {
          await result.current.createWorkItem('team-1', {
            title: 'Test Work Item',
          })
        } catch {
          // Expected to throw
        }
      })

      expect(result.current.error).toBe(testCase.expectedMessage)
    }
  })

  it('should clear messages before making API call', async () => {
    const mockWorkItem = {
      id: 'work-item-1',
      team_id: 'team-1',
      title: 'Test Work Item',
      type: WorkItemType.STORY,
      status: 'backlog',
      priority: 1.0,
      author_id: 'user-1',
      created_at: new Date().toISOString(),
    }

    mockWorkItemService.createWorkItem.mockResolvedValue(mockWorkItem)

    const { result } = renderHook(() => useCreateWorkItem())

    // First, set some error state
    await act(async () => {
      try {
        await result.current.createWorkItem('team-1', { title: '' })
      } catch {
        // Expected error
      }
    })

    expect(result.current.error).toBeTruthy()

    // Now make a successful call - error should be cleared
    await act(async () => {
      await result.current.createWorkItem('team-1', {
        title: 'Valid Work Item',
      })
    })

    expect(result.current.error).toBe(null)
    expect(result.current.successMessage).toBeTruthy()
  })
})
