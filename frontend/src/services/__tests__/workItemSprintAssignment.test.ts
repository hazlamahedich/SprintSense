import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios from 'axios'
import { workItemService } from '../workItemService'
import {
  SprintStatus,
  WorkItemType,
  WorkItemStatus,
  SprintStatus,
} from '../../types/workItem.types'

vi.mock('axios')

const mockedAxios = vi.mocked(axios, true)

describe('Work Item Sprint Assignment', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('Sprint Status Validation', () => {
    const teamId = 'team-1'
    const workItemId = 'work-1'
    const validFutureSprint = {
      id: 'sprint-future',
      status: SprintStatus.FUTURE,
      startDate: '2025-10-01',
      endDate: '2025-10-14',
    }
    const activeSprint = {
      id: 'sprint-active',
      status: SprintStatus.ACTIVE,
      startDate: '2025-09-15',
      endDate: '2025-09-28',
    }
    const closedSprint = {
      id: 'sprint-closed',
      status: SprintStatus.CLOSED,
      startDate: '2025-09-01',
      endDate: '2025-09-14',
    }

    it('should allow assignment to a future sprint', async () => {
      const updates = { sprintId: validFutureSprint.id }
      const mockResponse = {
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: validFutureSprint.id,
          title: 'Test Item',
          type: WorkItemType.TASK,
          status: WorkItemStatus.BACKLOG,
        },
      }

      mockedAxios.patch.mockResolvedValue(mockResponse)

      const result = await workItemService.updateWorkItem(
        teamId,
        workItemId,
        updates
      )

      expect(mockedAxios.patch).toHaveBeenCalledWith(
        `/api/v1/teams/${teamId}/work-items/${workItemId}`,
        updates
      )
      expect(result).toEqual(mockResponse.data)
    })

    it('should prevent assignment to an active sprint', async () => {
      const updates = { sprintId: activeSprint.id }
      const error = {
        response: {
          status: 400,
          data: {
            message: 'Cannot assign work item to an active sprint',
            code: 'INVALID_SPRINT_STATUS',
          },
        },
      }

      mockedAxios.patch.mockRejectedValue(error)

      await expect(
        workItemService.updateWorkItem(teamId, workItemId, updates)
      ).rejects.toEqual(error)

      expect(mockedAxios.patch).toHaveBeenCalledWith(
        `/api/v1/teams/${teamId}/work-items/${workItemId}`,
        updates
      )
    })

    it('should prevent assignment to a closed sprint', async () => {
      const updates = { sprintId: closedSprint.id }
      const error = {
        response: {
          status: 400,
          data: {
            message: 'Cannot assign work item to a closed sprint',
            code: 'INVALID_SPRINT_STATUS',
          },
        },
      }

      mockedAxios.patch.mockRejectedValue(error)

      await expect(
        workItemService.updateWorkItem(teamId, workItemId, updates)
      ).rejects.toEqual(error)

      expect(mockedAxios.patch).toHaveBeenCalledWith(
        `/api/v1/teams/${teamId}/work-items/${workItemId}`,
        updates
      )
    })

    it('should handle sprint status transitions correctly', async () => {
      // First, assign to a future sprint
      const assignToFuture = { sprintId: validFutureSprint.id }
      const futureAssignmentResponse = {
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: validFutureSprint.id,
          title: 'Test Item',
          type: WorkItemType.TASK,
          status: WorkItemStatus.BACKLOG,
        },
      }

      mockedAxios.patch.mockResolvedValueOnce(futureAssignmentResponse)

      await workItemService.updateWorkItem(teamId, workItemId, assignToFuture)

      // Then try to reassign to an active sprint (should fail)
      const reassignToActive = { sprintId: activeSprint.id }
      const error = {
        response: {
          status: 400,
          data: {
            message: 'Cannot assign work item to an active sprint',
            code: 'INVALID_SPRINT_STATUS',
          },
        },
      }

      mockedAxios.patch.mockRejectedValueOnce(error)

      await expect(
        workItemService.updateWorkItem(teamId, workItemId, reassignToActive)
      ).rejects.toEqual(error)

      expect(mockedAxios.patch).toHaveBeenCalledTimes(2)
    })

    it('should provide descriptive error messages for invalid assignments', async () => {
      const updates = { sprintId: activeSprint.id }
      const error = {
        response: {
          status: 400,
          data: {
            message:
              'Cannot assign work item to an active sprint. Work items can only be assigned to sprints with FUTURE status.',
            code: 'INVALID_SPRINT_STATUS',
            details: {
              allowedStatuses: ['FUTURE'],
              currentStatus: 'ACTIVE',
            },
          },
        },
      }

      mockedAxios.patch.mockRejectedValue(error)

      try {
        await workItemService.updateWorkItem(teamId, workItemId, updates)
      } catch (e) {
        expect(e.response.data).toMatchObject({
          message: expect.stringContaining('Cannot assign work item'),
          code: 'INVALID_SPRINT_STATUS',
          details: expect.objectContaining({
            allowedStatuses: expect.arrayContaining(['FUTURE']),
          }),
        })
      }
    })

    it('should handle reassignment between future sprints', async () => {
      const anotherFutureSprint = {
        id: 'sprint-future-2',
        status: SprintStatus.FUTURE,
        startDate: '2025-10-15',
        endDate: '2025-10-28',
      }

      // First assignment
      const firstAssignment = { sprintId: validFutureSprint.id }
      const firstResponse = {
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: validFutureSprint.id,
          title: 'Test Item',
        },
      }

      // Second assignment
      const secondAssignment = { sprintId: anotherFutureSprint.id }
      const secondResponse = {
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: anotherFutureSprint.id,
          title: 'Test Item',
        },
      }

      mockedAxios.patch
        .mockResolvedValueOnce(firstResponse)
        .mockResolvedValueOnce(secondResponse)

      // Perform first assignment
      await workItemService.updateWorkItem(teamId, workItemId, firstAssignment)
      expect(mockedAxios.patch).toHaveBeenCalledWith(
        `/api/v1/teams/${teamId}/work-items/${workItemId}`,
        firstAssignment
      )

      // Perform reassignment
      const result = await workItemService.updateWorkItem(
        teamId,
        workItemId,
        secondAssignment
      )
      expect(mockedAxios.patch).toHaveBeenCalledWith(
        `/api/v1/teams/${teamId}/work-items/${workItemId}`,
        secondAssignment
      )
      expect(result).toEqual(secondResponse.data)
    })
  })

  describe('Stale Data Handling', () => {
    const teamId = 'team-1'
    const workItemId = 'work-1'
    const futureSprint = {
      id: 'sprint-future',
      status: SprintStatus.FUTURE,
      startDate: '2025-10-01',
      endDate: '2025-10-14',
      version: 1,
    }

    it('should detect concurrent modifications', async () => {
      const updates = {
        sprintId: futureSprint.id,
        version: 1, // Current version
      }
      const error = {
        response: {
          status: 409,
          data: {
            message: 'Work item has been modified by another user',
            code: 'CONCURRENT_MODIFICATION',
            details: {
              currentVersion: 2,
              providedVersion: 1,
            },
          },
        },
      }

      mockedAxios.patch.mockRejectedValue(error)

      await expect(
        workItemService.updateWorkItem(teamId, workItemId, updates)
      ).rejects.toEqual(error)

      expect(mockedAxios.patch).toHaveBeenCalledWith(
        `/api/v1/teams/${teamId}/work-items/${workItemId}`,
        updates
      )
    })

    it('should handle outdated sprint references', async () => {
      const updates = { sprintId: 'deleted-sprint-id' }
      const error = {
        response: {
          status: 400,
          data: {
            message: 'Referenced sprint no longer exists',
            code: 'INVALID_SPRINT_REFERENCE',
            details: {
              sprintId: 'deleted-sprint-id',
            },
          },
        },
      }

      mockedAxios.patch.mockRejectedValue(error)

      await expect(
        workItemService.updateWorkItem(teamId, workItemId, updates)
      ).rejects.toEqual(error)
    })

    it('should resolve conflicts in work item assignments', async () => {
      // Service now retries on concurrency error; simulate: first 409 then success
      const updates = { sprintId: futureSprint.id, version: 1 }
      const concurrencyError = {
        response: {
          status: 409,
          data: {
            message: 'Work item has been modified',
            code: 'CONCURRENT_MODIFICATION',
            details: {
              currentVersion: 2,
              providedVersion: 1,
            },
          },
        },
      }

      const successResponse = {
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: futureSprint.id,
          version: 3,
          title: 'Test Item',
        },
      }

      mockedAxios.patch
        .mockRejectedValueOnce(concurrencyError)
        .mockResolvedValueOnce(successResponse)

      // Single call should internally retry and succeed
      const result = await workItemService.updateWorkItem(
        teamId,
        workItemId,
        updates
      )

      expect(result).toEqual(successResponse.data)
      expect(mockedAxios.patch).toHaveBeenCalledTimes(2)
      expect(mockedAxios.patch).toHaveBeenNthCalledWith(
        1,
        `/api/v1/teams/${teamId}/work-items/${workItemId}`,
        updates
      )
    })

    it('should maintain data consistency during concurrent operations', async () => {
      // With automatic retry, one operation may succeed after conflict
      const update1 = { sprintId: futureSprint.id, version: 1 }
      const update2 = { sprintId: 'sprint-future-2', version: 1 }

      const response1 = {
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: futureSprint.id,
          version: 2,
          title: 'Test Item',
        },
      }

      const retrySuccessForSecond = {
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: 'sprint-future-2',
          version: 2,
          title: 'Test Item',
        },
      }

      const concurrencyError = {
        response: {
          status: 409,
          data: {
            message: 'Work item has been modified',
            code: 'CONCURRENT_MODIFICATION',
            details: {
              currentVersion: 2,
              providedVersion: 1,
            },
          },
        },
      }

      // First operation succeeds immediately
      mockedAxios.patch.mockResolvedValueOnce(response1)
      // Second operation: first 409, then success after retry
      mockedAxios.patch
        .mockRejectedValueOnce(concurrencyError)
        .mockResolvedValueOnce(retrySuccessForSecond)

      // Execute operations in parallel
      const results = await Promise.allSettled([
        workItemService.updateWorkItem(teamId, workItemId, update1),
        workItemService.updateWorkItem(teamId, workItemId, update2),
      ])

      // Verify both operations succeeded eventually
      expect(results[0].status).toBe('fulfilled')
      expect(results[1].status).toBe('fulfilled')
      if (results[0].status === 'fulfilled') {
        expect(results[0].value).toEqual(response1.data)
      }
      if (results[1].status === 'fulfilled') {
        expect(results[1].value).toEqual(retrySuccessForSecond.data)
      }

      // Total calls: 1 for first op + 2 for second op (retry) = 3
      expect(mockedAxios.patch).toHaveBeenCalledTimes(3)
    })

    it('should handle race conditions in sprint status changes', async () => {
      // Attempt to assign to a sprint that was future but becomes active
      const updates = { sprintId: futureSprint.id }
      const error = {
        response: {
          status: 400,
          data: {
            message:
              'Sprint status has changed. Can only assign to FUTURE sprints.',
            code: 'INVALID_SPRINT_STATUS',
            details: {
              expectedStatus: SprintStatus.FUTURE,
              actualStatus: SprintStatus.ACTIVE,
            },
          },
        },
      }

      mockedAxios.patch.mockRejectedValue(error)

      await expect(
        workItemService.updateWorkItem(teamId, workItemId, updates)
      ).rejects.toEqual(error)

      expect(mockedAxios.patch).toHaveBeenCalledWith(
        `/api/v1/teams/${teamId}/work-items/${workItemId}`,
        updates
      )
    })
  })
})
