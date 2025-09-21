import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { vi } from 'vitest'
import { SprintStatus, type Sprint } from '@/types/sprint'
import { SprintList } from '@/components/sprints/SprintList'
import { useSprintStore } from '@/stores/sprintStore'

// Mock the sprint store
vi.mock('@/stores/sprintStore', () => ({
  useSprintStore: vi.fn(),
}))

describe('SprintList', () => {
  const mockSprints: Sprint[] = [
    {
      id: '1',
      teamId: 'team-1',
      name: 'Active Sprint',
      status: SprintStatus.ACTIVE,
      startDate: '2025-01-01',
      endDate: '2025-01-15',
      goal: 'Active sprint goal',
      createdAt: '2025-01-01T00:00:00Z',
      updatedAt: '2025-01-01T00:00:00Z',
    },
    {
      id: '2',
      teamId: 'team-1',
      name: 'Future Sprint',
      status: SprintStatus.FUTURE,
      startDate: '2025-02-01',
      endDate: '2025-02-15',
      goal: 'Future sprint goal',
      createdAt: '2025-01-01T00:00:00Z',
      updatedAt: '2025-01-01T00:00:00Z',
    },
    {
      id: '3',
      teamId: 'team-1',
      name: 'Closed Sprint',
      status: SprintStatus.CLOSED,
      startDate: '2024-12-01',
      endDate: '2024-12-15',
      goal: 'Closed sprint goal',
      createdAt: '2024-12-01T00:00:00Z',
      updatedAt: '2024-12-15T00:00:00Z',
    },
  ]

  const mockHandleCreateClick = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    ;(useSprintStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
      sprints: mockSprints,
      activeSprintId: '1',
      updateSprintStatus: vi.fn(),
    })
  })

  it('displays sprints in correct sections', () => {
    render(<SprintList teamId="team-1" onCreateClick={mockHandleCreateClick} />)

    // Check section headings
    expect(screen.getByText('Active Sprint')).toBeInTheDocument()
    expect(screen.getByText('Future Sprints')).toBeInTheDocument()
    expect(screen.getByText('Closed Sprints')).toBeInTheDocument()

    // Check sprint names
    expect(screen.getByText('Active Sprint')).toBeInTheDocument()
    expect(screen.getByText('Future Sprint')).toBeInTheDocument()
    expect(screen.getByText('Closed Sprint')).toBeInTheDocument()
  })

  it('shows correct status indicators', () => {
    render(<SprintList teamId="team-1" onCreateClick={mockHandleCreateClick} />)

    // Check status chips
    expect(screen.getByText('Active')).toBeInTheDocument()
    expect(screen.getByText('Future')).toBeInTheDocument()
    expect(screen.getByText('Closed')).toBeInTheDocument()
  })

  it('shows empty state when no sprints exist', () => {
    ;(useSprintStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
      sprints: [],
      activeSprintId: null,
      updateSprintStatus: vi.fn(),
    })

    render(<SprintList teamId="team-1" onCreateClick={mockHandleCreateClick} />)

    expect(screen.getByText('No sprints found')).toBeInTheDocument()
  })

  it('triggers create sprint dialog when add button is clicked', () => {
    render(<SprintList teamId="team-1" onCreateClick={mockHandleCreateClick} />)

    const addButton = screen.getByRole('button', { name: 'Add Sprint' })
    fireEvent.click(addButton)

    expect(mockHandleCreateClick).toHaveBeenCalled()
  })
})
