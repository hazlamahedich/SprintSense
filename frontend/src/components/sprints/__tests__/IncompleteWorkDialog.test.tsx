import React from 'react';
import { vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material';
import { IncompleteWorkDialog } from '../IncompleteWorkDialog';
import { getIncompleteItems, completeSprint } from '../../../api/sprint';

// Mock API functions
vi.mock('../../../api/sprint', () => ({
  getIncompleteItems: vi.fn(),
  completeSprint: vi.fn(),
}));

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
];

const mockTheme = createTheme();

const defaultProps = {
  open: true,
  sprintId: 'sprint-123',
  onClose: vi.fn(),
  onCompleted: vi.fn(),
};

describe('IncompleteWorkDialog', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    (getIncompleteItems as any).mockResolvedValue(mockItems);
    (completeSprint as any).mockResolvedValue({
      moved_count: 2,
      target: 'backlog',
    });
  });

  it('loads and displays incomplete items', async () => {
    render(
      <ThemeProvider theme={mockTheme}>
        <IncompleteWorkDialog {...defaultProps} />
      </ThemeProvider>,
    );

    // Shows loading initially
    expect(screen.getByRole('progressbar')).toBeInTheDocument();

    // Check items are displayed
    await waitFor(() => {
      expect(screen.getByText('Task 1')).toBeInTheDocument();
      expect(screen.getByText('Task 2')).toBeInTheDocument();
    });

    // Check summary is correct
    expect(screen.getByText(/2 incomplete items/)).toBeInTheDocument();
    expect(screen.getByText(/8 points/)).toBeInTheDocument();
  });

  it('handles error loading items', async () => {
    (getIncompleteItems as any).mockRejectedValue(new Error('Failed to load'));

    render(
      <ThemeProvider theme={mockTheme}>
        <IncompleteWorkDialog {...defaultProps} />
      </ThemeProvider>,
    );

    await waitFor(() => {
      expect(screen.getByText(/Failed to load/)).toBeInTheDocument();
    });
  });

  it('moves items to backlog', async () => {
    render(
      <ThemeProvider theme={mockTheme}>
        <IncompleteWorkDialog {...defaultProps} />
      </ThemeProvider>,
    );

    // Wait for items to load
    await waitFor(() => {
      expect(screen.getByText('Task 1')).toBeInTheDocument();
    });

    // Click move to backlog
    const moveButton = screen.getByText('Move to Backlog');
    fireEvent.click(moveButton);

    // Verify API call
    await waitFor(() => {
      expect(completeSprint).toHaveBeenCalledWith('sprint-123', {
        action: 'backlog',
        item_ids: ['1', '2'],
      });
    });

    // Check completion callback
    expect(defaultProps.onCompleted).toHaveBeenCalledWith({
      moved_count: 2,
      target: 'backlog',
    });
  });

  it('moves items to next sprint', async () => {
    (completeSprint as any).mockResolvedValue({
      moved_count: 2,
      target: 'next_sprint',
      next_sprint_id: 'next-123',
    });

    render(
      <ThemeProvider theme={mockTheme}>
        <IncompleteWorkDialog {...defaultProps} />
      </ThemeProvider>,
    );

    // Wait for items to load
    await waitFor(() => {
      expect(screen.getByText('Task 1')).toBeInTheDocument();
    });

    // Click move to next sprint
    const moveButton = screen.getByText('Move to Next Sprint');
    fireEvent.click(moveButton);

    // Verify API call
    await waitFor(() => {
      expect(completeSprint).toHaveBeenCalledWith('sprint-123', {
        action: 'next_sprint',
        item_ids: ['1', '2'],
      });
    });

    // Check completion callback
    expect(defaultProps.onCompleted).toHaveBeenCalledWith({
      moved_count: 2,
      target: 'next_sprint',
      next_sprint_id: 'next-123',
    });
  });

  it('handles move error', async () => {
    (completeSprint as any).mockRejectedValue(new Error('Failed to move items'));

    render(
      <ThemeProvider theme={mockTheme}>
        <IncompleteWorkDialog {...defaultProps} />
      </ThemeProvider>,
    );

    // Wait for items to load
    await waitFor(() => {
      expect(screen.getByText('Task 1')).toBeInTheDocument();
    });

    // Click move to backlog
    const moveButton = screen.getByText('Move to Backlog');
    fireEvent.click(moveButton);

    // Check error is displayed
    await waitFor(() => {
      expect(screen.getByText(/Failed to move items/)).toBeInTheDocument();
    });

    // Completion callback should not be called
    expect(defaultProps.onCompleted).not.toHaveBeenCalled();
  });

  it('closes dialog when no items are pending', async () => {
    (getIncompleteItems as any).mockResolvedValue([]);

    render(
      <ThemeProvider theme={mockTheme}>
        <IncompleteWorkDialog {...defaultProps} />
      </ThemeProvider>,
    );

    // Should show message and close
    await waitFor(() => {
      expect(defaultProps.onClose).toHaveBeenCalled();
    });
  });

  it('disables close during move operation', async () => {
    render(
      <ThemeProvider theme={mockTheme}>
        <IncompleteWorkDialog {...defaultProps} />
      </ThemeProvider>,
    );

    // Wait for items to load
    await waitFor(() => {
      expect(screen.getByText('Task 1')).toBeInTheDocument();
    });

    // Start move operation
    const moveButton = screen.getByText('Move to Backlog');
    fireEvent.click(moveButton);

    // Try to close dialog (click backdrop)
    const backdrop = document.querySelector('.MuiBackdrop-root');
    if (backdrop) {
      fireEvent.click(backdrop);
    }

    // Should not have called onClose
    expect(defaultProps.onClose).not.toHaveBeenCalled();

    // Buttons should be disabled
    expect(moveButton).toBeDisabled();
    expect(screen.getByText('Move to Next Sprint')).toBeDisabled();
  });
});
