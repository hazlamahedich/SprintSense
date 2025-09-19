/**
 * Tests for useArchiveWorkItem hook (Story 2.5)
 */

import { renderHook, act } from '@testing-library/react'
import { vi } from 'vitest'
import { useArchiveWorkItem } from '../useArchiveWorkItem'
import { workItemService } from '../../services/workItemService'
import { WorkItem, WorkItemStatus } from '../../types/workItem.types'

// Mock the workItemService module
vi.mock('../../services/workItemService', () => ({
  workItemService: {
    getWorkItem: vi.fn(),
    archiveWorkItem: vi.fn(),
  },
}))

// Get the mocked functions
const mockWorkItemService = workItemService as any

describe('useArchiveWorkItem', () => {
  const teamId = 'test-team-id'
  const workItemId = 'test-work-item-id'

  const mockWorkItem: WorkItem = {
    id: workItemId,
    team_id: teamId,
    author_id: 'author-id',
    title: 'Test Work Item',
    description: 'Test description',
    status: WorkItemStatus.BACKLOG,
    priority: 1.0,
    type: 'STORY',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  }

  const mockArchivedWorkItem: WorkItem = {
    ...mockWorkItem,
    status: WorkItemStatus.ARCHIVED,
    updated_at: '2024-01-02T00:00:00Z',
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockWorkItemService.getWorkItem.mockResolvedValue(mockWorkItem)
    mockWorkItemService.archiveWorkItem.mockResolvedValue(mockArchivedWorkItem)
  })

  it('initializes with correct default state', () => {
    const { result } = renderHook(() => useArchiveWorkItem(teamId))

    expect(result.current.isLoading).toBe(false)
    expect(result.current.error).toBe(null)
    expect(typeof result.current.archiveWorkItem).toBe('function')
    expect(typeof result.current.clearError).toBe('function')
  })

  it('successfully archives work item with optimistic update', async () => {
    const onOptimisticUpdate = vi.fn()
    const onSuccess = vi.fn()

    const { result } = renderHook(() =>
      useArchiveWorkItem(teamId, {
        onOptimisticUpdate,
        onSuccess,
      })
    )

    await act(async () => {
      await result.current.archiveWorkItem(workItemId)
    })

    // Check that optimistic update was called
    expect(onOptimisticUpdate).toHaveBeenCalledWith(workItemId, {
      ...mockWorkItem,
      status: WorkItemStatus.ARCHIVED,
      updated_at: expect.any(String),
    })

    // Check that success callback was called
    expect(onSuccess).toHaveBeenCalledWith(mockArchivedWorkItem)

    // Check final state
    expect(result.current.isLoading).toBe(false)
    expect(result.current.error).toBe(null)
  })

  it('handles archive failure with error state', async () => {
    const archiveError = new Error('Archive failed')
    mockWorkItemService.archiveWorkItem.mockRejectedValue(archiveError)

    const { result } = renderHook(() => useArchiveWorkItem(teamId))

    await act(async () => {
      try {
        await result.current.archiveWorkItem(workItemId)
      } catch (error) {
        // Expected to fail
      }
    })

    // Check final state
    expect(result.current.isLoading).toBe(false)
    expect(result.current.error).toBe('Archive failed')
  })

  it('shows loading state during archive operation', async () => {
    let resolveArchive: (value: WorkItem) => void
    const archivePromise = new Promise<WorkItem>((resolve) => {
      resolveArchive = resolve
    })

    mockWorkItemService.archiveWorkItem.mockReturnValue(archivePromise)

    const { result } = renderHook(() => useArchiveWorkItem(teamId))

    // Start archive operation
    act(() => {
      result.current.archiveWorkItem(workItemId)
    })

    // Check loading state
    expect(result.current.isLoading).toBe(true)
    expect(result.current.error).toBe(null)

    // Resolve the promise
    await act(async () => {
      resolveArchive!(mockArchivedWorkItem)
    })

    // Check final state
    expect(result.current.isLoading).toBe(false)
  })

  it('clears error when clearError is called', async () => {
    mockWorkItemService.archiveWorkItem.mockRejectedValue(
      new Error('Archive failed')
    )

    const { result } = renderHook(() => useArchiveWorkItem(teamId))

    // Create an error
    await act(async () => {
      try {
        await result.current.archiveWorkItem(workItemId)
      } catch {
        // Expected to fail
      }
    })

    expect(result.current.error).toBe('Archive failed')

    // Clear the error
    act(() => {
      result.current.clearError()
    })

    expect(result.current.error).toBe(null)
  })
})
