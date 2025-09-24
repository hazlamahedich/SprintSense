import { vi } from 'vitest'

const mockAuthService = {
  getToken: vi.fn(),
  refreshToken: vi.fn(),
  getCurrentUser: vi.fn(),
  hasRole: vi.fn(),
  hasTeamRole: vi.fn(),
  isTeamMember: vi.fn(),
  hasSprintPermission: vi.fn(),
  hasOrganizationPermission: vi.fn(),
  hasTemporaryRole: vi.fn(),
  isTemporaryRoleValid: vi.fn(),
  canDelegatePermission: vi.fn(),
  isDelegationValid: vi.fn(),
}

// Setup default implementations
vi.spyOn(mockAuthService, 'getToken').mockImplementation(
  () => undefined as unknown as string
)
vi.spyOn(mockAuthService, 'refreshToken').mockImplementation(
  async () => undefined as unknown as string
)
vi.spyOn(mockAuthService, 'getCurrentUser').mockImplementation(
  () => undefined as unknown as string
)
vi.spyOn(mockAuthService, 'hasRole').mockImplementation(() => false)
vi.spyOn(mockAuthService, 'hasTeamRole').mockImplementation(() => false)
vi.spyOn(mockAuthService, 'isTeamMember').mockImplementation(() => false)
vi.spyOn(mockAuthService, 'hasSprintPermission').mockImplementation(() => false)
vi.spyOn(mockAuthService, 'hasOrganizationPermission').mockImplementation(
  () => false
)
vi.spyOn(mockAuthService, 'hasTemporaryRole').mockImplementation(() => false)
vi.spyOn(mockAuthService, 'isTemporaryRoleValid').mockImplementation(
  () => false
)
vi.spyOn(mockAuthService, 'canDelegatePermission').mockImplementation(
  () => false
)
vi.spyOn(mockAuthService, 'isDelegationValid').mockImplementation(() => false)

const AuthService = mockAuthService
export { AuthService }
export default mockAuthService
