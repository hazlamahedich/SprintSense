import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import BacklogItem from '../BacklogItem'
import {
  WorkItem,
  WorkItemType,
  WorkItemStatus,
} from '../../../types/workItem.types'

// Mock work item for testing
const mockWorkItem: WorkItem = {
  id: '1',
  team_id: 'team-1',
  author_id: 'user-author',
  title: 'Test Work Item',
  description: 'This is a test work item',
  type: WorkItemType.TASK,
  status: WorkItemStatus.BACKLOG,
  priority: 3.0,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
  story_points: 5,
  assignee_id: 'user-1',
}

console.log('Starting BacklogItem test suite');

describe('BacklogItem', () => {
  const mockOnEdit = vi.fn()
  const mockOnDelete = vi.fn()
  const mockOnMove = vi.fn()

  beforeEach(() => {
    console.log('Setting up test...');
    vi.clearAllMocks();
    console.log('Mocks cleared');
  })

  it('renders work item information correctly', () => {
    console.log('Starting first test: renders work item information');
    console.log('Mock work item:', mockWorkItem);
    render(
      <BacklogItem
        workItem={mockWorkItem}
        teamId="team-1"
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    )

    // Check if title is rendered
    expect(screen.getByText('Test Work Item')).toBeInTheDocument()

    // Check if description is rendered
    expect(screen.getByText('This is a test work item')).toBeInTheDocument()

    // Check if type badge is rendered
    expect(screen.getByText('task')).toBeInTheDocument()

    // Check if status badge is rendered
    expect(screen.getByText('backlog')).toBeInTheDocument()

    // Check if priority badge is rendered (should show "Medium" label for priority 3.0)
    expect(screen.getByText('Medium')).toBeInTheDocument()
  })

  it('calls onEdit when edit button is clicked', () => {
    render(
      <BacklogItem
        workItem={mockWorkItem}
        teamId="team-1"
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    )

    const editButton = screen.getByTitle('Edit')
    fireEvent.click(editButton)

    expect(mockOnEdit).toHaveBeenCalledWith(mockWorkItem)
  })

  it('calls onDelete when delete button is clicked', () => {
    render(
      <BacklogItem
        workItem={mockWorkItem}
        teamId="team-1"
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    )

    const deleteButton = screen.getByTitle('Delete')
    fireEvent.click(deleteButton)

    expect(mockOnDelete).toHaveBeenCalledWith(mockWorkItem.id)
  })

  it('shows move buttons when showMoveButtons is true', () => {
    render(
      <BacklogItem
        workItem={mockWorkItem}
        teamId="team-1"
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onMove={mockOnMove}
        showMoveButtons={true}
      />
    )

    expect(screen.getByTitle('Move up')).toBeInTheDocument()
    expect(screen.getByTitle('Move down')).toBeInTheDocument()
  })

  it('hides move buttons when showMoveButtons is false', () => {
    render(
      <BacklogItem
        workItem={mockWorkItem}
        teamId="team-1"
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onMove={mockOnMove}
        showMoveButtons={false}
      />
    )

    expect(screen.queryByTitle('Move up')).not.toBeInTheDocument()
    expect(screen.queryByTitle('Move down')).not.toBeInTheDocument()
  })

  it('displays assignee information when available', () => {
    render(
      <BacklogItem
        workItem={mockWorkItem}
        teamId="team-1"
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    )

    expect(screen.getByText(/Assignee: user-1/)).toBeInTheDocument()
  })

  // Due date test removed as it's not part of current WorkItem interface

  it('displays story points when available', () => {
    render(
      <BacklogItem
        workItem={mockWorkItem}
        teamId="team-1"
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    )

    expect(screen.getByText(/Story Points: 5/)).toBeInTheDocument()
  })
})

