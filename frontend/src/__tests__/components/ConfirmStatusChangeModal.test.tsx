import React from 'react';
// Mock the Button component to avoid depending on lucide-react Loader2
vi.mock('@/components/ui/button-radix', () => {
  const React = require('react');
  const Button = React.forwardRef(
    ({ children, loading, disabled, onClick, className, 'aria-label': ariaLabel }: any, ref: any) => {
        if (loading) {
        return (
          <button
            ref={ref}
            className={className}
            disabled={true}
            aria-label={ariaLabel}
          >
            <div data-testid="loading-spinner" aria-hidden="true" />
            Updating...
          </button>
        );
      }

      return (
        <button
          ref={ref}
          className={className}
          disabled={disabled}
          onClick={onClick}
          aria-label={ariaLabel}
        >
          {children}
        </button>
      );
    }
  );
  Button.displayName = 'Button';
  return { Button, buttonVariants: () => '' };
});
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '../test-utils/setup';
import { vi } from 'vitest';

// Import components
import { ConfirmStatusChangeModal } from '@/components/common/ConfirmStatusChangeModal';
import { WorkItemStatus } from '@/types/workItem.types';

describe('ConfirmStatusChangeModal', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    onConfirm: vi.fn(),
    title: 'Update Status',
    targetStatus: WorkItemStatus.DONE,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders with correct title and message for Done status', () => {
    render(<ConfirmStatusChangeModal {...defaultProps} />);

    expect(screen.getByTestId('dialog-title')).toHaveTextContent('Update Status');
    expect(screen.getByText(/mark this item as Done/)).toBeInTheDocument();
  });

  it('renders with correct message for In Progress status', () => {
    render(
      <ConfirmStatusChangeModal
        {...defaultProps}
        targetStatus={WorkItemStatus.IN_PROGRESS}
      />
    );

    expect(screen.getByText(/move this item back to In Progress/)).toBeInTheDocument();
  });

  it('calls onClose when Cancel button is clicked', () => {
    render(<ConfirmStatusChangeModal {...defaultProps} />);

    fireEvent.click(screen.getByText('Cancel'));
    expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when close icon is clicked', () => {
    render(<ConfirmStatusChangeModal {...defaultProps} />);

    fireEvent.click(screen.getByLabelText('Close dialog'));
    expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onConfirm when Update Status button is clicked', async () => {
    const onConfirm = vi.fn().mockResolvedValue(undefined);
    render(<ConfirmStatusChangeModal {...defaultProps} onConfirm={onConfirm} />);

    fireEvent.click(screen.getByLabelText('Confirm changing status to done'));
    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it('shows loading state during confirmation', async () => {
    const onConfirm = vi.fn().mockImplementation(() => new Promise(() => {}));
    const { container } = render(
      <ConfirmStatusChangeModal
        {...defaultProps}
        onConfirm={onConfirm}
        isLoading={true}
      />
    );

    const updateButton = screen.getByRole('button', { name: 'Confirm changing status to done' });
    const cancelButton = screen.getByRole('button', { name: 'Cancel status change' });

    expect(updateButton).toHaveTextContent('Updating...');
    expect(updateButton).toBeDisabled();
    expect(cancelButton).toBeDisabled();
    expect(container.querySelector('[data-testid="loading-spinner"]')).toBeInTheDocument();
  });

  it('provides proper aria labels for accessibility', () => {
    render(<ConfirmStatusChangeModal {...defaultProps} />);

    expect(screen.getByLabelText('Close dialog')).toBeInTheDocument();
    expect(screen.getByLabelText('Cancel status change')).toBeInTheDocument();
    expect(
      screen.getByLabelText(`Confirm changing status to ${WorkItemStatus.DONE}`)
    ).toBeInTheDocument();
  });
});
