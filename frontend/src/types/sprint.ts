// Sprint status enum
export enum SprintStatus {
  FUTURE = 'future',
  ACTIVE = 'active',
  CLOSED = 'closed',
}

// Sprint interface
export interface Sprint {
  id: string
  teamId: string
  name: string
  status: SprintStatus
  startDate: string // ISO date string
  endDate: string // ISO date string
  goal?: string
  createdAt: string // ISO datetime string
  updatedAt: string // ISO datetime string
}

// Sprint creation payload
export interface SprintCreate {
  name: string
  startDate: string // ISO date string
  endDate: string // ISO date string
  goal?: string
}

// Sprint status update payload
export interface SprintStatusUpdate {
  status: SprintStatus
}
