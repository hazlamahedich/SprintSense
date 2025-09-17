import axios from 'axios'

// Create axios instance with base configuration
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include cookies for authentication
})

// Add request interceptor for logging (development only)
if (import.meta.env.DEV) {
  api.interceptors.request.use(
    (config) => {
      console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
      return config
    },
    (error) => {
      console.error('API Request Error:', error)
      return Promise.reject(error)
    }
  )

  api.interceptors.response.use(
    (response) => {
      console.log(`API Response: ${response.status} ${response.config.url}`)
      return response
    },
    (error) => {
      console.error(
        'API Response Error:',
        error.response?.status,
        error.message
      )
      return Promise.reject(error)
    }
  )
}

// API endpoints
export const healthApi = {
  // Basic health check
  checkHealth: async () => {
    const response = await api.get('/api/v1/health')
    return response.data
  },

  // Detailed health check with database status
  checkDetailedHealth: async () => {
    const response = await api.get('/api/v1/health/detailed')
    return response.data
  },
}

export const authApi = {
  // User login
  login: async (email: string, password: string) => {
    const response = await api.post('/api/v1/auth/login', {
      email,
      password,
    })
    return response.data
  },

  // User logout
  logout: async () => {
    const response = await api.post('/api/v1/auth/logout')
    return response.data
  },
}

export const userApi = {
  // User registration
  register: async (userData: {
    full_name: string
    email: string
    password: string
  }) => {
    const response = await api.post('/api/v1/users/register', userData)
    return response.data
  },

  // Get current user profile (placeholder for future implementation)
  getCurrentUser: async () => {
    const response = await api.get('/api/v1/users/me')
    return response.data
  },
}

export const teamsApi = {
  // Create a new team
  createTeam: async (teamData: { name: string }) => {
    const response = await api.post('/api/v1/teams/', teamData)
    return response.data
  },

  // Get teams for the current user (placeholder for future implementation)
  getUserTeams: async () => {
    const response = await api.get('/api/v1/teams/')
    return response.data
  },

  // Get team by ID (placeholder for future implementation)
  getTeam: async (teamId: string) => {
    const response = await api.get(`/api/v1/teams/${teamId}`)
    return response.data
  },
}

export const invitationsApi = {
  // Create a new team invitation
  createInvitation: async (
    teamId: string,
    invitationData: {
      email: string
      role: 'owner' | 'member'
    }
  ) => {
    const response = await api.post(
      `/api/v1/teams/${teamId}/invitations`,
      invitationData
    )
    return response.data
  },

  // Get all pending invitations for a team
  getTeamInvitations: async (teamId: string) => {
    const response = await api.get(`/api/v1/teams/${teamId}/invitations`)
    return response.data
  },
}
