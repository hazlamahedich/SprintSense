import { create } from 'zustand'

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
  
  // Actions
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setHealthStatus: (status: AppState['healthStatus']) => void
}

export const useAppStore = create<AppState>((set) => ({
  // Initial state
  isLoading: false,
  error: null,
  healthStatus: null,
  
  // Actions
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  setHealthStatus: (status) => set({ 
    healthStatus: status 
      ? { ...status, lastChecked: new Date() }
      : null 
  }),
}))