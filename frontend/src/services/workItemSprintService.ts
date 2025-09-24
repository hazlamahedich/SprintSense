import { supabase } from '../lib/supabaseClient'
import { WorkItem } from '../types/workItem.types'

interface SprintAssignmentResponse {
  workItemId: string
  sprintId: string | null
  version: number
}

export class WorkItemSprintService {
  // Subscribe to real-time updates
  static subscribeToWorkItemUpdates(callback: (workItem: WorkItem) => void) {
    const subscription = supabase
      .channel('work_items_changes')
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'work_items',
        },
        (payload) => {
          callback(payload.new as WorkItem)
        }
      )
      .subscribe()

    return () => {
      subscription.unsubscribe()
    }
  }

  // Assign work item to sprint
  static async assignToSprint(
    workItemId: string,
    sprintId: string | null,
    currentVersion: number
  ): Promise<SprintAssignmentResponse> {
    try {
      const response = await fetch(
        `/api/work-items/${workItemId}/sprint?` +
          new URLSearchParams({
            sprint_id: sprintId || '',
            current_version: currentVersion.toString(),
          }),
        {
          method: 'PATCH',
          credentials: 'include',
        }
      )

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to assign work item to sprint')
      }

      return await response.json()
    } catch (error) {
      console.error('Error assigning work item to sprint:', error)
      throw error
    }
  }
}
