import React, { useCallback } from 'react'
import {
  WorkItemType,
  WorkItemStatus,
  WorkItemFilters,
} from '../../types/workItem.types'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu'
import { Input } from '../ui/input'
import {
  FunnelIcon,
  XMarkIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline/index.js'

interface FilterControlsProps {
  filters: WorkItemFilters
  onFiltersChange: (filters: WorkItemFilters) => void
  onClearFilters: () => void
  className?: string
}

const TYPE_LABELS: Record<WorkItemType, string> = {
  [WorkItemType.EPIC]: 'Epic',
  [WorkItemType.FEATURE]: 'Feature',
  [WorkItemType.USER_STORY]: 'User Story',
  [WorkItemType.TASK]: 'Task',
  [WorkItemType.BUG]: 'Bug',
  [WorkItemType.TECHNICAL_DEBT]: 'Technical Debt',
}

const STATUS_LABELS: Record<WorkItemStatus, string> = {
  [WorkItemStatus.NEW]: 'New',
  [WorkItemStatus.APPROVED]: 'Approved',
  [WorkItemStatus.COMMITTED]: 'Committed',
  [WorkItemStatus.DONE]: 'Done',
}

// For now, we'll remove priority filtering since backend uses numeric priority
// This can be re-implemented with numeric ranges if needed in the future

export const FilterControls: React.FC<FilterControlsProps> = ({
  filters,
  onFiltersChange,
  onClearFilters,
  className = '',
}) => {
  const handleSearchChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      onFiltersChange({
        ...filters,
        search: e.target.value,
      })
    },
    [filters, onFiltersChange]
  )

  const handleTypeToggle = useCallback(
    (type: WorkItemType) => {
      const currentTypes = filters.types || []
      const newTypes = currentTypes.includes(type)
        ? currentTypes.filter((t) => t !== type)
        : [...currentTypes, type]

      onFiltersChange({
        ...filters,
        types: newTypes,
      })
    },
    [filters, onFiltersChange]
  )

  const handleStatusToggle = useCallback(
    (status: WorkItemStatus) => {
      const currentStatuses = filters.statuses || []
      const newStatuses = currentStatuses.includes(status)
        ? currentStatuses.filter((s) => s !== status)
        : [...currentStatuses, status]

      onFiltersChange({
        ...filters,
        statuses: newStatuses,
      })
    },
    [filters, onFiltersChange]
  )

  // Priority filtering removed - backend uses numeric priority values

  const handleAssigneeChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      onFiltersChange({
        ...filters,
        assigneeId: e.target.value || undefined,
      })
    },
    [filters, onFiltersChange]
  )

  const activeFiltersCount = [
    filters.search,
    filters.types?.length,
    filters.statuses?.length,
    filters.assigneeId,
  ].filter(Boolean).length

  const hasActiveFilters = activeFiltersCount > 0

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Search and Quick Actions */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* Search Input */}
        <div className="relative flex-1">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            placeholder="Search work items..."
            value={filters.search || ''}
            onChange={handleSearchChange}
            className="pl-10"
          />
        </div>

        {/* Filter Actions */}
        <div className="flex items-center gap-2">
          {hasActiveFilters && (
            <Button
              onClick={onClearFilters}
              variant="outline"
              size="sm"
              className="flex items-center gap-2"
            >
              <XMarkIcon className="w-4 h-4" />
              Clear All
            </Button>
          )}
        </div>
      </div>

      {/* Filter Dropdowns */}
      <div className="flex flex-wrap gap-3">
        {/* Type Filter */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              className="flex items-center gap-2"
            >
              <FunnelIcon className="w-4 h-4" />
              Type
              {filters.types && filters.types.length > 0 && (
                <Badge variant="secondary" className="text-xs">
                  {filters.types.length}
                </Badge>
              )}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-48">
            <DropdownMenuLabel>Work Item Type</DropdownMenuLabel>
            <DropdownMenuSeparator />
            {Object.entries(TYPE_LABELS).map(([type, label]) => (
              <DropdownMenuCheckboxItem
                key={type}
                checked={filters.types?.includes(type as WorkItemType) || false}
                onCheckedChange={() => handleTypeToggle(type as WorkItemType)}
              >
                {label}
              </DropdownMenuCheckboxItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Status Filter */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              className="flex items-center gap-2"
            >
              Status
              {filters.statuses && filters.statuses.length > 0 && (
                <Badge variant="secondary" className="text-xs">
                  {filters.statuses.length}
                </Badge>
              )}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-48">
            <DropdownMenuLabel>Status</DropdownMenuLabel>
            <DropdownMenuSeparator />
            {Object.entries(STATUS_LABELS).map(([status, label]) => (
              <DropdownMenuCheckboxItem
                key={status}
                checked={
                  filters.statuses?.includes(status as WorkItemStatus) || false
                }
                onCheckedChange={() =>
                  handleStatusToggle(status as WorkItemStatus)
                }
              >
                {label}
              </DropdownMenuCheckboxItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Priority Filter - Temporarily removed, will be re-implemented with numeric ranges */}

        {/* Assignee Filter */}
        <div className="flex items-center gap-2">
          <Input
            placeholder="Assignee ID..."
            value={filters.assigneeId || ''}
            onChange={handleAssigneeChange}
            className="w-32"
          />
        </div>
      </div>

      {/* Active Filters Display */}
      {hasActiveFilters && (
        <div className="flex flex-wrap gap-2 pt-2 border-t">
          {filters.search && (
            <Badge variant="outline" className="flex items-center gap-1">
              Search: "{filters.search}"
              <XMarkIcon
                className="w-3 h-3 cursor-pointer hover:text-red-600"
                onClick={() =>
                  onFiltersChange({ ...filters, search: undefined })
                }
              />
            </Badge>
          )}

          {filters.types?.map((type) => (
            <Badge
              key={type}
              variant="outline"
              className="flex items-center gap-1"
            >
              {TYPE_LABELS[type]}
              <XMarkIcon
                className="w-3 h-3 cursor-pointer hover:text-red-600"
                onClick={() => handleTypeToggle(type)}
              />
            </Badge>
          ))}

          {filters.statuses?.map((status) => (
            <Badge
              key={status}
              variant="outline"
              className="flex items-center gap-1"
            >
              {STATUS_LABELS[status]}
              <XMarkIcon
                className="w-3 h-3 cursor-pointer hover:text-red-600"
                onClick={() => handleStatusToggle(status)}
              />
            </Badge>
          ))}

          {/* Priority badges removed - using numeric priority now */}

          {filters.assigneeId && (
            <Badge variant="outline" className="flex items-center gap-1">
              Assignee: {filters.assigneeId}
              <XMarkIcon
                className="w-3 h-3 cursor-pointer hover:text-red-600"
                onClick={() =>
                  onFiltersChange({ ...filters, assigneeId: undefined })
                }
              />
            </Badge>
          )}
        </div>
      )}
    </div>
  )
}

export default FilterControls

