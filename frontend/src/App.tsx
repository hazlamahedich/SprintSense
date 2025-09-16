import React, { useEffect } from 'react'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { HealthPage } from './pages/HealthPage'
import { RegisterPage } from './pages/auth/RegisterPage'
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { useAppStore } from './store/appStore'

// Create Material-UI theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    h4: {
      fontWeight: 600,
    },
  },
})

function App() {
  const { initializeAuth } = useAppStore()
  
  // Initialize authentication on app startup
  useEffect(() => {
    initializeAuth()
  }, [])
  
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          {/* Protected routes - require authentication */}
          <Route path="/health" element={
            <ProtectedRoute>
              <HealthPage />
            </ProtectedRoute>
          } />
          
          {/* Public routes - no authentication required */}
          <Route path="/register" element={<RegisterPage />} />
          
          {/* Default route - redirect based on auth status */}
          <Route path="/" element={<Navigate to="/health" replace />} />
        </Routes>
      </Router>
    </ThemeProvider>
  )
}

export default App
