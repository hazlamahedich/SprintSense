import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { Sprint, SprintCreate, SprintStatus } from '@/types/sprint'
import * as sprintService from '@/services/sprintService'

interface SprintStore {
  // State
  sprints: Sprint[]
  activeSprintId: string | null
  loading: boolean
  error: string | null

  // Actions
  fetchTeamSprints: (teamId: string, includeClosed?: boolean) => Promise<void>
  createSprint: (teamId: string, data: SprintCreate) => Promise<void>
  updateSprintStatus: (sprintId: string, status: SprintStatus) => Promise<void>
  clearError: () => void
}

export const useSprintStore = create<SprintStore>()(
  devtools(
    (set) => ({
      // Initial state
      sprints: [],
      activeSprintId: null,
      loading: false,
      error: null,

      // Actions
      fetchTeamSprints: async (teamId: string, includeClosed = false) => {
        set({ loading: true, error: null })
        try {
          const sprints = await sprintService.listTeamSprints(
            teamId,
            includeClosed
          )
          const activeSprintId =
            sprints.find((s) => s.status === SprintStatus.ACTIVE)?.id ?? null
          set({ sprints, activeSprintId, loading: false })
        } catch (error) {
          set({
            error:
              error instanceof Error
                ? error.message
                : 'Failed to fetch sprints',
            loading: false,
          })
        }
      },

      createSprint: async (teamId: string, data: SprintCreate) => {
        set({ loading: true, error: null })
        try {
          const sprint = await sprintService.createSprint(teamId, data)
          set((state) => ({
            sprints: [...state.sprints, sprint],
            loading: false,
          }))
        } catch (error) {
          set({
            error:
              error instanceof Error
                ? error.message
                : 'Failed to create sprint',
            loading: false,
          })
        }
      },

      updateSprintStatus: async (sprintId: string, status: SprintStatus) => {
        set({ loading: true, error: null })
        try {
          const updatedSprint = await sprintService.updateSprintStatus(
            sprintId,
            { status }
          )
          set((state) => {
            const updatedSprints = state.sprints.map((sprint) =>
              sprint.id === sprintId ? updatedSprint : sprint
            )
            const activeSprintId =
              updatedSprint.status === SprintStatus.ACTIVE
                ? updatedSprint.id
                : updatedSprint.id === state.activeSprintId
                  ? null
                  : state.activeSprintId

            return {
              sprints: updatedSprints,
              activeSprintId,
              loading: false,
            }
          })
        } catch (error) {
          set({
            error:
              error instanceof Error
                ? error.message
                : 'Failed to update sprint status',
            loading: false,
          })
        }
      },

      clearError: () => set({ error: null }),
    }),
    { name: 'sprint-store' }
  )
)
