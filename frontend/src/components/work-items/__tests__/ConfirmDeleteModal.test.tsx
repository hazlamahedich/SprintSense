/**
 * Tests for ConfirmDeleteModal component (Story 2.5)
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import '@testing-library/jest-dom'
import { vi } from 'vitest'
import { ConfirmDeleteModal } from '../ConfirmDeleteModal'

// Mock the dialog components to simplify testing
vi.mock('../../ui/dialog', () => ({
  Dialog: ({ children, open, onOpenChange }: any) => (
    <div data-testid="dialog" data-open={open} onClick={onOpenChange}>
      {open && children}
    </div>
  ),
  DialogContent: ({ children, onKeyDown, ...props }: any) => (
    <div data-testid="dialog-content" onKeyDown={onKeyDown} {...props}>
      {children}
    </div>
  ),
  DialogHeader: ({ children }: any) => (
    <div data-testid="dialog-header">{children}</div>
  ),
  DialogTitle: ({ children, id }: any) => (
    <h2 data-testid="dialog-title" id={id}>
      {children}
    </h2>
  ),
  DialogFooter: ({ children }: any) => (
    <div data-testid="dialog-footer">{children}</div>
  ),
}))

// Mock the UI components
vi.mock('../../ui/button', () => ({
  Button: ({ children, onClick, disabled, variant, ref, ...props }: any) => (
    <button
      ref={ref}
      onClick={onClick}
      disabled={disabled}
      data-variant={variant}
      data-testid={`button-${variant || 'default'}`}
      {...props}
    >
      {children}
    </button>
  ),
}))

vi.mock('../../ui/alert', () => ({
  Alert: ({ children, className }: any) => (
    <div data-testid="alert" className={className}>
      {children}
    </div>
  ),
  AlertDescription: ({ children, id }: any) => (
    <div data-testid="alert-description" id={id}>
      {children}
    </div>
  ),
}))

describe('ConfirmDeleteModal', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    onConfirm: vi.fn().mockResolvedValue(undefined),
    workItemTitle: 'Test Work Item Title',
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders modal with correct title and content when open', () => {
    render(<ConfirmDeleteModal {...defaultProps} />)

    expect(screen.getByTestId('dialog')).toHaveAttribute('data-open', 'true')
    expect(screen.getByTestId('dialog-title')).toHaveTextContent(
      'Archive Work Item'
    )
    expect(screen.getByTestId('alert-description')).toBeInTheDocument()
    expect(screen.getByText(/Test Work Item Title/)).toBeInTheDocument()
  })

  it('does not render modal content when closed', () => {
    render(<ConfirmDeleteModal {...defaultProps} isOpen={false} />)

    expect(screen.getByTestId('dialog')).toHaveAttribute('data-open', 'false')
    expect(screen.queryByTestId('dialog-title')).not.toBeInTheDocument()
  })

  it('displays the correct work item title in the confirmation message', () => {
    const workItemTitle = 'My Special Work Item'
    render(
      <ConfirmDeleteModal {...defaultProps} workItemTitle={workItemTitle} />
    )

    expect(screen.getByText(/My Special Work Item/)).toBeInTheDocument()
    expect(
      screen.getByText(/Are you sure you want to archive/)
    ).toBeInTheDocument()
  })

  it('has correct accessibility attributes', () => {
    render(<ConfirmDeleteModal {...defaultProps} />)

    const dialogContent = screen.getByTestId('dialog-content')
    expect(dialogContent).toHaveAttribute('role', 'alertdialog')
    expect(dialogContent).toHaveAttribute('aria-modal', 'true')
    expect(dialogContent).toHaveAttribute(
      'aria-labelledby',
      'confirm-delete-title'
    )
    expect(dialogContent).toHaveAttribute(
      'aria-describedby',
      'confirm-delete-description'
    )

    const title = screen.getByTestId('dialog-title')
    expect(title).toHaveAttribute('id', 'confirm-delete-title')

    const description = screen.getByTestId('alert-description')
    expect(description).toHaveAttribute('id', 'confirm-delete-description')
  })

  it('calls onClose when Cancel button is clicked', async () => {
    const user = userEvent.setup()
    const mockOnClose = vi.fn()

    render(<ConfirmDeleteModal {...defaultProps} onClose={mockOnClose} />)

    const cancelButton = screen.getByTestId('button-outline')
    await user.click(cancelButton)

    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it('calls onConfirm when Archive button is clicked', async () => {
    const user = userEvent.setup()
    const mockOnConfirm = vi.fn().mockResolvedValue(undefined)

    render(<ConfirmDeleteModal {...defaultProps} onConfirm={mockOnConfirm} />)

    const archiveButton = screen.getByTestId('button-destructive')
    await user.click(archiveButton)

    expect(mockOnConfirm).toHaveBeenCalledTimes(1)
  })

  it('shows loading state when isLoading is true', () => {
    render(<ConfirmDeleteModal {...defaultProps} isLoading />)

    const archiveButton = screen.getByTestId('button-destructive')
    const cancelButton = screen.getByTestId('button-outline')

    expect(archiveButton).toHaveTextContent('Archiving...')
    expect(archiveButton).toBeDisabled()
    expect(cancelButton).toBeDisabled()
  })

  it('shows normal state when isLoading is false', () => {
    render(<ConfirmDeleteModal {...defaultProps} isLoading={false} />)

    const archiveButton = screen.getByTestId('button-destructive')
    const cancelButton = screen.getByTestId('button-outline')

    expect(archiveButton).toHaveTextContent('Archive')
    expect(archiveButton).not.toBeDisabled()
    expect(cancelButton).not.toBeDisabled()
  })

  it('prevents closing during loading state', async () => {
    const user = userEvent.setup()
    const mockOnClose = vi.fn()

    render(
      <ConfirmDeleteModal {...defaultProps} onClose={mockOnClose} isLoading />
    )

    // Try to click Cancel button during loading
    const cancelButton = screen.getByTestId('button-outline')
    await user.click(cancelButton)

    expect(mockOnClose).not.toHaveBeenCalled()
  })

  it('handles escape key to close modal when not loading', async () => {
    const mockOnClose = vi.fn()
    render(<ConfirmDeleteModal {...defaultProps} onClose={mockOnClose} />)

    const dialogContent = screen.getByTestId('dialog-content')
    fireEvent.keyDown(dialogContent, { key: 'Escape' })

    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it('prevents escape key from closing modal when loading', async () => {
    const mockOnClose = vi.fn()
    render(
      <ConfirmDeleteModal {...defaultProps} onClose={mockOnClose} isLoading />
    )

    const dialogContent = screen.getByTestId('dialog-content')
    fireEvent.keyDown(dialogContent, { key: 'Escape' })

    expect(mockOnClose).not.toHaveBeenCalled()
  })

  // Focus management test is complex to test in jsdom, skipping for now

  it('displays explanatory text about archiving behavior', () => {
    render(<ConfirmDeleteModal {...defaultProps} />)

    expect(
      screen.getByText(/This work item will be moved to the archived state/)
    ).toBeInTheDocument()
    expect(screen.getByText(/hidden from regular views/)).toBeInTheDocument()
    expect(screen.getByText(/This action can be undone/)).toBeInTheDocument()
  })

  it('has warning icon in the modal header', () => {
    render(<ConfirmDeleteModal {...defaultProps} />)

    // Check that the warning icon container is present
    const iconContainer = screen
      .getByTestId('dialog-header')
      .querySelector('.bg-red-100')
    expect(iconContainer).toBeInTheDocument()
  })

  it('prevents backdrop click from closing during loading', async () => {
    const mockOnClose = vi.fn()
    render(
      <ConfirmDeleteModal {...defaultProps} onClose={mockOnClose} isLoading />
    )

    const dialogContent = screen.getByTestId('dialog-content')
    fireEvent.click(dialogContent)

    // Should not close during loading
    expect(mockOnClose).not.toHaveBeenCalled()
  })

  it('correctly handles button variants and styling', () => {
    render(<ConfirmDeleteModal {...defaultProps} />)

    const cancelButton = screen.getByTestId('button-outline')
    const archiveButton = screen.getByTestId('button-destructive')

    expect(cancelButton).toHaveAttribute('data-variant', 'outline')
    expect(archiveButton).toHaveAttribute('data-variant', 'destructive')
  })
})
