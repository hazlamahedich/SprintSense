import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { User, authApi } from '../services/api'

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
  
  // Authentication state
  user: User | null
  accessToken: string | null
  isAuthenticated: boolean
  
  // Actions
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setHealthStatus: (status: AppState['healthStatus']) => void
  
  // Auth actions
  setAuth: (user: User, token: string) => void
  clearAuth: () => void
  initializeAuth: () => void
}

export const useAppStore = create<AppState>()(persist(
  (set, get) => ({
    // Initial state
    isLoading: false,
    error: null,
    healthStatus: null,
    user: null,
    accessToken: null,
    isAuthenticated: false,
    
    // Actions
    setLoading: (loading) => set({ isLoading: loading }),
    setError: (error) => set({ error }),
    setHealthStatus: (status) => set({ 
      healthStatus: status 
        ? { ...status, lastChecked: new Date() }
        : null 
    }),
    
    // Auth actions
    setAuth: (user, token) => {
      // Set the auth token for API calls
      authApi.setAuthToken(token)
      
      set({ 
        user,
        accessToken: token,
        isAuthenticated: true,
        error: null
      })
    },
    
    clearAuth: () => {
      // Remove the auth token from API calls
      authApi.removeAuthToken()
      
      set({
        user: null,
        accessToken: null,
        isAuthenticated: false
      })
    },
    
    initializeAuth: () => {
      const state = get()
      if (state.accessToken && state.user) {
        // Set the auth token for API calls on app initialization
        authApi.setAuthToken(state.accessToken)
        set({ isAuthenticated: true })
      }
    }
  }),
  {
    name: 'sprintsense-auth', // Storage key
    partialize: (state) => ({ 
      // Only persist authentication-related state
      user: state.user,
      accessToken: state.accessToken
    })
  }
))
