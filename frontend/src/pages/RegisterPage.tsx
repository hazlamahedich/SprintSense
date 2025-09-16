import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm, Controller } from 'react-hook-form'
import { yupResolver } from '@hookform/resolvers/yup'
import * as yup from 'yup'
import {
  Box,
  Card,
  CardContent,
  Container,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Paper,
  Divider,
  IconButton,
  InputAdornment,
} from '@mui/material'
import {
  Visibility,
  VisibilityOff,
  AccountCircle,
  Email,
  Lock,
  PersonAdd,
} from '@mui/icons-material'
import { userApi } from '../services/api'
import { useAppStore } from '../store/appStore'

// Validation schema using yup
const registrationSchema = yup.object().shape({
  full_name: yup
    .string()
    .required('Full name is required')
    .min(2, 'Full name must be at least 2 characters')
    .max(100, 'Full name must be less than 100 characters')
    .matches(
      /^[a-zA-Z\s\u00C0-\u017F\u4e00-\u9fff]*$/,
      'Full name can only contain letters, spaces, and accented characters'
    ),
  email: yup
    .string()
    .required('Email is required')
    .email('Please enter a valid email address')
    .max(255, 'Email must be less than 255 characters'),
  password: yup
    .string()
    .required('Password is required')
    .min(8, 'Password must be at least 8 characters')
    .matches(
      /^(?=.*[a-z])/,
      'Password must contain at least one lowercase letter'
    )
    .matches(
      /^(?=.*[A-Z])/,
      'Password must contain at least one uppercase letter'
    )
    .matches(/^(?=.*\d)/, 'Password must contain at least one number'),
  confirmPassword: yup
    .string()
    .required('Please confirm your password')
    .oneOf([yup.ref('password')], 'Passwords must match'),
})

type RegistrationFormData = yup.InferType<typeof registrationSchema>

interface RegistrationResponse {
  message: string
  user: {
    id: string
    email: string
    full_name: string
    is_active: boolean
    created_at: string
  }
  access_token: string
  token_type: string
}

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate()
  const { setError: setGlobalError, setUser, setAccessToken } = useAppStore()

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const {
    control,
    handleSubmit,
    formState: { errors, isValid },
    setError: setFormError,
  } = useForm<RegistrationFormData>({
    resolver: yupResolver(registrationSchema),
    mode: 'onChange',
    defaultValues: {
      full_name: '',
      email: '',
      password: '',
      confirmPassword: '',
    },
  })

  const onSubmit = async (data: RegistrationFormData) => {
    try {
      setLoading(true)
      setError(null)
      setGlobalError(null)

      // Remove confirmPassword before sending to API
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { confirmPassword, ...registrationData } = data

      const response = await userApi.register(registrationData)
      const result = response as RegistrationResponse

      // Update Zustand store with user data and token
      setUser(result.user)
      setAccessToken(result.access_token)

      // Navigate to dashboard (placeholder for now)
      navigate('/dashboard', { replace: true })
    } catch (err: unknown) {
      console.error('Registration error:', err)
      const error = err as {
        response?: { status?: number; data?: { detail?: string } }
        message?: string
      }

      if (error.response?.status === 409) {
        // Email already exists
        setFormError('email', {
          type: 'manual',
          message: 'This email address is already registered',
        })
      } else if (error.response?.status === 422) {
        // Validation errors from backend
        const errorMessage =
          error.response?.data?.detail ||
          'Please check your input and try again'
        setError(errorMessage)
      } else {
        // General error
        const errorMessage =
          error.response?.data?.detail ||
          error.message ||
          'Registration failed. Please try again.'
        setError(errorMessage)
      }
    } finally {
      setLoading(false)
    }
  }

  const handlePasswordVisibilityToggle = (
    field: 'password' | 'confirmPassword'
  ) => {
    if (field === 'password') {
      setShowPassword(!showPassword)
    } else {
      setShowConfirmPassword(!showConfirmPassword)
    }
  }

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          py: 4,
        }}
      >
        <Paper
          elevation={8}
          sx={{
            width: '100%',
            maxWidth: 480,
            borderRadius: 3,
            overflow: 'hidden',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          }}
        >
          <Box sx={{ p: 1 }}>
            <Card sx={{ borderRadius: 2 }}>
              <CardContent sx={{ p: 4 }}>
                {/* Header */}
                <Box sx={{ textAlign: 'center', mb: 3 }}>
                  <PersonAdd
                    sx={{
                      fontSize: 48,
                      color: 'primary.main',
                      mb: 1,
                    }}
                  />
                  <Typography variant="h4" component="h1" gutterBottom>
                    Create Account
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    Join SprintSense to get started
                  </Typography>
                </Box>

                <Divider sx={{ mb: 3 }} />

                {/* Error Alert */}
                {error && (
                  <Alert
                    severity="error"
                    sx={{ mb: 3 }}
                    onClose={() => setError(null)}
                  >
                    {error}
                  </Alert>
                )}

                {/* Registration Form */}
                <Box
                  component="form"
                  data-testid="registration-form"
                  onSubmit={handleSubmit(onSubmit)}
                >
                  {/* Full Name Field */}
                  <Controller
                    name="full_name"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="Full Name"
                        variant="outlined"
                        margin="normal"
                        error={!!errors.full_name}
                        helperText={errors.full_name?.message}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <AccountCircle color="action" />
                            </InputAdornment>
                          ),
                        }}
                        sx={{ mb: 2 }}
                      />
                    )}
                  />

                  {/* Email Field */}
                  <Controller
                    name="email"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="Email Address"
                        type="email"
                        variant="outlined"
                        margin="normal"
                        error={!!errors.email}
                        helperText={errors.email?.message}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Email color="action" />
                            </InputAdornment>
                          ),
                        }}
                        sx={{ mb: 2 }}
                      />
                    )}
                  />

                  {/* Password Field */}
                  <Controller
                    name="password"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="Password"
                        type={showPassword ? 'text' : 'password'}
                        variant="outlined"
                        margin="normal"
                        error={!!errors.password}
                        helperText={errors.password?.message}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Lock color="action" />
                            </InputAdornment>
                          ),
                          endAdornment: (
                            <InputAdornment position="end">
                              <IconButton
                                onClick={() =>
                                  handlePasswordVisibilityToggle('password')
                                }
                                edge="end"
                                aria-label="toggle password visibility"
                              >
                                {showPassword ? (
                                  <VisibilityOff />
                                ) : (
                                  <Visibility />
                                )}
                              </IconButton>
                            </InputAdornment>
                          ),
                        }}
                        sx={{ mb: 2 }}
                      />
                    )}
                  />

                  {/* Confirm Password Field */}
                  <Controller
                    name="confirmPassword"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="Confirm Password"
                        type={showConfirmPassword ? 'text' : 'password'}
                        variant="outlined"
                        margin="normal"
                        error={!!errors.confirmPassword}
                        helperText={errors.confirmPassword?.message}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Lock color="action" />
                            </InputAdornment>
                          ),
                          endAdornment: (
                            <InputAdornment position="end">
                              <IconButton
                                onClick={() =>
                                  handlePasswordVisibilityToggle(
                                    'confirmPassword'
                                  )
                                }
                                edge="end"
                                aria-label="toggle confirm password visibility"
                              >
                                {showConfirmPassword ? (
                                  <VisibilityOff />
                                ) : (
                                  <Visibility />
                                )}
                              </IconButton>
                            </InputAdornment>
                          ),
                        }}
                        sx={{ mb: 3 }}
                      />
                    )}
                  />

                  {/* Submit Button */}
                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    size="large"
                    disabled={loading || !isValid}
                    startIcon={
                      loading ? <CircularProgress size={20} /> : <PersonAdd />
                    }
                    sx={{
                      py: 1.5,
                      fontSize: '1.1rem',
                      fontWeight: 600,
                      background:
                        'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                      boxShadow: '0 3px 5px 2px rgba(102, 126, 234, .3)',
                      '&:hover': {
                        background:
                          'linear-gradient(45deg, #5a67d8 30%, #6b46c1 90%)',
                        boxShadow: '0 6px 10px 4px rgba(102, 126, 234, .3)',
                      },
                      '&:disabled': {
                        background:
                          'linear-gradient(45deg, #cbd5e0 30%, #a0aec0 90%)',
                        boxShadow: 'none',
                      },
                    }}
                  >
                    {loading ? 'Creating Account...' : 'Create Account'}
                  </Button>
                </Box>

                {/* Sign In Link */}
                <Box sx={{ mt: 3, textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    Already have an account?{' '}
                    <Link
                      to="/login"
                      style={{
                        color: '#667eea',
                        textDecoration: 'none',
                        fontWeight: 600,
                      }}
                    >
                      Sign in here
                    </Link>
                  </Typography>
                </Box>

                {/* Password Requirements */}
                <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    display="block"
                  >
                    Password requirements:
                  </Typography>
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    display="block"
                  >
                    • At least 8 characters long
                  </Typography>
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    display="block"
                  >
                    • Contains uppercase and lowercase letters
                  </Typography>
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    display="block"
                  >
                    • Contains at least one number
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Box>
        </Paper>
      </Box>
    </Container>
  )
}
