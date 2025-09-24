import axios from 'axios'

// Create axios instances with base configuration
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Create Supabase-specific axios instance
export const supabaseApi = axios.create({
  baseURL: import.meta.env.VITE_SUPABASE_URL || 'http://127.0.0.1:54321',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
    'apikey': import.meta.env.VITE_SUPABASE_ANON_KEY,
  },
})

// Attach Authorization header from localStorage (E2E and app auth)
api.interceptors.request.use(
  (config) => {
    try {
      if (typeof window !== 'undefined') {
        const token = window.localStorage.getItem('access_token')
        if (token) {
          config.headers = config.headers ?? {}
          // Only set if not already set explicitly
          if (!('Authorization' in config.headers)) {
            config.headers.Authorization = `Bearer ${token}`
          }
        }
      }
    } catch (e) {
      // Ignore storage access errors in non-browser contexts
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Add request/response logging in dev
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
  // User login using Supabase
  login: async (email: string, password: string) => {
    const response = await supabaseApi.post('/auth/v1/token?grant_type=password', {
      email,
      password,
    }, {
      headers: {
        'Content-Type': 'application/json',
        'apikey': import.meta.env.VITE_SUPABASE_ANON_KEY,
        'X-Client-Info': 'sprintsense-frontend',
      }
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
