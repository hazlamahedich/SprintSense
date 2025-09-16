import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider } from '@mui/material/styles'
import { LoginPage } from './LoginPage'
import { baseTheme } from '../theme'
import { useAppStore } from '../store/appStore'
import { authApi } from '../services/api'

// Mock the store
vi.mock('../store/appStore')
const mockUseAppStore = vi.mocked(useAppStore)

// Mock the API
vi.mock('../services/api', () => ({
  authApi: {
    login: vi.fn(),
  },
}))

// Mock react-router-dom navigation
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
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

describe('LoginPage', () => {
  const mockSetUser = vi.fn()
  const mockSetAccessToken = vi.fn()
  const mockSetLoading = vi.fn()
  const mockSetError = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    
    mockUseAppStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      accessToken: null,
      isLoading: false,
      error: null,
      healthStatus: null,
      setUser: mockSetUser,
      setAccessToken: mockSetAccessToken,
      setLoading: mockSetLoading,
      setError: mockSetError,
      setHealthStatus: vi.fn(),
      logout: vi.fn(),
    })
  })

  it('renders login form correctly', () => {
    render(<LoginPage />, { wrapper: TestWrapper })

    expect(screen.getByText('SprintSense')).toBeInTheDocument()
    expect(screen.getByText('Welcome Back')).toBeInTheDocument()
    expect(screen.getByText('Sign in to your account to continue')).toBeInTheDocument()
    expect(screen.getByLabelText('Email Address')).toBeInTheDocument()
    expect(screen.getByLabelText('Password')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
    expect(screen.getByText('Create Account')).toBeInTheDocument()
  })

  it('shows validation errors for invalid email', async () => {
    const user = userEvent.setup()
    render(<LoginPage />, { wrapper: TestWrapper })

    const emailInput = screen.getByLabelText('Email Address')
    
    await user.type(emailInput, 'invalid-email')
    await user.tab() // Trigger blur to show validation

    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument()
    })
  })

  it('shows validation errors for empty password', async () => {
    const user = userEvent.setup()
    render(<LoginPage />, { wrapper: TestWrapper })

    const passwordInput = screen.getByLabelText('Password')
    const emailInput = screen.getByLabelText('Email Address')
    
    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'test')
    await user.clear(passwordInput) // Clear password to trigger validation
    await user.tab() // Trigger blur

    await waitFor(() => {
      expect(screen.getByText('Password is required')).toBeInTheDocument()
    })
  })

  it('disables submit button when form is invalid', () => {
    render(<LoginPage />, { wrapper: TestWrapper })

    const submitButton = screen.getByRole('button', { name: /sign in/i })
    expect(submitButton).toBeDisabled()
  })

  it('enables submit button when form is valid', async () => {
    const user = userEvent.setup()
    render(<LoginPage />, { wrapper: TestWrapper })

    const emailInput = screen.getByLabelText('Email Address')
    const passwordInput = screen.getByLabelText('Password')

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'TestPassword123')

    await waitFor(() => {
      const submitButton = screen.getByRole('button', { name: /sign in/i })
      expect(submitButton).not.toBeDisabled()
    })
  })

  it('toggles password visibility', async () => {
    const user = userEvent.setup()
    render(<LoginPage />, { wrapper: TestWrapper })

    const passwordInput = screen.getByLabelText('Password')
    const toggleButton = screen.getByRole('button', { name: '' }) // Password visibility toggle

    // Initially password should be hidden
    expect(passwordInput).toHaveAttribute('type', 'password')

    // Click toggle to show password
    await user.click(toggleButton)
    expect(passwordInput).toHaveAttribute('type', 'text')

    // Click toggle to hide password again
    await user.click(toggleButton)
    expect(passwordInput).toHaveAttribute('type', 'password')
  })

  it('submits form with valid credentials and handles success', async () => {
    const user = userEvent.setup()
    const mockLoginResponse = {
      message: 'Login successful',
      user: {
        id: '123',
        email: 'test@example.com',
        full_name: 'Test User',
        is_active: true,
        created_at: '2023-01-01T00:00:00Z',
      },
    }

    vi.mocked(authApi.login).mockResolvedValue(mockLoginResponse)

    render(<LoginPage />, { wrapper: TestWrapper })

    const emailInput = screen.getByLabelText('Email Address')
    const passwordInput = screen.getByLabelText('Password')
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'TestPassword123')
    await user.click(submitButton)

    // Verify API call
    expect(authApi.login).toHaveBeenCalledWith('test@example.com', 'TestPassword123')

    // Verify store updates
    await waitFor(() => {
      expect(mockSetUser).toHaveBeenCalledWith(mockLoginResponse.user)
      expect(mockSetAccessToken).toHaveBeenCalledWith('authenticated')
    })

    // Verify navigation
    expect(mockNavigate).toHaveBeenCalledWith('/dashboard', { replace: true })
  })

  it('handles login error with invalid credentials', async () => {
    const user = userEvent.setup()
    const mockError = {
      response: { status: 401 },
    }

    vi.mocked(authApi.login).mockRejectedValue(mockError)

    render(<LoginPage />, { wrapper: TestWrapper })

    const emailInput = screen.getByLabelText('Email Address')
    const passwordInput = screen.getByLabelText('Password')
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'WrongPassword')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Invalid email or password. Please try again.')).toBeInTheDocument()
    })

    // Verify navigation was not called
    expect(mockNavigate).not.toHaveBeenCalled()
  })

  it('handles validation error', async () => {
    const user = userEvent.setup()
    const mockError = {
      response: { status: 422 },
    }

    vi.mocked(authApi.login).mockRejectedValue(mockError)

    render(<LoginPage />, { wrapper: TestWrapper })

    const emailInput = screen.getByLabelText('Email Address')
    const passwordInput = screen.getByLabelText('Password')
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Please check your email and password format.')).toBeInTheDocument()
    })
  })

  it('handles server error', async () => {
    const user = userEvent.setup()
    const mockError = {
      response: { status: 500 },
    }

    vi.mocked(authApi.login).mockRejectedValue(mockError)

    render(<LoginPage />, { wrapper: TestWrapper })

    const emailInput = screen.getByLabelText('Email Address')
    const passwordInput = screen.getByLabelText('Password')
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'TestPassword123')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Server error. Please try again later.')).toBeInTheDocument()
    })
  })

  it('handles network error', async () => {
    const user = userEvent.setup()
    const mockError = new Error('Network Error')

    vi.mocked(authApi.login).mockRejectedValue(mockError)

    render(<LoginPage />, { wrapper: TestWrapper })

    const emailInput = screen.getByLabelText('Email Address')
    const passwordInput = screen.getByLabelText('Password')
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'TestPassword123')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Login failed. Please check your connection and try again.')).toBeInTheDocument()
    })
  })

  it('shows loading state during submission', async () => {
    const user = userEvent.setup()
    
    // Mock a slow login call
    vi.mocked(authApi.login).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 1000))
    )

    render(<LoginPage />, { wrapper: TestWrapper })

    const emailInput = screen.getByLabelText('Email Address')
    const passwordInput = screen.getByLabelText('Password')
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'TestPassword123')
    await user.click(submitButton)

    // Check loading state
    expect(screen.getByText('Signing In...')).toBeInTheDocument()
    expect(screen.getByRole('progressbar')).toBeInTheDocument()
    expect(submitButton).toBeDisabled()
  })

  it('dismisses error message when close button is clicked', async () => {
    const user = userEvent.setup()
    const mockError = {
      response: { status: 401 },
    }

    vi.mocked(authApi.login).mockRejectedValue(mockError)

    render(<LoginPage />, { wrapper: TestWrapper })

    const emailInput = screen.getByLabelText('Email Address')
    const passwordInput = screen.getByLabelText('Password')
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'WrongPassword')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Invalid email or password. Please try again.')).toBeInTheDocument()
    })

    // Find and click the close button in the alert
    const closeButton = screen.getByRole('button', { name: /close/i })
    await user.click(closeButton)

    expect(screen.queryByText('Invalid email or password. Please try again.')).not.toBeInTheDocument()
  })

  it('navigates to register page when Create Account link is clicked', async () => {
    render(<LoginPage />, { wrapper: TestWrapper })

    const createAccountLink = screen.getByText('Create Account')
    
    // Since it's a Link component, we can't test navigation directly in this setup
    // but we can verify the link exists and has the correct href
    expect(createAccountLink.closest('a')).toHaveAttribute('href', '/register')
  })
})