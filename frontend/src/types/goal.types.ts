/**
 * TypeScript types for project goals.
 *
 * This file implements Story 3.1 requirements for AI-powered backlog prioritization
 * by defining types for strategic goals that guide AI recommendations.
 */

export interface ProjectGoal {
  id: string;
  team_id: string;
  description: string;
  priority_weight: number; // 1-10 scale
  success_metrics?: string | null;
  author_id: string;
  created_by: string;
  updated_by?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface ProjectGoalCreateRequest {
  description: string;
  priority_weight: number; // 1-10 scale
  success_metrics?: string;
}

export interface ProjectGoalUpdateRequest {
  description?: string;
  priority_weight?: number; // 1-10 scale
  success_metrics?: string;
}

export interface ProjectGoalListResponse {
  goals: ProjectGoal[];
  total: number;
}

export interface ProjectGoalValidationError {
  error_code: string;
  message: string;
  existing_goal_id?: string;
  recovery_action: string;
}

// UI-specific types
export interface GoalFormData {
  description: string;
  priority_weight: number;
  success_metrics: string;
}

export interface GoalFormErrors {
  description?: string;
  priority_weight?: string;
  success_metrics?: string;
  general?: string;
}

// Role-based permissions (AC2 requirements)
export type TeamRole = 'owner' | 'member';

export interface GoalPermissions {
  canView: boolean;
  canCreate: boolean;
  canEdit: boolean;
  canDelete: boolean;
}

export function getGoalPermissions(userRole?: TeamRole): GoalPermissions {
  const isOwner = userRole === 'owner';

  return {
    canView: true, // All team members can view goals (AC2)
    canCreate: isOwner, // Only owners can create goals (AC2)
    canEdit: isOwner, // Only owners can edit goals (AC2)
    canDelete: isOwner, // Only owners can delete goals (AC2)
  };
}

// Priority weight helpers for UI
export const PRIORITY_WEIGHT_MIN = 1;
export const PRIORITY_WEIGHT_MAX = 10;

export const PRIORITY_WEIGHT_LABELS: Record<number, string> = {
  1: 'Lowest',
  2: 'Very Low',
  3: 'Low',
  4: 'Below Average',
  5: 'Medium',
  6: 'Above Average',
  7: 'High',
  8: 'Very High',
  9: 'Critical',
  10: 'Highest',
};

export function getPriorityLabel(weight: number): string {
  return PRIORITY_WEIGHT_LABELS[weight] || `Priority ${weight}`;
}

export function getPriorityColor(weight: number): string {
  if (weight <= 2) return 'text-gray-500';
  if (weight <= 4) return 'text-blue-500';
  if (weight <= 6) return 'text-yellow-500';
  if (weight <= 8) return 'text-orange-500';
  return 'text-red-500';
}

// Character limits for validation (AC3 requirements)
export const DESCRIPTION_MAX_LENGTH = 500;
export const SUCCESS_METRICS_MAX_LENGTH = 1000;

// Example goals for onboarding (AC4 requirements)
export const EXAMPLE_GOALS: Omit<ProjectGoalCreateRequest, 'team_id'>[] = [
  {
    description: "Improve user engagement by 25% through better navigation and search functionality",
    priority_weight: 8,
    success_metrics: "Monthly active users increase by 25%, session duration increases by 15%"
  },
  {
    description: "Reduce customer support tickets by implementing comprehensive self-service features",
    priority_weight: 7,
    success_metrics: "Support ticket volume decreases by 30% within 3 months"
  },
  {
    description: "Enhance system performance and reliability to improve user experience",
    priority_weight: 9,
    success_metrics: "Page load times under 2 seconds, 99.9% uptime, user satisfaction score >4.5"
  },
  {
    description: "Increase product adoption among new users with improved onboarding",
    priority_weight: 6,
    success_metrics: "Onboarding completion rate >80%, first-week retention >60%"
  }
];
