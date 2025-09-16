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
