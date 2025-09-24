import React from 'react';
import { vi } from 'vitest';

// Mock implementation of Radix UI Select
const SelectMock = ({ value, onValueChange, children, ...props }: any) => {
  const [isOpen, setIsOpen] = React.useState(false);
  return (
    <div data-testid="select">
      {React.Children.map(children, (child) =>
        React.cloneElement(child as React.ReactElement, {
          value,
          onValueChange,
          isOpen,
          setIsOpen,
        })
      )}
    </div>
  );
};

const SelectTriggerMock = ({
  value,
  children,
  'aria-label': ariaLabel,
  className,
  isOpen,
  setIsOpen,
  ...props
}: any) => (
  <button
    type="button"
    role="combobox"
    aria-label={ariaLabel}
    aria-expanded={isOpen}
    aria-controls="radix-select-content"
  onClick={() => setIsOpen(true)}
    className={className}
    {...props}
  >
    {React.Children.map(children, (child) =>
      React.cloneElement(child as React.ReactElement, { value })
    )}
  </button>
);

const SelectValueMock = ({ value, children, placeholder, ...props }: any) => (
  <span {...props}>{value || placeholder}</span>
);

const SelectContentMock = ({ children, value, isOpen, onValueChange }: any) => {
  if (!isOpen) return null;
  return (
    <div
      role="listbox"
      id="radix-select-content"
      data-testid="select-content"
      aria-label="Options"
    >
      {React.Children.map(children, (child) =>
        React.cloneElement(child as React.ReactElement, {
          value,
          onValueChange,
        })
      )}
    </div>
  );
};

const SelectItemMock = ({ value, onValueChange, children, ...props }: any) => (
  <div
    role="option"
    aria-selected={false}
    onClick={() => onValueChange?.(value)}
    {...props}
  >
    {children}
  </div>
);

// Mock the module
vi.mock('@radix-ui/react-select', () => ({
  Root: SelectMock,
  Trigger: SelectTriggerMock,
  Value: SelectValueMock,
  Portal: ({ children }: any) => children,
  Content: SelectContentMock,
  Item: SelectItemMock,
  Group: ({ children }: any) => <div role="group">{children}</div>,
  ItemIndicator: ({ children }: any) => <span role="img">{children}</span>,
  ItemText: ({ children }: any) => <span>{children}</span>,
  Viewport: ({ children }: any) => children,
  Label: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Separator: (props: any) => <div role="separator" {...props} />,
}));
