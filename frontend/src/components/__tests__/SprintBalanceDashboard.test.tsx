import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { SprintBalanceDashboard } from '../SprintBalanceDashboard'
import { useSprintBalance } from '@/hooks/useSprintBalance'
import { vi } from 'vitest'

// Mock UI components
vi.mock('@/components/ui/alert', () => ({
  Alert: ({ children, ...props }) => <div {...props}>{children}</div>,
  AlertTitle: ({ children }) => <div>{children}</div>,
  AlertDescription: ({ children }) => <div>{children}</div>,
}))

vi.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick, ...props }) => (
    <button onClick={onClick} {...props}>
      {children}
    </button>
  ),
}))

vi.mock('@/components/ui/card', () => ({
  Card: ({ children, ...props }) => <div {...props}>{children}</div>,
  CardHeader: ({ children }) => <div>{children}</div>,
  CardContent: ({ children }) => <div>{children}</div>,
}))

vi.mock('@/components/ui/badge', () => ({
  Badge: ({ children }) => <div>{children}</div>,
}))

// Mock the hook
vi.mock('@/hooks/useSprintBalance', () => ({
  useSprintBalance: vi.fn(),
}))

// Mock chart.js
vi.mock('react-chartjs-2', () => ({
  Chart: () => null,
}))

const mockBalanceMetrics = {
  overallBalanceScore: 0.85,
  teamUtilization: 0.75,
  skillCoverage: 0.9,
  workloadDistribution: {
    'user-1': 35.5,
    'user-2': 28.5,
  },
  bottlenecks: ['High workload for team member user-1'],
  recommendations: [
    'Consider redistributing work from user-1 to user-2',
    'Sprint balance looks good overall',
  ],
}

describe('SprintBalanceDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state', () => {
    ;(useSprintBalance as jest.Mock).mockReturnValue({
      balanceMetrics: null,
      isLoading: true,
      isError: false,
      error: null,
      refreshBalance: vi.fn(),
    })

    render(<SprintBalanceDashboard sprintId="test-sprint" />)

    expect(screen.getAllByTestId('skeleton')).toHaveLength(4)
  })

  it('renders error state', () => {
    const error = new Error('Failed to load data')
    ;(useSprintBalance as jest.Mock).mockReturnValue({
      balanceMetrics: null,
      isLoading: false,
      isError: true,
      error,
      refreshBalance: vi.fn(),
    })

    render(<SprintBalanceDashboard sprintId="test-sprint" />)

    expect(
      screen.getByText(`Failed to load sprint balance data. ${error.message}`)
    ).toBeInTheDocument()
  })

  it('renders empty state', () => {
    ;(useSprintBalance as jest.Mock).mockReturnValue({
      balanceMetrics: null,
      isLoading: false,
      isError: false,
      error: null,
      refreshBalance: vi.fn(),
    })

    render(<SprintBalanceDashboard sprintId="test-sprint" />)

    expect(
      screen.getByText(/No sprint balance data available/i)
    ).toBeInTheDocument()
  })

  it('renders balance metrics', () => {
    const refreshBalance = vi.fn()
    ;(useSprintBalance as jest.Mock).mockReturnValue({
      balanceMetrics: mockBalanceMetrics,
      isLoading: false,
      isError: false,
      error: null,
      refreshBalance,
    })

    render(<SprintBalanceDashboard sprintId="test-sprint" />)

    // Check metrics
    expect(screen.getByText('85%')).toBeInTheDocument() // Overall balance
    expect(screen.getByText('75%')).toBeInTheDocument() // Team utilization
    expect(screen.getByText('90%')).toBeInTheDocument() // Skill coverage

    // Check bottlenecks
    expect(
      screen.getByText(/High workload for team member user-1/i)
    ).toBeInTheDocument()

    // Check recommendations
    mockBalanceMetrics.recommendations.forEach((recommendation) => {
      expect(screen.getByText(recommendation)).toBeInTheDocument()
    })
  })

  it('handles refresh click', async () => {
    const refreshBalance = vi.fn()
    ;(useSprintBalance as jest.Mock).mockReturnValue({
      balanceMetrics: mockBalanceMetrics,
      isLoading: false,
      isError: false,
      error: null,
      refreshBalance,
    })

    render(<SprintBalanceDashboard sprintId="test-sprint" />)

    const refreshButton = screen.getByRole('button', { name: /refresh/i })
    fireEvent.click(refreshButton)

    await waitFor(() => {
      expect(refreshBalance).toHaveBeenCalledTimes(1)
    })
  })

  it('updates when metrics change', () => {
    const initialMetrics = { ...mockBalanceMetrics }
    const updatedMetrics = {
      ...mockBalanceMetrics,
      overallBalanceScore: 0.95,
      recommendations: ['Sprint balance improved'],
    }

    const { rerender } = render(
      <SprintBalanceDashboard sprintId="test-sprint" />
    )

    // Initial render
    ;(useSprintBalance as jest.Mock).mockReturnValue({
      balanceMetrics: initialMetrics,
      isLoading: false,
      isError: false,
      error: null,
      refreshBalance: vi.fn(),
    })

    expect(screen.getByText('85%')).toBeInTheDocument()

    // Update metrics
    ;(useSprintBalance as jest.Mock).mockReturnValue({
      balanceMetrics: updatedMetrics,
      isLoading: false,
      isError: false,
      error: null,
      refreshBalance: vi.fn(),
    })

    rerender(<SprintBalanceDashboard sprintId="test-sprint" />)

    expect(screen.getByText('95%')).toBeInTheDocument()
    expect(screen.getByText('Sprint balance improved')).toBeInTheDocument()
  })
})
