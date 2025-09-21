import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { RecommendationsPanel } from '../components/feature/recommendations/RecommendationsPanel'
import { useWorkItemRecommendations } from '../hooks/useWorkItemRecommendations'

// Mock the hook
vi.mock('../hooks/useWorkItemRecommendations')

const mockRecommendation = {
  id: 'rec_123',
  title: 'Test Recommendation',
  description: 'Test Description',
  type: 'story',
  suggested_priority: 0.85,
  confidence_scores: {
    title: 0.9,
    description: 0.85,
    type: 0.95,
    priority: 0.8,
  },
  reasoning: 'Test reasoning',
  patterns_identified: ['test_pattern'],
  team_velocity_factor: 0.75,
}

describe('RecommendationsPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state correctly', () => {
    ;(useWorkItemRecommendations as jest.Mock).mockReturnValue({
      isLoading: true,
      error: null,
      recommendations: [],
    })

    render(<RecommendationsPanel teamId="team123" />)
    expect(screen.getByRole('progressbar')).toBeInTheDocument()
  })

  it('renders error state correctly', () => {
    const errorMessage = 'Failed to load recommendations'
    ;(useWorkItemRecommendations as jest.Mock).mockReturnValue({
      isLoading: false,
      error: new Error(errorMessage),
      recommendations: [],
    })

    render(<RecommendationsPanel teamId="team123" />)
    expect(screen.getByText(errorMessage)).toBeInTheDocument()
  })

  it('renders empty state correctly', () => {
    ;(useWorkItemRecommendations as jest.Mock).mockReturnValue({
      isLoading: false,
      error: null,
      recommendations: [],
    })

    render(<RecommendationsPanel teamId="team123" />)
    expect(
      screen.getByText('No recommendations available at this time')
    ).toBeInTheDocument()
  })

  it('renders recommendations correctly', () => {
    ;(useWorkItemRecommendations as jest.Mock).mockReturnValue({
      isLoading: false,
      error: null,
      recommendations: [mockRecommendation],
      acceptRecommendation: vi.fn(),
      modifyRecommendation: vi.fn(),
      provideRecommendationFeedback: vi.fn(),
    })

    render(<RecommendationsPanel teamId="team123" />)
    expect(screen.getByText('Test Recommendation')).toBeInTheDocument()
    expect(screen.getByText('Test Description')).toBeInTheDocument()
    expect(screen.getByText('Test reasoning')).toBeInTheDocument()
  })

  it('handles accept action correctly', async () => {
    const acceptMock = vi.fn()
    const modifyMock = vi.fn()
    const feedbackMock = vi.fn()
    ;(
      useWorkItemRecommendations as unknown as ReturnType<typeof vi.fn>
    ).mockReturnValue({
      isLoading: false,
      error: null,
      recommendations: [mockRecommendation],
      acceptRecommendation: acceptMock,
      modifyRecommendation: modifyMock,
      provideRecommendationFeedback: feedbackMock,
    })

    render(<RecommendationsPanel teamId="team123" />)
    fireEvent.click(screen.getByText('Accept'))

    await waitFor(() => {
      expect(acceptMock).toHaveBeenCalledWith('rec_123')
    })
  })

  it('handles modify action correctly', async () => {
    const modifyMock = vi.fn()
    ;(useWorkItemRecommendations as jest.Mock).mockReturnValue({
      isLoading: false,
      error: null,
      recommendations: [mockRecommendation],
      acceptRecommendation: vi.fn(),
      modifyRecommendation: modifyMock,
      provideRecommendationFeedback: vi.fn(),
    })

    render(<RecommendationsPanel teamId="team123" />)
    fireEvent.click(screen.getByText('Modify'))

    await waitFor(() => {
      expect(modifyMock).toHaveBeenCalledWith('rec_123')
    })
  })

  it('handles not useful feedback correctly', async () => {
    const feedbackMock = vi.fn()
    ;(useWorkItemRecommendations as jest.Mock).mockReturnValue({
      isLoading: false,
      error: null,
      recommendations: [mockRecommendation],
      acceptRecommendation: vi.fn(),
      modifyRecommendation: vi.fn(),
      provideRecommendationFeedback: feedbackMock,
    })

    render(<RecommendationsPanel teamId="team123" />)

    // Open feedback dialog
    await userEvent.click(screen.getByText('Not Useful'))

    // Open the select and choose a reason (MUI Select renders a listbox with options)
    const selectTrigger = screen.getByRole('combobox')
    await userEvent.click(selectTrigger)
    const option = await screen.findByRole('option', {
      name: /Irrelevant To Current Goals/i,
    })
    await userEvent.click(option)

    await userEvent.click(screen.getByText('Submit'))

    await waitFor(() => {
      expect(feedbackMock).toHaveBeenCalledWith(
        'rec_123',
        'not_useful',
        'irrelevant_to_current_goals'
      )
    })
  })

  it('validates custom feedback reason correctly', async () => {
    const feedbackMock = vi.fn()
    ;(useWorkItemRecommendations as jest.Mock).mockReturnValue({
      isLoading: false,
      error: null,
      recommendations: [mockRecommendation],
      acceptRecommendation: vi.fn(),
      modifyRecommendation: vi.fn(),
      provideRecommendationFeedback: feedbackMock,
    })

    render(<RecommendationsPanel teamId="team123" />)

    // Open feedback dialog
    await userEvent.click(screen.getByText('Not Useful'))

    // Open the select and choose 'Other'
    const selectTrigger = screen.getByRole('combobox')
    await userEvent.click(selectTrigger)
    const otherOption = await screen.findByRole('option', { name: /^Other$/i })
    await userEvent.click(otherOption)

    // Submit button should be disabled without custom reason
    expect(screen.getByText('Submit')).toBeDisabled()

    // Enter custom reason
    const customReasonInput = screen.getByPlaceholderText(
      'Please provide more details...'
    )
    await userEvent.type(customReasonInput, 'Custom reason')

    // Submit button should be enabled now
    expect(screen.getByText('Submit')).not.toBeDisabled()

    await userEvent.click(screen.getByText('Submit'))

    await waitFor(() => {
      expect(feedbackMock).toHaveBeenCalledWith(
        'rec_123',
        'not_useful',
        'Custom reason'
      )
    })
  })
})
