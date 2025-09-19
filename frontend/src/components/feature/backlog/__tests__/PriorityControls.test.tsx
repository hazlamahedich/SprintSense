/**
 * Tests for PriorityControls component
 * Covers Story 2.6 requirements for priority management functionality
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import PriorityControls from '../PriorityControls'
import { usePriorityUpdate } from '../../../../hooks/usePriorityUpdate'
import {
  PriorityAction,
  WorkItem,
  WorkItemType,
  WorkItemStatus,
} from '../../../../types/workItem.types'

// Mock the usePriorityUpdate hook
vi.mock('../../../../hooks/usePriorityUpdate')

const theme = createTheme()

const renderWithTheme = (component: React.ReactElement) => {
  return render(<ThemeProvider theme={theme}>{component}</ThemeProvider>)
}

describe('PriorityControls', () => {
  const mockWorkItem: WorkItem = {
    id: 'work-item-1',
    title: 'Test Work Item',
    description: 'Test description',
    priority: 5.0,
    type: WorkItemType.STORY,
    status: WorkItemStatus.BACKLOG,
    team_id: 'team-1',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
  }

  const defaultProps = {
    workItem: mockWorkItem,
    teamId: 'team-1',
    currentPosition: 2,
    totalItems: 5,
  }

  const mockUpdatePriority = vi.fn()
  const mockUsePriorityUpdate = {
    updatePriority: mockUpdatePriority,
    loading: false,
    error: null,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(usePriorityUpdate).mockReturnValue(mockUsePriorityUpdate)
  })

  it('should render all priority buttons', () => {
    renderWithTheme(<PriorityControls {...defaultProps} />)

    expect(
      screen.getByLabelText(
        /Move "Test Work Item" to top of backlog\. Position 2 of 5/
      )
    ).toBeInTheDocument()
    expect(
      screen.getByLabelText(
        /Move "Test Work Item" up one position\. Position 2 of 5/
      )
    ).toBeInTheDocument()
    expect(
      screen.getByLabelText(
        /Move "Test Work Item" down one position\. Position 2 of 5/
      )
    ).toBeInTheDocument()
    expect(
      screen.getByLabelText(
        /Move "Test Work Item" to bottom of backlog\. Position 2 of 5/
      )
    ).toBeInTheDocument()
  })

  it('should have proper group role and label', () => {
    renderWithTheme(<PriorityControls {...defaultProps} />)

    const group = screen.getByLabelText('Priority controls for Test Work Item')
    expect(group).toHaveAttribute('role', 'group')
  })

  it('should disable top buttons when item is at position 1', () => {
    renderWithTheme(<PriorityControls {...defaultProps} currentPosition={1} />)

    const moveToTopButton = screen.getByLabelText(
      /Move "Test Work Item" to top of backlog\. Position 1 of 5/
    )
    const moveUpButton = screen.getByLabelText(
      /Move "Test Work Item" up one position\. Position 1 of 5/
    )
    const moveDownButton = screen.getByLabelText(
      /Move "Test Work Item" down one position\. Position 1 of 5/
    )
    const moveToBottomButton = screen.getByLabelText(
      /Move "Test Work Item" to bottom of backlog\. Position 1 of 5/
    )

    expect(moveToTopButton).toBeDisabled()
    expect(moveUpButton).toBeDisabled()
    expect(moveDownButton).not.toBeDisabled()
    expect(moveToBottomButton).not.toBeDisabled()
  })

  it('should disable bottom buttons when item is at last position', () => {
    renderWithTheme(
      <PriorityControls {...defaultProps} currentPosition={5} totalItems={5} />
    )

    const moveToTopButton = screen.getByLabelText(
      /Move "Test Work Item" to top of backlog\. Position 5 of 5/
    )
    const moveUpButton = screen.getByLabelText(
      /Move "Test Work Item" up one position\. Position 5 of 5/
    )
    const moveDownButton = screen.getByLabelText(
      /Move "Test Work Item" down one position\. Position 5 of 5/
    )
    const moveToBottomButton = screen.getByLabelText(
      /Move "Test Work Item" to bottom of backlog\. Position 5 of 5/
    )

    expect(moveToTopButton).not.toBeDisabled()
    expect(moveUpButton).not.toBeDisabled()
    expect(moveDownButton).toBeDisabled()
    expect(moveToBottomButton).toBeDisabled()
  })

  it('should disable all buttons when there is only one item', () => {
    renderWithTheme(
      <PriorityControls {...defaultProps} currentPosition={1} totalItems={1} />
    )

    const buttons = screen.getAllByRole('button')
    buttons.forEach((button) => {
      expect(button).toBeDisabled()
    })
  })

  it('should disable all buttons when component is disabled', () => {
    renderWithTheme(<PriorityControls {...defaultProps} disabled />)

    const buttons = screen.getAllByRole('button')
    buttons.forEach((button) => {
      expect(button).toBeDisabled()
    })
  })

  it('should call updatePriority with correct parameters when move up is clicked', async () => {
    renderWithTheme(<PriorityControls {...defaultProps} />)

    const moveUpButton = screen.getByLabelText(
      /Move "Test Work Item" up one position\. Position 2 of 5/
    )
    fireEvent.click(moveUpButton)

    expect(mockUpdatePriority).toHaveBeenCalledWith({
      workItemId: 'work-item-1',
      teamId: 'team-1',
      action: PriorityAction.MOVE_UP,
      currentPriority: 5.0,
    })
  })

  it('should call updatePriority with correct parameters when move to top is clicked', async () => {
    renderWithTheme(<PriorityControls {...defaultProps} />)

    const moveToTopButton = screen.getByLabelText(
      /Move "Test Work Item" to top of backlog\. Position 2 of 5/
    )
    fireEvent.click(moveToTopButton)

    expect(mockUpdatePriority).toHaveBeenCalledWith({
      workItemId: 'work-item-1',
      teamId: 'team-1',
      action: PriorityAction.MOVE_TO_TOP,
      currentPriority: 5.0,
    })
  })

  it('should show loading state on all buttons when updating', () => {
    vi.mocked(usePriorityUpdate).mockReturnValue({
      ...mockUsePriorityUpdate,
      loading: true,
    })

    renderWithTheme(<PriorityControls {...defaultProps} />)

    const buttons = screen.getAllByRole('button')
    buttons.forEach((button) => {
      expect(button).toBeDisabled()
    })

    // Check for loading spinners
    expect(screen.getAllByRole('progressbar')).toHaveLength(4)
  })

  it('should display success snackbar when update succeeds', async () => {
    const mockOnSuccess = vi.fn()
    const updatedWorkItem = { ...mockWorkItem, priority: 6.0 }

    renderWithTheme(
      <PriorityControls {...defaultProps} onSuccess={mockOnSuccess} />
    )

    // Simulate the hook calling onSuccess
    const hookArgs = vi.mocked(usePriorityUpdate).mock.calls[0][0]
    hookArgs.onSuccess?.(updatedWorkItem)

    await waitFor(() => {
      expect(
        screen.getByText(/Priority updated successfully for "Test Work Item"/)
      ).toBeInTheDocument()
    })

    expect(mockOnSuccess).toHaveBeenCalledWith(updatedWorkItem)
  })

  it('should display error snackbar when update fails', async () => {
    const mockOnError = vi.fn()
    const errorMessage = 'Failed to update priority'

    renderWithTheme(
      <PriorityControls {...defaultProps} onError={mockOnError} />
    )

    // Simulate the hook calling onError
    const hookArgs = vi.mocked(usePriorityUpdate).mock.calls[0][0]
    hookArgs.onError?.(errorMessage)

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument()
    })

    expect(mockOnError).toHaveBeenCalledWith(errorMessage)
  })

  it('should display conflict snackbar when update has conflict', async () => {
    const mockOnConflict = vi.fn()
    const conflictMessage = 'Priority has been updated by another user'

    renderWithTheme(
      <PriorityControls {...defaultProps} onConflict={mockOnConflict} />
    )

    // Simulate the hook calling onConflict
    const hookArgs = vi.mocked(usePriorityUpdate).mock.calls[0][0]
    hookArgs.onConflict?.(conflictMessage)

    await waitFor(() => {
      expect(screen.getByText(conflictMessage)).toBeInTheDocument()
    })

    expect(mockOnConflict).toHaveBeenCalledWith(conflictMessage)
  })

  it('should close snackbar when close button is clicked', async () => {
    renderWithTheme(<PriorityControls {...defaultProps} />)

    // Simulate success to show snackbar
    const hookArgs = vi.mocked(usePriorityUpdate).mock.calls[0][0]
    const updatedWorkItem = { ...mockWorkItem, priority: 6.0 }
    hookArgs.onSuccess?.(updatedWorkItem)

    await waitFor(() => {
      expect(
        screen.getByText(/Priority updated successfully/)
      ).toBeInTheDocument()
    })

    const closeButton = screen.getByRole('button', { name: /close/i })
    fireEvent.click(closeButton)

    await waitFor(() => {
      expect(
        screen.queryByText(/Priority updated successfully/)
      ).not.toBeInTheDocument()
    })
  })

  it('should not call updatePriority when disabled and button is clicked', () => {
    renderWithTheme(<PriorityControls {...defaultProps} disabled />)

    const moveUpButton = screen.getByLabelText(
      /Move "Test Work Item" up one position\. Position 2 of 5/
    )
    fireEvent.click(moveUpButton)

    expect(mockUpdatePriority).not.toHaveBeenCalled()
  })

  it('should include position information in aria labels', () => {
    renderWithTheme(<PriorityControls {...defaultProps} />)

    const moveUpButton = screen.getByLabelText(
      /Move "Test Work Item" up one position\. Position 2 of 5/
    )
    expect(moveUpButton).toBeInTheDocument()
  })

  it('should handle missing position information gracefully', () => {
    renderWithTheme(
      <PriorityControls workItem={mockWorkItem} teamId="team-1" />
    )

    // Should still render but may have different behavior
    const group = screen.getByLabelText('Priority controls for Test Work Item')
    expect(group).toBeInTheDocument()
  })
})
