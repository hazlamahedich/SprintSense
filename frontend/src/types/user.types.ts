export interface User {
  id: string
  email: string
  name: string
  roles: string[]
  teamRoles: {
    [teamId: string]: string[]
  }
}

export interface UserProfile extends User {
  avatar: string
  bio: string
  preferences: {
    theme: string
    notifications: {
      email: boolean
      push: boolean
    }
  }
}

export interface TeamRole {
  teamId: string
  role: string
}
