import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import { InviteUserModal } from '../InviteUserModal'
import { invitationsApi } from '../../../services/api'

// Mock the API
vi.mock('../../../services/api', () => ({
  invitationsApi: {
    createInvitation: vi.fn(),
  },
}))

const mockInvitationsApi = invitationsApi as {
  createInvitation: ReturnType<typeof vi.fn>
}

// Mock props
const mockProps = {
  open: true,
  onClose: vi.fn(),
  teamId: 'team-123',
  teamName: 'Test Team',
  onInvitationSent: vi.fn(),
}

describe('InviteUserModal', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders modal with correct title and form elements', () => {
    render(<InviteUserModal {...mockProps} />)

    expect(screen.getByText('Invite User to Test Team')).toBeInTheDocument()
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/role/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /send invitation/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument()
  })

  it('does not render when open is false', () => {
    render(<InviteUserModal {...mockProps} open={false} />)

    expect(screen.queryByText('Invite User to Test Team')).not.toBeInTheDocument()
  })

  it('validates required email field', async () => {
    const user = userEvent.setup()
    render(<InviteUserModal {...mockProps} />)

    const submitButton = screen.getByRole('button', { name: /send invitation/i })

    // Try to submit without email
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument()
    })
  })

  it('validates email format', async () => {
    const user = userEvent.setup()
    render(<InviteUserModal {...mockProps} />)

    const emailInput = screen.getByLabelText(/email address/i)
    const submitButton = screen.getByRole('button', { name: /send invitation/i })

    // Enter invalid email
    await user.type(emailInput, 'invalid-email')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument()
    })
  })

  it('submits form with valid data', async () => {
    const user = userEvent.setup()
    mockInvitationsApi.createInvitation.mockResolvedValue({
      message: 'Invitation sent successfully',
      invitation: { id: '123', email: 'test@example.com' }
    })

    render(<InviteUserModal {...mockProps} />)

    const emailInput = screen.getByLabelText(/email address/i)
    const submitButton = screen.getByRole('button', { name: /send invitation/i })

    // Fill form
    await user.type(emailInput, 'test@example.com')
    await user.click(submitButton)

    // Check API was called
    await waitFor(() => {
      expect(mockInvitationsApi.createInvitation).toHaveBeenCalledWith('team-123', {
        email: 'test@example.com',
        role: 'member',
      })
    })

    // Check success message
    await waitFor(() => {
      expect(screen.getByText(/invitation sent successfully/i)).toBeInTheDocument()
    })

    // Check callback was called
    expect(mockProps.onInvitationSent).toHaveBeenCalled()
  })

  it('handles API error for existing team member', async () => {
    const user = userEvent.setup()
    mockInvitationsApi.createInvitation.mockRejectedValue({
      response: {
        status: 409,
        data: { detail: 'This user is already a member of this team' }
      }
    })

    render(<InviteUserModal {...mockProps} />)

    const emailInput = screen.getByLabelText(/email address/i)
    const submitButton = screen.getByRole('button', { name: /send invitation/i })

    await user.type(emailInput, 'existing@example.com')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/this user is already a member of this team/i)).toBeInTheDocument()
    })
  })

  it('handles API error for duplicate invitation', async () => {
    const user = userEvent.setup()
    mockInvitationsApi.createInvitation.mockRejectedValue({
      response: {
        status: 409,
        data: { detail: 'An invitation has already been sent to this email' }
      }
    })

    render(<InviteUserModal {...mockProps} />)

    const emailInput = screen.getByLabelText(/email address/i)
    const submitButton = screen.getByRole('button', { name: /send invitation/i })

    await user.type(emailInput, 'duplicate@example.com')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/an invitation has already been sent to this email/i)).toBeInTheDocument()
    })
  })

  it('handles authorization error', async () => {
    const user = userEvent.setup()
    mockInvitationsApi.createInvitation.mockRejectedValue({
      response: {
        status: 403,
        data: { detail: 'Only team owners can send invitations' }
      }
    })

    render(<InviteUserModal {...mockProps} />)

    const emailInput = screen.getByLabelText(/email address/i)
    const submitButton = screen.getByRole('button', { name: /send invitation/i })

    await user.type(emailInput, 'test@example.com')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/only team owners can send invitations/i)).toBeInTheDocument()
    })
  })

  it('handles rate limit error', async () => {
    const user = userEvent.setup()
    mockInvitationsApi.createInvitation.mockRejectedValue({
      response: {
        status: 429,
        data: { detail: 'Too many requests' }
      }
    })

    render(<InviteUserModal {...mockProps} />)

    const emailInput = screen.getByLabelText(/email address/i)
    const submitButton = screen.getByRole('button', { name: /send invitation/i })

    await user.type(emailInput, 'test@example.com')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/too many invitations sent\. please try again later/i)).toBeInTheDocument()
    })
  })

  it('allows selecting different roles', async () => {
    const user = userEvent.setup()
    render(<InviteUserModal {...mockProps} />)

    // Open role select
    const roleSelect = screen.getByLabelText(/role/i)
    await user.click(roleSelect)

    // Should see role options
    expect(screen.getByText('Member')).toBeInTheDocument()
    expect(screen.getByText('Owner')).toBeInTheDocument()

    // Select owner role
    await user.click(screen.getByText('Owner'))

    // Check role is selected
    expect(screen.getByDisplayValue('owner')).toBeInTheDocument()
  })

  it('calls onClose when cancel button is clicked', async () => {
    const user = userEvent.setup()
    render(<InviteUserModal {...mockProps} />)

    const cancelButton = screen.getByRole('button', { name: /cancel/i })
    await user.click(cancelButton)

    expect(mockProps.onClose).toHaveBeenCalled()
  })

  it('calls onClose when close icon is clicked', async () => {
    const user = userEvent.setup()
    render(<InviteUserModal {...mockProps} />)

    const closeButton = screen.getByRole('button', { name: '' }) // Close icon button
    await user.click(closeButton)

    expect(mockProps.onClose).toHaveBeenCalled()
  })

  it('prevents closing while submission is in progress', async () => {
    const user = userEvent.setup()
    // Make API call hang
    mockInvitationsApi.createInvitation.mockImplementation(() => new Promise(() => {}))

    render(<InviteUserModal {...mockProps} />)

    const emailInput = screen.getByLabelText(/email address/i)
    const submitButton = screen.getByRole('button', { name: /send invitation/i })
    const cancelButton = screen.getByRole('button', { name: /cancel/i })

    // Start submission
    await user.type(emailInput, 'test@example.com')
    await user.click(submitButton)

    // Wait for loading state
    await waitFor(() => {
      expect(screen.getByText(/sending\.\.\./i)).toBeInTheDocument()
    })

    // Try to close - should be disabled
    expect(cancelButton).toBeDisabled()
  })

  it('resets form after successful submission', async () => {
    const user = userEvent.setup()
    mockInvitationsApi.createInvitation.mockResolvedValue({
      message: 'Invitation sent successfully',
      invitation: { id: '123', email: 'test@example.com' }
    })

    render(<InviteUserModal {...mockProps} />)

    const emailInput = screen.getByLabelText(/email address/i)
    const submitButton = screen.getByRole('button', { name: /send invitation/i })

    // Fill and submit form
    await user.type(emailInput, 'test@example.com')
    await user.click(submitButton)

    // Wait for success and auto-close
    await waitFor(() => {
      expect(screen.getByText(/invitation sent successfully/i)).toBeInTheDocument()
    }, { timeout: 2000 })

    // Form should be reset (check that email field is empty when modal reopens)
    expect(emailInput).toHaveValue('')
  })
})
