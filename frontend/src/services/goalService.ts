/**
 * API service for project goals.
 *
 * This service implements Story 3.1 requirements for goal management
 * with proper error handling and type safety.
 */

import {
  ProjectGoal,
  ProjectGoalCreateRequest,
  ProjectGoalUpdateRequest,
  ProjectGoalListResponse,
} from '../types/goal.types'
import { api } from './api'

export class GoalService {
  /**
   * Get all project goals for a team.
   * Implements AC2: All team members can view goals.
   */
  static async getGoals(teamId: string): Promise<ProjectGoalListResponse> {
    try {
      const response = await api.get(`/teams/${teamId}/goals`)
      return response.data
    } catch (error) {
      console.error('Failed to fetch project goals:', error)
      throw error
    }
  }

  /**
   * Create a new project goal.
   * Implements AC2: Only Product Owners and Team Owners can create goals.
   * Implements AC3: Goal content validation and uniqueness checks.
   */
  static async createGoal(
    teamId: string,
    goalData: ProjectGoalCreateRequest
  ): Promise<ProjectGoal> {
    try {
      const response = await api.post(`/teams/${teamId}/goals`, goalData)
      return response.data
    } catch (error) {
      console.error('Failed to create project goal:', error)
      throw error
    }
  }

  /**
   * Update an existing project goal.
   * Implements AC2: Only Product Owners and Team Owners can update goals.
   * Implements AC3: Validation and uniqueness checks on updates.
   */
  static async updateGoal(
    teamId: string,
    goalId: string,
    goalData: ProjectGoalUpdateRequest
  ): Promise<ProjectGoal> {
    try {
      const response = await api.put(
        `/teams/${teamId}/goals/${goalId}`,
        goalData
      )
      return response.data
    } catch (error) {
      console.error('Failed to update project goal:', error)
      throw error
    }
  }

  /**
   * Delete a project goal.
   * Implements AC2: Only Product Owners and Team Owners can delete goals.
   */
  static async deleteGoal(teamId: string, goalId: string): Promise<void> {
    try {
      await api.delete(`/teams/${teamId}/goals/${goalId}`)
    } catch (error) {
      console.error('Failed to delete project goal:', error)
      throw error
    }
  }

  /**
   * Validate goal data on the client side before API calls.
   * Implements AC3: Real-time validation and character counting.
   */
  static validateGoalData(goalData: Partial<ProjectGoalCreateRequest>): {
    isValid: boolean
    errors: Record<string, string>
  } {
    const errors: Record<string, string> = {}

    // Description validation
    if (!goalData.description || goalData.description.trim().length === 0) {
      errors.description = 'Goal description is required'
    } else if (goalData.description.trim().length > 500) {
      errors.description = 'Description cannot exceed 500 characters'
    }

    // Priority weight validation
    if (
      goalData.priority_weight === undefined ||
      goalData.priority_weight === null
    ) {
      errors.priority_weight = 'Priority weight is required'
    } else if (goalData.priority_weight < 1 || goalData.priority_weight > 10) {
      errors.priority_weight = 'Priority weight must be between 1 and 10'
    }

    // Success metrics validation (optional but length-limited)
    if (
      goalData.success_metrics &&
      goalData.success_metrics.trim().length > 1000
    ) {
      errors.success_metrics = 'Success metrics cannot exceed 1000 characters'
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors,
    }
  }

  /**
   * Check for potential duplicate goals on the client side.
   * Implements AC3: Goal uniqueness validation.
   */
  static checkForDuplicate(
    description: string,
    existingGoals: ProjectGoal[],
    excludeId?: string
  ): ProjectGoal | null {
    const normalizedDescription = description.trim().toLowerCase()

    return (
      existingGoals.find(
        (goal) =>
          goal.id !== excludeId &&
          goal.description.trim().toLowerCase() === normalizedDescription
      ) || null
    )
  }

  /**
   * Get character count for real-time feedback.
   * Implements AC3: Real-time character counting.
   */
  static getCharacterCount(text: string): {
    count: number
    remaining: number
    maxLength: number
  } {
    const count = text.length
    const maxLength = 500 // Description max length

    return {
      count,
      remaining: maxLength - count,
      maxLength,
    }
  }

  /**
   * Get success metrics character count.
   */
  static getSuccessMetricsCharacterCount(text: string): {
    count: number
    remaining: number
    maxLength: number
  } {
    const count = text.length
    const maxLength = 1000 // Success metrics max length

    return {
      count,
      remaining: maxLength - count,
      maxLength,
    }
  }

  /**
   * Format error messages from API responses.
   * Handles structured error responses from the backend.
   */
  static formatApiError(error: any): string {
    // Handle structured API error responses
    if (error.response?.data?.error) {
      const apiError = error.response.data.error

      // Handle validation errors
      if (apiError.code === 'DUPLICATE_GOAL') {
        return 'A goal with this description already exists. Please choose a different description.'
      }

      if (apiError.code === 'INSUFFICIENT_PERMISSIONS') {
        return 'You do not have permission to perform this action. Only team owners can manage goals.'
      }

      if (apiError.code === 'NOT_TEAM_MEMBER') {
        return 'You must be a team member to access team goals.'
      }

      if (apiError.code === 'GOAL_NOT_FOUND') {
        return 'The requested goal could not be found. It may have been deleted.'
      }

      // Return the API error message if available
      return (
        apiError.message || 'An error occurred while processing your request.'
      )
    }

    // Handle network errors
    if (error.code === 'NETWORK_ERROR' || !error.response) {
      return 'Unable to connect to the server. Please check your internet connection.'
    }

    // Handle HTTP status codes
    if (error.response?.status) {
      switch (error.response.status) {
        case 400:
          return 'Invalid request. Please check your input and try again.'
        case 401:
          return 'You are not authenticated. Please log in and try again.'
        case 403:
          return 'You do not have permission to perform this action.'
        case 404:
          return 'The requested resource could not be found.'
        case 422:
          return 'The provided data is invalid. Please check your input.'
        case 500:
          return 'A server error occurred. Please try again later.'
        default:
          return 'An unexpected error occurred. Please try again.'
      }
    }

    // Fallback error message
    return 'An unexpected error occurred. Please try again.'
  }
}
