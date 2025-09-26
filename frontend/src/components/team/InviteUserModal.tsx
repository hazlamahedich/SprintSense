import React, { useState } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Box,
  Typography,
  IconButton,
} from '@mui/material'
import { Close as CloseIcon } from '@mui/icons-material'
import { useForm, Controller } from 'react-hook-form'
import { invitationsApi } from '../../services/api'
import type {
  InvitationFormData,
  InvitationError,
} from '../../types/invitations'

interface InviteUserModalProps {
  open: boolean
  onClose: () => void
  teamId: string
  teamName: string
  onInvitationSent?: () => void
}

export const InviteUserModal: React.FC<InviteUserModalProps> = ({
  open,
  onClose,
  teamId,
  teamName,
  onInvitationSent,
}) => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<InvitationError | null>(null)
  const [success, setSuccess] = useState(false)

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<InvitationFormData>({
    defaultValues: {
      email: '',
      role: 'member',
    },
  })

  const handleClose = () => {
    if (!isLoading) {
      reset()
      setError(null)
      setSuccess(false)
      onClose()
    }
  }

  const onSubmit = async (data: InvitationFormData) => {
    setIsLoading(true)
    setError(null)

    try {
      await invitationsApi.createInvitation(teamId, {
        email: data.email,
        role: data.role,
      })

      setSuccess(true)
      reset()

      // Call callback after successful invitation
      if (onInvitationSent) {
        onInvitationSent()
      }

      // Close modal after a brief delay to show success message
      setTimeout(() => {
        setSuccess(false)
        handleClose()
      }, 1500)
    } catch (err: unknown) {
      console.error('Failed to send invitation:', err)

      // Cast error to handle response properties
      const error = err as {
        response?: { status?: number; data?: { detail?: string } }
      }

      // Handle different error scenarios
      if (error.response?.status === 409) {
        if (error.response.data?.detail?.includes('already a member')) {
          setError({
            message: 'This user is already a member of this team',
            field: 'email',
          })
        } else if (error.response.data?.detail?.includes('already been sent')) {
          setError({
            message: 'An invitation has already been sent to this email',
            field: 'email',
          })
        } else {
          setError({
            message: error.response.data?.detail || 'Invitation already exists',
          })
        }
      } else if (error.response?.status === 403) {
        setError({
          message: 'Only team owners can send invitations',
        })
      } else if (error.response?.status === 422) {
        setError({
          message: 'Please enter a valid email address',
          field: 'email',
        })
      } else if (error.response?.status === 429) {
        setError({
          message: 'Too many invitations sent. Please try again later.',
        })
      } else {
        setError({
          message: 'Failed to send invitation. Please try again.',
        })
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: { borderRadius: 2 },
      }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" component="div">
            Invite User to {teamName}
          </Typography>
          <IconButton
            edge="end"
            color="inherit"
            onClick={handleClose}
            disabled={isLoading}
            size="small"
          >
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Send an invitation to join your team. The user will receive access
              based on their assigned role.
            </Typography>
          </Box>

          {success && (
            <Alert severity="success" sx={{ mb: 2 }} variant="filled">
              Invitation sent successfully!
            </Alert>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }} variant="outlined">
              {error.message}
            </Alert>
          )}

          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Controller
              name="email"
              control={control}
              rules={{
                required: 'Email is required',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Please enter a valid email address',
                },
              }}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Email Address"
                  type="email"
                  fullWidth
                  variant="outlined"
                  disabled={isLoading}
                  error={!!errors.email || error?.field === 'email'}
                  helperText={
                    errors.email?.message ||
                    (error?.field === 'email' ? error.message : '')
                  }
                  placeholder="user@example.com"
                  autoFocus
                />
              )}
            />

            <Controller
              name="role"
              control={control}
              rules={{
                required: 'Role is required',
              }}
              render={({ field }) => (
                <FormControl fullWidth variant="outlined" disabled={isLoading}>
                  <InputLabel>Role</InputLabel>
                  <Select {...field} label="Role" error={!!errors.role}>
                    <MenuItem value="member">
                      <Box>
                        <Typography variant="body1">Member</Typography>
                        <Typography variant="caption" color="text.secondary">
                          Can view and participate in team activities
                        </Typography>
                      </Box>
                    </MenuItem>
                    <MenuItem value="owner">
                      <Box>
                        <Typography variant="body1">Owner</Typography>
                        <Typography variant="caption" color="text.secondary">
                          Can manage team settings and send invitations
                        </Typography>
                      </Box>
                    </MenuItem>
                  </Select>
                  {errors.role && (
                    <Typography
                      variant="caption"
                      color="error"
                      sx={{ mt: 0.5, ml: 1 }}
                    >
                      {errors.role.message}
                    </Typography>
                  )}
                </FormControl>
              )}
            />
          </Box>
        </DialogContent>

        <DialogActions sx={{ p: 2, pt: 1 }}>
          <Button onClick={handleClose} disabled={isLoading} color="inherit">
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={isLoading || success}
            startIcon={isLoading ? <CircularProgress size={16} /> : null}
          >
            {isLoading ? 'Sending...' : 'Send Invitation'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  )
}

