import React from 'react';
import { Button } from '../../ui/button';
import { Plus, Sparkles } from 'lucide-react';

interface CreateWorkItemButtonProps {
  onClick: () => void;
  disabled?: boolean;
  variant?: 'floating' | 'header' | 'inline';
  className?: string;
}

export const CreateWorkItemButton: React.FC<CreateWorkItemButtonProps> = ({
  onClick,
  disabled = false,
  variant = 'header',
  className = ''
}) => {
  const baseClasses = "relative overflow-hidden transition-all duration-200 font-medium";

  const variantClasses = {
    floating: `
      fixed bottom-6 right-6 z-50 h-14 w-14 rounded-full shadow-lg hover:shadow-xl
      bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800
      text-white border-0 transform hover:scale-105 active:scale-95
    `,
    header: `
      h-10 px-4 rounded-lg shadow-md hover:shadow-lg
      bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800
      text-white border-0 transform hover:-translate-y-0.5 active:translate-y-0
    `,
    inline: `
      h-9 px-3 rounded-md
      bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800
      text-white border-0 hover:shadow-md
    `
  };

  const content = {
    floating: (
      <div className="flex items-center justify-center">
        <Plus className="w-6 h-6" />
      </div>
    ),
    header: (
      <div className="flex items-center gap-2">
        <div className="relative">
          <Plus className="w-4 h-4" />
          <Sparkles className="w-2 h-2 absolute -top-1 -right-1 text-yellow-300 animate-pulse" />
        </div>
        <span>Create Work Item</span>
      </div>
    ),
    inline: (
      <div className="flex items-center gap-2">
        <Plus className="w-4 h-4" />
        <span>Add Item</span>
      </div>
    )
  };

  const ariaLabels = {
    floating: "Create new work item (floating button)",
    header: "Create new work item",
    inline: "Add new work item"
  };

  return (
    <Button
      onClick={onClick}
      disabled={disabled}
      className={`
        ${baseClasses}
        ${variantClasses[variant]}
        ${disabled ? 'opacity-50 cursor-not-allowed transform-none shadow-none' : ''}
        ${className}
      `}
      aria-label={ariaLabels[variant]}
      title={variant === 'floating' ? 'Create New Work Item' : undefined}
    >
      {/* Shine effect overlay */}
      <div
        className={`
          absolute inset-0 -top-1 -left-1 bg-gradient-to-r from-transparent via-white to-transparent
          opacity-0 group-hover:opacity-20 transform -skew-x-12 transition-all duration-700
          ${variant === 'floating' ? 'group-hover:animate-pulse' : ''}
        `}
      />

      {/* Button content */}
      <div className="relative z-10">
        {content[variant]}
      </div>

      {/* Tooltip for floating variant */}
      {variant === 'floating' && (
        <div className="absolute right-full mr-3 top-1/2 transform -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
          <div className="bg-gray-900 text-white text-xs rounded-md px-2 py-1 whitespace-nowrap">
            Create Work Item
            <div className="absolute left-full top-1/2 transform -translate-y-1/2 w-0 h-0 border-l-4 border-l-gray-900 border-y-4 border-y-transparent"></div>
          </div>
        </div>
      )}
    </Button>
  );
};

export default CreateWorkItemButton;