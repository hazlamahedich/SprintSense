/**
 * Sprint API client functions
 */
import { API_BASE_URL } from '../config';
import { IncompleteTask, MoveType, CompleteSprintRequest, CompleteSprintResponse } from '../types/sprint';

/**
 * Get incomplete items for a sprint
 */
export async function getIncompleteItems(sprintId: string): Promise<IncompleteTask[]> {
  const response = await fetch(`${API_BASE_URL}/api/sprints/${sprintId}/incomplete-items`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch incomplete items: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Complete a sprint and move incomplete items
 */
export async function completeSprint(
  sprintId: string,
  payload: CompleteSprintRequest,
): Promise<CompleteSprintResponse> {
  const response = await fetch(`${API_BASE_URL}/api/sprints/${sprintId}/complete`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Failed to complete sprint: ${response.statusText}`);
  }

  return response.json();
}
