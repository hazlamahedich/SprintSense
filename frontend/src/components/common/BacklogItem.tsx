import React from 'react';
import { WorkItem, WorkItemType, WorkItemStatus, WorkItemPriority } from '../../types/workItem.types';
import { Card, CardHeader, CardContent, CardFooter } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import {
  CalendarIcon,
  UserIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  MinusIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/react/24/outline';

interface BacklogItemProps {
  workItem: WorkItem;
  onEdit: (workItem: WorkItem) => void;
  onDelete: (id: string) => void;
  onMove?: (id: string, direction: 'up' | 'down') => void;
  showMoveButtons?: boolean;
  className?: string;
}

const TYPE_COLORS: Record<WorkItemType, string> = {
  [WorkItemType.EPIC]: 'bg-purple-100 text-purple-800',
  [WorkItemType.FEATURE]: 'bg-blue-100 text-blue-800',
  [WorkItemType.USER_STORY]: 'bg-green-100 text-green-800',
  [WorkItemType.TASK]: 'bg-yellow-100 text-yellow-800',
  [WorkItemType.BUG]: 'bg-red-100 text-red-800',
  [WorkItemType.TECHNICAL_DEBT]: 'bg-gray-100 text-gray-800'
};

const STATUS_COLORS: Record<WorkItemStatus, string> = {
  [WorkItemStatus.NEW]: 'bg-slate-100 text-slate-800',
  [WorkItemStatus.APPROVED]: 'bg-cyan-100 text-cyan-800',
  [WorkItemStatus.COMMITTED]: 'bg-blue-100 text-blue-800',
  [WorkItemStatus.DONE]: 'bg-green-100 text-green-800'
};

const PRIORITY_COLORS: Record<WorkItemPriority, string> = {
  [WorkItemPriority.LOW]: 'bg-gray-100 text-gray-600',
  [WorkItemPriority.MEDIUM]: 'bg-yellow-100 text-yellow-600',
  [WorkItemPriority.HIGH]: 'bg-orange-100 text-orange-600',
  [WorkItemPriority.CRITICAL]: 'bg-red-100 text-red-600'
};

const PRIORITY_ICONS = {
  [WorkItemPriority.LOW]: MinusIcon,
  [WorkItemPriority.MEDIUM]: MinusIcon,
  [WorkItemPriority.HIGH]: ArrowUpIcon,
  [WorkItemPriority.CRITICAL]: ArrowUpIcon
};

export const BacklogItem: React.FC<BacklogItemProps> = ({
  workItem,
  onEdit,
  onDelete,
  onMove,
  showMoveButtons = false,
  className = ''
}) => {
  const PriorityIcon = PRIORITY_ICONS[workItem.priority];

  const handleEdit = () => {
    onEdit(workItem);
  };

  const handleDelete = () => {
    onDelete(workItem.id);
  };

  const handleMoveUp = () => {
    onMove?.(workItem.id, 'up');
  };

  const handleMoveDown = () => {
    onMove?.(workItem.id, 'down');
  };

  return (
    <Card className={`hover:shadow-md transition-shadow ${className}`}>
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <div className="flex items-center gap-2 flex-1">
            <Badge className={TYPE_COLORS[workItem.type]}>
              {workItem.type.replace('_', ' ')}
            </Badge>
            <Badge className={STATUS_COLORS[workItem.status]}>
              {workItem.status}
            </Badge>
            <Badge className={`${PRIORITY_COLORS[workItem.priority]} flex items-center gap-1`}>
              <PriorityIcon className="w-3 h-3" />
              {workItem.priority}
            </Badge>
          </div>
          <div className="flex items-center gap-1">
            {showMoveButtons && onMove && (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleMoveUp}
                  className="p-1 h-8 w-8"
                  title="Move up"
                >
                  <ArrowUpIcon className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleMoveDown}
                  className="p-1 h-8 w-8"
                  title="Move down"
                >
                  <ArrowDownIcon className="w-4 h-4" />
                </Button>
              </>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleEdit}
              className="p-1 h-8 w-8"
              title="Edit"
            >
              <PencilIcon className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDelete}
              className="p-1 h-8 w-8 text-red-600 hover:text-red-800"
              title="Delete"
            >
              <TrashIcon className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pb-2">
        <h3 className="font-semibold text-lg mb-2 line-clamp-2">
          {workItem.title}
        </h3>
        {workItem.description && (
          <p className="text-gray-600 text-sm line-clamp-3 mb-3">
            {workItem.description}
          </p>
        )}
        <div className="flex items-center gap-4 text-sm text-gray-500">
          {workItem.assigneeId && (
            <div className="flex items-center gap-1">
              <UserIcon className="w-4 h-4" />
              <span>Assignee: {workItem.assigneeId}</span>
            </div>
          )}
          {workItem.dueDate && (
            <div className="flex items-center gap-1">
              <CalendarIcon className="w-4 h-4" />
              <span>Due: {new Date(workItem.dueDate).toLocaleDateString()}</span>
            </div>
          )}
        </div>
      </CardContent>

      <CardFooter className="pt-2 border-t">
        <div className="flex justify-between items-center w-full text-xs text-gray-500">
          <span>ID: {workItem.id.slice(0, 8)}</span>
          <div className="flex items-center gap-4">
            {workItem.storyPoints && (
              <span>Story Points: {workItem.storyPoints}</span>
            )}
            <span>Created: {new Date(workItem.createdAt).toLocaleDateString()}</span>
          </div>
        </div>
      </CardFooter>
    </Card>
  );
};

export default BacklogItem;
