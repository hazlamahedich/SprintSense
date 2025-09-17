import React from 'react';
import { Button } from '../ui/button';
import { ToggleGroup, ToggleGroupItem } from '../ui/toggle-group';
import {
  ListBulletIcon,
  Squares2X2Icon,
  TableCellsIcon
} from '@heroicons/react/24/outline';

export enum ViewMode {
  LIST = 'list',
  KANBAN = 'kanban',
  TABLE = 'table'
}

interface ViewModeToggleProps {
  viewMode: ViewMode;
  onViewModeChange: (mode: ViewMode) => void;
  className?: string;
}

const VIEW_MODE_OPTIONS = [
  {
    value: ViewMode.LIST,
    label: 'List View',
    icon: ListBulletIcon,
    description: 'View work items in a vertical list format'
  },
  {
    value: ViewMode.KANBAN,
    label: 'Kanban Board',
    icon: Squares2X2Icon,
    description: 'View work items in a kanban board organized by status'
  },
  {
    value: ViewMode.TABLE,
    label: 'Table View',
    icon: TableCellsIcon,
    description: 'View work items in a structured table format'
  }
];

export const ViewModeToggle: React.FC<ViewModeToggleProps> = ({
  viewMode,
  onViewModeChange,
  className = ''
}) => {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span className="text-sm font-medium text-gray-700">View:</span>

      <ToggleGroup
        type="single"
        value={viewMode}
        onValueChange={(value) => {
          if (value && Object.values(ViewMode).includes(value as ViewMode)) {
            onViewModeChange(value as ViewMode);
          }
        }}
        className="bg-gray-100 p-1 rounded-md"
      >
        {VIEW_MODE_OPTIONS.map((option) => {
          const IconComponent = option.icon;
          return (
            <ToggleGroupItem
              key={option.value}
              value={option.value}
              aria-label={option.label}
              title={option.description}
              className="flex items-center gap-2 px-3 py-2 text-sm rounded data-[state=on]:bg-white data-[state=on]:shadow-sm"
            >
              <IconComponent className="w-4 h-4" />
              <span className="hidden sm:inline">{option.label}</span>
            </ToggleGroupItem>
          );
        })}
      </ToggleGroup>
    </div>
  );
};

export default ViewModeToggle;
