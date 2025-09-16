import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAppStore } from '../../store/appStore'
import { CircularProgress, Box } from '@mui/material'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAppStore()
  const location = useLocation()

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    )
  }

  // If not authenticated, redirect to register page with return path
  if (!isAuthenticated) {
    return (
      <Navigate 
        to="/register" 
        state={{ from: location }} 
        replace 
      />
    )
  }

  // If authenticated, render the protected component
  return <>{children}</>
}