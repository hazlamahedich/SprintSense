/**
 * TypeScript interfaces for invitation-related data structures
 */

export interface Invitation {
  id: string
  team_id: string
  email: string
  role: 'owner' | 'member'
  status: 'pending' | 'accepted' | 'declined'
  inviter_id: string
  created_at: string
}

export interface InvitationListItem {
  id: string
  email: string
  role: 'owner' | 'member'
  status: 'pending' | 'accepted' | 'declined'
  inviter_name: string
  created_at: string
}

export interface InvitationCreateRequest {
  email: string
  role: 'owner' | 'member'
}

export interface InvitationCreateResponse {
  message: string
  invitation: Invitation
}

export interface InvitationListResponse {
  invitations: InvitationListItem[]
}

export interface InvitationFormData {
  email: string
  role: 'owner' | 'member'
}

export interface InvitationError {
  message: string
  field?: string
}
