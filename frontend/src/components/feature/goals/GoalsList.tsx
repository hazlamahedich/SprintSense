/**
 * Goals List component for displaying and managing project goals.
 *
 * Implements Story 3.1 AC1,2,3,4: Goals Discovery & Access, Goal Management Interface,
 * Goal Content & Validation, Empty State & Onboarding.
 */

import React, { useEffect } from 'react'
import {
  useGoals,
  useGoalForm,
  useGoalPermissions,
  useGoalOnboarding,
} from '../../../stores/goalStore'
import {
  ProjectGoal,
  getPriorityLabel,
  getPriorityColor,
  EXAMPLE_GOALS,
} from '../../../types/goal.types'
import { Button } from '../../ui/button'
import { Card } from '../../ui/card'
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
} from '@heroicons/react/24/outline/index.js'

interface GoalsListProps {
  teamId: string
  userRole?: 'owner' | 'member'
}

export const GoalsList: React.FC<GoalsListProps> = ({ teamId, userRole }) => {
  const { goals, loading, error, loadGoals } = useGoals()
  const { permissions } = useGoalPermissions()
  const { openCreateForm, openEditForm, deleteGoal } = useGoalForm()
  const { hasCompletedOnboarding } = useGoalOnboarding()

  // Load goals when component mounts or teamId changes
  useEffect(() => {
    if (teamId) {
      loadGoals(teamId)
    }
  }, [teamId, loadGoals])

  // Handle goal deletion with confirmation
  const handleDeleteGoal = async (goal: ProjectGoal) => {
    if (
      window.confirm(
        `Are you sure you want to delete the goal "${goal.description}"?`
      )
    ) {
      try {
        await deleteGoal(teamId, goal.id)
      } catch (error) {
        // Error handling is managed by the store
        console.error('Failed to delete goal:', error)
      }
    }
  }

  // Show error state
  if (error) {
    return (
      <Card className="p-6">
        <div className="text-center">
          <div className="text-red-500 text-lg mb-2">⚠️ Error</div>
          <p className="text-gray-600 mb-4">{error.message}</p>
          <Button onClick={() => loadGoals(teamId)} variant="outline">
            Retry
          </Button>
        </div>
      </Card>
    )
  }

  // Show empty state with onboarding (AC4)
  if (!loading && goals.length === 0) {
    return (
      <Card className="p-8">
        <div className="text-center">
          <div className="text-6xl mb-4">🎯</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Create Your First Goal
          </h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Define strategic goals to guide AI prioritization recommendations.
            Goals help the AI understand what matters most for your team's
            success.
          </p>

          {permissions.canCreate ? (
            <div className="space-y-6">
              <Button
                onClick={openCreateForm}
                className="flex items-center gap-2"
              >
                <PlusIcon className="w-4 h-4" />
                Create Your First Goal
              </Button>

              {/* Example goals for guidance */}
              <div className="border-t pt-6">
                <h4 className="text-sm font-medium text-gray-700 mb-3">
                  Example Goals:
                </h4>
                <div className="grid gap-3 text-left max-w-2xl mx-auto">
                  {EXAMPLE_GOALS.slice(0, 3).map((example, index) => (
                    <div key={index} className="bg-gray-50 rounded p-3 text-sm">
                      <div className="font-medium text-gray-900 mb-1">
                        Priority {example.priority_weight}:{' '}
                        {example.description}
                      </div>
                      <div className="text-gray-600">
                        Success: {example.success_metrics}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">
              Contact your team owner to create goals for this team.
            </p>
          )}
        </div>
      </Card>
    )
  }

  // Show loading state
  if (loading && goals.length === 0) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, index) => (
          <Card key={index} className="p-4 animate-pulse">
            <div className="flex justify-between items-start mb-3">
              <div className="flex items-center gap-2">
                <div className="h-6 w-20 bg-gray-200 rounded"></div>
                <div className="h-6 w-6 bg-gray-200 rounded-full"></div>
              </div>
              <div className="flex gap-1">
                <div className="h-8 w-8 bg-gray-200 rounded"></div>
                <div className="h-8 w-8 bg-gray-200 rounded"></div>
              </div>
            </div>
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          </Card>
        ))}
      </div>
    )
  }

  // Show goals list (AC1,2,3)
  return (
    <div className="space-y-4">
      {/* Header with create button */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            Project Goals ({goals.length})
          </h2>
          <p className="text-sm text-gray-600">
            Strategic goals to guide AI prioritization recommendations
          </p>
        </div>

        {permissions.canCreate && (
          <Button onClick={openCreateForm} className="flex items-center gap-2">
            <PlusIcon className="w-4 h-4" />
            Add Goal
          </Button>
        )}
      </div>

      {/* Goals list ordered by priority */}
      <div className="space-y-3">
        {goals.map((goal) => (
          <Card key={goal.id} className="p-4 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start">
              {/* Goal content */}
              <div className="flex-1 pr-4">
                <div className="flex items-center gap-2 mb-2">
                  <span
                    className={`
                    inline-flex items-center px-2 py-1 rounded-full text-xs font-medium
                    ${getPriorityColor(goal.priority_weight)}
                    bg-opacity-10 border border-current border-opacity-20
                  `}
                  >
                    Priority {goal.priority_weight}:{' '}
                    {getPriorityLabel(goal.priority_weight)}
                  </span>
                  <span className="w-2 h-2 rounded-full bg-current opacity-50"></span>
                </div>

                <h3 className="font-medium text-gray-900 mb-2 leading-tight">
                  {goal.description}
                </h3>

                {goal.success_metrics && (
                  <p className="text-sm text-gray-600 mb-2">
                    <span className="font-medium">Success metrics:</span>{' '}
                    {goal.success_metrics}
                  </p>
                )}

                <div className="text-xs text-gray-500">
                  Created {new Date(goal.created_at).toLocaleDateString()}
                  {goal.updated_at && goal.updated_at !== goal.created_at && (
                    <span>
                      {' '}
                      • Updated {new Date(goal.updated_at).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>

              {/* Action buttons */}
              {(permissions.canEdit || permissions.canDelete) && (
                <div className="flex gap-1">
                  {permissions.canEdit && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => openEditForm(goal)}
                      className="p-2"
                      title="Edit goal"
                    >
                      <PencilIcon className="w-4 h-4" />
                    </Button>
                  )}

                  {permissions.canDelete && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteGoal(goal)}
                      className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50"
                      title="Delete goal"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              )}
            </div>
          </Card>
        ))}
      </div>

      {/* Loading more indicator */}
      {loading && goals.length > 0 && (
        <div className="flex justify-center py-4">
          <div className="flex items-center gap-2 text-gray-600">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
            <span className="text-sm">Refreshing...</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default GoalsList

