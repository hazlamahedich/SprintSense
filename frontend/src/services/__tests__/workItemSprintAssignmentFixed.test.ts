import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios from 'axios'
import { workItemService } from '../workItemService'
import {
  SprintStatus,
  WorkItemType,
  WorkItemStatus,
} from '../../types/workItem.types'

import { vi } from 'vitest'

vi.mock('axios')

const mockedAxios = vi.mocked(axios, true)

describe('Work Item Sprint Assignment', () => {
  const teamId = 'team-1'
  const workItemId = 'work-1'
  const futureSprint = {
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

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('Sprint Status Validation', () => {
    it('should allow assignment to a future sprint', async () => {
      const updates = { sprintId: futureSprint.id }
      const mockResponse = {
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: futureSprint.id,
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
      const assignToFuture = { sprintId: futureSprint.id }
      const futureAssignmentResponse = {
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: futureSprint.id,
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
      const firstAssignment = { sprintId: futureSprint.id }
      const firstResponse = {
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: futureSprint.id,
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
})
