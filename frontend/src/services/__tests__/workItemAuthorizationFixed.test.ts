import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios from 'axios'
import { workItemService } from '../workItemService'
import { AuthService } from '../authService'
import {
  SprintStatus,
  WorkItemType,
  WorkItemStatus,
} from '../../types/workItem.types'

import { vi } from 'vitest'

vi.mock('axios')
vi.mock('../authService')

// Import mock service
import mockAuthService from '../__mocks__/authService'

const mockedAxios = vi.mocked(axios, true)
const mockedAuthService = vi.mocked(AuthService, true)

describe('Work Item Authorization', () => {
  const teamId = 'team-1'
  const workItemId = 'work-1'
  const userId = 'user-1'
  const validToken = 'valid-token'
  const expiredToken = 'expired-token'
  const futureSprint = {
    id: 'sprint-future',
    status: SprintStatus.FUTURE,
    startDate: '2025-10-01',
    endDate: '2025-10-14',
  }

  beforeEach(() => {
    vi.clearAllMocks()
    // Mock AuthService to return valid token by default
    AuthService.getToken = vi.fn().mockReturnValue(validToken)
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('Role-Based Access Control', () => {
    it('should enforce role-based access for sprint assignments', async () => {
      const updates = { sprintId: futureSprint.id }

      // Mock unauthorized user role
      AuthService.hasRole = vi.fn().mockReturnValue(false)

      const error = {
        response: {
          status: 403,
          data: {
            message:
              'User does not have required role to modify sprint assignments',
            code: 'INSUFFICIENT_ROLE',
            details: {
              requiredRole: 'SPRINT_PLANNER',
              userRoles: ['VIEWER'],
            },
          },
        },
      }

      mockedAxios.patch.mockRejectedValue(error)

      await expect(
        workItemService.updateWorkItem(teamId, workItemId, updates)
      ).rejects.toEqual(error)
    })

    it('should validate team membership for sprint assignments', async () => {
      const updates = { sprintId: futureSprint.id }

      // Mock non-team member status
      AuthService.isTeamMember = vi.fn().mockReturnValue(false)

      const error = {
        response: {
          status: 403,
          data: {
            message: 'User is not a member of the team',
            code: 'TEAM_ACCESS_DENIED',
            details: {
              teamId,
              userId,
            },
          },
        },
      }

      mockedAxios.patch.mockRejectedValue(error)

      await expect(
        workItemService.updateWorkItem(teamId, workItemId, updates)
      ).rejects.toEqual(error)
    })

    it('should validate sprint access permissions', async () => {
      const updates = { sprintId: futureSprint.id }

      // Mock insufficient sprint permissions
      AuthService.hasSprintPermission = vi.fn().mockReturnValue(false)

      const error = {
        response: {
          status: 403,
          data: {
            message: 'User does not have permission to modify this sprint',
            code: 'SPRINT_ACCESS_DENIED',
            details: {
              sprintId: futureSprint.id,
              requiredPermission: 'MODIFY',
            },
          },
        },
      }

      mockedAxios.patch.mockRejectedValue(error)

      await expect(
        workItemService.updateWorkItem(teamId, workItemId, updates)
      ).rejects.toEqual(error)
    })
  })

  describe('Session Management', () => {
    it('should handle expired sessions correctly', async () => {
      const updates = { sprintId: futureSprint.id }

      // Mock expired token
      AuthService.getToken = vi.fn().mockReturnValue(expiredToken)

      const error = {
        response: {
          status: 401,
          data: {
            message: 'Session has expired',
            code: 'SESSION_EXPIRED',
          },
        },
      }

      mockedAxios.patch.mockRejectedValue(error)

      // Verify service handles expired session
      await expect(
        workItemService.updateWorkItem(teamId, workItemId, updates)
      ).rejects.toEqual(error)

      // Verify AuthService refreshToken was called
      expect(AuthService.refreshToken).toHaveBeenCalled()
    })

    it('should retry requests with refreshed token', async () => {
      const updates = { sprintId: futureSprint.id }
      const newToken = 'refreshed-token'

      // First call fails with expired token
      mockedAxios.patch
        .mockRejectedValueOnce({
          response: {
            status: 401,
            data: { code: 'SESSION_EXPIRED' },
          },
        })
        .mockResolvedValueOnce({
          data: {
            id: workItemId,
            team_id: teamId,
            sprint_id: futureSprint.id,
          },
        })

      // Mock token refresh
      AuthService.refreshToken = vi.fn().mockResolvedValue(newToken)

      // Execute request
      await workItemService.updateWorkItem(teamId, workItemId, updates)

      // Verify token was refreshed and request was retried
      expect(AuthService.refreshToken).toHaveBeenCalled()
      expect(mockedAxios.patch).toHaveBeenCalledTimes(2)
    })

    it('should handle invalid tokens', async () => {
      const updates = { sprintId: futureSprint.id }

      // Mock invalid token
      AuthService.getToken = vi.fn().mockReturnValue('invalid-token')

      const error = {
        response: {
          status: 401,
          data: {
            message: 'Invalid authentication token',
            code: 'INVALID_TOKEN',
          },
        },
      }

      mockedAxios.patch.mockRejectedValue(error)

      await expect(
        workItemService.updateWorkItem(teamId, workItemId, updates)
      ).rejects.toEqual(error)
    })
  })

  describe('Permission Inheritance', () => {
    it('should handle inherited team admin permissions', async () => {
      const updates = { sprintId: futureSprint.id }

      // Mock team admin role
      AuthService.hasRole = vi.fn().mockReturnValue(true)
      AuthService.hasTeamRole = vi.fn().mockReturnValue(true)

      const successResponse = {
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: futureSprint.id,
          title: 'Test Item',
        },
      }

      mockedAxios.patch.mockResolvedValue(successResponse)

      const result = await workItemService.updateWorkItem(
        teamId,
        workItemId,
        updates
      )

      expect(result).toEqual(successResponse.data)
      expect(AuthService.hasTeamRole).toHaveBeenCalledWith(teamId, 'ADMIN')
    })

    it('should validate organization-level permissions', async () => {
      const updates = { sprintId: futureSprint.id }

      // Mock insufficient org permissions
      AuthService.hasOrganizationPermission = vi.fn().mockReturnValue(false)

      const error = {
        response: {
          status: 403,
          data: {
            message: 'Insufficient organization-level permissions',
            code: 'ORG_ACCESS_DENIED',
            details: {
              organizationId: 'org-1',
              requiredPermission: 'MANAGE_SPRINTS',
            },
          },
        },
      }

      mockedAxios.patch.mockRejectedValue(error)

      await expect(
        workItemService.updateWorkItem(teamId, workItemId, updates)
      ).rejects.toEqual(error)
    })
  })

  describe('Authorization Edge Cases', () => {
    it('should handle deleted user sessions', async () => {
      const updates = { sprintId: futureSprint.id }

      const error = {
        response: {
          status: 401,
          data: {
            message: 'User account has been deleted',
            code: 'USER_DELETED',
          },
        },
      }

      mockedAxios.patch.mockRejectedValue(error)

      await expect(
        workItemService.updateWorkItem(teamId, workItemId, updates)
      ).rejects.toEqual(error)
    })

    it('should handle temporary role assignments', async () => {
      const updates = { sprintId: futureSprint.id }

      // Mock temporary role assignment
      AuthService.hasTemporaryRole = vi.fn().mockReturnValue(true)
      AuthService.isTemporaryRoleValid = vi.fn().mockReturnValue(true)

      const successResponse = {
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: futureSprint.id,
          title: 'Test Item',
        },
      }

      mockedAxios.patch.mockResolvedValue(successResponse)

      const result = await workItemService.updateWorkItem(
        teamId,
        workItemId,
        updates
      )

      expect(result).toEqual(successResponse.data)
      expect(AuthService.isTemporaryRoleValid).toHaveBeenCalled()
    })

    it('should handle concurrent permission changes', async () => {
      const updates = { sprintId: futureSprint.id }

      // First call succeeds with valid permissions
      const successResponse = {
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: futureSprint.id,
        },
      }

      // Second call fails due to revoked permissions
      const error = {
        response: {
          status: 403,
          data: {
            message: 'Permissions have been revoked',
            code: 'PERMISSIONS_REVOKED',
          },
        },
      }

      mockedAxios.patch
        .mockResolvedValueOnce(successResponse)
        .mockRejectedValueOnce(error)

      // First call succeeds
      const result = await workItemService.updateWorkItem(
        teamId,
        workItemId,
        updates
      )
      expect(result).toEqual(successResponse.data)

      // Second call fails
      await expect(
        workItemService.updateWorkItem(teamId, workItemId, updates)
      ).rejects.toEqual(error)
    })

    it('should handle permission delegation', async () => {
      const updates = {
        sprintId: futureSprint.id,
        delegatedBy: 'admin-user',
      }

      // Mock delegation checks
      AuthService.canDelegatePermission = vi.fn().mockReturnValue(true)
      AuthService.isDelegationValid = vi.fn().mockReturnValue(true)

      const successResponse = {
        data: {
          id: workItemId,
          team_id: teamId,
          sprint_id: futureSprint.id,
          delegatedBy: 'admin-user',
        },
      }

      mockedAxios.patch.mockResolvedValue(successResponse)

      const result = await workItemService.updateWorkItem(
        teamId,
        workItemId,
        updates
      )

      expect(result).toEqual(successResponse.data)
      expect(AuthService.canDelegatePermission).toHaveBeenCalled()
      expect(AuthService.isDelegationValid).toHaveBeenCalled()
    })
  })
})
