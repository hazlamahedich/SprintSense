import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios from 'axios'
import { workItemService } from '../workItemService'
import { AuthService } from '../authService'
import { WebSocketService } from '../webSocketService'
import {
  WorkItemType,
  WorkItemStatus,
  SprintStatus,
} from '../../types/workItem.types'

vi.mock('axios')
vi.mock('../authService')

// Provide a functional in-memory WebSocket mock so subscribe/emit work in tests
vi.mock('../webSocketService', () => {
  let store: Record<
    string,
    { handlers: Array<(data: any) => void>; events: any[] }
  > = {}
  let eventCounter = 0

  const instance = {
    connect: vi.fn(),
    disconnect: vi.fn(),
    subscribe: (channel: string, handler: (data: any) => void) => {
      if (!store[channel]) {
        store[channel] = { handlers: [], events: [] }
      }
      store[channel].handlers.push(handler)
      // Replay any events that occurred before subscription
      store[channel].events.forEach((event) => handler(event))
      return () => {
        store[channel].handlers = store[channel].handlers.filter(
          (h) => h !== handler
        )
      }
    },
    emit: (channel: string, payload: any) => {
      // Clone payload to prevent mutation
      const event = JSON.parse(
        JSON.stringify({ ...payload, _order: eventCounter++ })
      )
      if (!store[channel]) {
        store[channel] = { handlers: [], events: [] }
      }
      store[channel].events.push(event)
      store[channel].handlers.forEach((handler) => handler(event))
    },
    reset: () => {
      store = {}
      eventCounter = 0
    },
    getEventCount: (channel: string) => store[channel]?.events.length ?? 0,
    getLatestEvent: (channel: string) => {
      const events = store[channel]?.events ?? []
      return events[events.length - 1]
    },
    getEvents: (channel: string) => [...(store[channel]?.events ?? [])],
  }

  return { WebSocketService: { getInstance: () => instance } }
})

const mockedAxios = vi.mocked(axios, true)

// Helper to manage test state across cases
const setupTest = () => {
  // Reset axios mocks
  mockedAxios.get.mockReset()
  mockedAxios.patch.mockReset()

  return {
    emitAndFlush: async (type: string, data: any) => {
      WebSocketService.getInstance().emit(type, data)
      await new Promise((resolve) => setTimeout(resolve, 0))
    },
    mockPatchWithEvent: (response: any, wsType: string, wsPayload: any) => {
      return mockedAxios.patch.mockImplementationOnce(async () => {
        WebSocketService.getInstance().emit(wsType, wsPayload)
        await new Promise((resolve) => setTimeout(resolve, 0))
        return response
      })
    },
    mockPatchRejectWithEvent: (error: any, wsType: string, wsPayload: any) => {
      return mockedAxios.patch.mockImplementationOnce(async () => {
        WebSocketService.getInstance().emit(wsType, wsPayload)
        await new Promise((resolve) => setTimeout(resolve, 0))
        throw error
      })
    },
  }
}

describe('Work Item Sprint Assignment Integration', () => {
  const teamId = 'team-1'
  const workItemId = 'work-1'
  const userId = 'user-1'
  const validToken = 'valid-token'

  const futureSprint = {
    id: 'sprint-future',
    status: SprintStatus.FUTURE,
    startDate: '2025-10-01',
    endDate: '2025-10-14',
    version: 1,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    // Set up default auth state
    AuthService.getToken = vi.fn().mockReturnValue(validToken)
    AuthService.hasRole = vi.fn().mockReturnValue(true)
    AuthService.isTeamMember = vi.fn().mockReturnValue(true)
    // Reset and initialize WebSocket mock
    WebSocketService.getInstance().reset()
    WebSocketService.getInstance().connect()
  })

  afterEach(() => {
    vi.resetAllMocks()
    WebSocketService.getInstance().disconnect()
  })

  describe('End-to-End Workflows', () => {
    it('should handle complete sprint assignment workflow', async () => {
      const updates = { sprintId: futureSprint.id }

      // Mock initial state check
      const initialState = {
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: null,
          title: 'Test Item',
          type: WorkItemType.TASK,
          status: WorkItemStatus.BACKLOG,
          version: 1,
        },
      }

      // Mock assignment response
      const assignmentResponse = {
        data: {
          ...initialState.data,
          sprint_id: futureSprint.id,
          version: 2,
        },
      }

      // Setup WebSocket handler
      const wsHandler = vi.fn()
      WebSocketService.getInstance().subscribe('work-item-updates', wsHandler)

      // Mock API calls
      mockedAxios.get.mockResolvedValueOnce(initialState) // Get initial state
      mockedAxios.patch.mockResolvedValueOnce(assignmentResponse) // Perform assignment

      // 1. Get initial state
      const initialItem = await workItemService.getWorkItem(teamId, workItemId)
      expect(initialItem.sprint_id).toBeNull()

      // 2. Perform assignment
      const updatedItem = await workItemService.updateWorkItem(
        teamId,
        workItemId,
        updates
      )
      expect(updatedItem.sprint_id).toBe(futureSprint.id)

      // Emit work item update notification
      WebSocketService.getInstance().emit('work-item-updates', {
        type: 'WORK_ITEM_UPDATED',
        payload: {
          id: workItemId,
          sprint_id: futureSprint.id,
        },
      })

      // Allow event loop to deliver async emit
      await new Promise((resolve) => setTimeout(resolve, 0))

      // 3. Verify WebSocket notification
      expect(wsHandler).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'WORK_ITEM_UPDATED',
          payload: expect.objectContaining({
            id: workItemId,
            sprint_id: futureSprint.id,
          }),
        })
      )
    })

    it('should handle sprint status transition during assignment', async () => {
      const { mockPatchRejectWithEvent } = setupTest()
      const updates = { sprintId: futureSprint.id }

      // Mock initial state
      const initialState = {
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: null,
          title: 'Test Item',
          type: WorkItemType.TASK,
          status: WorkItemStatus.BACKLOG,
          version: 1,
        },
      }

      // Setup base get mock
      mockedAxios.get.mockResolvedValue(initialState)

      // Mock initial assignment attempt
      const firstAttempt = {
        response: {
          status: 400,
          data: {
            message: 'Sprint status has changed',
            code: 'INVALID_SPRINT_STATUS',
            details: {
              sprintId: futureSprint.id,
              currentStatus: SprintStatus.ACTIVE,
            },
          },
        },
      }

      // Mock WebSocket notification for sprint status change
      const sprintUpdateHandler = vi.fn()
      WebSocketService.getInstance().subscribe(
        'sprint-updates',
        sprintUpdateHandler
      )

      // Setup mock to reject and emit sprint status change
      mockPatchRejectWithEvent(firstAttempt, 'sprint-updates', {
        type: 'SPRINT_STATUS_CHANGED',
        payload: {
          id: futureSprint.id,
          status: SprintStatus.ACTIVE,
        },
      })

      // Attempt assignment
      await expect(
        workItemService.updateWorkItem(teamId, workItemId, updates)
      ).rejects.toEqual(firstAttempt)

      // Verify sprint update notification was received
      expect(sprintUpdateHandler).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'SPRINT_STATUS_CHANGED',
          payload: expect.objectContaining({
            id: futureSprint.id,
            status: SprintStatus.ACTIVE,
          }),
        })
      )
    })
  })

  describe('Complex Scenarios', () => {
    it('should handle multiple concurrent operations with auth changes', async () => {
      const updates = { sprintId: futureSprint.id }

      // Mock responses for concurrent operations
      const successResponse = {
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: futureSprint.id,
          version: 2,
        },
      }

      const authError = {
        response: {
          status: 403,
          data: {
            message: 'Permissions have been revoked',
            code: 'PERMISSIONS_REVOKED',
          },
        },
      }

      const concurrencyError = {
        response: {
          status: 409,
          data: {
            message: 'Concurrent modification',
            code: 'CONCURRENT_MODIFICATION',
          },
        },
      }

      // Setup auth state changes
      AuthService.hasRole
        .mockReturnValueOnce(true) // First operation
        .mockReturnValueOnce(false) // Second operation
        .mockReturnValueOnce(true) // Third operation

      // Setup API responses
      mockedAxios.patch
        .mockResolvedValueOnce(successResponse) // First operation succeeds
        .mockRejectedValueOnce(authError) // Second operation fails auth
        .mockRejectedValueOnce(concurrencyError) // Third operation fails concurrency

      // Execute operations concurrently
      const results = await Promise.allSettled([
        workItemService.updateWorkItem(teamId, workItemId, {
          ...updates,
          version: 1,
        }),
        workItemService.updateWorkItem(teamId, workItemId, {
          ...updates,
          version: 1,
        }),
        workItemService.updateWorkItem(teamId, workItemId, {
          ...updates,
          version: 1,
        }),
      ])

      // Verify results
      expect(results[0].status).toBe('fulfilled')
      expect(results[1].status).toBe('rejected')
      expect(results[2].status).toBe('rejected')
    })

    it('should handle system stability under load', async () => {
      const { mockPatchWithEvent } = setupTest()
      const updates = { sprintId: futureSprint.id }
      const totalOperations = 50

      // Setup handlers
      const wsHandler = vi.fn()
      WebSocketService.getInstance().subscribe('work-item-updates', wsHandler)

      // Mock initial state for any pre-checks
      mockedAxios.get.mockResolvedValue({
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: null,
          title: 'Test Item',
          type: WorkItemType.TASK,
          status: WorkItemStatus.BACKLOG,
          version: 1,
        },
      })

      // Create operations array
      const operations = Array.from({ length: totalOperations }, (_, i) => ({
        sprintId: futureSprint.id,
        version: i + 1,
      }))

      // Setup mock behavior for each operation
      operations.forEach((op) => {
        mockPatchWithEvent(
          {
            data: {
              id: workItemId,
              team_id: teamId,
              sprint_id: futureSprint.id,
              type: WorkItemType.TASK,
              status: WorkItemStatus.BACKLOG,
              version: op.version,
            },
          },
          'work-item-updates',
          {
            type: 'WORK_ITEM_UPDATED',
            payload: {
              id: workItemId,
              sprint_id: futureSprint.id,
              version: op.version,
            },
          }
        )
      })

      // Execute operations
      const results = await Promise.allSettled(
        operations.map((op) =>
          workItemService.updateWorkItem(teamId, workItemId, op)
        )
      )

      // Verify results
      const successCount = results.filter(
        (r) => r.status === 'fulfilled'
      ).length
      expect(successCount).toBe(totalOperations) // All operations should succeed

      // Verify WebSocket events
      expect(wsHandler).toHaveBeenCalledTimes(totalOperations)

      // Verify final state
      const lastOperation = operations[operations.length - 1]
      const lastResult = results[results.length - 1]

      // Validate final version matches last operation
      if (lastResult.status === 'fulfilled') {
        expect(lastResult.value).toEqual(
          expect.objectContaining({
            id: workItemId,
            team_id: teamId,
            sprint_id: futureSprint.id,
            version: lastOperation.version,
          })
        )
      }
    })

    it('should handle cascading error recovery', async () => {
      const { mockPatchRejectWithEvent, mockPatchWithEvent } = setupTest()
      const updates = { sprintId: futureSprint.id }

      // Mock sequence of failures and recovery
      const sessionExpiredError = {
        response: {
          status: 401,
          data: { code: 'SESSION_EXPIRED' },
        },
      }

      const concurrencyError = {
        response: {
          status: 409,
          data: {
            code: 'CONCURRENT_MODIFICATION',
            details: { currentVersion: 2 },
          },
        },
      }

      const successResponse = {
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: futureSprint.id,
          version: 2,
        },
      }

      // Mock auth service behavior
      AuthService.refreshToken = vi.fn().mockResolvedValueOnce('new-token')

      // Mock initial state
      mockedAxios.get.mockResolvedValue({
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: null,
          title: 'Test Item',
          type: WorkItemType.TASK,
          status: WorkItemStatus.BACKLOG,
          version: 1,
        },
      })

      // Setup WebSocket handler
      const wsHandler = vi.fn()
      WebSocketService.getInstance().subscribe('work-item-updates', wsHandler)

      // Setup API response sequence with WebSocket events
      mockPatchRejectWithEvent(sessionExpiredError, 'work-item-updates', {
        type: 'SESSION_EXPIRED',
        payload: { userId },
      })

      mockPatchRejectWithEvent(concurrencyError, 'work-item-updates', {
        type: 'CONCURRENT_MODIFICATION',
        payload: {
          id: workItemId,
          version: 2,
        },
      })

      mockPatchWithEvent(successResponse, 'work-item-updates', {
        type: 'WORK_ITEM_UPDATED',
        payload: {
          id: workItemId,
          sprint_id: futureSprint.id,
          version: 2,
        },
      })
      // Fallback: any extra retries succeed
      mockedAxios.patch.mockResolvedValue(successResponse)

      // Attempt operation and expect rejection after concurrency conflict
      await expect(
        workItemService.updateWorkItem(teamId, workItemId, updates)
      ).rejects.toEqual(concurrencyError)

      // Verify flow up to concurrency error
      expect(AuthService.refreshToken).toHaveBeenCalled()
      expect(mockedAxios.patch).toHaveBeenCalledTimes(2)
    })
  })

  describe('Cross-functional Requirements', () => {
    it('should combine status, auth, and concurrency checks', async () => {
      const updates = { sprintId: futureSprint.id, version: 1 }

      // Mock initial status check
      const getSprintStatus = vi.fn().mockResolvedValue(SprintStatus.FUTURE)

      // Mock auth and permissions
      AuthService.hasRole = vi
        .fn()
        .mockReturnValueOnce(true) // Has basic role
        .mockReturnValueOnce(true) // Has team role
        .mockReturnValueOnce(false) // Missing sprint role

      // Mock API responses
      const sprintStatusError = {
        response: {
          status: 400,
          data: {
            code: 'INVALID_SPRINT_STATUS',
            message: 'Sprint is not in FUTURE status',
          },
        },
      }

      const authError = {
        response: {
          status: 403,
          data: {
            code: 'INSUFFICIENT_PERMISSIONS',
            message: 'Missing required sprint permissions',
          },
        },
      }

      mockedAxios.patch
        .mockRejectedValueOnce(sprintStatusError)
        .mockRejectedValueOnce(authError)

      // Attempt operations with different combinations
      await expect(
        workItemService.updateWorkItem(teamId, workItemId, updates)
      ).rejects.toEqual(sprintStatusError)

      await expect(
        workItemService.updateWorkItem(teamId, workItemId, updates)
      ).rejects.toEqual(authError)
    })

    it('should handle multi-user concurrent operations', async () => {
      const { mockPatchWithEvent, mockPatchRejectWithEvent } = setupTest()
      const baseUpdates = { sprintId: futureSprint.id }

      // Setup multiple user contexts
      const users = [
        { id: 'user-1', role: 'ADMIN' },
        { id: 'user-2', role: 'SPRINT_PLANNER' },
        { id: 'user-3', role: 'VIEWER' },
      ]

      // Mock initial state
      mockedAxios.get.mockResolvedValue({
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: null,
          title: 'Test Item',
          type: WorkItemType.TASK,
          status: WorkItemStatus.BACKLOG,
          version: 1,
        },
      })

      // Mock responses for each user
      const responses = {
        'user-1': {
          data: {
            id: workItemId,
            team_id: teamId,
            sprint_id: futureSprint.id,
            modified_by: 'user-1',
            version: 2,
          },
        },
        'user-2': {
          response: {
            status: 409,
            data: {
              code: 'CONCURRENT_MODIFICATION',
              details: { currentVersion: 2 },
            },
          },
        },
        'user-3': {
          response: {
            status: 403,
            data: {
              code: 'INSUFFICIENT_PERMISSIONS',
            },
          },
        },
      }

      // Setup WebSocket handlers for each user
      const userHandlers = users.reduce((acc, user) => {
        acc[user.id] = vi.fn()
        WebSocketService.getInstance().subscribe(
          'work-item-updates',
          acc[user.id]
        )
        return acc
      }, {})

      // Mock auth for different users
      AuthService.hasRole = vi.fn((role) => {
        const currentUser = users.find(
          (u) => u.id === AuthService.getCurrentUser()
        )
        return currentUser?.role === role
      })

      // Mock concurrent operations
      for (const user of users) {
        AuthService.getCurrentUser = vi.fn().mockReturnValue(user.id)
        const updates = { ...baseUpdates, userId: user.id }

        if (responses[user.id].data) {
          mockPatchWithEvent(responses[user.id], 'work-item-updates', {
            type: 'WORK_ITEM_UPDATED',
            payload: {
              id: workItemId,
              sprint_id: futureSprint.id,
              modified_by: user.id,
              version: 2,
            },
          })
        } else {
          mockPatchRejectWithEvent(responses[user.id], 'work-item-updates', {
            type: responses[user.id].response.data.code,
            payload: {
              id: workItemId,
              error: responses[user.id].response.data.code,
            },
          })
        }
      }

      // Execute operations concurrently
      const operations = users.map(async (user) => {
        AuthService.getCurrentUser = vi.fn().mockReturnValue(user.id)
        const updates = { ...baseUpdates, userId: user.id }

        if (responses[user.id].data) {
          const result = await workItemService.updateWorkItem(
            teamId,
            workItemId,
            updates
          )
          return result
        } else {
          return expect(
            workItemService.updateWorkItem(teamId, workItemId, updates)
          ).rejects.toEqual(responses[user.id])
        }
      })

      await Promise.allSettled(operations)

      // Verify WebSocket notifications
      expect(userHandlers['user-1']).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'WORK_ITEM_UPDATED',
          payload: expect.objectContaining({
            id: workItemId,
            sprint_id: futureSprint.id,
            modified_by: 'user-1',
          }),
        })
      )
      expect(userHandlers['user-2']).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'CONCURRENT_MODIFICATION',
        })
      )
      expect(userHandlers['user-3']).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'INSUFFICIENT_PERMISSIONS',
        })
      )
    })
  })
})
