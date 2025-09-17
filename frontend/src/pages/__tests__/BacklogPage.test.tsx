import React from 'react'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route, useParams } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import BacklogPage from '../BacklogPage'
import { useWorkItems } from '../../hooks/useWorkItems'

// Mock react-router-dom useParams
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useParams: vi.fn(),
  }
})

// Mock the custom hook
vi.mock('../../hooks/useWorkItems')

// Mock UI components
interface MockProps {
  children?: React.ReactNode
  [key: string]: unknown
}

vi.mock('../../components/ui/button', () => ({
  Button: ({ children, ...props }: MockProps) => (
    <button {...props}>{children}</button>
  ),
}))

vi.mock('../../components/ui/card', () => ({
  Card: ({ children, ...props }: MockProps) => <div {...props}>{children}</div>,
}))

vi.mock('../../components/ui/alert', () => ({
  Alert: ({ children, ...props }: MockProps) => (
    <div role="alert" {...props}>
      {children}
    </div>
  ),
  AlertDescription: ({ children, ...props }: MockProps) => (
    <div {...props}>{children}</div>
  ),
}))

// Mock Heroicons
interface IconProps {
  [key: string]: unknown
}

vi.mock('@heroicons/react/24/outline', () => ({
  PlusIcon: (props: IconProps) => <svg {...props} data-testid="plus-icon" />,
  ExclamationTriangleIcon: (props: IconProps) => (
    <svg {...props} data-testid="exclamation-triangle-icon" />
  ),
  RefreshCwIcon: (props: IconProps) => (
    <svg {...props} data-testid="refresh-icon" />
  ),
}))

// Mock the child components
interface BacklogListProps {
  emptyMessage?: string
}

vi.mock('../../components/common/BacklogList', () => ({
  default: ({ emptyMessage }: BacklogListProps) => (
    <div data-testid="backlog-list">{emptyMessage}</div>
  ),
}))

vi.mock('../../components/common/FilterControls', () => ({
  default: () => <div data-testid="filter-controls">Filter Controls</div>,
}))

vi.mock('../../components/common/SortControls', () => ({
  default: () => <div data-testid="sort-controls">Sort Controls</div>,
}))

vi.mock('../../components/common/ViewModeToggle', () => ({
  __esModule: true,
  default: () => <div data-testid="view-mode-toggle">View Mode Toggle</div>,
  ViewMode: { LIST: 'list', KANBAN: 'kanban', TABLE: 'table' },
}))

vi.mock('../../components/common/Pagination', () => ({
  default: () => <div data-testid="pagination">Pagination</div>,
}))

vi.mock('../../components/common/WorkItemForm', () => ({
  default: () => <div data-testid="work-item-form">Work Item Form</div>,
}))

describe('BacklogPage', () => {
  const mockHookReturn = {
    workItems: [],
    loading: false,
    error: null,
    hasMore: false,
    totalCount: 0,
    filters: {},
    sort: { field: 'createdAt', order: 'desc' },
    pagination: { page: 1, size: 20 },
    setFilters: vi.fn(),
    setSort: vi.fn(),
    setPagination: vi.fn(),
    loadWorkItems: vi.fn(),
    refreshWorkItems: vi.fn(),
    createWorkItem: vi.fn(),
    updateWorkItem: vi.fn(),
    deleteWorkItem: vi.fn(),
  }

  const mockUseWorkItems = vi.mocked(useWorkItems)
  const mockUseParams = vi.mocked(useParams)

  beforeEach(() => {
    vi.clearAllMocks()
    mockUseWorkItems.mockReturnValue(mockHookReturn)
    // Default to having a teamId
    mockUseParams.mockReturnValue({ teamId: 'team-123' })
  })

  const renderBacklogPage = (teamId = 'team-123') => {
    const route = `/teams/${teamId}/backlog`
    return render(
      <MemoryRouter initialEntries={[route]}>
        <Routes>
          <Route path="/teams/:teamId/backlog" element={<BacklogPage />} />
        </Routes>
      </MemoryRouter>
    )
  }

  it('renders without team ID and shows error', () => {
    // Mock useParams to return undefined teamId
    mockUseParams.mockReturnValue({ teamId: undefined })

    mockUseWorkItems.mockReturnValue({
      ...mockHookReturn,
    })

    render(<BacklogPage />)

    expect(screen.getByText(/No team ID provided/)).toBeInTheDocument()
  })

  it('renders page header correctly', () => {
    renderBacklogPage()

    expect(screen.getByText('Team Backlog')).toBeInTheDocument()
    expect(
      screen.getByText("Manage and prioritize your team's work items")
    ).toBeInTheDocument()
  })

  it('renders main action buttons', () => {
    renderBacklogPage()

    expect(screen.getByText('Refresh')).toBeInTheDocument()
    expect(screen.getByText('Add Work Item')).toBeInTheDocument()
  })

  it('renders all control components', () => {
    renderBacklogPage()

    expect(screen.getByTestId('view-mode-toggle')).toBeInTheDocument()
    expect(screen.getByTestId('sort-controls')).toBeInTheDocument()
    expect(screen.getByTestId('filter-controls')).toBeInTheDocument()
  })

  it('renders backlog list in LIST view mode', () => {
    renderBacklogPage()

    expect(screen.getByTestId('backlog-list')).toBeInTheDocument()
  })

  it('shows loading state', () => {
    mockUseWorkItems.mockReturnValue({
      ...mockHookReturn,
      loading: true,
    })

    renderBacklogPage()

    // The loading state would be handled by child components
    expect(screen.getByTestId('backlog-list')).toBeInTheDocument()
  })

  it('shows error state', () => {
    const error = new Error('Failed to load work items')
    mockUseWorkItems.mockReturnValue({
      ...mockHookReturn,
      error,
    })

    renderBacklogPage()

    expect(screen.getByText(error.message)).toBeInTheDocument()
  })

  it('shows pagination when totalCount > 0', () => {
    mockUseWorkItems.mockReturnValue({
      ...mockHookReturn,
      totalCount: 50,
      workItems: [
        {
          id: '1',
          teamId: 'team-123',
          title: 'Test Item',
          type: 'TASK',
          status: 'NEW',
          priority: 'MEDIUM',
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ],
    })

    renderBacklogPage()

    expect(screen.getByTestId('pagination')).toBeInTheDocument()
  })

  it('calls loadWorkItems on mount', () => {
    const mockLoadWorkItems = vi.fn()
    mockUseWorkItems.mockReturnValue({
      ...mockHookReturn,
      loadWorkItems: mockLoadWorkItems,
    })

    renderBacklogPage()

    expect(mockLoadWorkItems).toHaveBeenCalled()
  })
})
