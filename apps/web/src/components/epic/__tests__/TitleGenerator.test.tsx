import React from 'react';
import { act, render, screen, waitFor } from '@testing-library/react';
import { fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TitleGenerator } from '../TitleGenerator';
import { useTitleGeneration } from '../../../hooks/useTitleGeneration';

// Mock the hook
jest.mock('../../../hooks/useTitleGeneration');

describe('TitleGenerator', () => {
  const mockGenerateTitle = jest.fn();
  const mockUseTitleGeneration = useTitleGeneration as jest.Mock;

  beforeEach(() => {
    mockUseTitleGeneration.mockReturnValue({
      generateTitle: mockGenerateTitle,
      isLoading: false
    });
  });

  const defaultProps = {
    description: 'Test description',
    teamId: 'team1',
    category: 'test',
    onTitleGenerated: jest.fn(),
    onTitleUpdated: jest.fn()
  };

  it('renders correctly', () => {
    render(<TitleGenerator {...defaultProps} />);

    expect(screen.getByRole('textbox', { name: /epic title/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /generate title/i })).toBeInTheDocument();
  });

  it('handles title generation', async () => {
    const generatedTitle = 'Generated Title';
    mockGenerateTitle.mockResolvedValueOnce({
      title: generatedTitle,
      confidence: 0.9,
      metadata: { cacheHit: false }
    });

    render(<TitleGenerator {...defaultProps} />);

    const generateButton = screen.getByRole('button', { name: /generate title/i });
    await act(async () => {
      await userEvent.click(generateButton);
    });

    await waitFor(() => {
      expect(mockGenerateTitle).toHaveBeenCalledWith({
        description: defaultProps.description,
        context: {
          teamId: defaultProps.teamId,
          category: defaultProps.category
        },
        options: {
          style: 'concise',
          maxLength: 100
        }
      });
    });

    expect(defaultProps.onTitleGenerated).toHaveBeenCalledWith(generatedTitle);
    expect(screen.getByText('Title generated successfully')).toBeInTheDocument();
  });

  it('handles manual title updates', async () => {
    render(<TitleGenerator {...defaultProps} />);

    const titleInput = screen.getByRole('textbox', { name: /epic title/i });
    await act(async () => {
      await userEvent.type(titleInput, 'Manual Title');
    });

    expect(defaultProps.onTitleUpdated).toHaveBeenCalledWith('Manual Title');
  });

  it('handles loading state', async () => {
    mockUseTitleGeneration.mockReturnValue({
      generateTitle: mockGenerateTitle,
      isLoading: true
    });

    render(<TitleGenerator {...defaultProps} />);

    const generateButton = screen.getByRole('button', { name: /generate title/i });
    const titleInput = screen.getByRole('textbox', { name: /epic title/i });

    expect(generateButton).toBeDisabled();
    expect(titleInput).toBeDisabled();
  });

  it('handles error state', async () => {
    const errorMessage = 'Failed to generate title';
    mockGenerateTitle.mockRejectedValueOnce(new Error(errorMessage));

    render(<TitleGenerator {...defaultProps} />);

    const generateButton = screen.getByRole('button', { name: /generate title/i });
    await act(async () => {
      await userEvent.click(generateButton);
      // Wait for state updates
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('disables generation when description is empty', () => {
    render(<TitleGenerator {...defaultProps} description="" />);

    const generateButton = screen.getByRole('button', { name: /generate title/i });
    expect(generateButton).toBeDisabled();
  });

  it('clears title when description changes', async () => {
    const { rerender } = render(<TitleGenerator {...defaultProps} />);

    const titleInput = screen.getByRole('textbox', { name: /epic title/i });
    await act(async () => {
      await userEvent.type(titleInput, 'Some title');
      // Wait for any additional state updates
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    rerender(<TitleGenerator {...defaultProps} description="New description" />);
    expect(titleInput).toHaveValue('');
  });

  // Accessibility tests
  it('meets accessibility requirements', async () => {
    render(<TitleGenerator {...defaultProps} />);

    // Input is properly labeled
    expect(screen.getByLabelText(/epic title/i)).toBeInTheDocument();

    // Button is accessible by role and name
    expect(screen.getByRole('button', { name: /generate title/i })).toBeInTheDocument();

    // Error message has role="alert"
    mockGenerateTitle.mockRejectedValueOnce(new Error('Test error'));
    await act(async () => {
      await userEvent.click(screen.getByRole('button'));
      // Wait for any additional state updates
      await new Promise(resolve => setTimeout(resolve, 0));
      // Wait for state updates
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
  });
});
