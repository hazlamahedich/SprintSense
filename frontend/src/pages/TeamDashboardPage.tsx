import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Paper,
  Chip,
  Alert,
  CircularProgress,
  Grid,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  ArrowBack as ArrowBackIcon,
  PersonAdd as PersonAddIcon,
  Groups as GroupsIcon,
  Settings as SettingsIcon,
  People as PeopleIcon,
} from '@mui/icons-material'
import { useAppStore } from '../store/appStore'
import { teamsApi } from '../services/api'
import { InviteUserModal, PendingInvitations } from '../components/team'

interface Team {
  id: string
  name: string
  created_at: string
  updated_at?: string
}

export const TeamDashboardPage: React.FC = () => {
  const { teamId } = useParams<{ teamId: string }>()
  const navigate = useNavigate()
  const { user } = useAppStore()

  const [team, setTeam] = useState<Team | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [inviteModalOpen, setInviteModalOpen] = useState(false)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  // Fetch team data
  useEffect(() => {
    const fetchTeam = async () => {
      if (!teamId) {
        setError('Team ID is required')
        setIsLoading(false)
        return
      }

      try {
        const teamData = await teamsApi.getTeam(teamId)
        setTeam(teamData.team)
      } catch (err: unknown) {
        console.error('Failed to fetch team:', err)

        // Cast error to handle response properties
        const error = err as { response?: { status?: number } }

        if (error.response?.status === 404) {
          setError('Team not found')
        } else if (error.response?.status === 403) {
          setError('You do not have permission to view this team')
        } else {
          setError('Failed to load team. Please try again.')
        }
      } finally {
        setIsLoading(false)
      }
    }

    fetchTeam()
  }, [teamId])

  const handleInviteUser = () => {
    setInviteModalOpen(true)
  }

  const handleInviteModalClose = () => {
    setInviteModalOpen(false)
  }

  const handleInvitationSent = () => {
    // Trigger refresh of pending invitations
    setRefreshTrigger((prev) => prev + 1)
  }

  const handleBackToDashboard = () => {
    navigate('/dashboard')
  }

  // Loading state
  if (isLoading) {
    return (
      <Container maxWidth="lg">
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="50vh"
        >
          <Box textAlign="center">
            <CircularProgress size={40} />
            <Typography variant="body1" color="text.secondary" sx={{ mt: 2 }}>
              Loading team dashboard...
            </Typography>
          </Box>
        </Box>
      </Container>
    )
  }

  // Error state
  if (error || !team) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ py: 4 }}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={handleBackToDashboard}
            sx={{ mb: 3 }}
          >
            Back to Dashboard
          </Button>

          <Alert severity="error" variant="outlined">
            {error || 'Team not found'}
          </Alert>
        </Box>
      </Container>
    )
  }

  // Redirect if no user
  if (!user) {
    navigate('/login', { replace: true })
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
              flexWrap: 'wrap',
              gap: 2,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <IconButton
                onClick={handleBackToDashboard}
                sx={{
                  color: 'white',
                  mr: 2,
                  '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.1)' },
                }}
              >
                <ArrowBackIcon />
              </IconButton>

              <GroupsIcon sx={{ fontSize: 32, mr: 2 }} />

              <Box>
                <Typography
                  variant="h4"
                  component="h1"
                  sx={{ fontWeight: 'bold' }}
                >
                  {team.name}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Team Dashboard
                </Typography>
              </Box>
            </Box>

            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="Team Settings">
                <IconButton
                  sx={{
                    color: 'white',
                    '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.1)' },
                  }}
                >
                  <SettingsIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </Paper>

        <Grid container spacing={3}>
          {/* Team Information */}
          <Grid item xs={12} md={8}>
            <Card sx={{ mb: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Box display="flex" alignItems="center" mb={2}>
                  <DashboardIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">Team Information</Typography>
                </Box>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Box>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      gutterBottom
                    >
                      Team Name
                    </Typography>
                    <Typography variant="h6" color="primary">
                      {team.name}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      gutterBottom
                    >
                      Created
                    </Typography>
                    <Typography variant="body1">
                      {new Date(team.created_at).toLocaleDateString('en-US', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      gutterBottom
                    >
                      Your Role
                    </Typography>
                    <Chip
                      label="Owner"
                      color="primary"
                      icon={<PeopleIcon />}
                      variant="outlined"
                    />
                  </Box>
                </Box>
              </CardContent>
            </Card>

            {/* Team Management Section */}
            <Card>
              <CardContent sx={{ p: 3 }}>
                <Box display="flex" alignItems="center" mb={2}>
                  <PeopleIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">Team Management</Typography>
                </Box>

                <Typography variant="body2" color="text.secondary" paragraph>
                  Manage your team members and send invitations to collaborate.
                </Typography>

                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <Button
                    variant="contained"
                    startIcon={<PersonAddIcon />}
                    onClick={handleInviteUser}
                    sx={{
                      textTransform: 'none',
                      borderRadius: 2,
                      px: 3,
                      py: 1,
                    }}
                  >
                    Invite User
                  </Button>

                  <Button
                    variant="outlined"
                    startIcon={<PeopleIcon />}
                    sx={{
                      textTransform: 'none',
                      borderRadius: 2,
                      px: 3,
                      py: 1,
                    }}
                  >
                    View Members
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Sidebar */}
          <Grid item xs={12} md={4}>
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Quick Stats
                </Typography>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Box
                    sx={{ display: 'flex', justifyContent: 'space-between' }}
                  >
                    <Typography variant="body2" color="text.secondary">
                      Team Members
                    </Typography>
                    <Chip label="1" size="small" color="primary" />
                  </Box>

                  <Box
                    sx={{ display: 'flex', justifyContent: 'space-between' }}
                  >
                    <Typography variant="body2" color="text.secondary">
                      Active Projects
                    </Typography>
                    <Chip label="0" size="small" />
                  </Box>

                  <Box
                    sx={{ display: 'flex', justifyContent: 'space-between' }}
                  >
                    <Typography variant="body2" color="text.secondary">
                      Pending Invitations
                    </Typography>
                    <Chip label="View Below" size="small" color="warning" />
                  </Box>
                </Box>
              </CardContent>
            </Card>

            {/* Coming Soon Card */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  🚀 Coming Soon
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Sprint planning, task management, and team analytics features
                  will be available in upcoming releases.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Pending Invitations Section */}
        <PendingInvitations teamId={team.id} refreshTrigger={refreshTrigger} />

        {/* Invite User Modal */}
        <InviteUserModal
          open={inviteModalOpen}
          onClose={handleInviteModalClose}
          teamId={team.id}
          teamName={team.name}
          onInvitationSent={handleInvitationSent}
        />
      </Box>
    </Container>
  )
}
