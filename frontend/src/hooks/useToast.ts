import { useCallback } from 'react'

interface ToastOptions {
  title: string
  description: string
  status: 'success' | 'error' | 'warning' | 'info'
  duration?: number
}

export const useToast = () => {
  const showToast = useCallback((options: ToastOptions) => {
    // TODO: Replace with actual toast implementation
    console.log('Toast:', options)
  }, [])

  return { showToast }
}
