/**
 * Zustand store for backlog state management.
 * Handles work items, filtering, sorting, and pagination.
 */

import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

import {
  BacklogState,
  WorkItemCreateRequest,
  WorkItemFilters,
  WorkItemUpdateRequest,
} from '../types/workItem.types'
import { workItemService } from '../services/workItemService'

interface BacklogActions {
  // Data loading
  loadWorkItems: (teamId: string, reset?: boolean) => Promise<void>
  refreshWorkItems: () => Promise<void>

  // CRUD operations
  createWorkItem: (teamId: string, data: WorkItemCreateRequest) => Promise<void>
  updateWorkItem: (
    teamId: string,
    workItemId: string,
    data: WorkItemUpdateRequest
  ) => Promise<void>
  deleteWorkItem: (teamId: string, workItemId: string) => Promise<void>

  // Filtering and sorting
  setFilter: (key: keyof WorkItemFilters, value: string | undefined) => void
  clearFilters: () => void
  setSort: (sortBy: string, sortOrder: 'asc' | 'desc') => void

  // Pagination
  setPage: (page: number) => void
  nextPage: () => void
  prevPage: () => void

  // State management
  setTeam: (teamId: string) => void
  clearError: () => void
  reset: () => void
}

type BacklogStore = BacklogState & BacklogActions

const initialState: BacklogState = {
  workItems: [],
  loading: false,
  error: null,
  filters: {
    sort_by: 'priority',
    sort_order: 'asc',
  },
  pagination: {
    page: 1,
    limit: 50,
    offset: 0,
    total: 0,
  },
  selectedTeamId: null,
}

export const useBacklogStore = create<BacklogStore>()(
  devtools(
    (set, get) => ({
      ...initialState,

      // Load work items with current filters and pagination
      loadWorkItems: async (teamId: string, reset = false) => {
        const state = get()

        // If reset or team changed, reset pagination
        if (reset || state.selectedTeamId !== teamId) {
          set({
            selectedTeamId: teamId,
            pagination: { ...initialState.pagination },
            error: null,
          })
        }

        set({ loading: true, error: null })

        try {
          const currentState = get()
          const response = await workItemService.getWorkItems(
            teamId,
            currentState.pagination.limit,
            currentState.pagination.offset,
            currentState.filters
          )

          set({
            workItems: response.items,
            pagination: {
              ...currentState.pagination,
              page: response.page,
              total: response.total,
            },
            loading: false,
          })
        } catch (error) {
          const errorMessage =
            error instanceof Error ? error.message : 'Unknown error'
          set({
            loading: false,
            error: {
              error: 'load_failed',
              message: errorMessage,
            },
            workItems: [],
          })
        }
      },

      // Refresh current data
      refreshWorkItems: async () => {
        const { selectedTeamId, loadWorkItems } = get()
        if (selectedTeamId) {
          await loadWorkItems(selectedTeamId, false)
        }
      },

      // Create new work item
      createWorkItem: async (teamId: string, data: WorkItemCreateRequest) => {
        set({ loading: true, error: null })

        try {
          const newItem = await workItemService.createWorkItem(teamId, data)

          // Add to current list and refresh to get updated pagination
          const state = get()
          set({
            workItems: [newItem, ...state.workItems],
            loading: false,
          })

          // Refresh to get accurate totals
          await get().refreshWorkItems()
        } catch (error) {
          const errorMessage =
            error instanceof Error ? error.message : 'Unknown error'
          set({
            loading: false,
            error: {
              error: 'create_failed',
              message: errorMessage,
            },
          })
          throw error
        }
      },

      // Update existing work item
      updateWorkItem: async (
        teamId: string,
        workItemId: string,
        data: WorkItemUpdateRequest
      ) => {
        set({ loading: true, error: null })

        try {
          const updatedItem = await workItemService.updateWorkItem(
            teamId,
            workItemId,
            data
          )

          const state = get()
          set({
            workItems: state.workItems.map((item) =>
              item.id === workItemId ? updatedItem : item
            ),
            loading: false,
          })
        } catch (error) {
          const errorMessage =
            error instanceof Error ? error.message : 'Unknown error'
          set({
            loading: false,
            error: {
              error: 'update_failed',
              message: errorMessage,
            },
          })
          throw error
        }
      },

      // Delete (archive) work item
      deleteWorkItem: async (teamId: string, workItemId: string) => {
        set({ loading: true, error: null })

        try {
          await workItemService.deleteWorkItem(teamId, workItemId)

          const state = get()
          set({
            workItems: state.workItems.filter((item) => item.id !== workItemId),
            loading: false,
          })

          // Refresh to get accurate totals
          await get().refreshWorkItems()
        } catch (error) {
          const errorMessage =
            error instanceof Error ? error.message : 'Unknown error'
          set({
            loading: false,
            error: {
              error: 'delete_failed',
              message: errorMessage,
            },
          })
          throw error
        }
      },

      // Set individual filter
      setFilter: (key: keyof WorkItemFilters, value: string | undefined) => {
        const state = get()
        const newFilters = {
          ...state.filters,
          [key]: value,
        }

        set({
          filters: newFilters,
          pagination: { ...initialState.pagination }, // Reset pagination
        })

        // Auto-reload if team is selected
        if (state.selectedTeamId) {
          setTimeout(
            () => get().loadWorkItems(state.selectedTeamId!, true),
            100
          )
        }
      },

      // Clear all filters
      clearFilters: () => {
        set({
          filters: {
            sort_by: 'priority',
            sort_order: 'asc',
          },
          pagination: { ...initialState.pagination },
        })

        const { selectedTeamId } = get()
        if (selectedTeamId) {
          get().loadWorkItems(selectedTeamId, true)
        }
      },

      // Set sorting
      setSort: (sortBy: string, sortOrder: 'asc' | 'desc') => {
        const state = get()
        set({
          filters: {
            ...state.filters,
            sort_by: sortBy,
            sort_order: sortOrder,
          },
          pagination: { ...initialState.pagination },
        })

        if (state.selectedTeamId) {
          get().loadWorkItems(state.selectedTeamId, true)
        }
      },

      // Pagination controls
      setPage: (page: number) => {
        const state = get()
        const offset = (page - 1) * state.pagination.limit

        set({
          pagination: {
            ...state.pagination,
            page,
            offset,
          },
        })

        if (state.selectedTeamId) {
          get().loadWorkItems(state.selectedTeamId, false)
        }
      },

      nextPage: () => {
        const state = get()
        const maxPage = Math.ceil(
          state.pagination.total / state.pagination.limit
        )
        if (state.pagination.page < maxPage) {
          get().setPage(state.pagination.page + 1)
        }
      },

      prevPage: () => {
        const state = get()
        if (state.pagination.page > 1) {
          get().setPage(state.pagination.page - 1)
        }
      },

      // State management
      setTeam: (teamId: string) => {
        set({ selectedTeamId: teamId })
        get().loadWorkItems(teamId, true)
      },

      clearError: () => {
        set({ error: null })
      },

      reset: () => {
        set(initialState)
      },
    }),
    {
      name: 'backlog-store',
    }
  )
)
