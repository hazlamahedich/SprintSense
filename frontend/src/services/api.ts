import axios from 'axios'

// Create axios instance with base configuration
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
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
      console.error('API Response Error:', error.response?.status, error.message)
      return Promise.reject(error)
    }
  )
}

// Types for API responses
export interface User {
  id: string
  email: string
  full_name: string
  created_at: string
  updated_at: string
}

export interface AuthResponse {
  user: User
  access_token: string
  token_type: string
}

export interface RegisterRequest {
  email: string
  password: string
  full_name: string
}

export interface ApiError {
  detail: string
  error_type?: string
  errors?: string[]
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
  // Register a new user
  register: async (userData: RegisterRequest): Promise<AuthResponse> => {
    const response = await api.post('/api/v1/auth/register', userData)
    return response.data
  },

  // Set authorization header for future requests
  setAuthToken: (token: string) => {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  },

  // Remove authorization header
  removeAuthToken: () => {
    delete api.defaults.headers.common['Authorization']
  },
}
