/**
 * Custom hook for work items data fetching and management.
 * Provides a clean interface to the backlog store.
 */

import { useCallback, useEffect } from 'react'
import { useBacklogStore } from '../stores/backlogStore'
import {
  WorkItem,
  WorkItemCreateRequest,
  WorkItemFilters,
  WorkItemUpdateRequest,
  WorkItemSort,
  WorkItemPagination,
  ApiError,
} from '../types/workItem.types'

export interface UseWorkItemsReturn {
  // Data
  workItems: WorkItem[]
  loading: boolean
  error: ApiError | null
  hasMore: boolean
  totalCount: number
  filters: WorkItemFilters
  sort: WorkItemSort
  pagination: WorkItemPagination

  // Actions
  loadWorkItems: () => Promise<void>
  refreshWorkItems: () => Promise<void>
  createWorkItem: (data: WorkItemCreateRequest) => Promise<void>
  updateWorkItem: (
    workItemId: string,
    data: WorkItemUpdateRequest
  ) => Promise<void>
  deleteWorkItem: (workItemId: string) => Promise<void>

  // State setters
  setFilters: (filters: WorkItemFilters) => void
  setSort: (sort: WorkItemSort) => void
  setPagination: (
    pagination:
      | WorkItemPagination
      | ((prev: WorkItemPagination) => WorkItemPagination)
  ) => void
}

/**
 * Hook for work items management.
 * @param teamId - Optional team ID to auto-load work items
 */
export const useWorkItems = (teamId?: string): UseWorkItemsReturn => {
  const {
    workItems,
    loading,
    error,
    pagination,
    filters,
    selectedTeamId,
    loadWorkItems: storeLoadWorkItems,
    refreshWorkItems: storeRefreshWorkItems,
    createWorkItem: storeCreateWorkItem,
    updateWorkItem: storeUpdateWorkItem,
    deleteWorkItem: storeDeleteWorkItem,
    setFilter,
    clearFilters,
    setSort: storeSetSort,
    setPage,
    setTeam,
    clearError,
  } = useBacklogStore()

  // Auto-load work items when teamId changes
  useEffect(() => {
    if (teamId && teamId !== selectedTeamId) {
      setTeam(teamId)
    }
  }, [teamId, selectedTeamId, setTeam])

  // Memoized actions to match expected interface
  const loadWorkItems = useCallback(async () => {
    if (teamId) {
      await storeLoadWorkItems(teamId)
    }
  }, [teamId, storeLoadWorkItems])

  const refreshWorkItems = useCallback(async () => {
    await storeRefreshWorkItems()
  }, [storeRefreshWorkItems])

  const createWorkItem = useCallback(
    async (data: CreateWorkItemRequest) => {
      if (teamId) {
        const dataWithTeam = { ...data, teamId }
        await storeCreateWorkItem(teamId, dataWithTeam)
      }
    },
    [teamId, storeCreateWorkItem]
  )

  const updateWorkItem = useCallback(
    async (workItemId: string, data: WorkItemUpdateRequest) => {
      if (teamId) {
        await storeUpdateWorkItem(teamId, workItemId, data)
      }
    },
    [teamId, storeUpdateWorkItem]
  )

  const deleteWorkItem = useCallback(
    async (workItemId: string) => {
      if (teamId) {
        await storeDeleteWorkItem(teamId, workItemId)
      }
    },
    [teamId, storeDeleteWorkItem]
  )

  const setFilters = useCallback(
    (newFilters: WorkItemFilters) => {
      Object.entries(newFilters).forEach(([key, value]) => {
        setFilter(key as keyof WorkItemFilters, value)
      })
    },
    [setFilter]
  )

  const setSort = useCallback(
    (sort: WorkItemSort) => {
      storeSetSort(sort.field, sort.order)
    },
    [storeSetSort]
  )

  const setPagination = useCallback(
    (
      paginationOrUpdater:
        | WorkItemPagination
        | ((prev: WorkItemPagination) => WorkItemPagination)
    ) => {
      if (typeof paginationOrUpdater === 'function') {
        const currentPagination = {
          page: pagination.page,
          size: pagination.limit,
        }
        const newPagination = paginationOrUpdater(currentPagination)
        setPage(newPagination.page)
      } else {
        setPage(paginationOrUpdater.page)
      }
    },
    [pagination, setPage]
  )

  // Computed values
  const totalPages = Math.ceil(pagination.total / pagination.limit)
  const hasMore = pagination.page < totalPages

  return {
    // Data
    workItems,
    loading,
    error,
    hasMore,
    totalCount: pagination.total,
    filters,
    sort: {
      field: filters.sort_by || 'priority',
      order: filters.sort_order || 'asc',
    },
    pagination: {
      page: pagination.page,
      size: pagination.limit,
    },

    // Actions
    loadWorkItems,
    refreshWorkItems,
    createWorkItem,
    updateWorkItem,
    deleteWorkItem,

    // State setters
    setFilters,
    setSort,
    setPagination,
    clearFilters,
    clearError,
  }
}
