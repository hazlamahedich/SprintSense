/**
 * Work item API service for backend communication.
 * Implements API calls for work item operations.
 */

import axios from 'axios'
import {
  WorkItem,
  CreateWorkItemRequest,
  UpdateWorkItemRequest,
  WorkItemFilters,
  WorkItemSort,
  GetWorkItemsResponse,
  SortOrder,
  PriorityUpdateRequest,
} from '../types/workItem.types'

interface GetWorkItemsOptions {
  filters?: WorkItemFilters
  sort?: WorkItemSort
  page?: number
  size?: number
}

interface QueryParams {
  page: number
  size: number
  search?: string
  types?: string
  statuses?: string
  priorities?: string
  assigneeId?: string
  sortField?: string
  sortOrder?: string
}

class WorkItemServiceClass {
  private baseUrl = '/api/v1/teams'

  /**
   * Get work items for a team with filtering, sorting, and pagination.
   */
  async getWorkItems(
    teamId: string,
    options: GetWorkItemsOptions = {}
  ): Promise<GetWorkItemsResponse> {
    const { filters = {}, sort, page = 1, size = 20 } = options

    const params: QueryParams = {
      page,
      size,
    }

    // Add filters
    if (filters.search) {
      params.search = filters.search
    }

    if (filters.types && filters.types.length > 0) {
      params.types =
        filters.types.length === 1 ? filters.types[0] : filters.types.join(',')
    }

    if (filters.statuses && filters.statuses.length > 0) {
      params.statuses = filters.statuses.join(',')
    }

    if (filters.priorities && filters.priorities.length > 0) {
      params.priorities =
        filters.priorities.length === 1
          ? filters.priorities[0]
          : filters.priorities.join(',')
    }

    if (filters.assigneeId) {
      params.assigneeId = filters.assigneeId
    }

    // Add sorting
    if (sort) {
      params.sortField = sort.field
      params.sortOrder = sort.order === SortOrder.ASC ? 'asc' : 'desc'
    }

    const response = await axios.get(`${this.baseUrl}/${teamId}/work-items`, {
      params,
    })

    // Transform response to match expected format
    const data = response.data
    return {
      items: data.items || data.workItems || [],
      total: data.total || 0,
      page: data.page || 1,
      size: data.size || 20,
    }
  }

  /**
   * Get a single work item by ID.
   */
  async getWorkItem(teamId: string, workItemId: string): Promise<WorkItem> {
    const response = await axios.get(
      `${this.baseUrl}/${teamId}/work-items/${workItemId}`
    )
    return response.data
  }

  /**
   * Create a new work item.
   */
  async createWorkItem(
    teamId: string,
    workItemData: CreateWorkItemRequest
  ): Promise<WorkItem> {
    const response = await axios.post(
      `${this.baseUrl}/${teamId}/work-items`,
      workItemData
    )
    return response.data
  }

  /**
   * Update an existing work item.
   */
  async updateWorkItem(
    teamId: string,
    workItemId: string,
    workItemData: UpdateWorkItemRequest
  ): Promise<WorkItem> {
    const response = await axios.patch(
      `${this.baseUrl}/${teamId}/work-items/${workItemId}`,
      workItemData
    )
    return response.data
  }

  /**
   * Archive (soft delete) a work item.
   */
  async archiveWorkItem(teamId: string, workItemId: string): Promise<WorkItem> {
    const response = await axios.patch(
      `${this.baseUrl}/${teamId}/work-items/${workItemId}/archive`
    )
    return response.data
  }

  /**
   * Delete a work item.
   */
  async deleteWorkItem(teamId: string, workItemId: string): Promise<void> {
    await axios.delete(`${this.baseUrl}/${teamId}/work-items/${workItemId}`)
  }

  /**
   * Update work item priority using priority actions.
   * Implements Story 2.6 requirements for accessible priority management.
   */
  async updateWorkItemPriority(
    teamId: string,
    workItemId: string,
    priorityData: PriorityUpdateRequest
  ): Promise<WorkItem> {
    const response = await axios.patch(
      `${this.baseUrl}/${teamId}/work-items/${workItemId}/priority`,
      priorityData
    )
    return response.data
  }
}

// Export singleton instance
export const workItemService = new WorkItemServiceClass()
export default workItemService
