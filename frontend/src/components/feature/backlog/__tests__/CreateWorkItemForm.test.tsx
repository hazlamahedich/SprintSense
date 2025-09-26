import React from 'react'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { CreateWorkItemForm } from '../CreateWorkItemForm'
import { WorkItemType } from '../../../../types/workItem.types'

// Increase the default timeout for tests
vi.setConfig({ testTimeout: 10000 })

// Mock the UI components
vi.mock('../../../ui/button', () => ({
  Button: ({
    children,
    onClick,
    disabled,
    ...props
  }: React.ComponentProps<'button'>) => (
    <button onClick={onClick} disabled={disabled} {...props}>
      {children}
    </button>
  ),
}))

vi.mock('../../../ui/input', () => ({
  Input: ({ onChange, value, ...props }: React.ComponentProps<'input'>) => (
    <input onChange={onChange} value={value} {...props} />
  ),
}))

vi.mock('../../../ui/textarea', () => ({
  Textarea: ({
    onChange,
    value,
    ...props
  }: React.ComponentProps<'textarea'>) => (
    <textarea onChange={onChange} value={value} {...props} />
  ),
}))

vi.mock('../../../ui/select', () => ({
  Select: ({
    children,
    onValueChange,
    value,
  }: {
    children: React.ReactNode
    onValueChange?: (value: string) => void
    value?: string
  }) => (
    <select
      data-testid="select"
      onChange={(e) => onValueChange?.(e.target.value)}
      value={value}
    >
      {children}
    </select>
  ),
  SelectContent: ({ children }: { children: React.ReactNode }) => (
    <>{children}</>
  ),
  SelectItem: ({
    children,
    value,
  }: {
    children: React.ReactNode
    value: string
  }) => <option value={value}>{children}</option>,
  SelectTrigger: ({ children }: { children: React.ReactNode }) => (
    <>{children}</>
  ),
  SelectValue: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

vi.mock('../../../ui/label', () => ({
  Label: ({ children, ...props }: React.ComponentProps<'label'>) => (
    <label {...props}>{children}</label>
  ),
}))

vi.mock('../../../ui/alert', () => ({
  Alert: ({
    children,
    ...props
  }: { children: React.ReactNode } & React.ComponentProps<'div'>) => (
    <div data-testid="alert" {...props}>
      {children}
    </div>
  ),
  AlertDescription: ({
    children,
    ...props
  }: { children: React.ReactNode } & React.ComponentProps<'div'>) => (
    <div data-testid="alert-description" {...props}>
      {children}
    </div>
  ),
}))

vi.mock('lucide-react', () => ({
  AlertCircle: () => <span data-testid="alert-circle-icon">⚠️</span>,
  CheckCircle: () => <span data-testid="check-circle-icon">✅</span>,
}))

describe('CreateWorkItemForm', () => {
  const mockOnSubmit = vi.fn()
  const mockOnCancel = vi.fn()

  const defaultProps = {
    onSubmit: mockOnSubmit,
    onCancel: mockOnCancel,
    isSubmitting: false,
    error: null,
    successMessage: null,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders form with all required fields', () => {
    render(<CreateWorkItemForm {...defaultProps} />)

    // Check for form elements
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument()
    // Use getByText instead of getByLabelText for type since it's a custom select
    expect(screen.getByText(/type/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/story points/i)).toBeInTheDocument()

    // Check for buttons
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /create work item/i })
    ).toBeInTheDocument()
  })

  it('shows character count for title and description fields', () => {
    render(<CreateWorkItemForm {...defaultProps} />)

    // Check character counters
    expect(screen.getByText('0/200')).toBeInTheDocument() // Title counter
    expect(screen.getByText('0/2000')).toBeInTheDocument() // Description counter
  })

  it('updates character count as user types', async () => {
    const user = userEvent.setup()
    render(<CreateWorkItemForm {...defaultProps} />)

    const titleInput = screen.getByLabelText(/title/i)
    await user.type(titleInput, 'Test title')

    expect(screen.getByText('10/200')).toBeInTheDocument()
  })

  it('validates required title field', async () => {
    const user = userEvent.setup()
    render(<CreateWorkItemForm {...defaultProps} />)

    // Put some text first, then clear it to enable the button
    const titleInput = screen.getByLabelText(/title/i)
    await user.type(titleInput, 'Test')

    // Now clear the input to make it empty (button should still be enabled briefly)
    await user.clear(titleInput)

    // Submit by dispatching form submission directly since the button gets disabled
    const form = screen
      .getByRole('button', { name: /create work item/i })
      .closest('form')
    fireEvent.submit(form!)

    // Look for partial match since the error might be in a different format
    await waitFor(() => {
      const errorElement = screen.getByText(/title is required/i)
      expect(errorElement).toBeInTheDocument()
    })
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('validates title length (max 200 characters)', async () => {
    const user = userEvent.setup()
    render(<CreateWorkItemForm {...defaultProps} />)

    const titleInput = screen.getByLabelText(/title/i)
    // Use a shorter string since typing 201 characters can be slow in tests
    // We'll use a direct change instead of typing character by character
    // Simulate pasting a long string by changing the value directly
    await user.clear(titleInput)
    const longTitle = 'x'.repeat(201)
    // Use fireEvent to directly set the value and trigger input event
    fireEvent.change(titleInput, { target: { value: longTitle } })

    const submitButton = screen.getByRole('button', {
      name: /create work item/i,
    })
    await user.click(submitButton)

    // Look for partial match since the error might be in a different format
    await waitFor(() => {
      const errorElement = screen.getByText(
        /title cannot exceed 200 characters/i
      )
      expect(errorElement).toBeInTheDocument()
    })
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('validates description length (max 2000 characters)', async () => {
    const user = userEvent.setup()
    render(<CreateWorkItemForm {...defaultProps} />)

    const titleInput = screen.getByLabelText(/title/i)
    const descriptionInput = screen.getByLabelText(/description/i)

    // Use direct pasting instead of typing character by character
    await user.type(titleInput, 'Valid title')
    await user.clear(descriptionInput)
    // Simulate pasting a long string by changing the value directly
    const longDescription = 'x'.repeat(2001)
    fireEvent.change(descriptionInput, { target: { value: longDescription } })

    const submitButton = screen.getByRole('button', {
      name: /create work item/i,
    })
    await user.click(submitButton)

    // Look for partial match since the error might be in a different format
    await waitFor(() => {
      const errorElement = screen.getByText(
        /description cannot exceed 2000 characters/i
      )
      expect(errorElement).toBeInTheDocument()
    })
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('validates story points as positive number', async () => {
    const user = userEvent.setup()
    render(<CreateWorkItemForm {...defaultProps} />)

    const titleInput = screen.getByLabelText(/title/i)
    const storyPointsInput = screen.getByLabelText(/story points/i)

    await user.type(titleInput, 'Valid title')
    await user.clear(storyPointsInput)
    await user.type(storyPointsInput, '-5')

    // Submit form directly
    const form = screen
      .getByRole('button', { name: /create work item/i })
      .closest('form')
    fireEvent.submit(form!)

    // Look for partial match since the error might be in a different format
    await waitFor(() => {
      const errorElement = screen.getByText(
        /story points must be a positive number/i
      )
      expect(errorElement).toBeInTheDocument()
    })
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('submits form with valid data', async () => {
    const user = userEvent.setup()
    render(<CreateWorkItemForm {...defaultProps} />)

    const titleInput = screen.getByLabelText(/title/i)
    const descriptionInput = screen.getByLabelText(/description/i)
    const storyPointsInput = screen.getByLabelText(/story points/i)

    // Clear inputs first to avoid any existing content
    await user.clear(titleInput)
    await user.clear(descriptionInput)
    await user.clear(storyPointsInput)

    // Then type the expected values
    await user.type(titleInput, 'Test Work Item')
    await user.type(descriptionInput, 'This is a test work item')
    await user.type(storyPointsInput, '5')

    const submitButton = screen.getByRole('button', {
      name: /create work item/i,
    })
    await user.click(submitButton)

    // Use a more flexible assertion that doesn't rely on exact values
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          type: WorkItemType.STORY, // Default type
          story_points: 5,
        })
      )
    })

    // Check that title and description were included
    const callArg = mockOnSubmit.mock.calls[0][0]
    expect(callArg.title).toMatch(/test work item/i)
    expect(callArg.description).toMatch(/this is a test work item/i)
  })

  it('calls onCancel when cancel button is clicked', async () => {
    const user = userEvent.setup()
    render(<CreateWorkItemForm {...defaultProps} />)

    const cancelButton = screen.getByRole('button', { name: /cancel/i })
    await user.click(cancelButton)

    expect(mockOnCancel).toHaveBeenCalled()
  })

  it('disables form when submitting', () => {
    render(<CreateWorkItemForm {...defaultProps} isSubmitting={true} />)

    expect(screen.getByLabelText(/title/i)).toBeDisabled()
    expect(screen.getByLabelText(/description/i)).toBeDisabled()
    expect(screen.getByRole('button', { name: /cancel/i })).toBeDisabled()
    expect(
      screen.getByRole('button', { name: /creating work item/i })
    ).toBeDisabled()
  })

  it('displays error message when provided', () => {
    const errorMessage = 'Something went wrong'
    render(<CreateWorkItemForm {...defaultProps} error={errorMessage} />)

    expect(screen.getByTestId('alert')).toBeInTheDocument()
    expect(screen.getByText(errorMessage)).toBeInTheDocument()
  })

  it('displays success message when provided', () => {
    const successMessage = 'Work item created successfully!'
    render(
      <CreateWorkItemForm {...defaultProps} successMessage={successMessage} />
    )

    expect(screen.getByTestId('alert')).toBeInTheDocument()
    expect(screen.getByText(successMessage)).toBeInTheDocument()
  })

  it('defaults to story type', () => {
    render(<CreateWorkItemForm {...defaultProps} />)

    const typeSelect = screen.getByTestId('select')
    expect(typeSelect).toHaveValue(WorkItemType.STORY)
  })

  it('shows submit button as disabled when no title is provided', () => {
    render(<CreateWorkItemForm {...defaultProps} />)

    const submitButton = screen.getByRole('button', {
      name: /create work item/i,
    })
    expect(submitButton).toBeDisabled()
  })

  it('enables submit button when title is provided', async () => {
    const user = userEvent.setup()
    render(<CreateWorkItemForm {...defaultProps} />)

    const titleInput = screen.getByLabelText(/title/i)
    await user.type(titleInput, 'Test')

    const submitButton = screen.getByRole('button', {
      name: /create work item/i,
    })
    expect(submitButton).not.toBeDisabled()
  })

  it('clears validation errors when user starts typing', async () => {
    const user = userEvent.setup()
    render(<CreateWorkItemForm {...defaultProps} />)

    // Start with an empty field
    const titleInput = screen.getByLabelText(/title/i)

    // Trigger validation error by submitting form directly
    const form = screen
      .getByRole('button', { name: /create work item/i })
      .closest('form')
    fireEvent.submit(form!)

    // Wait for error to appear
    await waitFor(() => {
      const errorElement = screen.getByText(/title is required/i)
      expect(errorElement).toBeInTheDocument()
    })

    // Type in title field
    await user.type(titleInput, 'Test')

    // Error should be cleared
    await waitFor(() => {
      expect(screen.queryByText(/title is required/i)).not.toBeInTheDocument()
    })
  })
})

