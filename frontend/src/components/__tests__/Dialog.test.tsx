import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import { Dialog, DialogHeader, DialogFooter } from '../ui/dialog-core';

describe('Dialog', () => {
  it('renders when isOpen is true', () => {
    const onClose = vi.fn();
    render(
      <Dialog isOpen onClose={onClose}>
        <DialogHeader>Test Dialog</DialogHeader>
        <div>Content</div>
        <DialogFooter>
          <button>Close</button>
        </DialogFooter>
      </Dialog>
    );

    expect(screen.getByText('Test Dialog')).toBeInTheDocument();
    expect(screen.getByText('Content')).toBeInTheDocument();
    expect(screen.getByText('Close')).toBeInTheDocument();
  });

  it('does not render when isOpen is false', () => {
    const onClose = vi.fn();
    render(
      <Dialog isOpen={false} onClose={onClose}>
        <div>Content</div>
      </Dialog>
    );

    expect(screen.queryByText('Content')).not.toBeInTheDocument();
  });

  it('calls onClose when clicking the close button', () => {
    const onClose = vi.fn();
    render(
      <Dialog isOpen onClose={onClose}>
        <div>Content</div>
      </Dialog>
    );

    const closeButton = screen.getByLabelText('Close dialog');
    fireEvent.click(closeButton);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when pressing Escape', () => {
    const onClose = vi.fn();
    render(
      <Dialog isOpen onClose={onClose}>
        <div>Content</div>
      </Dialog>
    );

    fireEvent.keyDown(document.body, { key: 'Escape' });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('applies custom className', () => {
    const onClose = vi.fn();
    render(
      <Dialog isOpen onClose={onClose} className="custom-class">
        <div>Content</div>
      </Dialog>
    );

    expect(screen.getByRole('dialog')).toHaveClass('custom-class');
  });

  it('handles DialogHeader and DialogFooter styles', () => {
    render(
      <Dialog isOpen onClose={vi.fn()}>
        <DialogHeader className="header-class">Header</DialogHeader>
        <div>Content</div>
        <DialogFooter className="footer-class">Footer</DialogFooter>
      </Dialog>
    );

    expect(screen.getByText('Header').closest('div')).toHaveClass('header-class');
    expect(screen.getByText('Footer').closest('div')).toHaveClass('footer-class');
  });

  it('removes event listeners on unmount', () => {
    const onClose = vi.fn();
    const { unmount } = render(
      <Dialog isOpen onClose={onClose}>
        <div>Content</div>
      </Dialog>
    );

    unmount();
    fireEvent.keyDown(document.body, { key: 'Escape' });
    expect(onClose).not.toHaveBeenCalled();
  });
});
