import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { WorkItemSprintAssignment } from '../WorkItemSprintAssignment'
import { WorkItemSprintService } from '../../services/workItemSprintService'
import { useToast } from '../../hooks/useToast'

// Mock dependencies
vi.mock('../../services/workItemSprintService')
vi.mock('../../hooks/useToast')

describe('WorkItemSprintAssignment', () => {
  const mockWorkItem = {
    id: '123',
    sprintId: null,
    version: 1,
    title: 'Test Work Item',
  }

  const mockSprints = [
    { id: 'sprint1', name: 'Sprint 1', status: 'Future' },
    { id: 'sprint2', name: 'Sprint 2', status: 'Active' },
    { id: 'sprint3', name: 'Sprint 3', status: 'Future' },
  ]

  const mockOnAssign = vi.fn()
  const mockShowToast = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    ;(useToast as any).mockReturnValue({ showToast: mockShowToast })
    ;(WorkItemSprintService.subscribeToWorkItemUpdates as any).mockReturnValue(
      vi.fn()
    )
  })

  it('renders only Future sprints in dropdown', () => {
    render(
      <WorkItemSprintAssignment
        workItem={mockWorkItem}
        onAssign={mockOnAssign}
        sprints={mockSprints}
      />
    )

    const options = screen.getAllByRole('option')
    expect(options).toHaveLength(3) // "No Sprint" + 2 Future sprints
    expect(options[1].textContent).toBe('Sprint 1')
    expect(options[2].textContent).toBe('Sprint 3')
  })

  it('handles sprint assignment successfully', async () => {
    const updatedWorkItem = {
      ...mockWorkItem,
      sprintId: 'sprint1',
      version: 2,
    }

    ;(WorkItemSprintService.assignToSprint as any).mockResolvedValueOnce({
      workItemId: '123',
      sprintId: 'sprint1',
      version: 2,
    })

    render(
      <WorkItemSprintAssignment
        workItem={mockWorkItem}
        onAssign={mockOnAssign}
        sprints={mockSprints}
      />
    )

    const select = screen.getByRole('combobox')
    fireEvent.change(select, { target: { value: 'sprint1' } })

    await waitFor(() => {
      expect(WorkItemSprintService.assignToSprint).toHaveBeenCalledWith(
        '123',
        'sprint1',
        1
      )
      expect(mockOnAssign).toHaveBeenCalledWith(
        expect.objectContaining(updatedWorkItem)
      )
      expect(mockShowToast).toHaveBeenCalledWith(
        expect.objectContaining({
          status: 'success',
          title: 'Success',
        })
      )
    })
  })

  it('handles error during sprint assignment', async () => {
    const error = new Error('Assignment failed')
    ;(WorkItemSprintService.assignToSprint as any).mockRejectedValueOnce(error)

    render(
      <WorkItemSprintAssignment
        workItem={mockWorkItem}
        onAssign={mockOnAssign}
        sprints={mockSprints}
      />
    )

    const select = screen.getByRole('combobox')
    fireEvent.change(select, { target: { value: 'sprint1' } })

    await waitFor(() => {
      expect(mockShowToast).toHaveBeenCalledWith(
        expect.objectContaining({
          status: 'error',
          title: 'Error',
          description: 'Assignment failed',
        })
      )
      expect(screen.getByText('Assignment failed')).toBeInTheDocument()
    })
  })

  it('handles removing work item from sprint', async () => {
    const workItemWithSprint = {
      ...mockWorkItem,
      sprintId: 'sprint1',
    }

    ;(WorkItemSprintService.assignToSprint as any).mockResolvedValueOnce({
      workItemId: '123',
      sprintId: null,
      version: 2,
    })

    render(
      <WorkItemSprintAssignment
        workItem={workItemWithSprint}
        onAssign={mockOnAssign}
        sprints={mockSprints}
      />
    )

    const select = screen.getByRole('combobox')
    fireEvent.change(select, { target: { value: '' } })

    await waitFor(() => {
      expect(WorkItemSprintService.assignToSprint).toHaveBeenCalledWith(
        '123',
        null,
        1
      )
      expect(mockShowToast).toHaveBeenCalledWith(
        expect.objectContaining({
          status: 'success',
          description: 'Work item removed from sprint',
        })
      )
    })
  })

  it('disables select during loading state', async () => {
    let resolveAssignment: (value: any) => void
    const assignmentPromise = new Promise((resolve) => {
      resolveAssignment = resolve
    })

    ;(WorkItemSprintService.assignToSprint as any).mockReturnValue(
      assignmentPromise
    )

    render(
      <WorkItemSprintAssignment
        workItem={mockWorkItem}
        onAssign={mockOnAssign}
        sprints={mockSprints}
      />
    )

    const select = screen.getByRole('combobox')
    fireEvent.change(select, { target: { value: 'sprint1' } })

    expect(select).toBeDisabled()
    expect(
      screen.getByText('Updating sprint assignment...')
    ).toBeInTheDocument()

    resolveAssignment!({
      workItemId: '123',
      sprintId: 'sprint1',
      version: 2,
    })

    await waitFor(() => {
      expect(select).not.toBeDisabled()
      expect(
        screen.queryByText('Updating sprint assignment...')
      ).not.toBeInTheDocument()
    })
  })
})
