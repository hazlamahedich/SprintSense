/**
 * TypeScript types for work items.
 * Must match backend Pydantic schemas.
 */

export enum WorkItemType {
  EPIC = "EPIC",
  FEATURE = "FEATURE",
  USER_STORY = "USER_STORY",
  TASK = "TASK",
  BUG = "BUG",
  TECHNICAL_DEBT = "TECHNICAL_DEBT"
}

export enum WorkItemStatus {
  NEW = "NEW",
  APPROVED = "APPROVED",
  COMMITTED = "COMMITTED",
  DONE = "DONE"
}

export enum WorkItemPriority {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL"
}

export enum SortOrder {
  ASC = "asc",
  DESC = "desc"
}

export interface WorkItem {
  id: string;
  teamId: string;
  title: string;
  description?: string;
  type: WorkItemType;
  status: WorkItemStatus;
  priority: WorkItemPriority;
  assigneeId?: string;
  dueDate?: Date | string;
  storyPoints?: number;
  acceptanceCriteria?: string;
  tags?: string[];
  createdAt: Date | string;
  updatedAt: Date | string;
}

// Request/Response interfaces
export interface GetWorkItemsResponse {
  workItems: WorkItem[];
  total: number;
  page: number;
  size: number;
  hasMore: boolean;
}

export interface CreateWorkItemRequest {
  teamId: string;
  title: string;
  description?: string;
  type: WorkItemType;
  status: WorkItemStatus;
  priority: WorkItemPriority;
  assigneeId?: string;
  dueDate?: string;
  storyPoints?: number;
  acceptanceCriteria?: string;
  tags?: string[];
}

export interface UpdateWorkItemRequest {
  title?: string;
  description?: string;
  type?: WorkItemType;
  status?: WorkItemStatus;
  priority?: WorkItemPriority;
  assigneeId?: string;
  dueDate?: string;
  storyPoints?: number;
  acceptanceCriteria?: string;
  tags?: string[];
}

// Filtering and sorting
export interface WorkItemFilters {
  search?: string;
  types?: WorkItemType[];
  statuses?: WorkItemStatus[];
  priorities?: WorkItemPriority[];
  assigneeId?: string;
  dueDate?: {
    from?: string;
    to?: string;
  };
}

export interface WorkItemSort {
  field: string;
  order: SortOrder;
}

export interface WorkItemPagination {
  page: number;
  size: number;
}

// API related interfaces
export interface ApiError {
  message: string;
  details?: Record<string, unknown>;
}

// Store state interfaces
export interface BacklogState {
  workItems: WorkItem[];
  loading: boolean;
  error: ApiError | null;
  hasMore: boolean;
  totalCount: number;
  filters: WorkItemFilters;
  sort: WorkItemSort;
  pagination: WorkItemPagination;
}
