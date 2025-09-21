/**
 * Tests for usePriorityUpdate hook
 * Covers Story 2.6 requirements for priority update functionality
 */

import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { usePriorityUpdate } from '../usePriorityUpdate'
import { workItemService } from '../../services/workItemService'
import { PriorityAction, WorkItem } from '../../types/workItem.types'

// Mock the workItemService
vi.mock('../../services/workItemService', () => ({
  workItemService: {
    updateWorkItemPriority: vi.fn(),
  },
}))

describe('usePriorityUpdate', () => {
  const mockWorkItem: WorkItem = {
    id: 'work-item-1',
    title: 'Test Work Item',
    description: 'Test description',
    priority: 5.0,
    type: 'STORY',
    status: 'BACKLOG',
    team_id: 'team-1',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
  }

  const mockOnSuccess = vi.fn()
  const mockOnError = vi.fn()
  const mockOnConflict = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should initialize with correct default state', () => {
    const { result } = renderHook(() =>
      usePriorityUpdate({
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        onConflict: mockOnConflict,
      })
    )

    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBe(null)
    expect(typeof result.current.updatePriority).toBe('function')
  })

  it('should set loading state during update', async () => {
    const mockPromise = new Promise((resolve) => setTimeout(resolve, 100))
    vi.mocked(workItemService.updateWorkItemPriority).mockReturnValue(
      mockPromise
    )

    const { result } = renderHook(() =>
      usePriorityUpdate({
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        onConflict: mockOnConflict,
      })
    )

    act(() => {
      result.current.updatePriority({
        workItemId: 'work-item-1',
        teamId: 'team-1',
        action: PriorityAction.MOVE_UP,
        currentPriority: 5.0,
      })
    })

    expect(result.current.loading).toBe(true)

    await act(() => mockPromise)
    expect(result.current.loading).toBe(false)
  })

  it('should call onSuccess when priority update succeeds', async () => {
    const updatedWorkItem = { ...mockWorkItem, priority: 6.0 }
    vi.mocked(workItemService.updateWorkItemPriority).mockResolvedValue(
      updatedWorkItem
    )

    const { result } = renderHook(() =>
      usePriorityUpdate({
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        onConflict: mockOnConflict,
      })
    )

    await act(async () => {
      await result.current.updatePriority({
        workItemId: 'work-item-1',
        teamId: 'team-1',
        action: PriorityAction.MOVE_UP,
        currentPriority: 5.0,
      })
    })

    expect(mockOnSuccess).toHaveBeenCalledWith(updatedWorkItem)
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBe(null)
  })

  it('should call onError when priority update fails with generic error', async () => {
    const errorMessage = 'Network error'
    vi.mocked(workItemService.updateWorkItemPriority).mockRejectedValue(
      new Error(errorMessage)
    )

    const { result } = renderHook(() =>
      usePriorityUpdate({
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        onConflict: mockOnConflict,
      })
    )

    await act(async () => {
      try {
        await result.current.updatePriority({
          workItemId: 'work-item-1',
          teamId: 'team-1',
          action: PriorityAction.MOVE_UP,
          currentPriority: 5.0,
        })
      } catch {
        // Expected to fail
      }
    })

    expect(mockOnError).toHaveBeenCalledWith('Network error')
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBe('Network error')
  })

  it('should call onConflict when priority update fails with 409 conflict', async () => {
    const conflictMessage = 'Priority has been updated by another user'
    const conflictError = {
      response: {
        status: 409,
        data: { detail: conflictMessage },
      },
    }
    vi.mocked(workItemService.updateWorkItemPriority).mockRejectedValue(
      conflictError
    )

    const { result } = renderHook(() =>
      usePriorityUpdate({
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        onConflict: mockOnConflict,
      })
    )

    await act(async () => {
      try {
        await result.current.updatePriority({
          workItemId: 'work-item-1',
          teamId: 'team-1',
          action: PriorityAction.MOVE_UP,
          currentPriority: 5.0,
        })
      } catch {
        // Expected to fail
      }
    })

    expect(mockOnConflict).toHaveBeenCalledWith(['Item priority has changed'])
    expect(result.current.loading).toBe(false)
  })

  it('should handle multiple concurrent requests correctly', async () => {
    const updatedWorkItem1 = { ...mockWorkItem, priority: 6.0 }
    const updatedWorkItem2 = {
      ...mockWorkItem,
      id: 'work-item-2',
      priority: 2.0,
    }

    vi.mocked(workItemService.updateWorkItemPriority)
      .mockResolvedValueOnce(updatedWorkItem1)
      .mockResolvedValueOnce(updatedWorkItem2)

    const { result } = renderHook(() =>
      usePriorityUpdate({
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        onConflict: mockOnConflict,
      })
    )

    // Start first request
    const firstPromise = act(async () => {
      await result.current.updatePriority({
        workItemId: 'work-item-1',
        teamId: 'team-1',
        action: PriorityAction.MOVE_UP,
        currentPriority: 5.0,
      })
    })

    // Start second request
    const secondPromise = act(async () => {
      await result.current.updatePriority({
        workItemId: 'work-item-2',
        teamId: 'team-1',
        action: PriorityAction.MOVE_DOWN,
        currentPriority: 3.0,
      })
    })

    await Promise.all([firstPromise, secondPromise])

    expect(result.current.loading).toBe(false)
    expect(mockOnSuccess).toHaveBeenCalledTimes(2)
  })

  it.skip('should clear error state on successful update', async () => {
    const { result } = renderHook(() =>
      usePriorityUpdate({
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        onConflict: mockOnConflict,
      })
    )

    // First request fails
    const errorMessage = 'Network error'
    vi.mocked(workItemService.updateWorkItemPriority).mockRejectedValueOnce(
      new Error(errorMessage)
    )

    await act(async () => {
      try {
        await result.current.updatePriority({
          workItemId: 'work-item-1',
          teamId: 'team-1',
          action: PriorityAction.MOVE_UP,
          currentPriority: 5.0,
        })
      } catch {
        // Expected to fail
      }
    })

    expect(result.current.error).toBe(errorMessage)

    // Second request succeeds
    const updatedWorkItem = { ...mockWorkItem, priority: 6.0 }
    vi.mocked(workItemService.updateWorkItemPriority).mockResolvedValueOnce(
      updatedWorkItem
    )

    await act(async () => {
      await result.current.updatePriority({
        workItemId: 'work-item-1',
        teamId: 'team-1',
        action: PriorityAction.MOVE_UP,
        currentPriority: 5.0,
      })
    })

    expect(result.current.error).toBe(null)
    expect(mockOnSuccess).toHaveBeenCalledWith(updatedWorkItem)
  })
})
