import React from 'react'
import { vi, beforeAll } from 'vitest'
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react'
import { ThemeProvider, createTheme } from '@mui/material'
import { IncompleteWorkDialog } from '../IncompleteWorkDialog'
import { getIncompleteItems, completeSprint } from '../../../api/sprint'

// Import framer-motion mocks
import '../../../test/mocks/framer-motion'

// Mock API functions
vi.mock('../../../api/sprint', () => ({
  getIncompleteItems: vi.fn(),
  completeSprint: vi.fn(),
}))

// Mock data
const mockItems = [
  {
    id: '1',
    title: 'Task 1',
    status: 'In Progress',
    points: 5,
    assignee_name: 'John Doe',
    created_at: '2025-09-24T12:00:00Z',
  },
  {
    id: '2',
    title: 'Task 2',
    status: 'To Do',
    points: 3,
    assignee_name: 'Jane Smith',
    created_at: '2025-09-24T12:00:00Z',
  },
]

const mockTheme = createTheme()

const defaultProps = {
  open: true,
  sprintId: 'sprint-123',
  onClose: vi.fn(),
  onCompleted: vi.fn(),
}

describe('IncompleteWorkDialog', () => {
  beforeAll(() => {
    // Mock window.matchMedia for framer-motion
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation((query) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    })
  })

  beforeEach(() => {
    vi.resetAllMocks()
    ;(getIncompleteItems as any).mockResolvedValue(mockItems)
    ;(completeSprint as any).mockResolvedValue({
      moved_count: 2,
      target: 'backlog',
    })
  })

  it('loads and displays incomplete items', async () => {
    render(
      <ThemeProvider theme={mockTheme}>
        <IncompleteWorkDialog {...defaultProps} />
      </ThemeProvider>
    )

    // Shows loading initially
    expect(screen.getByRole('progressbar')).toBeInTheDocument()

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
    })

    // Now check the table content
    expect(screen.getByRole('cell', { name: 'Task 1' })).toBeInTheDocument()
    expect(screen.getByRole('cell', { name: 'Task 2' })).toBeInTheDocument()

    // Check summary is correct
    expect(screen.getByText(/2 incomplete items/)).toBeInTheDocument()
    expect(screen.getByText(/8 points/)).toBeInTheDocument()
  })

  it('handles error loading items', async () => {
    ;(getIncompleteItems as any).mockRejectedValue(new Error('Failed to load'))

    render(
      <ThemeProvider theme={mockTheme}>
        <IncompleteWorkDialog {...defaultProps} />
      </ThemeProvider>
    )

    await waitFor(() => {
      expect(screen.getByText(/Failed to load/)).toBeInTheDocument()
    })
  })

  it('moves items to backlog', async () => {
    await act(async () => {
      render(
        <ThemeProvider theme={mockTheme}>
          <IncompleteWorkDialog {...defaultProps} />
        </ThemeProvider>
      )
    })

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
    })

    // Click move to backlog
    const moveButton = screen.getByText('Move to Backlog')
    await act(async () => {
      fireEvent.click(moveButton)
    })

    // Verify API call
    await waitFor(() => {
      expect(completeSprint).toHaveBeenCalledWith('sprint-123', {
        action: 'backlog',
        item_ids: ['1', '2'],
      })
    })

    // Check completion callback
    expect(defaultProps.onCompleted).toHaveBeenCalledWith({
      moved_count: 2,
      target: 'backlog',
    })
  })

  it('moves items to next sprint', async () => {
    ;(completeSprint as any).mockResolvedValue({
      moved_count: 2,
      target: 'next_sprint',
      next_sprint_id: 'next-123',
    })

    await act(async () => {
      render(
        <ThemeProvider theme={mockTheme}>
          <IncompleteWorkDialog {...defaultProps} />
        </ThemeProvider>
      )
    })

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
    })

    // Click move to next sprint
    const moveButton = screen.getByText('Move to Next Sprint')
    await act(async () => {
      fireEvent.click(moveButton)
    })

    // Verify API call
    await waitFor(() => {
      expect(completeSprint).toHaveBeenCalledWith('sprint-123', {
        action: 'next_sprint',
        item_ids: ['1', '2'],
      })
    })

    // Check completion callback
    expect(defaultProps.onCompleted).toHaveBeenCalledWith({
      moved_count: 2,
      target: 'next_sprint',
      next_sprint_id: 'next-123',
    })
  })

  it('handles move error', async () => {
    ;(completeSprint as any).mockRejectedValue(
      new Error('Failed to move items')
    )

    await act(async () => {
      render(
        <ThemeProvider theme={mockTheme}>
          <IncompleteWorkDialog {...defaultProps} />
        </ThemeProvider>
      )
    })

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
    })

    // Click move to backlog
    const moveButton = screen.getByText('Move to Backlog')
    await act(async () => {
      fireEvent.click(moveButton)
    })

    // Check error is displayed
    await waitFor(() => {
      expect(screen.getByText(/Failed to move items/)).toBeInTheDocument()
    })

    // Completion callback should not be called
    expect(defaultProps.onCompleted).not.toHaveBeenCalled()
  })

  it('closes dialog when no items are pending', async () => {
    ;(getIncompleteItems as any).mockResolvedValue([])

    await act(async () => {
      render(
        <ThemeProvider theme={mockTheme}>
          <IncompleteWorkDialog {...defaultProps} />
        </ThemeProvider>
      )
    })

    // Should show message and close
    await waitFor(() => {
      expect(defaultProps.onClose).toHaveBeenCalled()
    })
  })

  it('disables close during move operation', async () => {
    // Mock completeSprint to resolve after a short delay to keep moving state true
    ;(completeSprint as any).mockImplementation(
      () =>
        new Promise((resolve) =>
          setTimeout(() => resolve({ moved_count: 2, target: 'backlog' }), 200)
        )
    )

    await act(async () => {
      render(
        <ThemeProvider theme={mockTheme}>
          <IncompleteWorkDialog {...defaultProps} />
        </ThemeProvider>
      )
    })

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
    })

    // Start move operation
    const moveButton = screen.getByText('Move to Backlog')
    await act(async () => {
      fireEvent.click(moveButton)
    })

    // Buttons should be disabled while request is in-flight
    await waitFor(() => {
      expect(screen.getByTestId('move-backlog')).toHaveAttribute(
        'aria-disabled',
        'true'
      )
      expect(screen.getByTestId('move-next')).toHaveAttribute(
        'aria-disabled',
        'true'
      )
    })

    // Try to close dialog (click backdrop)
    const backdrop = document.querySelector('.MuiBackdrop-root')
    await act(async () => {
      if (backdrop) {
        fireEvent.click(backdrop)
      }
    })

    // Should not have called onClose during move
    expect(defaultProps.onClose).not.toHaveBeenCalled()

    // Wait for request to complete and buttons to re-enable
    await waitFor(() => {
      expect(screen.getByTestId('move-backlog')).toHaveAttribute(
        'aria-disabled',
        'false'
      )
      expect(screen.getByTestId('move-next')).toHaveAttribute(
        'aria-disabled',
        'false'
      )
    })
  })
})
