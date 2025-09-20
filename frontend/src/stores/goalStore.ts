/**
 * Zustand store for project goals state management.
 * Handles goals CRUD operations, loading states, and error handling.
 *
 * Implements Story 3.1 requirements for comprehensive goal management
 * with role-based permissions and real-time updates.
 */

import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

import {
  ProjectGoal,
  ProjectGoalCreateRequest,
  ProjectGoalUpdateRequest,
  TeamRole,
  GoalPermissions,
  getGoalPermissions,
} from '../types/goal.types'
import { GoalService } from '../services/goalService'

// Goal-specific state
interface GoalState {
  goals: ProjectGoal[]
  loading: boolean
  error: {
    error: string
    message: string
  } | null
  selectedTeamId: string | null
  userRole: TeamRole | null
  permissions: GoalPermissions
  // UI state for forms
  isFormOpen: boolean
  editingGoal: ProjectGoal | null
  // Onboarding state
  hasCompletedOnboarding: boolean
}

// Store actions
interface GoalActions {
  // Data loading
  loadGoals: (teamId: string) => Promise<void>
  refreshGoals: () => Promise<void>

  // CRUD operations
  createGoal: (teamId: string, data: ProjectGoalCreateRequest) => Promise<void>
  updateGoal: (
    teamId: string,
    goalId: string,
    data: ProjectGoalUpdateRequest
  ) => Promise<void>
  deleteGoal: (teamId: string, goalId: string) => Promise<void>

  // UI state management
  openCreateForm: () => void
  openEditForm: (goal: ProjectGoal) => void
  closeForm: () => void

  // Permission management
  setUserRole: (role: TeamRole | null) => void
  setTeam: (teamId: string, userRole?: TeamRole) => void

  // Onboarding
  completeOnboarding: () => void

  // Error handling
  clearError: () => void
  reset: () => void
}

type GoalStore = GoalState & GoalActions

const initialState: GoalState = {
  goals: [],
  loading: false,
  error: null,
  selectedTeamId: null,
  userRole: null,
  permissions: getGoalPermissions(), // Default permissions (view-only)
  isFormOpen: false,
  editingGoal: null,
  hasCompletedOnboarding: false,
}

export const useGoalStore = create<GoalStore>()(
  devtools(
    (set, get) => ({
      ...initialState,

      // Load goals for a team
      loadGoals: async (teamId: string) => {
        set({ loading: true, error: null, selectedTeamId: teamId })

        try {
          const response = await GoalService.getGoals(teamId)

          set({
            goals: response.goals,
            loading: false,
          })
        } catch (error) {
          const errorMessage = GoalService.formatApiError(error)

          set({
            loading: false,
            error: {
              error: 'load_failed',
              message: errorMessage,
            },
            goals: [],
          })
        }
      },

      // Refresh current goals
      refreshGoals: async () => {
        const { selectedTeamId } = get()
        if (selectedTeamId) {
          await get().loadGoals(selectedTeamId)
        }
      },

      // Create new goal
      createGoal: async (teamId: string, data: ProjectGoalCreateRequest) => {
        const state = get()

        // Check permissions
        if (!state.permissions.canCreate) {
          throw new Error('You do not have permission to create goals')
        }

        set({ loading: true, error: null })

        try {
          const newGoal = await GoalService.createGoal(teamId, data)

          // Add to current list (goals are ordered by priority_weight desc)
          const currentGoals = get().goals
          const updatedGoals = [...currentGoals, newGoal].sort(
            (a, b) => b.priority_weight - a.priority_weight
          )

          set({
            goals: updatedGoals,
            loading: false,
            isFormOpen: false, // Close form on success
          })
        } catch (error) {
          const errorMessage = GoalService.formatApiError(error)

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

      // Update existing goal
      updateGoal: async (
        teamId: string,
        goalId: string,
        data: ProjectGoalUpdateRequest
      ) => {
        const state = get()

        // Check permissions
        if (!state.permissions.canEdit) {
          throw new Error('You do not have permission to edit goals')
        }

        set({ loading: true, error: null })

        try {
          const updatedGoal = await GoalService.updateGoal(teamId, goalId, data)

          const currentGoals = get().goals
          const updatedGoals = currentGoals
            .map((goal) => (goal.id === goalId ? updatedGoal : goal))
            .sort((a, b) => b.priority_weight - a.priority_weight)

          set({
            goals: updatedGoals,
            loading: false,
            isFormOpen: false,
            editingGoal: null,
          })
        } catch (error) {
          const errorMessage = GoalService.formatApiError(error)

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

      // Delete goal
      deleteGoal: async (teamId: string, goalId: string) => {
        const state = get()

        // Check permissions
        if (!state.permissions.canDelete) {
          throw new Error('You do not have permission to delete goals')
        }

        set({ loading: true, error: null })

        try {
          await GoalService.deleteGoal(teamId, goalId)

          const currentGoals = get().goals
          const updatedGoals = currentGoals.filter((goal) => goal.id !== goalId)

          set({
            goals: updatedGoals,
            loading: false,
          })
        } catch (error) {
          const errorMessage = GoalService.formatApiError(error)

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

      // UI state management
      openCreateForm: () => {
        const state = get()
        if (!state.permissions.canCreate) {
          set({
            error: {
              error: 'permission_denied',
              message: 'You do not have permission to create goals',
            },
          })
          return
        }

        set({
          isFormOpen: true,
          editingGoal: null,
          error: null,
        })
      },

      openEditForm: (goal: ProjectGoal) => {
        const state = get()
        if (!state.permissions.canEdit) {
          set({
            error: {
              error: 'permission_denied',
              message: 'You do not have permission to edit goals',
            },
          })
          return
        }

        set({
          isFormOpen: true,
          editingGoal: goal,
          error: null,
        })
      },

      closeForm: () => {
        set({
          isFormOpen: false,
          editingGoal: null,
          error: null,
        })
      },

      // Permission management
      setUserRole: (role: TeamRole | null) => {
        set({
          userRole: role,
          permissions: getGoalPermissions(role),
        })
      },

      setTeam: (teamId: string, userRole?: TeamRole) => {
        set({
          selectedTeamId: teamId,
          userRole: userRole || null,
          permissions: getGoalPermissions(userRole),
          goals: [], // Clear goals when switching teams
          error: null,
        })
      },

      // Onboarding
      completeOnboarding: () => {
        set({ hasCompletedOnboarding: true })
      },

      // Error handling
      clearError: () => {
        set({ error: null })
      },

      reset: () => {
        set(initialState)
      },
    }),
    {
      name: 'goal-store', // For Redux DevTools
    }
  )
)

// Custom hooks for common use cases
export const useGoals = () => {
  const store = useGoalStore()
  return {
    goals: store.goals,
    loading: store.loading,
    error: store.error,
    loadGoals: store.loadGoals,
    refreshGoals: store.refreshGoals,
  }
}

export const useGoalPermissions = () => {
  const store = useGoalStore()
  return {
    permissions: store.permissions,
    userRole: store.userRole,
    setUserRole: store.setUserRole,
  }
}

export const useGoalForm = () => {
  const store = useGoalStore()
  return {
    isFormOpen: store.isFormOpen,
    editingGoal: store.editingGoal,
    openCreateForm: store.openCreateForm,
    openEditForm: store.openEditForm,
    closeForm: store.closeForm,
    createGoal: store.createGoal,
    updateGoal: store.updateGoal,
  }
}

export const useGoalOnboarding = () => {
  const store = useGoalStore()
  return {
    hasCompletedOnboarding: store.hasCompletedOnboarding,
    completeOnboarding: store.completeOnboarding,
    goals: store.goals,
  }
}
