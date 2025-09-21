import { Sprint, SprintCreate, SprintStatusUpdate } from '@/types/sprint'
import { ApiError } from '@/types/error'
import { API_URL } from '@/config'

const SPRINTS_BASE_URL = `${API_URL}/api/v1`

export async function createSprint(
  teamId: string,
  sprintData: SprintCreate
): Promise<Sprint> {
  const response = await fetch(`${SPRINTS_BASE_URL}/teams/${teamId}/sprints`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include', // Send cookies
    body: JSON.stringify(sprintData),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new ApiError(
      error.detail || 'Failed to create sprint',
      response.status
    )
  }

  return response.json()
}

export async function updateSprintStatus(
  sprintId: string,
  statusData: SprintStatusUpdate
): Promise<Sprint> {
  const response = await fetch(`${SPRINTS_BASE_URL}/sprints/${sprintId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(statusData),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new ApiError(
      error.detail || 'Failed to update sprint status',
      response.status
    )
  }

  return response.json()
}

export async function listTeamSprints(
  teamId: string,
  includeClosed = false
): Promise<Sprint[]> {
  const url = new URL(`${SPRINTS_BASE_URL}/teams/${teamId}/sprints`)
  url.searchParams.append('include_closed', includeClosed.toString())

  const response = await fetch(url.toString(), {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
  })

  if (!response.ok) {
    const error = await response.json()
    throw new ApiError(
      error.detail || 'Failed to fetch sprints',
      response.status
    )
  }

  return response.json()
}
