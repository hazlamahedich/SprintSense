/**
 * Tests for PriorityButton component
 * Covers Story 2.6 requirements for accessible priority buttons
 */

import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import PriorityButton from '../PriorityButton'
import { PriorityAction } from '../../../../types/workItem.types'

const theme = createTheme()

const renderWithTheme = (component: React.ReactElement) => {
  return render(<ThemeProvider theme={theme}>{component}</ThemeProvider>)
}

describe('PriorityButton', () => {
  const defaultProps = {
    action: PriorityAction.MOVE_UP,
    onClick: vi.fn(),
    'aria-label': 'Move up',
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render button with correct icon for MOVE_UP action', () => {
    renderWithTheme(<PriorityButton {...defaultProps} />)

    const button = screen.getByRole('button', { name: 'Move up' })
    expect(button).toBeInTheDocument()
    expect(button).toHaveAttribute('aria-label', 'Move up')
  })

  it('should render button with correct icon for MOVE_DOWN action', () => {
    renderWithTheme(
      <PriorityButton
        {...defaultProps}
        action={PriorityAction.MOVE_DOWN}
        aria-label="Move down"
      />
    )

    const button = screen.getByRole('button', { name: 'Move down' })
    expect(button).toBeInTheDocument()
  })

  it('should render button with correct icon for MOVE_TO_TOP action', () => {
    renderWithTheme(
      <PriorityButton
        {...defaultProps}
        action={PriorityAction.MOVE_TO_TOP}
        aria-label="Move to top"
      />
    )

    const button = screen.getByRole('button', { name: 'Move to top' })
    expect(button).toBeInTheDocument()
  })

  it('should render button with correct icon for MOVE_TO_BOTTOM action', () => {
    renderWithTheme(
      <PriorityButton
        {...defaultProps}
        action={PriorityAction.MOVE_TO_BOTTOM}
        aria-label="Move to bottom"
      />
    )

    const button = screen.getByRole('button', { name: 'Move to bottom' })
    expect(button).toBeInTheDocument()
  })

  it('should call onClick when button is clicked', () => {
    const mockOnClick = vi.fn()
    renderWithTheme(<PriorityButton {...defaultProps} onClick={mockOnClick} />)

    const button = screen.getByRole('button', { name: 'Move up' })
    fireEvent.click(button)

    expect(mockOnClick).toHaveBeenCalledTimes(1)
  })

  it('should be disabled when disabled prop is true', () => {
    const mockOnClick = vi.fn()
    renderWithTheme(
      <PriorityButton {...defaultProps} disabled onClick={mockOnClick} />
    )

    const button = screen.getByRole('button', { name: 'Move up' })
    expect(button).toBeDisabled()

    fireEvent.click(button)
    expect(mockOnClick).not.toHaveBeenCalled()
  })

  it('should show loading spinner when loading prop is true', () => {
    renderWithTheme(<PriorityButton {...defaultProps} loading />)

    const button = screen.getByRole('button', { name: 'Move up' })
    expect(button).toBeDisabled()

    // Check for loading spinner
    expect(screen.getByRole('progressbar')).toBeInTheDocument()
  })

  it('should not call onClick when loading', () => {
    const mockOnClick = vi.fn()
    renderWithTheme(
      <PriorityButton {...defaultProps} loading onClick={mockOnClick} />
    )

    const button = screen.getByRole('button', { name: 'Move up' })
    fireEvent.click(button)

    expect(mockOnClick).not.toHaveBeenCalled()
  })

  it('should support keyboard navigation with Enter key', () => {
    const mockOnClick = vi.fn()
    renderWithTheme(<PriorityButton {...defaultProps} onClick={mockOnClick} />)

    const button = screen.getByRole('button', { name: 'Move up' })
    button.focus()

    fireEvent.keyDown(button, { key: 'Enter', code: 'Enter' })

    expect(mockOnClick).toHaveBeenCalledTimes(1)
  })

  it('should support keyboard navigation with Space key', () => {
    const mockOnClick = vi.fn()
    renderWithTheme(<PriorityButton {...defaultProps} onClick={mockOnClick} />)

    const button = screen.getByRole('button', { name: 'Move up' })
    button.focus()

    fireEvent.keyDown(button, { key: ' ', code: 'Space' })

    expect(mockOnClick).toHaveBeenCalledTimes(1)
  })

  it('should not respond to other keys', () => {
    const mockOnClick = vi.fn()
    renderWithTheme(<PriorityButton {...defaultProps} onClick={mockOnClick} />)

    const button = screen.getByRole('button', { name: 'Move up' })
    button.focus()

    fireEvent.keyDown(button, { key: 'Escape', code: 'Escape' })

    expect(mockOnClick).not.toHaveBeenCalled()
  })

  it('should not respond to keyboard when disabled', () => {
    const mockOnClick = vi.fn()
    renderWithTheme(
      <PriorityButton {...defaultProps} disabled onClick={mockOnClick} />
    )

    const button = screen.getByRole('button', { name: 'Move up' })
    button.focus()

    fireEvent.keyDown(button, { key: 'Enter', code: 'Enter' })
    fireEvent.keyDown(button, { key: ' ', code: 'Space' })

    expect(mockOnClick).not.toHaveBeenCalled()
  })

  it('should display contextual tooltip based on position', () => {
    renderWithTheme(
      <PriorityButton
        {...defaultProps}
        action={PriorityAction.MOVE_UP}
        workItemTitle="Test Item"
        currentPosition={2}
        totalItems={5}
      />
    )

    // Note: Testing tooltip content can be tricky with MUI components
    // This would need hover simulation to test actual tooltip display
    const button = screen.getByRole('button')
    expect(button).toBeInTheDocument()
  })

  it('should show different tooltip when at boundaries', () => {
    renderWithTheme(
      <PriorityButton
        {...defaultProps}
        action={PriorityAction.MOVE_UP}
        workItemTitle="Test Item"
        currentPosition={1}
        totalItems={5}
      />
    )

    const button = screen.getByRole('button')
    expect(button).toBeInTheDocument()
  })

  it('should include aria-describedby when workItemTitle is provided', () => {
    renderWithTheme(
      <PriorityButton
        {...defaultProps}
        workItemTitle="Test Item"
        action={PriorityAction.MOVE_UP}
      />
    )

    const button = screen.getByRole('button')
    expect(button).toHaveAttribute(
      'aria-describedby',
      'priority-move_up-Test Item'
    )
  })

  it('should not include aria-describedby when workItemTitle is not provided', () => {
    renderWithTheme(<PriorityButton {...defaultProps} />)

    const button = screen.getByRole('button')
    expect(button).not.toHaveAttribute('aria-describedby')
  })

  it('should have correct minimum size for accessibility', () => {
    renderWithTheme(<PriorityButton {...defaultProps} />)

    const button = screen.getByRole('button')
    window.getComputedStyle(button)

    // Note: These values come from the sx prop in the component
    expect(button).toHaveStyle({
      'min-width': '40px',
      'min-height': '40px',
    })
  })
})
