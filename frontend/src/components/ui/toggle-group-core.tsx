import React from 'react';

interface ToggleGroupContext {
  value: string;
  onChange: (value: string) => void;
}

const ToggleGroupContext = React.createContext<ToggleGroupContext | undefined>(
  undefined
);

interface ToggleGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  value: string;
  onChange: (value: string) => void;
  type?: 'single' | 'multiple';
}

const ToggleGroup = React.forwardRef<HTMLDivElement, ToggleGroupProps>(
  ({ className, value, onChange, children, type = 'single', ...props }, ref) => {
    return (
      <ToggleGroupContext.Provider value={{ value, onChange }}>
        <div
          ref={ref}
          className={`inline-flex items-center justify-center rounded-lg bg-gray-100 p-1 ${
            className || ''
          }`}
          role="group"
          {...props}
        >
          {children}
        </div>
      </ToggleGroupContext.Provider>
    );
  }
);

interface ToggleGroupItemProps
  extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'value'> {
  value: string;
}

const ToggleGroupItem = React.forwardRef<HTMLButtonElement, ToggleGroupItemProps>(
  ({ className, children, value, ...props }, ref) => {
    const context = React.useContext(ToggleGroupContext);
    if (!context) {
      throw new Error('ToggleGroupItem must be used within a ToggleGroup');
    }

    const isSelected = context.value === value;

    return (
      <button
        ref={ref}
        className={`inline-flex items-center justify-center rounded-md px-3 py-1.5 text-sm font-medium transition-all hover:bg-white hover:shadow-sm ${
          isSelected ? 'bg-white shadow-sm' : ''
        } ${className || ''}`}
        role="radio"
        tabIndex={0}
        aria-checked={isSelected}
        onClick={() => context.onChange(value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            context.onChange(value);
          }
        }}
        {...props}
      >
        {children}
      </button>
    );
  }
);

ToggleGroup.displayName = 'ToggleGroup';
ToggleGroupItem.displayName = 'ToggleGroupItem';

export { ToggleGroup, ToggleGroupItem };
