import React from 'react'
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Paper,
  Chip,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  ExitToApp as LogoutIcon,
  Person as PersonIcon,
  Add as AddIcon,
  Groups as GroupsIcon,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../store/appStore'
import { authApi } from '../services/api'

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate()
  const { user, logout } = useAppStore()

  const handleLogout = async () => {
    try {
      // Call backend logout endpoint
      await authApi.logout()
    } catch (error) {
      console.error('Logout error:', error)
      // Continue with logout even if API call fails
    } finally {
      // Clear local state regardless
      logout()
      navigate('/', { replace: true })
    }
  }

  if (!user) {
    // Redirect to home if no user
    navigate('/', { replace: true })
    return null
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* Header */}
        <Paper
          elevation={2}
          sx={{
            p: 3,
            mb: 4,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
          }}
        >
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <DashboardIcon sx={{ fontSize: 32, mr: 2 }} />
              <Typography variant="h4" component="h1">
                SprintSense Dashboard
              </Typography>
            </Box>

            <Button
              variant="outlined"
              startIcon={<LogoutIcon />}
              onClick={handleLogout}
              sx={{
                color: 'white',
                borderColor: 'white',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  borderColor: 'white',
                },
              }}
            >
              Logout
            </Button>
          </Box>
        </Paper>

        {/* Welcome Section */}
        <Card sx={{ mb: 4 }}>
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <PersonIcon sx={{ fontSize: 32, mr: 2, color: 'primary.main' }} />
              <Typography variant="h5" component="h2">
                Welcome, {user.full_name}!
              </Typography>
            </Box>

            <Typography variant="body1" color="text.secondary" paragraph>
              🎉 Congratulations! You have successfully registered for
              SprintSense. Your account has been created and you are now logged
              in.
            </Typography>

            {/* User Details */}
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Account Information
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ minWidth: 100 }}
                  >
                    <strong>Name:</strong>
                  </Typography>
                  <Typography variant="body2">{user.full_name}</Typography>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ minWidth: 100 }}
                  >
                    <strong>Email:</strong>
                  </Typography>
                  <Typography variant="body2">{user.email}</Typography>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ minWidth: 100 }}
                  >
                    <strong>Status:</strong>
                  </Typography>
                  <Chip
                    label={user.is_active ? 'Active' : 'Inactive'}
                    color={user.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ minWidth: 100 }}
                  >
                    <strong>Joined:</strong>
                  </Typography>
                  <Typography variant="body2">
                    {new Date(user.created_at).toLocaleDateString()}
                  </Typography>
                </Box>
              </Box>
            </Box>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card sx={{ mb: 4 }}>
          <CardContent sx={{ p: 4 }}>
            <Typography
              variant="h6"
              gutterBottom
              sx={{ display: 'flex', alignItems: 'center' }}
            >
              <GroupsIcon sx={{ mr: 1, color: 'primary.main' }} />
              Team Management
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Create and manage your teams to organize your work effectively.
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => navigate('/teams/create')}
                sx={{
                  textTransform: 'none',
                  borderRadius: 2,
                  px: 3,
                  py: 1,
                  background:
                    'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                  '&:hover': {
                    background:
                      'linear-gradient(45deg, #5a6fd8 30%, #6a4190 90%)',
                  },
                }}
              >
                Create New Team
              </Button>

              <Button
                variant="outlined"
                startIcon={<GroupsIcon />}
                sx={{
                  textTransform: 'none',
                  borderRadius: 2,
                  px: 3,
                  py: 1,
                }}
                disabled
              >
                View Teams (Coming Soon)
              </Button>
            </Box>
          </CardContent>
        </Card>

        {/* Placeholder Content */}
        <Card>
          <CardContent sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              🚀 SprintSense Platform Coming Soon
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              This is a placeholder dashboard. The full SprintSense agile
              project management platform features will be implemented in
              upcoming stories.
            </Typography>

            <Typography variant="body2" color="text.secondary">
              Stay tuned for sprint planning, task management, team
              collaboration, and powerful analytics features!
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Container>
  )
}
