import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { vi } from 'vitest'
import { SprintStatus } from '@/types/sprint'
import { SprintStatusButton } from '@/components/sprints/SprintStatusButton'

describe('SprintStatusButton', () => {
  const mockOnStart = vi.fn()
  const mockOnClose = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('displays start button for future sprint', () => {
    render(
      <SprintStatusButton
        disabled={false}
        currentStatus={SprintStatus.FUTURE}
        onStart={mockOnStart}
        onClose={mockOnClose}
      />
    )

    const button = screen.getByRole('button', { name: 'Start Sprint' })
    expect(button).toBeEnabled()
    expect(button).toHaveTextContent('Start Sprint')
  })

  it('disables button when another sprint is active', () => {
    render(
      <SprintStatusButton
        disabled={true}
        currentStatus={SprintStatus.FUTURE}
        onStart={mockOnStart}
        onClose={mockOnClose}
      />
    )

    const button = screen.getByRole('button', { name: 'Start Sprint' })
    expect(button).toBeDisabled()
  })

  it('shows close button for active sprint', () => {
    render(
      <SprintStatusButton
        disabled={false}
        currentStatus={SprintStatus.ACTIVE}
        onStart={mockOnStart}
        onClose={mockOnClose}
      />
    )

    const button = screen.getByRole('button', { name: 'Close Sprint' })
    expect(button).toBeEnabled()
    expect(button).toHaveTextContent('Close Sprint')
  })

  it('updates sprint status correctly when clicking start', () => {
    render(
      <SprintStatusButton
        disabled={false}
        currentStatus={SprintStatus.FUTURE}
        onStart={mockOnStart}
        onClose={mockOnClose}
      />
    )

    const button = screen.getByRole('button', { name: 'Start Sprint' })
    fireEvent.click(button)
    expect(mockOnStart).toHaveBeenCalled()
    expect(mockOnClose).not.toHaveBeenCalled()
  })

  it('updates sprint status correctly when clicking close', () => {
    render(
      <SprintStatusButton
        disabled={false}
        currentStatus={SprintStatus.ACTIVE}
        onStart={mockOnStart}
        onClose={mockOnClose}
      />
    )

    const button = screen.getByRole('button', { name: 'Close Sprint' })
    fireEvent.click(button)
    expect(mockOnClose).toHaveBeenCalled()
    expect(mockOnStart).not.toHaveBeenCalled()
  })

  it('shows disabled button for closed sprint', () => {
    render(
      <SprintStatusButton
        disabled={false}
        currentStatus={SprintStatus.CLOSED}
        onStart={mockOnStart}
        onClose={mockOnClose}
      />
    )

    const button = screen.getByRole('button', { name: 'Closed' })
    expect(button).toBeDisabled()
    expect(button).toHaveTextContent('Closed')
  })
})
