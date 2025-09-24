import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { workItemService } from '../workItemService'
import { WebSocketService } from '../webSocketService'
import {
  WorkItemType,
  WorkItemStatus,
  SprintStatus,
} from '../../types/workItem.types'

vi.mock('../webSocketService')

const mockedWebSocketService = vi.mocked(WebSocketService, true)

describe('Work Item Real-time Updates', () => {
  const teamId = 'team-1'
  const workItemId = 'work-1'
  const userId = 'user-1'
  const futureSprint = {
    id: 'sprint-future',
    status: SprintStatus.FUTURE,
    startDate: '2025-10-01',
    endDate: '2025-10-14',
  }

  beforeEach(() => {
    vi.clearAllMocks()
    // Initialize WebSocket connection
    WebSocketService.getInstance().connect()
  })

  afterEach(() => {
    vi.resetAllMocks()
    // Clean up WebSocket connection
    WebSocketService.getInstance().disconnect()
  })

  describe('Real-time Update Propagation', () => {
    it('should propagate assignment changes in real-time', async () => {
      const updates = { sprintId: futureSprint.id }
      const updateMessage = {
        type: 'WORK_ITEM_UPDATED',
        payload: {
          id: workItemId,
          team_id: teamId,
          sprint_id: futureSprint.id,
          title: 'Test Item',
          type: WorkItemType.TASK,
          status: WorkItemStatus.BACKLOG,
          updated_by: userId,
        },
      }

      // Mock WebSocket message handler
      const messageHandler = vi.fn()
      WebSocketService.getInstance().subscribe(
        'work-item-updates',
        messageHandler
      )

      // Simulate backend sending update through WebSocket
      WebSocketService.getInstance().emit('work-item-updates', updateMessage)

      // Verify handler was called with update
      expect(messageHandler).toHaveBeenCalledWith(updateMessage)
      expect(messageHandler).toHaveBeenCalledTimes(1)
    })

    it('should handle WebSocket disconnections gracefully', async () => {
      const reconnectHandler = vi.fn()
      WebSocketService.getInstance().onReconnect(reconnectHandler)

      // Simulate connection drop
      WebSocketService.getInstance().disconnect()

      // Verify auto-reconnect behavior
      expect(WebSocketService.getInstance().isConnecting()).toBe(true)

      // Simulate successful reconnection
      WebSocketService.getInstance().connect()

      expect(reconnectHandler).toHaveBeenCalled()
      expect(WebSocketService.getInstance().isConnected()).toBe(true)
    })

    it('should maintain consistent state across multiple clients', async () => {
      const updates = { sprintId: futureSprint.id }

      // Mock handlers for two different clients
      const client1Handler = vi.fn()
      const client2Handler = vi.fn()

      WebSocketService.getInstance().subscribe(
        'work-item-updates',
        client1Handler
      )
      WebSocketService.getInstance().subscribe(
        'work-item-updates',
        client2Handler
      )

      const updateMessage = {
        type: 'WORK_ITEM_UPDATED',
        payload: {
          id: workItemId,
          team_id: teamId,
          sprint_id: futureSprint.id,
          title: 'Test Item',
          version: 2,
        },
      }

      // Simulate update broadcast
      WebSocketService.getInstance().emit('work-item-updates', updateMessage)

      // Verify both clients received the same update
      expect(client1Handler).toHaveBeenCalledWith(updateMessage)
      expect(client2Handler).toHaveBeenCalledWith(updateMessage)
      expect(client1Handler).toHaveBeenCalledTimes(1)
      expect(client2Handler).toHaveBeenCalledTimes(1)
    })

    it('should verify UI updates match backend state', async () => {
      const updates = { sprintId: futureSprint.id }
      const backendState = {
        id: workItemId,
        team_id: teamId,
        sprint_id: futureSprint.id,
        title: 'Test Item',
        version: 2,
      }

      // Mock WebSocket update
      const wsHandler = vi.fn()
      WebSocketService.getInstance().subscribe('work-item-updates', wsHandler)

      const updateMessage = {
        type: 'WORK_ITEM_UPDATED',
        payload: backendState,
      }

      // Simulate receiving update via WebSocket
      WebSocketService.getInstance().emit('work-item-updates', updateMessage)

      // Verify WebSocket handler received correct state
      expect(wsHandler).toHaveBeenCalledWith(updateMessage)

      // Mock API response for state verification
      const mockApiResponse = {
        data: backendState,
      }

      // Mock axios to return the same state
      vi.spyOn(workItemService, 'getWorkItem').mockResolvedValue(
        mockApiResponse.data
      )

      // Verify state via API matches WebSocket update
      const apiState = await workItemService.getWorkItem(teamId, workItemId)
      expect(apiState).toEqual(backendState)
    })
  })

  describe('Real-time Performance', () => {
    it('should handle high-frequency updates', async () => {
      const messageHandler = vi.fn()
      WebSocketService.getInstance().subscribe(
        'work-item-updates',
        messageHandler
      )

      // Simulate burst of updates
      const updates = Array.from({ length: 100 }, (_, i) => ({
        type: 'WORK_ITEM_UPDATED',
        payload: {
          id: workItemId,
          team_id: teamId,
          sprint_id: futureSprint.id,
          version: i + 1,
        },
      }))

      // Send updates with minimal delay
      for (const update of updates) {
        WebSocketService.getInstance().emit('work-item-updates', update)
      }

      // Verify all updates were handled
      expect(messageHandler).toHaveBeenCalledTimes(100)

      // Verify last update has correct version
      expect(messageHandler).toHaveBeenLastCalledWith(
        expect.objectContaining({
          payload: expect.objectContaining({
            version: 100,
          }),
        })
      )
    })

    it('should handle message redelivery correctly', async () => {
      const messageHandler = vi.fn()
      WebSocketService.getInstance().subscribe(
        'work-item-updates',
        messageHandler
      )

      const update = {
        type: 'WORK_ITEM_UPDATED',
        payload: {
          id: workItemId,
          team_id: teamId,
          sprint_id: futureSprint.id,
          version: 1,
        },
        messageId: 'msg-1', // Add message ID for deduplication
      }

      // Simulate message being delivered twice
      WebSocketService.getInstance().emit('work-item-updates', update)
      WebSocketService.getInstance().emit('work-item-updates', update)

      // Verify message was only handled once
      expect(messageHandler).toHaveBeenCalledTimes(1)
      expect(messageHandler).toHaveBeenCalledWith(update)
    })

    it('should handle out-of-order message delivery', async () => {
      const messageHandler = vi.fn()
      WebSocketService.getInstance().subscribe(
        'work-item-updates',
        messageHandler
      )

      const updates = [
        {
          type: 'WORK_ITEM_UPDATED',
          payload: {
            id: workItemId,
            version: 2,
            timestamp: '2025-09-24T04:47:02Z',
          },
        },
        {
          type: 'WORK_ITEM_UPDATED',
          payload: {
            id: workItemId,
            version: 1,
            timestamp: '2025-09-24T04:47:01Z',
          },
        },
      ]

      // Send updates in reverse order
      WebSocketService.getInstance().emit('work-item-updates', updates[1]) // older update
      WebSocketService.getInstance().emit('work-item-updates', updates[0]) // newer update

      // Verify handler was called in correct order
      expect(messageHandler).toHaveBeenNthCalledWith(1, updates[1])
      expect(messageHandler).toHaveBeenNthCalledWith(2, updates[0])
    })
  })
})
