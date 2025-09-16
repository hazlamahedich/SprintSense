import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

// Mock the health API
vi.mock('./services/api', () => ({
  healthApi: {
    checkHealth: vi.fn().mockResolvedValue({
      status: 'OK',
      service: 'SprintSense Backend'
    }),
    checkDetailedHealth: vi.fn().mockResolvedValue({
      status: 'OK',
      service: 'SprintSense Backend',
      database: 'connected',
      version: '0.1.0'
    })
  },
  authApi: {
    register: vi.fn(),
    setAuthToken: vi.fn(),
    removeAuthToken: vi.fn()
  }
}))

// Mock the store
vi.mock('./store/appStore', () => ({
  useAppStore: vi.fn()
}))

// Mock react-router-dom to control navigation
const mockNavigate = vi.fn()
const mockLocation = { pathname: '/test', search: '', hash: '', state: null, key: 'default' }
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    BrowserRouter: ({ children }: { children: React.ReactNode }) => <div data-testid="router">{children}</div>,
    Routes: ({ children }: { children: React.ReactNode }) => <div data-testid="routes">{children}</div>,
    Route: ({ element }: { element: React.ReactNode }) => <div data-testid="route">{element}</div>,
    Navigate: () => <div data-testid="navigate" />,
    useNavigate: () => mockNavigate,
    useLocation: () => mockLocation
  }
})

describe('App', () => {
  beforeEach(async () => {
    vi.clearAllMocks()
    
    // Mock store with authenticated user to access protected routes
    const { useAppStore } = await import('./store/appStore')
    const mockUseAppStore = vi.mocked(useAppStore)
    mockUseAppStore.mockReturnValue({
      initializeAuth: vi.fn(),
      setAuth: vi.fn(),
      clearAuth: vi.fn(),
      setLoading: vi.fn(),
      setError: vi.fn(),
      setHealthStatus: vi.fn(),
      user: {
        id: 'test-user-id',
        email: 'test@example.com',
        full_name: 'Test User',
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z'
      },
      accessToken: 'test-token',
      isAuthenticated: true,
      isLoading: false,
      error: null,
      healthStatus: null
    })
  })
  
  it('renders application with theme and router', () => {
    render(<App />)
    
    // Verify the app renders with router
    expect(screen.getByTestId('router')).toBeInTheDocument()
  })

  it('initializes authentication on mount', async () => {
    const mockInitializeAuth = vi.fn()
    const { useAppStore } = await import('./store/appStore')
    const mockUseAppStore = vi.mocked(useAppStore)
    mockUseAppStore.mockReturnValue({
      initializeAuth: mockInitializeAuth,
      setAuth: vi.fn(),
      clearAuth: vi.fn(),
      setLoading: vi.fn(),
      setError: vi.fn(),
      setHealthStatus: vi.fn(),
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      healthStatus: null
    })
    
    render(<App />)
    
    expect(mockInitializeAuth).toHaveBeenCalledOnce()
  })
})
