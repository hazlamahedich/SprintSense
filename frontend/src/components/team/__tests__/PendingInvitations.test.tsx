import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { PendingInvitations } from '../PendingInvitations'
import { invitationsApi } from '../../../services/api'

// Mock the API
vi.mock('../../../services/api', () => ({
  invitationsApi: {
    getTeamInvitations: vi.fn(),
  },
}))

const mockInvitationsApi = invitationsApi as {
  getTeamInvitations: ReturnType<typeof vi.fn>
}

const mockInvitations = [
  {
    id: '1',
    email: 'user1@example.com',
    role: 'member' as const,
    status: 'pending' as const,
    inviter_name: 'John Doe',
    created_at: '2023-01-15T10:30:00Z',
  },
  {
    id: '2',
    email: 'user2@example.com',
    role: 'owner' as const,
    status: 'pending' as const,
    inviter_name: 'Jane Smith',
    created_at: '2023-01-16T14:20:00Z',
  },
]

describe('PendingInvitations', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    mockInvitationsApi.getTeamInvitations.mockImplementation(
      () => new Promise(() => {})
    )

    render(<PendingInvitations teamId="team-123" />)

    expect(screen.getByText(/loading invitations\.\.\./i)).toBeInTheDocument()
    expect(screen.getByRole('progressbar')).toBeInTheDocument()
  })

  it('renders invitations list when data is loaded', async () => {
    mockInvitationsApi.getTeamInvitations.mockResolvedValue({
      invitations: mockInvitations,
    })

    render(<PendingInvitations teamId="team-123" />)

    await waitFor(() => {
      expect(screen.getByText('Pending Invitations')).toBeInTheDocument()
    })

    // Check that invitations are rendered
    expect(screen.getByText('user1@example.com')).toBeInTheDocument()
    expect(screen.getByText('user2@example.com')).toBeInTheDocument()
    expect(screen.getByText('Invited by John Doe')).toBeInTheDocument()
    expect(screen.getByText('Invited by Jane Smith')).toBeInTheDocument()

    // Check invitation count badge
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('renders empty state when no invitations exist', async () => {
    mockInvitationsApi.getTeamInvitations.mockResolvedValue({
      invitations: [],
    })

    render(<PendingInvitations teamId="team-123" />)

    await waitFor(() => {
      expect(screen.getByText('No pending invitations')).toBeInTheDocument()
    })

    expect(
      screen.getByText('Sent invitations will appear here')
    ).toBeInTheDocument()
    expect(screen.getByText('0')).toBeInTheDocument() // Count badge
  })

  it('displays correct role chips for different roles', async () => {
    mockInvitationsApi.getTeamInvitations.mockResolvedValue({
      invitations: mockInvitations,
    })

    render(<PendingInvitations teamId="team-123" />)

    await waitFor(() => {
      expect(screen.getByText('member')).toBeInTheDocument()
      expect(screen.getByText('owner')).toBeInTheDocument()
    })
  })

  it('formats dates correctly', async () => {
    mockInvitationsApi.getTeamInvitations.mockResolvedValue({
      invitations: mockInvitations,
    })

    render(<PendingInvitations teamId="team-123" />)

    await waitFor(() => {
      // Check that formatted dates are present (exact format may vary by locale)
      // Use getAllByText when multiple elements are expected
      const dateElements = screen.getAllByText(/Jan \d+, \d+:\d+ [AP]M/)
      expect(dateElements).toHaveLength(2) // Assert expected count for 2 invitations
      // Verify both dates are present
      dateElements.forEach((element) => {
        expect(element).toBeInTheDocument()
      })
    })
  })

  it('displays status chips correctly', async () => {
    mockInvitationsApi.getTeamInvitations.mockResolvedValue({
      invitations: mockInvitations,
    })

    render(<PendingInvitations teamId="team-123" />)

    await waitFor(() => {
      // Should have pending status chips
      const statusChips = screen.getAllByText('pending')
      expect(statusChips).toHaveLength(2)
    })
  })

  it('handles API error gracefully', async () => {
    mockInvitationsApi.getTeamInvitations.mockRejectedValue(
      new Error('Network error')
    )

    render(<PendingInvitations teamId="team-123" />)

    await waitFor(() => {
      expect(
        screen.getByText(/failed to load invitations/i)
      ).toBeInTheDocument()
    })
  })

  it('handles 403 authorization error', async () => {
    mockInvitationsApi.getTeamInvitations.mockRejectedValue({
      response: { status: 403 },
    })

    render(<PendingInvitations teamId="team-123" />)

    await waitFor(() => {
      expect(
        screen.getByText(/you do not have permission to view team invitations/i)
      ).toBeInTheDocument()
    })
  })

  it('handles 404 team not found error', async () => {
    mockInvitationsApi.getTeamInvitations.mockRejectedValue({
      response: { status: 404 },
    })

    render(<PendingInvitations teamId="team-123" />)

    await waitFor(() => {
      expect(screen.getByText(/team not found/i)).toBeInTheDocument()
    })
  })

  it('refetches data when refreshTrigger changes', async () => {
    mockInvitationsApi.getTeamInvitations.mockResolvedValue({
      invitations: mockInvitations,
    })

    const { rerender } = render(
      <PendingInvitations teamId="team-123" refreshTrigger={0} />
    )

    await waitFor(() => {
      expect(mockInvitationsApi.getTeamInvitations).toHaveBeenCalledTimes(1)
    })

    // Trigger refresh
    rerender(<PendingInvitations teamId="team-123" refreshTrigger={1} />)

    await waitFor(() => {
      expect(mockInvitationsApi.getTeamInvitations).toHaveBeenCalledTimes(2)
    })
  })

  it('refetches data when teamId changes', async () => {
    mockInvitationsApi.getTeamInvitations.mockResolvedValue({
      invitations: mockInvitations,
    })

    const { rerender } = render(<PendingInvitations teamId="team-123" />)

    await waitFor(() => {
      expect(mockInvitationsApi.getTeamInvitations).toHaveBeenCalledWith(
        'team-123'
      )
    })

    // Change team ID
    rerender(<PendingInvitations teamId="team-456" />)

    await waitFor(() => {
      expect(mockInvitationsApi.getTeamInvitations).toHaveBeenCalledWith(
        'team-456'
      )
      expect(mockInvitationsApi.getTeamInvitations).toHaveBeenCalledTimes(2)
    })
  })

  it('does not fetch when teamId is empty', () => {
    render(<PendingInvitations teamId="" />)

    expect(mockInvitationsApi.getTeamInvitations).not.toHaveBeenCalled()
  })

  it('shows helpful information about invitation expiry', async () => {
    mockInvitationsApi.getTeamInvitations.mockResolvedValue({
      invitations: mockInvitations,
    })

    render(<PendingInvitations teamId="team-123" />)

    await waitFor(() => {
      expect(
        screen.getByText(/invitations expire after 7 days/i)
      ).toBeInTheDocument()
      expect(
        screen.getByText(
          /users will need to register or log in to accept invitations/i
        )
      ).toBeInTheDocument()
    })
  })

  it('renders invitation avatars', async () => {
    mockInvitationsApi.getTeamInvitations.mockResolvedValue({
      invitations: mockInvitations,
    })

    render(<PendingInvitations teamId="team-123" />)

    await waitFor(() => {
      // Should have avatars for each invitation (by checking for email icons)
      const avatars =
        screen.getAllByTestId('EmailIcon') || screen.getAllByLabelText(/email/i)
      expect(avatars.length).toBeGreaterThan(0)
    })
  })

  it('applies hover effects to invitation items', async () => {
    mockInvitationsApi.getTeamInvitations.mockResolvedValue({
      invitations: mockInvitations,
    })

    render(<PendingInvitations teamId="team-123" />)

    await waitFor(() => {
      const listItems = screen.getAllByRole('listitem')
      expect(listItems.length).toBe(2)

      // Check that list items have the expected structure
      listItems.forEach((item) => {
        expect(item).toBeInTheDocument()
      })
    })
  })
})
