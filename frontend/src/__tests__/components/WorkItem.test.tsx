import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '../test-utils/setup';
import { vi } from 'vitest';
import { WorkItem } from '@/components/common/WorkItem';
import * as SelectPrimitive from '@radix-ui/react-select';
import { WorkItemStatus } from '@/types/workItem.types';
import { useWorkItemStatus } from '@/hooks/useWorkItemStatus';

// Mock the custom hook
vi.mock('@/hooks/useWorkItemStatus', () => ({
  useWorkItemStatus: vi.fn(),
}));

describe('WorkItem', () => {
  const mockWorkItem = {
    id: '123',
    title: 'Test Work Item',
    description: 'Test description',
    status: WorkItemStatus.TODO,
    story_points: 5,
    created_at: '2025-09-24T10:00:00Z',
    completed_at: null,
  };

  const mockTeamId = 'team123';

  const mockHookReturn = {
    isConfirmOpen: false,
    isLoading: false,
    targetStatus: null,
    handleStatusChange: vi.fn(),
    handleConfirm: vi.fn(),
    handleClose: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useWorkItemStatus).mockReturnValue(mockHookReturn);
  });

  it('renders work item details', () => {
    render(<WorkItem workItem={mockWorkItem} teamId={mockTeamId} />);

    expect(screen.getByText('Test Work Item')).toBeInTheDocument();
    expect(screen.getByText('Test description')).toBeInTheDocument();
    expect(screen.getByText('5 pts')).toBeInTheDocument();
    expect(screen.getByLabelText('Status: todo')).toBeInTheDocument();
  });

  it('displays completion date when available', () => {
    const completedWorkItem = {
      ...mockWorkItem,
      status: WorkItemStatus.DONE,
      completed_at: '2025-09-24T11:00:00Z',
    };

    render(<WorkItem workItem={completedWorkItem} teamId={mockTeamId} />);

    expect(screen.getByText(/Completed:/)).toBeInTheDocument();
  });

it('handles status change', async () => {
    render(<WorkItem workItem={mockWorkItem} teamId={mockTeamId} />);

    // Click the Select Trigger to open the dropdown
    const selectTrigger = screen.getByLabelText('Change work item status');
    fireEvent.click(selectTrigger);

    // Click on the done option
    const doneOption = screen.getByRole('option', { name: 'done' });
    fireEvent.click(doneOption);

    expect(mockHookReturn.handleStatusChange).toHaveBeenCalledWith(
      WorkItemStatus.DONE
    );
  });

  it('shows confirmation dialog when changing status', () => {
    vi.mocked(useWorkItemStatus).mockReturnValue({
      ...mockHookReturn,
      isConfirmOpen: true,
      targetStatus: WorkItemStatus.DONE,
    });

    render(<WorkItem workItem={mockWorkItem} teamId={mockTeamId} />);

    expect(screen.getByText(/Update Status: Test Work Item/)).toBeInTheDocument();
  });

  it('applies correct status colors', () => {
    const getStatusColor = (status: WorkItemStatus) => {
      const workItem = { ...mockWorkItem, status };
      render(<WorkItem workItem={workItem} teamId={mockTeamId} />);
      return screen.getByLabelText(`Status: ${status}`).className;
    };

    expect(getStatusColor(WorkItemStatus.DONE)).toContain('bg-green-100');
    expect(getStatusColor(WorkItemStatus.IN_PROGRESS)).toContain('bg-blue-100');
    expect(getStatusColor(WorkItemStatus.TODO)).toContain('bg-yellow-100');
  });

  it('provides proper aria labels for accessibility', () => {
    render(<WorkItem workItem={mockWorkItem} teamId={mockTeamId} />);

    expect(screen.getByLabelText('Status: todo')).toBeInTheDocument();
    expect(screen.getByLabelText('Story Points: 5')).toBeInTheDocument();
    expect(screen.getByLabelText('Change work item status')).toBeInTheDocument();
  });
});
