import React from 'react'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider } from '@mui/material/styles'
import { CreateTeamPage } from '../CreateTeamPage'
import { useAppStore } from '../../store/appStore'
import { teamsApi } from '../../services/api'
import { baseTheme } from '../../theme'

// Mock dependencies
vi.mock('../../store/appStore')
vi.mock('../../services/api')
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: vi.fn(),
  }
})

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    <ThemeProvider theme={baseTheme}>
      {children}
    </ThemeProvider>
  </BrowserRouter>
)

describe('CreateTeamPage', () => {
  const mockNavigate = vi.fn()
  const mockSetLoading = vi.fn()
  
  const mockUser = {
    id: '123',
    email: 'test@example.com',
    full_name: 'Test User',
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
  }

  beforeEach(async () => {
    vi.clearAllMocks()
    
    // Mock useNavigate
    const { useNavigate } = await import('react-router-dom')
    vi.mocked(useNavigate).mockReturnValue(mockNavigate)
    
    // Mock useAppStore
    vi.mocked(useAppStore).mockReturnValue({
      user: mockUser,
      isAuthenticated: true,
      setLoading: mockSetLoading,
      isLoading: false,
      error: null,
      healthStatus: null,
      accessToken: 'mock-token',
      setError: vi.fn(),
      setHealthStatus: vi.fn(),
      setUser: vi.fn(),
      setAccessToken: vi.fn(),
      logout: vi.fn(),
    })
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('Component Rendering', () => {
    it('should render the create team form', () => {
      render(
        <TestWrapper>
          <CreateTeamPage />
        </TestWrapper>
      )

      expect(screen.getByText('Create New Team')).toBeInTheDocument()
      expect(screen.getByLabelText('Team Name')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /create team/i })).toBeInTheDocument()
      expect(screen.getByText('Back to Dashboard')).toBeInTheDocument()
    })

    it('should render with creative design elements', () => {
      render(
        <TestWrapper>
          <CreateTeamPage />
        </TestWrapper>
      )

      // Check for unique design elements
      expect(screen.getByText('Give your team a unique name to get started with collaborative project management')).toBeInTheDocument()
      expect(screen.getByText('You will be automatically assigned as the team owner')).toBeInTheDocument()
    })
  })

  describe('Form Validation', () => {
    it('should show validation error for empty team name', async () => {
      const user = userEvent.setup()
      render(
        <TestWrapper>
          <CreateTeamPage />
        </TestWrapper>
      )

      const submitButton = screen.getByRole('button', { name: /create team/i })
      expect(submitButton).toBeDisabled()

      const teamNameInput = screen.getByLabelText('Team Name')
      await user.type(teamNameInput, 'Test')
      await user.clear(teamNameInput)

      await waitFor(() => {
        expect(screen.getByText('Team name is required')).toBeInTheDocument()
      })
    })

    it('should show validation error for team name that is only whitespace', async () => {
      const user = userEvent.setup()
      render(
        <TestWrapper>
          <CreateTeamPage />
        </TestWrapper>
      )

      const teamNameInput = screen.getByLabelText('Team Name')
      await user.type(teamNameInput, '   ')

      await waitFor(() => {
        expect(screen.getByText('Team name cannot be only whitespace')).toBeInTheDocument()
      })
    })

    it('should show validation error for team name exceeding 100 characters', async () => {
      const user = userEvent.setup()
      render(
        <TestWrapper>
          <CreateTeamPage />
        </TestWrapper>
      )

      const teamNameInput = screen.getByLabelText('Team Name')
      const longName = 'a'.repeat(101)
      await user.type(teamNameInput, longName)

      await waitFor(() => {
        expect(screen.getByText('Team name cannot exceed 100 characters')).toBeInTheDocument()
      })
    })

    it('should enable submit button when valid team name is entered', async () => {
      const user = userEvent.setup()
      render(
        <TestWrapper>
          <CreateTeamPage />
        </TestWrapper>
      )

      const teamNameInput = screen.getByLabelText('Team Name')
      const submitButton = screen.getByRole('button', { name: /create team/i })

      expect(submitButton).toBeDisabled()

      await user.type(teamNameInput, 'Valid Team Name')

      await waitFor(() => {
        expect(submitButton).toBeEnabled()
      })
    })

    it('should show team name preview when valid name is entered', async () => {
      const user = userEvent.setup()
      render(
        <TestWrapper>
          <CreateTeamPage />
        </TestWrapper>
      )

      const teamNameInput = screen.getByLabelText('Team Name')
      await user.type(teamNameInput, 'My Awesome Team')

      await waitFor(() => {
        expect(screen.getByText('Team Preview:')).toBeInTheDocument()
        expect(screen.getByText('My Awesome Team')).toBeInTheDocument()
      })
    })
  })

  describe('Form Submission', () => {
    it('should successfully create a team and redirect', async () => {
      const user = userEvent.setup()
      const mockCreateTeam = vi.mocked(teamsApi.createTeam)
      mockCreateTeam.mockResolvedValueOnce({
        message: 'Team created successfully',
        team: {
          id: '456',
          name: 'Test Team',
          members: [
            {
              user_id: '123',
              role: 'owner',
            },
          ],
        },
      })

      render(
        <TestWrapper>
          <CreateTeamPage />
        </TestWrapper>
      )

      const teamNameInput = screen.getByLabelText('Team Name')
      const submitButton = screen.getByRole('button', { name: /create team/i })

      await user.type(teamNameInput, 'Test Team')
      
      await waitFor(() => {
        expect(submitButton).toBeEnabled()
      })

      await user.click(submitButton)

      // Check API call
      await waitFor(() => {
        expect(mockCreateTeam).toHaveBeenCalledWith({
          name: 'Test Team',
        })
      })
      
      expect(mockSetLoading).toHaveBeenCalledWith(true)

      // Check success state
      await waitFor(() => {
        expect(screen.getByText('Team Created Successfully!')).toBeInTheDocument()
        expect(screen.getByText('Welcome to "Test Team"')).toBeInTheDocument()
      })

      // Check navigation after delay
      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 2100))
      })

      expect(mockNavigate).toHaveBeenCalledWith('/dashboard', { replace: true })
    })

    it('should trim whitespace from team name before submission', async () => {
      const user = userEvent.setup()
      const mockCreateTeam = vi.mocked(teamsApi.createTeam)
      mockCreateTeam.mockResolvedValueOnce({
        message: 'Team created successfully',
        team: { id: '456', name: 'Trimmed Team', members: [] },
      })

      render(
        <TestWrapper>
          <CreateTeamPage />
        </TestWrapper>
      )

      const teamNameInput = screen.getByLabelText('Team Name')
      const submitButton = screen.getByRole('button', { name: /create team/i })

      await user.type(teamNameInput, '  Trimmed Team  ')
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockCreateTeam).toHaveBeenCalledWith({
          name: 'Trimmed Team',
        })
      })
    })
  })

  describe('Error Handling', () => {
    it('should handle duplicate team name error', async () => {
      const user = userEvent.setup()
      const mockCreateTeam = vi.mocked(teamsApi.createTeam)
      mockCreateTeam.mockRejectedValueOnce({
        response: {
          status: 409,
          data: { detail: 'Team name already exists' },
        },
      })

      render(
        <TestWrapper>
          <CreateTeamPage />
        </TestWrapper>
      )

      const teamNameInput = screen.getByLabelText('Team Name')
      const submitButton = screen.getByRole('button', { name: /create team/i })

      await user.type(teamNameInput, 'Duplicate Team')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('A team with this name already exists. Please choose a different name.')).toBeInTheDocument()
      })
    })

    it('should handle validation error', async () => {
      const user = userEvent.setup()
      const mockCreateTeam = vi.mocked(teamsApi.createTeam)
      mockCreateTeam.mockRejectedValueOnce({
        response: {
          status: 422,
          data: { detail: 'Validation error' },
        },
      })

      render(
        <TestWrapper>
          <CreateTeamPage />
        </TestWrapper>
      )

      const teamNameInput = screen.getByLabelText('Team Name')
      const submitButton = screen.getByRole('button', { name: /create team/i })

      await user.type(teamNameInput, 'Invalid Team')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Please check your team name format.')).toBeInTheDocument()
      })
    })

    it('should handle authentication error and redirect to login', async () => {
      const user = userEvent.setup()
      const mockCreateTeam = vi.mocked(teamsApi.createTeam)
      mockCreateTeam.mockRejectedValueOnce({
        response: {
          status: 401,
          data: { detail: 'Unauthorized' },
        },
      })

      render(
        <TestWrapper>
          <CreateTeamPage />
        </TestWrapper>
      )

      const teamNameInput = screen.getByLabelText('Team Name')
      const submitButton = screen.getByRole('button', { name: /create team/i })

      await user.type(teamNameInput, 'Test Team')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('You need to be logged in to create a team.')).toBeInTheDocument()
      })

      // Check navigation after delay
      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 2100))
      })

      expect(mockNavigate).toHaveBeenCalledWith('/login')
    })

    it('should handle server error', async () => {
      const user = userEvent.setup()
      const mockCreateTeam = vi.mocked(teamsApi.createTeam)
      mockCreateTeam.mockRejectedValueOnce({
        response: {
          status: 500,
          data: { detail: 'Internal server error' },
        },
      })

      render(
        <TestWrapper>
          <CreateTeamPage />
        </TestWrapper>
      )

      const teamNameInput = screen.getByLabelText('Team Name')
      const submitButton = screen.getByRole('button', { name: /create team/i })

      await user.type(teamNameInput, 'Test Team')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Server error. Please try again later.')).toBeInTheDocument()
      })
    })

    it('should handle network error', async () => {
      const user = userEvent.setup()
      const mockCreateTeam = vi.mocked(teamsApi.createTeam)
      mockCreateTeam.mockRejectedValueOnce(new Error('Network error'))

      render(
        <TestWrapper>
          <CreateTeamPage />
        </TestWrapper>
      )

      const teamNameInput = screen.getByLabelText('Team Name')
      const submitButton = screen.getByRole('button', { name: /create team/i })

      await user.type(teamNameInput, 'Test Team')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Failed to create team. Please check your connection and try again.')).toBeInTheDocument()
      })
    })

    it('should allow dismissing error messages', async () => {
      const user = userEvent.setup()
      const mockCreateTeam = vi.mocked(teamsApi.createTeam)
      mockCreateTeam.mockRejectedValueOnce({
        response: {
          status: 409,
        },
      })

      render(
        <TestWrapper>
          <CreateTeamPage />
        </TestWrapper>
      )

      const teamNameInput = screen.getByLabelText('Team Name')
      const submitButton = screen.getByRole('button', { name: /create team/i })

      await user.type(teamNameInput, 'Test Team')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('A team with this name already exists. Please choose a different name.')).toBeInTheDocument()
      })

      // Find and click the dismiss button
      const dismissButton = screen.getByLabelText('Close')
      await user.click(dismissButton)

      await waitFor(() => {
        expect(screen.queryByText('A team with this name already exists. Please choose a different name.')).not.toBeInTheDocument()
      })
    })
  })

  describe('Navigation', () => {
    it('should navigate back to dashboard when back button is clicked', async () => {
      const user = userEvent.setup()
      render(
        <TestWrapper>
          <CreateTeamPage />
        </TestWrapper>
      )

      const backButton = screen.getByText('Back to Dashboard')
      await user.click(backButton)

      expect(mockNavigate).toHaveBeenCalledWith('/dashboard')
    })
  })

  describe('Accessibility', () => {
    it('should have proper form labels and structure', () => {
      const { container } = render(
        <TestWrapper>
          <CreateTeamPage />
        </TestWrapper>
      )

      expect(screen.getByLabelText('Team Name')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /create team/i })).toBeInTheDocument()
      expect(container.querySelector('form')).toBeInTheDocument()
    })

    it('should have proper heading structure', () => {
      render(
        <TestWrapper>
          <CreateTeamPage />
        </TestWrapper>
      )

      expect(screen.getByRole('heading', { name: /create new team/i })).toBeInTheDocument()
    })
  })
})