import { renderHook, act, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { useWorkItemStatus } from '@/hooks/useWorkItemStatus';
import { WorkItemStatus } from '@/types/workItem.types';
import { workItemService } from '@/services/workItemService';

const mockUpdateWorkItem = vi.fn();

// Mock dependencies
vi.mock('@/services/workItemService', () => ({
  workItemService: {
    updateWorkItem: vi.fn(),
  },
}));

vi.mock('@/hooks/useWebSocket', () => ({
  useWebSocket: () => ({
    socket: {
      emit: vi.fn(),
    },
  }),
}));

vi.mock('@/hooks/useToast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}));

vi.mock('@/stores/workItemStore', () => ({
  useWorkItemStore: () => () => ({
    updateWorkItem: mockUpdateWorkItem
  })
}));

describe('useWorkItemStatus', () => {
  const mockWorkItem = {
    id: '123',
    title: 'Test Item',
    status: WorkItemStatus.TODO,
  };

  const mockTeamId = 'team123';

  beforeEach(() => {
    vi.clearAllMocks();
    mockUpdateWorkItem.mockResolvedValue({});
  });

  it('initializes with default state', () => {
    const { result } = renderHook(() =>
      useWorkItemStatus({ workItem: mockWorkItem, teamId: mockTeamId })
    );

    expect(result.current.isConfirmOpen).toBe(false);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.targetStatus).toBe(null);
  });

  it('opens confirmation dialog with target status', () => {
    const { result } = renderHook(() =>
      useWorkItemStatus({ workItem: mockWorkItem, teamId: mockTeamId })
    );

    act(() => {
      result.current.handleStatusChange(WorkItemStatus.DONE);
    });

    expect(result.current.isConfirmOpen).toBe(true);
    expect(result.current.targetStatus).toBe(WorkItemStatus.DONE);
  });

  it('closes confirmation dialog and resets state', () => {
    const { result } = renderHook(() =>
      useWorkItemStatus({ workItem: mockWorkItem, teamId: mockTeamId })
    );

    act(() => {
      result.current.handleStatusChange(WorkItemStatus.DONE);
    });

    act(() => {
      result.current.handleClose();
    });

    expect(result.current.isConfirmOpen).toBe(false);
    expect(result.current.targetStatus).toBe(null);
  });

  it('updates work item status successfully', async () => {
    // Initialize mocks
    const updatedWorkItem = {
      ...mockWorkItem,
      status: WorkItemStatus.DONE,
    };
    vi.mocked(workItemService.updateWorkItem).mockResolvedValueOnce(updatedWorkItem);
    mockUpdateWorkItem.mockResolvedValueOnce(updatedWorkItem);
    const updatedItem = {
      ...mockWorkItem,
      status: WorkItemStatus.DONE,
    };

    vi.mocked(workItemService.updateWorkItem).mockResolvedValueOnce(updatedItem);

    const { result } = renderHook(() =>
      useWorkItemStatus({ workItem: mockWorkItem, teamId: mockTeamId })
    );

    // Set initial status
    act(() => {
      result.current.handleStatusChange(WorkItemStatus.DONE);
    });

    expect(result.current.isConfirmOpen).toBe(true);
    expect(result.current.targetStatus).toBe(WorkItemStatus.DONE);

    // Confirm the status change
    await act(async () => {
      await result.current.handleConfirm();
    });

    // Wait for state to stabilize after async operations
    await waitFor(() => {
      expect(workItemService.updateWorkItem).toHaveBeenCalledWith(
        mockTeamId,
        mockWorkItem.id,
        { status: WorkItemStatus.DONE }
      );
      expect(result.current.isConfirmOpen).toBe(false);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.targetStatus).toBe(null);
    });
  });

  it('handles error during status update', async () => {
    vi.mocked(workItemService.updateWorkItem).mockRejectedValueOnce(
      new Error('Update failed')
    );

    const { result } = renderHook(() =>
      useWorkItemStatus({ workItem: mockWorkItem, teamId: mockTeamId })
    );

    await act(async () => {
      result.current.handleStatusChange(WorkItemStatus.DONE);
    });

    await act(async () => {
      await result.current.handleConfirm();
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.targetStatus).toBe(null);
    // Error toast should be shown, but we're not testing UI components here
  });
});
