import { create } from 'zustand'

interface User {
  id: string
  email: string
  full_name: string
  is_active: boolean
  created_at: string
}

interface AppState {
  // App-wide state
  isLoading: boolean
  error: string | null

  // Health status
  healthStatus: {
    status: string
    service: string
    lastChecked?: Date
  } | null

  // User state
  user: User | null
  isAuthenticated: boolean
  accessToken: string | null

  // Actions
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setHealthStatus: (status: AppState['healthStatus']) => void
  setUser: (user: User | null) => void
  setAccessToken: (token: string | null) => void
  logout: () => void
}

export const useAppStore = create<AppState>((set, get) => {
  // Initialize from localStorage on startup
  const initializeAuth = () => {
    try {
      const token = localStorage.getItem('access_token')
      const userStr = localStorage.getItem('user')
      const user = userStr ? JSON.parse(userStr) : null

      return {
        accessToken: token,
        user,
        isAuthenticated: !!(token && user),
      }
    } catch {
      // Clear corrupted data
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      return {
        accessToken: null,
        user: null,
        isAuthenticated: false,
      }
    }
  }

  const authState = initializeAuth()

  return {
    // Initial state
    isLoading: false,
    error: null,
    healthStatus: null,

    // Auth state
    ...authState,

    // Actions
    setLoading: (loading) => set({ isLoading: loading }),
    setError: (error) => set({ error }),
    setHealthStatus: (status) =>
      set({
        healthStatus: status ? { ...status, lastChecked: new Date() } : null,
      }),

    setUser: (user) => {
      if (user) {
        localStorage.setItem('user', JSON.stringify(user))
      } else {
        localStorage.removeItem('user')
      }
      set({
        user,
        isAuthenticated: !!(user && get().accessToken),
      })
    },

    setAccessToken: (token) => {
      if (token) {
        localStorage.setItem('access_token', token)
      } else {
        localStorage.removeItem('access_token')
      }
      set({
        accessToken: token,
        isAuthenticated: !!(token && get().user),
      })
    },

    logout: () => {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      set({
        user: null,
        accessToken: null,
        isAuthenticated: false,
      })
    },
  }
})
