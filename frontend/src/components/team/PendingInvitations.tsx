import React, { useState, useEffect, useCallback } from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Avatar,
  Tooltip,
} from '@mui/material'
import {
  Email as EmailIcon,
  Person as PersonIcon,
  AccessTime as TimeIcon,
} from '@mui/icons-material'
import { invitationsApi } from '../../services/api'
import { InvitationListItem } from '../../types/invitations'

interface PendingInvitationsProps {
  teamId: string
  refreshTrigger?: number // Used to trigger refresh from parent component
}

export const PendingInvitations: React.FC<PendingInvitationsProps> = ({
  teamId,
  refreshTrigger,
}) => {
  const [invitations, setInvitations] = useState<InvitationListItem[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchInvitations = useCallback(async () => {
    if (!teamId) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await invitationsApi.getTeamInvitations(teamId)
      setInvitations(response.invitations)
    } catch (err: unknown) {
      console.error('Failed to fetch invitations:', err)

      // Cast error to handle response properties
      const error = err as { response?: { status?: number } }

      if (error.response?.status === 403) {
        setError('You do not have permission to view team invitations')
      } else if (error.response?.status === 404) {
        setError('Team not found')
      } else {
        setError('Failed to load invitations. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }, [teamId])

  // Initial fetch and refresh when dependencies change
  useEffect(() => {
    fetchInvitations()
  }, [teamId, refreshTrigger, fetchInvitations])

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const getRoleColor = (role: string): 'primary' | 'secondary' | 'default' => {
    switch (role) {
      case 'owner':
        return 'primary'
      case 'member':
        return 'secondary'
      default:
        return 'default'
    }
  }

  const getRoleIcon = (role: string) => {
    return role === 'owner' ? <PersonIcon fontSize="small" /> : <PersonIcon fontSize="small" />
  }

  if (isLoading) {
    return (
      <Card sx={{ mt: 2 }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="center" py={3}>
            <CircularProgress size={24} sx={{ mr: 2 }} />
            <Typography variant="body2" color="text.secondary">
              Loading invitations...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card sx={{ mt: 2 }}>
        <CardContent>
          <Alert severity="error" variant="outlined">
            {error}
          </Alert>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card sx={{ mt: 2 }}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <EmailIcon sx={{ mr: 1, color: 'text.secondary' }} />
          <Typography variant="h6" component="div">
            Pending Invitations
          </Typography>
          <Chip
            label={invitations.length}
            size="small"
            color="primary"
            sx={{ ml: 1 }}
          />
        </Box>

        {invitations.length === 0 ? (
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            py={4}
            sx={{
              backgroundColor: 'grey.50',
              borderRadius: 1,
              border: '1px dashed',
              borderColor: 'grey.300'
            }}
          >
            <EmailIcon sx={{ fontSize: 48, color: 'grey.400', mb: 1 }} />
            <Typography variant="body1" color="text.secondary" align="center">
              No pending invitations
            </Typography>
            <Typography variant="body2" color="text.secondary" align="center">
              Sent invitations will appear here
            </Typography>
          </Box>
        ) : (
          <List disablePadding>
            {invitations.map((invitation, index) => (
              <React.Fragment key={invitation.id}>
                {index > 0 && <Divider />}
                <ListItem
                  sx={{
                    py: 2,
                    px: 0,
                    '&:hover': {
                      backgroundColor: 'action.hover',
                      borderRadius: 1,
                    },
                  }}
                >
                  <Box sx={{ mr: 2 }}>
                    <Avatar sx={{ width: 40, height: 40, bgcolor: 'primary.light' }}>
                      <EmailIcon />
                    </Avatar>
                  </Box>

                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="body1" component="span">
                          {invitation.email}
                        </Typography>
                        <Chip
                          label={invitation.role}
                          size="small"
                          color={getRoleColor(invitation.role)}
                          icon={getRoleIcon(invitation.role)}
                          variant="outlined"
                        />
                      </Box>
                    }
                    secondary={
                      <Box display="flex" flexDirection="column" gap={0.5} mt={0.5}>
                        <Typography variant="caption" color="text.secondary">
                          Invited by {invitation.inviter_name}
                        </Typography>
                        <Box display="flex" alignItems="center">
                          <TimeIcon sx={{ fontSize: 14, mr: 0.5, color: 'text.secondary' }} />
                          <Typography variant="caption" color="text.secondary">
                            {formatDate(invitation.created_at)}
                          </Typography>
                        </Box>
                      </Box>
                    }
                  />

                  <ListItemSecondaryAction>
                    <Tooltip title={`Status: ${invitation.status}`}>
                      <Chip
                        label={invitation.status}
                        size="small"
                        color={invitation.status === 'pending' ? 'warning' : 'default'}
                        sx={{
                          textTransform: 'capitalize',
                          minWidth: 70,
                        }}
                      />
                    </Tooltip>
                  </ListItemSecondaryAction>
                </ListItem>
              </React.Fragment>
            ))}
          </List>
        )}

        {invitations.length > 0 && (
          <Box mt={2}>
            <Typography variant="caption" color="text.secondary">
              Invitations expire after 7 days. Users will need to register or log in to accept invitations.
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}
