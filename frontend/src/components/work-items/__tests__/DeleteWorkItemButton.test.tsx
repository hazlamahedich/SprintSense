/**
 * Tests for DeleteWorkItemButton component (Story 2.5)
 */

import React from 'react';
import '@heroicons/react/24/outline';
import { render, screen, waitFor, act } from '@testing-library/react'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import userEvent from '@testing-library/user-event'
import '@testing-library/jest-dom'
import { vi } from 'vitest'
import { DeleteWorkItemButton } from '../DeleteWorkItemButton'

// Mock the ConfirmDeleteModal component
vi.mock('../ConfirmDeleteModal', () => ({
  ConfirmDeleteModal: ({
    isOpen,
    onClose,
    onConfirm,
    workItemTitle,
    isLoading,
  }: {
    isOpen: boolean
    onClose: () => void
    onConfirm: () => Promise<void>
    workItemTitle: string
    isLoading: boolean
  }) => (
    <div data-testid="confirm-delete-modal" data-is-open={isOpen}>
      {isOpen && (
        <div>
          <div data-testid="modal-title">{workItemTitle}</div>
          <div data-testid="modal-loading">
            {isLoading ? 'Loading' : 'Not Loading'}
          </div>
          <button data-testid="modal-cancel" onClick={onClose}>
            Cancel
          </button>
          <button data-testid="modal-confirm" onClick={onConfirm}>
            Confirm
          </button>
        </div>
      )}
    </div>
  ),
}))

describe('DeleteWorkItemButton', () => {
  const defaultProps = {
    workItemId: 'test-work-item-id',
    workItemTitle: 'Test Work Item',
    teamId: 'test-team-id',
    onArchive: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders delete button with correct accessibility attributes', () => {
    render(<DeleteWorkItemButton {...defaultProps} />)

    const button = screen.getByRole('button', {
      name: /delete work item: test work item/i,
    })
    expect(button).toBeInTheDocument()
    expect(button).toHaveAttribute('title', 'Delete work item')
    expect(button).toHaveAttribute(
      'aria-label',
      'Delete work item: Test Work Item'
    )
  })

  it('opens confirmation modal when delete button is clicked', async () => {
    const user = userEvent.setup()
    render(<DeleteWorkItemButton {...defaultProps} />)

    const deleteButton = screen.getByRole('button', {
      name: /delete work item/i,
    })
    await user.click(deleteButton)

    expect(screen.getByTestId('modal-title')).toHaveTextContent(
      'Test Work Item'
    )
    expect(screen.getByTestId('modal-loading')).toHaveTextContent('Not Loading')
  })

  it('does not open modal when button is disabled', () => {
    render(<DeleteWorkItemButton {...defaultProps} disabled />)

    const deleteButton = screen.getByRole('button', {
      name: /delete work item/i,
    })
    expect(deleteButton).toBeDisabled()

    // Modal should not be rendered when button is disabled and not clicked
    expect(screen.queryByTestId('modal-title')).not.toBeInTheDocument()
  })

  it('calls onArchive when modal confirm is clicked', async () => {
    const user = userEvent.setup()
    const mockOnArchive = vi.fn().mockResolvedValue(undefined)

    render(<DeleteWorkItemButton {...defaultProps} onArchive={mockOnArchive} />)

    // Open modal
    const deleteButton = screen.getByRole('button', {
      name: /delete work item/i,
    })
    await user.click(deleteButton)

    // Confirm deletion
    const confirmButton = screen.getByTestId('modal-confirm')
    await user.click(confirmButton)

    expect(mockOnArchive).toHaveBeenCalledWith('test-work-item-id')
  })

  it('manages loading state during archive operation', async () => {
    const user = userEvent.setup()
    let resolveArchive: () => void
    const mockOnArchive = vi.fn().mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveArchive = resolve
        })
    )

    render(<DeleteWorkItemButton {...defaultProps} onArchive={mockOnArchive} />)

    // Open modal
    const deleteButton = screen.getByRole('button', {
      name: /delete work item/i,
    })
    await user.click(deleteButton)
    expect(screen.getByTestId('modal-title')).toBeInTheDocument()

    // Confirm deletion - this should start loading
    const confirmButton = screen.getByTestId('modal-confirm')
    await user.click(confirmButton)

    // Verify the archive function was called
    expect(mockOnArchive).toHaveBeenCalledWith('test-work-item-id')

    // Complete the operation
    resolveArchive!()

    // Verify modal closes after completion
    // Wait for loading state to be reflected
    await waitFor(() => {
      expect(screen.getByTestId('modal-loading')).toHaveTextContent('Loading')
    })

    // Wait for modal to close after archive completes
    await waitFor(() => {
      expect(screen.queryByTestId('modal-title')).not.toBeInTheDocument()
    })
  })

  it('handles archive failure gracefully', async () => {
    const user = userEvent.setup()
    const mockOnArchive = vi.fn().mockRejectedValue(new Error('Archive failed'))
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    render(<DeleteWorkItemButton {...defaultProps} onArchive={mockOnArchive} />)

    // Open modal
    const deleteButton = screen.getByRole('button', {
      name: /delete work item/i,
    })
    await user.click(deleteButton)

    // Confirm deletion
    const confirmButton = screen.getByTestId('modal-confirm')
    await user.click(confirmButton)

    await act(async () => {
      expect(consoleSpy).toHaveBeenCalledWith(
        'Failed to archive work item:',
        expect.any(Error)
      )
      expect(screen.getByTestId('modal-loading')).toHaveTextContent(
        'Not Loading'
      )
    })

    consoleSpy.mockRestore()
  })

  it('closes modal when cancel is clicked', async () => {
    const user = userEvent.setup()
    render(<DeleteWorkItemButton {...defaultProps} />)

    // Open modal
    const deleteButton = screen.getByRole('button', {
      name: /delete work item/i,
    })
    await user.click(deleteButton)

    expect(screen.getByTestId('modal-title')).toBeInTheDocument()

    // Cancel
    const cancelButton = screen.getByTestId('modal-cancel')
    await user.click(cancelButton)

    expect(screen.queryByTestId('modal-title')).not.toBeInTheDocument()
  })

  it('prevents modal close during loading', async () => {
    const user = userEvent.setup()
    const mockOnArchive = vi
      .fn()
      .mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      )

    render(<DeleteWorkItemButton {...defaultProps} onArchive={mockOnArchive} />)

    // Open modal
    const deleteButton = screen.getByRole('button', {
      name: /delete work item/i,
    })
    await user.click(deleteButton)

    // Start archive operation
    const confirmButton = screen.getByTestId('modal-confirm')
    await user.click(confirmButton)

    // Try to cancel during loading
    const cancelButton = screen.getByTestId('modal-cancel')
    await user.click(cancelButton)

    // Modal should still be open during loading
    expect(screen.getByTestId('modal-title')).toBeInTheDocument()
  })

  it('applies custom className and size props', () => {
    render(
      <DeleteWorkItemButton
        {...defaultProps}
        className="custom-class"
        size="lg"
      />
    )

    const button = screen.getByRole('button', { name: /delete work item/i })
    expect(button).toHaveClass('custom-class')
  })

  it('has correct styling classes for destructive action', () => {
    render(<DeleteWorkItemButton {...defaultProps} />)

    const button = screen.getByRole('button', { name: /delete work item/i })
    expect(button).toHaveClass('text-red-600')
    expect(button).toHaveClass('hover:text-red-800')
    expect(button).toHaveClass('hover:bg-red-50')
  })
})

