import React, { useCallback } from 'react';
import { WorkItemSort, SortOrder } from '../../types/workItem.types';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import {
  ArrowsUpDownIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  Bars3BottomLeftIcon
} from '@heroicons/react/24/outline';

interface SortControlsProps {
  sort: WorkItemSort;
  onSortChange: (sort: WorkItemSort) => void;
  className?: string;
}

const SORT_FIELD_LABELS: Record<string, string> = {
  'createdAt': 'Created Date',
  'updatedAt': 'Updated Date',
  'title': 'Title',
  'priority': 'Priority',
  'status': 'Status',
  'type': 'Type',
  'dueDate': 'Due Date',
  'storyPoints': 'Story Points'
};

const SORT_ORDER_LABELS: Record<SortOrder, string> = {
  [SortOrder.ASC]: 'Ascending',
  [SortOrder.DESC]: 'Descending'
};

export const SortControls: React.FC<SortControlsProps> = ({
  sort,
  onSortChange,
  className = ''
}) => {
  const handleFieldChange = useCallback((field: string) => {
    onSortChange({
      ...sort,
      field
    });
  }, [sort, onSortChange]);

  const handleOrderToggle = useCallback(() => {
    onSortChange({
      ...sort,
      order: sort.order === SortOrder.ASC ? SortOrder.DESC : SortOrder.ASC
    });
  }, [sort, onSortChange]);

  const currentFieldLabel = SORT_FIELD_LABELS[sort.field] || sort.field;
  const currentOrderLabel = SORT_ORDER_LABELS[sort.order];

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {/* Sort Field Dropdown */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm" className="flex items-center gap-2">
            <Bars3BottomLeftIcon className="w-4 h-4" />
            Sort by: {currentFieldLabel}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-48">
          <DropdownMenuLabel>Sort Field</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuRadioGroup
            value={sort.field}
            onValueChange={handleFieldChange}
          >
            {Object.entries(SORT_FIELD_LABELS).map(([field, label]) => (
              <DropdownMenuRadioItem key={field} value={field}>
                {label}
              </DropdownMenuRadioItem>
            ))}
          </DropdownMenuRadioGroup>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Sort Order Toggle */}
      <Button
        onClick={handleOrderToggle}
        variant="outline"
        size="sm"
        className="flex items-center gap-2"
        title={`Currently ${currentOrderLabel}. Click to toggle.`}
      >
        {sort.order === SortOrder.ASC ? (
          <ArrowUpIcon className="w-4 h-4" />
        ) : (
          <ArrowDownIcon className="w-4 h-4" />
        )}
        {currentOrderLabel}
      </Button>

      {/* Sort Summary Badge */}
      <Badge variant="secondary" className="flex items-center gap-1 text-xs">
        <ArrowsUpDownIcon className="w-3 h-3" />
        {currentFieldLabel} ({sort.order === SortOrder.ASC ? '↑' : '↓'})
      </Badge>
    </div>
  );
};

export default SortControls;
