import React from 'react';
import { Dialog } from '@headlessui/react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { Button } from '@/components/ui/button-radix';
import { WorkItemStatus } from '@/types/workItem.types';

interface ConfirmStatusChangeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void>;
  title: string;
  targetStatus: WorkItemStatus;
  isLoading?: boolean;
}

export const ConfirmStatusChangeModal: React.FC<ConfirmStatusChangeModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  targetStatus,
  isLoading = false,
}) => {
  // Generate message based on target status
  const getMessage = (status: WorkItemStatus) => {
    switch (status) {
      case WorkItemStatus.DONE:
        return 'Are you sure you want to mark this item as Done? This will record the completion date for velocity tracking.';
      case WorkItemStatus.IN_PROGRESS:
        return 'Are you sure you want to move this item back to In Progress? This will clear any recorded completion date.';
      default:
        return `Are you sure you want to change the status to ${status}?`;
    }
  };

  return (
    <Dialog
      open={isOpen}
      onClose={onClose}
      className="relative z-50"
    >
      {/* Backdrop overlay */}
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />

      {/* Full-screen container */}
      <div className="fixed inset-0 flex items-center justify-center p-4">
        {/* Dialog panel */}
        <Dialog.Panel className="mx-auto max-w-md rounded-lg bg-white p-6 shadow-xl">
          <div className="flex items-center justify-between">
            <Dialog.Title className="text-lg font-semibold">
              {title}
            </Dialog.Title>
            <button
              type="button"
              onClick={onClose}
              className="rounded-full p-1 hover:bg-gray-100"
              aria-label="Close dialog"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>

          <Dialog.Description className="mt-4">
            {getMessage(targetStatus)}
          </Dialog.Description>

          <div className="mt-6 flex justify-end space-x-4">
            <Button
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
              aria-label="Cancel status change"
            >
              Cancel
            </Button>
            <Button
              onClick={onConfirm}
              disabled={isLoading}
              loading={isLoading}
              aria-label={`Confirm changing status to ${targetStatus}`}
            >
              {isLoading ? 'Updating...' : 'Update Status'}
            </Button>
          </div>
        </Dialog.Panel>
      </div>
    </Dialog>
  );
};

export default ConfirmStatusChangeModal;
