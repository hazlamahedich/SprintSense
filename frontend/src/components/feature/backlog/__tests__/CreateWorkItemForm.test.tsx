import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { CreateWorkItemForm } from '../CreateWorkItemForm'
import { WorkItemType } from '../../../../types/workItem.types'

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
    expect(screen.getByLabelText(/type/i)).toBeInTheDocument()
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

    const submitButton = screen.getByRole('button', {
      name: /create work item/i,
    })
    await user.click(submitButton)

    expect(screen.getByText('Title is required')).toBeInTheDocument()
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('validates title length (max 200 characters)', async () => {
    const user = userEvent.setup()
    render(<CreateWorkItemForm {...defaultProps} />)

    const titleInput = screen.getByLabelText(/title/i)
    const longTitle = 'x'.repeat(201)

    await user.type(titleInput, longTitle)

    const submitButton = screen.getByRole('button', {
      name: /create work item/i,
    })
    await user.click(submitButton)

    expect(
      screen.getByText('Title cannot exceed 200 characters')
    ).toBeInTheDocument()
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('validates description length (max 2000 characters)', async () => {
    const user = userEvent.setup()
    render(<CreateWorkItemForm {...defaultProps} />)

    const titleInput = screen.getByLabelText(/title/i)
    const descriptionInput = screen.getByLabelText(/description/i)
    const longDescription = 'x'.repeat(2001)

    await user.type(titleInput, 'Valid title')
    await user.type(descriptionInput, longDescription)

    const submitButton = screen.getByRole('button', {
      name: /create work item/i,
    })
    await user.click(submitButton)

    expect(
      screen.getByText('Description cannot exceed 2000 characters')
    ).toBeInTheDocument()
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('validates story points as positive number', async () => {
    const user = userEvent.setup()
    render(<CreateWorkItemForm {...defaultProps} />)

    const titleInput = screen.getByLabelText(/title/i)
    const storyPointsInput = screen.getByLabelText(/story points/i)

    await user.type(titleInput, 'Valid title')
    await user.type(storyPointsInput, '-5')

    const submitButton = screen.getByRole('button', {
      name: /create work item/i,
    })
    await user.click(submitButton)

    expect(
      screen.getByText('Story points must be a positive number')
    ).toBeInTheDocument()
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('submits form with valid data', async () => {
    const user = userEvent.setup()
    render(<CreateWorkItemForm {...defaultProps} />)

    const titleInput = screen.getByLabelText(/title/i)
    const descriptionInput = screen.getByLabelText(/description/i)
    const storyPointsInput = screen.getByLabelText(/story points/i)

    await user.type(titleInput, 'Test Work Item')
    await user.type(descriptionInput, 'This is a test work item')
    await user.type(storyPointsInput, '5')

    const submitButton = screen.getByRole('button', {
      name: /create work item/i,
    })
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        title: 'Test Work Item',
        description: 'This is a test work item',
        type: WorkItemType.STORY, // Default type
        story_points: 5,
      })
    })
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

    // Trigger validation error first
    const submitButton = screen.getByRole('button', {
      name: /create work item/i,
    })
    await user.click(submitButton)

    expect(screen.getByText('Title is required')).toBeInTheDocument()

    // Type in title field
    const titleInput = screen.getByLabelText(/title/i)
    await user.type(titleInput, 'Test')

    // Error should be cleared
    expect(screen.queryByText('Title is required')).not.toBeInTheDocument()
  })
})
