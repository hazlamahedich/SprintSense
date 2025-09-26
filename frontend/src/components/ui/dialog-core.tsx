import React from 'react';
import { X } from 'lucide-react';

interface DialogProps extends React.DialogHTMLAttributes<HTMLDialogElement> {
  isOpen: boolean;
  onClose: () => void;
}

const Dialog = React.forwardRef<HTMLDialogElement, DialogProps>(
  ({ className, isOpen, onClose, children, ...props }, ref) => {
    React.useEffect(() => {
      const handleEscape = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
          onClose();
        }
      };

      if (isOpen) {
        document.addEventListener('keydown', handleEscape);
        document.body.style.overflow = 'hidden';
      }

      return () => {
        document.removeEventListener('keydown', handleEscape);
        document.body.style.overflow = '';
      };
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    return (
      <div className="fixed inset-0 z-50 bg-black bg-opacity-50">
        <dialog
          ref={ref}
          className={`fixed top-1/2 left-1/2 z-50 w-full max-w-lg -translate-x-1/2 -translate-y-1/2 rounded-lg bg-white p-6 shadow-lg ${className || ''}`}
          {...props}
          open
        >
          <button
            onClick={onClose}
            className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-white transition-opacity hover:opacity-100"
            aria-label="Close dialog"
          >
            <X className="h-4 w-4" />
          </button>
          {children}
        </dialog>
      </div>
    );
  }
);

const DialogHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, children, ...props }, ref) => (
  <div
    ref={ref}
    className={`mb-4 flex flex-col space-y-1.5 ${className || ''}`}
    {...props}
  >
    {children}
  </div>
));

const DialogFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, children, ...props }, ref) => (
  <div
    ref={ref}
    className={`mt-6 flex justify-end space-x-2 ${className || ''}`}
    {...props}
  >
    {children}
  </div>
));

Dialog.displayName = 'Dialog';
DialogHeader.displayName = 'DialogHeader';
DialogFooter.displayName = 'DialogFooter';

export { Dialog, DialogHeader, DialogFooter };
