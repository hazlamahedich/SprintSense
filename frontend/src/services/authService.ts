import { User } from '../types/user.types'

class AuthService {
  private static instance: AuthService
  private currentUser: User | null = null
  private token: string | null = null

  private constructor() {}

  public static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService()
    }
    return AuthService.instance
  }

  public getToken(): string | null {
    return this.token
  }

  public async refreshToken(): Promise<string> {
    // Implementation would go here
    this.token = 'new-token'
    return this.token
  }

  public getCurrentUser(): User | null {
    return this.currentUser
  }

  public hasRole(role: string): boolean {
    if (!this.currentUser?.roles) return false
    return this.currentUser.roles.includes(role)
  }

  public hasTeamRole(teamId: string, role: string): boolean {
    if (!this.currentUser?.teamRoles?.[teamId]) return false
    return this.currentUser.teamRoles[teamId].includes(role)
  }

  public isTeamMember(teamId: string): boolean {
    return Boolean(this.currentUser?.teamRoles?.[teamId])
  }

  public hasSprintPermission(sprintId: string): boolean {
    return true // Implement actual permission check
  }

  public hasOrganizationPermission(permission: string): boolean {
    return true // Implement actual permission check
  }

  public hasTemporaryRole(role: string): boolean {
    return false // Implement actual temporary role check
  }

  public isTemporaryRoleValid(): boolean {
    return true // Implement actual validation
  }

  public canDelegatePermission(): boolean {
    return true // Implement actual delegation check
  }

  public isDelegationValid(): boolean {
    return true // Implement actual validation
  }
}

export default AuthService.getInstance()
