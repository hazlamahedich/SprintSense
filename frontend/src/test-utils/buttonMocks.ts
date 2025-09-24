import React from 'react';
import { vi } from 'vitest';

// Mock for button component
vi.mock('@/components/ui/button-radix', () => {
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
            Loading...
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
