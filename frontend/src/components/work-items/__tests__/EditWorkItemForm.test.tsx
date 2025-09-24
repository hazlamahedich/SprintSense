/**
 * Unit tests for EditWorkItemForm component.
 * Tests form validation, pre-population, optimistic updates, and error handling.
 */

import React from 'react'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'

import EditWorkItemForm from '../EditWorkItemForm'
import {
  WorkItem,
  WorkItemType,
  WorkItemStatus,
} from '../../../types/workItem.types'
import { workItemService } from '../../../services/workItemService'

// Mock the workItemService
vi.mock('../../../services/workItemService', () => ({
  workItemService: {
    updateWorkItem: vi.fn(),
  },
}))

const mockWorkItemService = vi.mocked(workItemService)

describe('EditWorkItemForm', () => {
  const mockWorkItem: WorkItem = {
    id: '123e4567-e89b-12d3-a456-426614174000',
    team_id: '987fcdeb-51a2-43c1-9f44-123456789abc',
    author_id: 'author-123',
    assignee_id: 'assignee-456',
    title: 'Test Work Item',
    description: 'Test description for work item',
    type: WorkItemType.STORY,
    status: WorkItemStatus.BACKLOG,
    priority: 3.5,
    story_points: 8,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }

  const defaultProps = {
    workItem: mockWorkItem,
    teamId: 'team-123',
    onSave: vi.fn(),
    onCancel: vi.fn(),
    onError: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('pre-populates form with work item data (AC1)', () => {
    render(<EditWorkItemForm {...defaultProps} />)

    // Check that form fields are pre-populated
    expect(screen.getByDisplayValue('Test Work Item')).toBeInTheDocument()
    expect(
      screen.getByDisplayValue('Test description for work item')
    ).toBeInTheDocument()
    // Check select dropdowns have correct values selected
    expect(screen.getByRole('combobox', { name: /type/i })).toHaveValue('story')
    expect(screen.getByRole('combobox', { name: /status/i })).toHaveValue(
      'backlog'
    )
    expect(screen.getByDisplayValue('3.5')).toBeInTheDocument()
    expect(screen.getByDisplayValue('8')).toBeInTheDocument()
  })

  it('validates required title field (AC2)', async () => {
    const user = userEvent.setup()
    render(<EditWorkItemForm {...defaultProps} />)

    // Clear the title field
    const titleInput = screen.getByRole('textbox', { name: /title/i })
    await user.clear(titleInput)

    // Try to submit
    const saveButton = screen.getByRole('button', { name: /save changes/i })
    await user.click(saveButton)

    // Should show validation error
    await waitFor(() => {
      expect(screen.getByText('Title is required')).toBeInTheDocument()
    })
  })

  it('validates title length limit (AC2)', async () => {
    const user = userEvent.setup()
    render(<EditWorkItemForm {...defaultProps} />)

    // Enter title exceeding 200 characters
    const titleInput = screen.getByRole('textbox', { name: /title/i })
    const longTitle = 'a'.repeat(201)
    await user.clear(titleInput)
    await user.type(titleInput, longTitle)

    // Should show validation error
    await waitFor(() => {
      expect(
        screen.getByText('Title cannot exceed 200 characters')
      ).toBeInTheDocument()
    })
  })

  it('validates description length limit (AC2)', async () => {
    render(<EditWorkItemForm {...defaultProps} />)

    // Enter description exceeding 2000 characters
    const descriptionInput = screen.getByRole('textbox', {
      name: /description/i,
    })
    const longDescription = 'a'.repeat(2001)

    // Use fireEvent.change for large text to avoid timeout
    fireEvent.change(descriptionInput, { target: { value: longDescription } })

    // Should show validation error
    await waitFor(() => {
      expect(
        screen.getByText('Description cannot exceed 2000 characters')
      ).toBeInTheDocument()
    })
  })

  it('validates priority is not negative (AC2)', async () => {
    const user = userEvent.setup()
    render(<EditWorkItemForm {...defaultProps} />)

    // Enter negative priority
    const priorityInput = screen.getByRole('spinbutton', { name: /priority/i })
    await user.clear(priorityInput)
    await user.type(priorityInput, '-1')

    // Try to submit
    const saveButton = screen.getByRole('button', { name: /save changes/i })
    await user.click(saveButton)

    // Should show validation error
    await waitFor(() => {
      expect(
        screen.getByText('Priority cannot be negative')
      ).toBeInTheDocument()
    })
  })

  it('validates story points is not negative (AC2)', async () => {
    const user = userEvent.setup()
    render(<EditWorkItemForm {...defaultProps} />)

    // Enter negative story points
    const storyPointsInput = screen.getByRole('spinbutton', {
      name: /story points/i,
    })
    await user.clear(storyPointsInput)
    await user.type(storyPointsInput, '-5')

    // Try to submit
    const saveButton = screen.getByRole('button', { name: /save changes/i })
    await user.click(saveButton)

    // Should show validation error
    await waitFor(() => {
      expect(
        screen.getByText('Story points cannot be negative')
      ).toBeInTheDocument()
    })
  })

  it('shows character count for title and description', () => {
    render(<EditWorkItemForm {...defaultProps} />)

    // Check character counts are displayed
    expect(screen.getByText('14/200 characters')).toBeInTheDocument() // Title length
    expect(screen.getByText('30/2000 characters')).toBeInTheDocument() // Description length
  })

  it('tracks unsaved changes indicator', async () => {
    const user = userEvent.setup()
    render(<EditWorkItemForm {...defaultProps} />)

    // Initially no unsaved changes
    expect(
      screen.queryByText('You have unsaved changes')
    ).not.toBeInTheDocument()

    // Make a change
    const titleInput = screen.getByRole('textbox', { name: /title/i })
    await user.type(titleInput, ' Updated')

    // Should show unsaved changes indicator
    await waitFor(() => {
      expect(screen.getByText('You have unsaved changes')).toBeInTheDocument()
    })
  })

  it('performs optimistic update on save (AC3, AC4)', async () => {
    const user = userEvent.setup()
    const mockOnSave = vi.fn()

    // Mock successful API response with delay
    mockWorkItemService.updateWorkItem.mockImplementationOnce(
      () =>
        new Promise((resolve) =>
          setTimeout(
            () =>
              resolve({
                ...mockWorkItem,
                title: 'Updated Title',
              }),
            100
          )
        )
    )

    render(<EditWorkItemForm {...defaultProps} onSave={mockOnSave} />)

    // Make changes
    const titleInput = screen.getByRole('textbox', { name: /title/i })
    await user.clear(titleInput)
    await user.type(titleInput, 'Updated Title')

    // Submit
    const saveButton = screen.getByRole('button', { name: /save changes/i })
    await user.click(saveButton)

    // Should immediately call onSave with optimistic update
    expect(mockOnSave).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Updated Title',
        updated_at: expect.any(String),
      })
    )

    // Should show saving indicator
    expect(screen.getByText('Saving changes...')).toBeInTheDocument()

    // Wait for API call to complete
    await waitFor(() => {
      expect(mockWorkItemService.updateWorkItem).toHaveBeenCalledWith(
        'team-123',
        mockWorkItem.id,
        { title: 'Updated Title' }
      )
    })

    // Should call onSave again with real API response
    await waitFor(() => {
      expect(mockOnSave).toHaveBeenCalledTimes(2)
    })
  })

  it('rolls back optimistic update on API error (AC4)', async () => {
    const user = userEvent.setup()
    const mockOnSave = vi.fn()
    const mockOnError = vi.fn()

    // Mock API error
    const apiError = new Error('API Error')
    apiError.response = {
      data: {
        detail: {
          message: 'Update failed',
        },
      },
    }
    mockWorkItemService.updateWorkItem.mockRejectedValueOnce(apiError)

    render(
      <EditWorkItemForm
        {...defaultProps}
        onSave={mockOnSave}
        onError={mockOnError}
      />
    )

    // Make changes
    const titleInput = screen.getByRole('textbox', { name: /title/i })
    await user.clear(titleInput)
    await user.type(titleInput, 'Updated Title')

    // Submit
    const saveButton = screen.getByRole('button', { name: /save changes/i })
    await user.click(saveButton)

    // Should first call onSave with optimistic update
    expect(mockOnSave).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Updated Title',
      })
    )

    // Wait for error handling
    await waitFor(() => {
      // Should rollback by calling onSave with original data
      expect(mockOnSave).toHaveBeenCalledWith(mockWorkItem)

      // Should call onError
      expect(mockOnError).toHaveBeenCalledWith('Update failed')

      // Should show error message
      expect(screen.getByText('Update failed')).toBeInTheDocument()
    })
  })

  it('handles structured error responses (AC5)', async () => {
    const user = userEvent.setup()
    const mockOnError = vi.fn()

    // Mock structured error response
    const structuredError = new Error('API Error')
    structuredError.response = {
      data: {
        detail: {
          error: 'validation_error',
          message: 'Title cannot be empty',
          recovery_action: 'Please provide a valid title',
        },
      },
    }
    mockWorkItemService.updateWorkItem.mockRejectedValueOnce(structuredError)

    render(<EditWorkItemForm {...defaultProps} onError={mockOnError} />)

    // Make changes and submit
    const titleInput = screen.getByRole('textbox', { name: /title/i })
    await user.clear(titleInput)
    await user.type(titleInput, 'Updated Title')

    const saveButton = screen.getByRole('button', { name: /save changes/i })
    await user.click(saveButton)

    // Should handle structured error
    await waitFor(() => {
      expect(screen.getByText('Title cannot be empty')).toBeInTheDocument()
      expect(mockOnError).toHaveBeenCalledWith('Title cannot be empty')
    })
  })

  it('skips API call when no changes made', async () => {
    const user = userEvent.setup()
    const mockOnSave = vi.fn()

    render(<EditWorkItemForm {...defaultProps} onSave={mockOnSave} />)

    // Submit without making changes
    const saveButton = screen.getByRole('button', { name: /save changes/i })
    await user.click(saveButton)

    // Should not make API call
    expect(mockWorkItemService.updateWorkItem).not.toHaveBeenCalled()

    // Should still call onSave with original item
    expect(mockOnSave).toHaveBeenCalledWith(mockWorkItem)
  })

  it('only sends changed fields in update request', async () => {
    const user = userEvent.setup()

    mockWorkItemService.updateWorkItem.mockResolvedValueOnce({
      ...mockWorkItem,
      title: 'Updated Title',
      priority: 5.0,
    })

    render(<EditWorkItemForm {...defaultProps} />)

    // Make changes to specific fields only
    const titleInput = screen.getByRole('textbox', { name: /title/i })
    await user.clear(titleInput)
    await user.type(titleInput, 'Updated Title')

    const priorityInput = screen.getByRole('spinbutton', { name: /priority/i })
    await user.clear(priorityInput)
    await user.type(priorityInput, '5')

    // Submit
    const saveButton = screen.getByRole('button', { name: /save changes/i })
    await user.click(saveButton)

    // Should only send changed fields
    await waitFor(() => {
      expect(mockWorkItemService.updateWorkItem).toHaveBeenCalledWith(
        'team-123',
        mockWorkItem.id,
        {
          title: 'Updated Title',
          priority: 5,
        }
      )
    })
  })

  it('disables save button when validation errors exist', async () => {
    const user = userEvent.setup()
    render(<EditWorkItemForm {...defaultProps} />)

    // Create validation error
    const titleInput = screen.getByRole('textbox', { name: /title/i })
    await user.clear(titleInput)

    // Save button should be disabled
    const saveButton = screen.getByRole('button', { name: /save changes/i })
    await waitFor(() => {
      expect(saveButton).toBeDisabled()
    })
  })

  it('shows loading state during save', async () => {
    const user = userEvent.setup()

    // Mock slow API response
    const slowPromise = new Promise((resolve) => {
      setTimeout(() => resolve({ ...mockWorkItem, title: 'Updated' }), 100)
    })
    mockWorkItemService.updateWorkItem.mockReturnValueOnce(slowPromise)

    render(<EditWorkItemForm {...defaultProps} />)

    // Make change and submit
    const titleInput = screen.getByRole('textbox', { name: /title/i })
    await user.type(titleInput, ' Updated')

    const saveButton = screen.getByRole('button', { name: /save changes/i })
    await user.click(saveButton)

    // Should show loading state (allow for async render)
    await waitFor(
      () => {
        const submitButton = screen.getByRole('button', {
          name: /save|saving/i,
        })
        expect(submitButton).toHaveAttribute('disabled')
      },
      { timeout: 1000 }
    )

    // Verify loading text
    const submitText = screen.getByRole('button', {
      name: /save|saving/i,
    }).textContent
    expect(submitText === 'Saving...' || submitText === 'Saving...').toBe(true)

    // Wait for completion
    await waitFor(
      () => {
        const button = screen.getByRole('button', { name: /save changes/i })
        expect(button).not.toHaveAttribute('disabled')
      },
      { timeout: 1000 }
    )
  })

  it('calls onCancel when cancel button clicked', async () => {
    const user = userEvent.setup()
    const mockOnCancel = vi.fn()

    render(<EditWorkItemForm {...defaultProps} onCancel={mockOnCancel} />)

    const cancelButton = screen.getByRole('button', { name: /cancel/i })
    await user.click(cancelButton)

    expect(mockOnCancel).toHaveBeenCalled()
  })

  it('clears field errors when user starts typing', async () => {
    const user = userEvent.setup()
    render(<EditWorkItemForm {...defaultProps} />)

    // Create validation error
    const titleInput = screen.getByRole('textbox', { name: /title/i })
    await user.clear(titleInput)

    // Try to submit to trigger error
    const saveButton = screen.getByRole('button', { name: /save changes/i })
    await user.click(saveButton)

    // Should show error
    await waitFor(() => {
      expect(screen.getByText('Title is required')).toBeInTheDocument()
    })

    // Start typing to clear error
    await user.type(titleInput, 'New Title')

    // Error should be cleared
    await waitFor(() => {
      expect(screen.queryByText('Title is required')).not.toBeInTheDocument()
    })
  })

  it('prevents form submission with Enter key when errors exist', async () => {
    const user = userEvent.setup()
    const mockOnSave = vi.fn()

    render(<EditWorkItemForm {...defaultProps} onSave={mockOnSave} />)

    // Create validation error
    const titleInput = screen.getByRole('textbox', { name: /title/i })
    await user.clear(titleInput)

    // Try to submit with Enter
    await user.type(titleInput, '{enter}')

    // Should not call onSave due to validation error
    expect(mockOnSave).not.toHaveBeenCalled()
  })
})
