import { useState } from 'react';
import { WorkItem, WorkItemStatus } from '@/types/workItem.types';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useToast } from '@/hooks/useToast';
import { workItemService } from '@/services/workItemService';
import { useWorkItemStore } from '@/stores/workItemStore';

interface UseWorkItemStatusProps {
  workItem: WorkItem;
  teamId: string;
}

export const useWorkItemStatus = ({ workItem, teamId }: UseWorkItemStatusProps) => {
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [targetStatus, setTargetStatus] = useState<WorkItemStatus | null>(null);
  const { toast } = useToast();
  const { socket } = useWebSocket();
  const updateWorkItem = useWorkItemStore((state) => state.updateWorkItem);

  const handleStatusChange = async (newStatus: WorkItemStatus) => {
    setTargetStatus(newStatus);
    setIsConfirmOpen(true);
  };

  const handleConfirm = async () => {
    if (!targetStatus) return;

    setIsLoading(true);
    try {
      const updatedItem = await workItemService.updateWorkItem(
        teamId,
        workItem.id,
        { status: targetStatus }
      );

      updateWorkItem(updatedItem);

      // Broadcast status change via WebSocket
      socket?.emit('workItemStatusChanged', {
        teamId,
        workItemId: workItem.id,
        newStatus: targetStatus,
        updatedItem,
      });

      toast({
        title: 'Status Updated',
        description: `Work item marked as ${targetStatus}`,
        variant: 'success',
      });

      setIsConfirmOpen(false);
    } catch (error) {
      console.error('Error updating status:', error);
      toast({
        title: 'Error',
        description: 'Failed to update work item status. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
      setTargetStatus(null);
    }
  };

  const handleClose = () => {
    setIsConfirmOpen(false);
    setTargetStatus(null);
  };

  return {
    isConfirmOpen,
    isLoading,
    targetStatus,
    handleStatusChange,
    handleConfirm,
    handleClose,
  };
};

export default useWorkItemStatus;
