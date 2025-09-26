import React from 'react';
import { render, screen } from '@testing-library/react';
import { WorkItemList } from '../WorkItemList';

describe('WorkItemList', () => {
  it('renders list headers correctly', () => {
    render(<WorkItemList isLoading={false} />);

    expect(screen.getByText('Title')).toBeInTheDocument();
    expect(screen.getByText('Story Points')).toBeInTheDocument();
    expect(screen.getByText('Assignee')).toBeInTheDocument();
  });

  it('renders loading state correctly', () => {
    render(<WorkItemList isLoading={true} />);

    const skeletons = screen.getAllByRole('row');
    // Header row + 3 loading rows
    expect(skeletons).toHaveLength(4);
  });

  it('renders work items when not loading', () => {
    render(<WorkItemList isLoading={false} />);

    expect(screen.getByText('Implement user authentication')).toBeInTheDocument();
    expect(screen.getByText('Add error handling')).toBeInTheDocument();
    expect(screen.getByText('Create documentation')).toBeInTheDocument();
  });

  it('shows story points and assignees', () => {
    render(<WorkItemList isLoading={false} />);

    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('John')).toBeInTheDocument();
    expect(screen.getByText('Sarah')).toBeInTheDocument();
    expect(screen.getByText('Mike')).toBeInTheDocument();
  });

  it('renders within a card', () => {
    render(<WorkItemList isLoading={false} />);

    expect(screen.getByText('Sprint Work Items')).toBeInTheDocument();
  });
});
