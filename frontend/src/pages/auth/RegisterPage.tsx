import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Container,
  Paper,
  InputAdornment,
  IconButton,
} from '@mui/material'
import {
  Visibility,
  VisibilityOff,
  Person,
  Email,
  Lock,
} from '@mui/icons-material'
import { authApi, ApiError } from '../../services/api'
import { useAppStore } from '../../store/appStore'

interface FormData {
  email: string
  password: string
  confirmPassword: string
  full_name: string
}

interface FormErrors {
  email?: string
  password?: string
  confirmPassword?: string
  full_name?: string
  general?: string
}

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate()
  const { setAuth, setLoading, isLoading } = useAppStore()
  
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  })
  
  const [errors, setErrors] = useState<FormErrors>({})
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid'
    }

    // Full name validation
    if (!formData.full_name.trim()) {
      newErrors.full_name = 'Full name is required'
    } else if (formData.full_name.trim().length < 2) {
      newErrors.full_name = 'Full name must be at least 2 characters'
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required'
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters'
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password'
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleInputChange = (field: keyof FormData) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }))
    
    // Clear field-specific error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }))
    }
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setLoading(true)
    setErrors({})

    try {
      const response = await authApi.register({
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name.trim(),
      })

      // Set authentication state
      setAuth(response.user, response.access_token)

      // Redirect to dashboard (or wherever authenticated users should go)
      navigate('/health') // For now, redirect to health page
      
    } catch (error: any) {
      console.error('Registration error:', error)
      
      if (error.response?.data) {
        const apiError = error.response.data as ApiError
        
        if (apiError.errors) {
          // Password validation errors
          setErrors({
            password: apiError.errors.join(', ')
          })
        } else if (apiError.error_type === 'UserAlreadyExistsError') {
          setErrors({
            email: 'An account with this email already exists'
          })
        } else {
          setErrors({
            general: apiError.detail || 'Registration failed. Please try again.'
          })
        }
      } else {
        setErrors({
          general: 'Network error. Please check your connection and try again.'
        })
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="sm">
      <Box sx={{ 
        py: 8,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}>
        <Paper elevation={3} sx={{ width: '100%', maxWidth: 400 }}>
          <Card>
            <CardContent sx={{ p: 4 }}>
              <Box sx={{ textAlign: 'center', mb: 3 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                  Join SprintSense
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Create your account to start managing sprints with AI
                </Typography>
              </Box>

              {errors.general && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {errors.general}
                </Alert>
              )}

              <Box component="form" onSubmit={handleSubmit}>
                <TextField
                  fullWidth
                  label="Full Name"
                  type="text"
                  value={formData.full_name}
                  onChange={handleInputChange('full_name')}
                  error={!!errors.full_name}
                  helperText={errors.full_name}
                  sx={{ mb: 2 }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Person color="action" />
                      </InputAdornment>
                    ),
                  }}
                  disabled={isLoading}
                />

                <TextField
                  fullWidth
                  label="Email Address"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange('email')}
                  error={!!errors.email}
                  helperText={errors.email}
                  sx={{ mb: 2 }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Email color="action" />
                      </InputAdornment>
                    ),
                  }}
                  disabled={isLoading}
                />

                <TextField
                  fullWidth
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={handleInputChange('password')}
                  error={!!errors.password}
                  helperText={errors.password}
                  sx={{ mb: 2 }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Lock color="action" />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                          disabled={isLoading}
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  disabled={isLoading}
                />

                <TextField
                  fullWidth
                  label="Confirm Password"
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={formData.confirmPassword}
                  onChange={handleInputChange('confirmPassword')}
                  error={!!errors.confirmPassword}
                  helperText={errors.confirmPassword}
                  sx={{ mb: 3 }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Lock color="action" />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                          edge="end"
                          disabled={isLoading}
                        >
                          {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  disabled={isLoading}
                />

                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={isLoading}
                  sx={{ mb: 2 }}
                >
                  {isLoading ? (
                    <CircularProgress size={24} />
                  ) : (
                    'Create Account'
                  )}
                </Button>

                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    Already have an account?{' '}
                    <Button
                      variant="text"
                      onClick={() => navigate('/login')}
                      disabled={isLoading}
                      sx={{ textTransform: 'none' }}
                    >
                      Sign In
                    </Button>
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  By creating an account, you agree to our Terms of Service and Privacy Policy.
                  Your password must contain at least 8 characters with uppercase, lowercase, numbers, and special characters.
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Paper>
      </Box>
    </Container>
  )
}