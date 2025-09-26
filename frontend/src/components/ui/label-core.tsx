import React from 'react';

interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  optional?: boolean;
}

const Label = React.forwardRef<HTMLLabelElement, LabelProps>(
  ({ className, optional, children, ...props }, ref) => {
    return (
      <label
        ref={ref}
        className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${
          className || ''
        }`}
        {...props}
      >
        {children}
        {optional && (
          <span className="ml-1 text-xs text-gray-500">(optional)</span>
        )}
      </label>
    );
  }
);

Label.displayName = 'Label';

export { Label };
