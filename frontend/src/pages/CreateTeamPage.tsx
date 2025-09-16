import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm, Controller } from 'react-hook-form'
import { yupResolver } from '@hookform/resolvers/yup'
import * as yup from 'yup'
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  TextField,
  Typography,
  Alert,
  Paper,
  CircularProgress,
  InputAdornment,
  useTheme,
  Fade,
  Grow,
} from '@mui/material'
import { Groups, ArrowBack, Add, CheckCircle, Edit } from '@mui/icons-material'
import { useAppStore } from '../store/appStore'
import { teamsApi } from '../services/api'

// Validation schema
const createTeamSchema = yup.object({
  name: yup
    .string()
    .required('Team name is required')
    .min(1, 'Team name cannot be empty')
    .max(100, 'Team name cannot exceed 100 characters')
    .test(
      'no-only-whitespace',
      'Team name cannot be only whitespace',
      (value) => {
        return value ? value.trim().length > 0 : false
      }
    ),
})

interface CreateTeamFormData {
  name: string
}

export const CreateTeamPage: React.FC = () => {
  const navigate = useNavigate()
  const theme = useTheme()
  const { setLoading } = useAppStore()

  const [createError, setCreateError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)

  const {
    control,
    handleSubmit,
    formState: { errors, isValid },
    watch,
  } = useForm<CreateTeamFormData>({
    resolver: yupResolver(createTeamSchema),
    mode: 'onChange',
    defaultValues: {
      name: '',
    },
  })

  const teamName = watch('name')

  const onSubmit = async (data: CreateTeamFormData) => {
    setIsSubmitting(true)
    setCreateError(null)
    setLoading(true)

    try {
      // Trim whitespace before submission
      const trimmedData = {
        name: data.name.trim(),
      }

      const result = await teamsApi.createTeam(trimmedData)

      // Show success animation
      setShowSuccess(true)

      // Wait for animation then redirect to team dashboard
      setTimeout(() => {
        // Navigate to the created team's dashboard
        if (result.team?.id) {
          navigate(`/teams/${result.team.id}`, { replace: true })
        } else {
          // Fallback to main dashboard if no team ID
          navigate('/dashboard', { replace: true })
        }
      }, 2000)
    } catch (error: unknown) {
      console.error('Team creation error:', error)

      // Handle different error types
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as {
          response?: { status?: number; data?: { detail?: string } }
        }
        if (axiosError.response?.status === 409) {
          setCreateError(
            'A team with this name already exists. Please choose a different name.'
          )
        } else if (axiosError.response?.status === 422) {
          setCreateError('Please check your team name format.')
        } else if (axiosError.response?.status === 401) {
          setCreateError('You need to be logged in to create a team.')
          // Redirect to login after a delay
          setTimeout(() => navigate('/login'), 2000)
        } else if (
          axiosError.response?.status &&
          axiosError.response.status >= 500
        ) {
          setCreateError('Server error. Please try again later.')
        } else {
          setCreateError(
            axiosError.response?.data?.detail ||
              'Failed to create team. Please try again.'
          )
        }
      } else {
        setCreateError(
          'Failed to create team. Please check your connection and try again.'
        )
      }
    } finally {
      setIsSubmitting(false)
      setLoading(false)
    }
  }

  const handleGoBack = () => {
    navigate('/dashboard')
  }

  if (showSuccess) {
    return (
      <Container
        maxWidth="sm"
        sx={{
          py: 8,
          display: 'flex',
          alignItems: 'center',
          minHeight: '100vh',
        }}
      >
        <Fade in={showSuccess} timeout={1000}>
          <Paper
            elevation={8}
            sx={{
              p: 6,
              textAlign: 'center',
              background: `linear-gradient(135deg, ${theme.palette.success.light} 0%, ${theme.palette.success.main} 100%)`,
              color: 'white',
              borderRadius: 4,
              width: '100%',
            }}
          >
            <Grow in={showSuccess} timeout={1500}>
              <CheckCircle sx={{ fontSize: 80, mb: 2 }} />
            </Grow>
            <Typography
              variant="h4"
              component="h1"
              fontWeight="bold"
              gutterBottom
            >
              Team Created Successfully!
            </Typography>
            <Typography variant="h6" sx={{ opacity: 0.9 }}>
              Welcome to "{teamName.trim()}"
            </Typography>
            <Typography variant="body1" sx={{ mt: 2, opacity: 0.8 }}>
              Redirecting to your dashboard...
            </Typography>
          </Paper>
        </Fade>
      </Container>
    )
  }

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Paper
        elevation={8}
        sx={{
          p: 4,
          background: `linear-gradient(135deg, ${theme.palette.background.paper} 0%, ${theme.palette.grey[50]} 100%)`,
          borderRadius: 3,
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Decorative background elements */}
        <Box
          sx={{
            position: 'absolute',
            top: -50,
            right: -50,
            width: 200,
            height: 200,
            background: `radial-gradient(circle, ${theme.palette.primary.main}15 0%, transparent 70%)`,
            borderRadius: '50%',
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            bottom: -30,
            left: -30,
            width: 150,
            height: 150,
            background: `radial-gradient(circle, ${theme.palette.secondary.main}10 0%, transparent 70%)`,
            borderRadius: '50%',
          }}
        />

        {/* Back Button */}
        <Box sx={{ mb: 3 }}>
          <Button
            startIcon={<ArrowBack />}
            onClick={handleGoBack}
            variant="outlined"
            sx={{
              borderRadius: 2,
              textTransform: 'none',
              borderColor: theme.palette.grey[300],
              color: theme.palette.text.secondary,
              '&:hover': {
                borderColor: theme.palette.primary.main,
                color: theme.palette.primary.main,
                backgroundColor: `${theme.palette.primary.main}08`,
              },
            }}
          >
            Back to Dashboard
          </Button>
        </Box>

        {/* Header */}
        <Box
          sx={{ textAlign: 'center', mb: 4, position: 'relative', zIndex: 1 }}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mb: 2,
            }}
          >
            <Box
              sx={{
                background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                borderRadius: 3,
                p: 2,
                mr: 2,
                transform: 'rotate(5deg)',
                boxShadow: `0 8px 32px ${theme.palette.primary.main}30`,
              }}
            >
              <Groups sx={{ color: 'white', fontSize: 32 }} />
            </Box>
            <Typography
              variant="h4"
              component="h1"
              fontWeight="bold"
              sx={{
                background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Create New Team
            </Typography>
          </Box>
          <Typography
            variant="body1"
            color="text.secondary"
            sx={{ maxWidth: 400, mx: 'auto', lineHeight: 1.6 }}
          >
            Give your team a unique name to get started with collaborative
            project management
          </Typography>
        </Box>

        {/* Error Alert */}
        {createError && (
          <Fade in={!!createError}>
            <Alert
              severity="error"
              sx={{
                mb: 3,
                borderRadius: 2,
                '& .MuiAlert-icon': {
                  fontSize: '1.5rem',
                },
              }}
              onClose={() => setCreateError(null)}
            >
              {createError}
            </Alert>
          </Fade>
        )}

        {/* Create Team Form */}
        <Card
          elevation={3}
          sx={{
            borderRadius: 3,
            border: `1px solid ${theme.palette.grey[200]}`,
            position: 'relative',
            zIndex: 1,
          }}
        >
          <CardContent sx={{ p: 4 }}>
            <form onSubmit={handleSubmit(onSubmit)} noValidate>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                {/* Team Name Field */}
                <Controller
                  name="name"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Team Name"
                      fullWidth
                      variant="outlined"
                      error={!!errors.name}
                      helperText={errors.name?.message}
                      disabled={isSubmitting}
                      placeholder="e.g. Marketing Team, Development Squad, Product Team"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Edit color={errors.name ? 'error' : 'action'} />
                          </InputAdornment>
                        ),
                      }}
                      sx={{
                        '& .MuiOutlinedInput-root': {
                          borderRadius: 2,
                          fontSize: '1.1rem',
                          '&:hover': {
                            '& .MuiOutlinedInput-notchedOutline': {
                              borderColor: theme.palette.primary.main,
                            },
                          },
                          '&.Mui-focused': {
                            '& .MuiOutlinedInput-notchedOutline': {
                              borderWidth: 2,
                              borderColor: theme.palette.primary.main,
                            },
                          },
                        },
                        '& .MuiInputLabel-root.Mui-focused': {
                          color: theme.palette.primary.main,
                        },
                      }}
                    />
                  )}
                />

                {/* Team Name Preview */}
                {teamName.trim() && !errors.name && (
                  <Fade in={!!teamName.trim()}>
                    <Paper
                      sx={{
                        p: 2,
                        backgroundColor: `${theme.palette.primary.main}08`,
                        border: `1px solid ${theme.palette.primary.main}30`,
                        borderRadius: 2,
                      }}
                    >
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        gutterBottom
                      >
                        Team Preview:
                      </Typography>
                      <Typography
                        variant="h6"
                        color="primary"
                        fontWeight="bold"
                      >
                        {teamName.trim()}
                      </Typography>
                    </Paper>
                  </Fade>
                )}

                {/* Create Button */}
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  fullWidth
                  disabled={!isValid || isSubmitting}
                  sx={{
                    py: 1.5,
                    borderRadius: 2,
                    fontSize: '1.1rem',
                    fontWeight: 'bold',
                    textTransform: 'none',
                    background: `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.secondary.main} 90%)`,
                    boxShadow: `0 4px 20px ${theme.palette.primary.main}40`,
                    '&:hover': {
                      background: `linear-gradient(45deg, ${theme.palette.primary.dark} 30%, ${theme.palette.secondary.dark} 90%)`,
                      boxShadow: `0 6px 25px ${theme.palette.primary.main}50`,
                      transform: 'translateY(-2px)',
                    },
                    '&:disabled': {
                      background: theme.palette.grey[300],
                      boxShadow: 'none',
                      transform: 'none',
                    },
                    transition: 'all 0.3s ease',
                  }}
                  startIcon={
                    isSubmitting ? (
                      <CircularProgress size={20} color="inherit" />
                    ) : (
                      <Add />
                    )
                  }
                >
                  {isSubmitting ? 'Creating Team...' : 'Create Team'}
                </Button>

                {/* Info Text */}
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{
                    textAlign: 'center',
                    mt: 1,
                    fontSize: '0.9rem',
                  }}
                >
                  You will be automatically assigned as the team owner
                </Typography>
              </Box>
            </form>
          </CardContent>
        </Card>
      </Paper>
    </Container>
  )
}
