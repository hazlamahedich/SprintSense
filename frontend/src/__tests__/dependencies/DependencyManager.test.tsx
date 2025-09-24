import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DependencyManager } from '../../components/dependencies/DependencyManager';
import { WorkItemStatus, DependencyType } from '../../types/dependencies';
import * as dependencyService from '../../services/dependencies';

// Import test setup and mocks
import { vi } from 'vitest';
vi.mock('../../services/dependencies');

// Mock work items for testing
const mockWorkItems = [
  {
    id: '1',
    title: 'Task 1',
    description: 'Description 1',
    status: WorkItemStatus.NOT_STARTED,
    priority: 1,
    createdAt: '2025-09-24T00:00:00Z',
    updatedAt: '2025-09-24T00:00:00Z'
  },
  {
    id: '2',
    title: 'Task 2',
    description: 'Description 2',
    status: WorkItemStatus.IN_PROGRESS,
    priority: 2,
    createdAt: '2025-09-24T00:00:00Z',
    updatedAt: '2025-09-24T00:00:00Z'
  }
];

// Mock dependencies for testing
const mockDependencies = [
  {
    id: '1-2',
    source: { id: '1', title: 'Task 1' },
    target: { id: '2', title: 'Task 2' },
    type: DependencyType.BLOCKS,
    isCritical: true,
    confidence: 0.95,
    createdAt: '2025-09-24T00:00:00Z',
    updatedAt: '2025-09-24T00:00:00Z'
  }
];

// Create a wrapper component with QueryClientProvider
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('DependencyManager', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks();

    // Setup default mock implementations
    vi.mocked(dependencyService.analyzeDependencies).mockResolvedValue(mockDependencies);
    vi.mocked(dependencyService.suggestDependencyChain).mockResolvedValue(mockWorkItems);
  });

  it('renders empty state when no work items are provided', () => {
    render(<DependencyManager workItems={[]} />, { wrapper: createWrapper() });

    expect(screen.getByText(/no work items available/i)).toBeInTheDocument();
  });

  it('renders loading state while analyzing dependencies', () => {
    render(<DependencyManager workItems={mockWorkItems} />, { wrapper: createWrapper() });

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('displays dependency graph when analysis is complete', async () => {
    render(<DependencyManager workItems={mockWorkItems} />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('Dependency Analysis')).toBeInTheDocument();
    });

    expect(screen.getByRole('button', { name: /refresh/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /suggest chain/i })).toBeInTheDocument();
  });

  it('handles refresh button click', async () => {
    render(<DependencyManager workItems={mockWorkItems} />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /refresh/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /refresh/i }));

    expect(dependencyService.analyzeDependencies).toHaveBeenCalledTimes(2); // Initial + refresh
  });

  it('handles suggest chain button click', async () => {
    render(<DependencyManager workItems={mockWorkItems} />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /suggest chain/i })).toBeInTheDocument();
    });

    // Click the suggest chain button
    fireEvent.click(screen.getByRole('button', { name: /suggest chain/i }));

    await waitFor(() => {
      // Verify the function was called with work items array and some timestamp
      expect(dependencyService.suggestDependencyChain).toHaveBeenCalled();
      expect(screen.getByText('Suggested Work Order')).toBeInTheDocument();
    });
  });

  it('displays error state when analysis fails', async () => {
    vi.mocked(dependencyService.analyzeDependencies).mockRejectedValue(new Error('Analysis failed'));

    render(<DependencyManager workItems={mockWorkItems} />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText(/failed to analyze dependencies/i)).toBeInTheDocument();
    });

    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });

  it('shows work item details when clicked', async () => {
    const { container } = render(<DependencyManager workItems={mockWorkItems} />, { wrapper: createWrapper() });

    // Wait for graph to render
    await waitFor(() => {
      expect(screen.getByText('Dependency Analysis')).toBeInTheDocument();
    });

    // Wait for data to load and graph to be ready
    await waitFor(() => {
      expect(screen.getByText(mockWorkItems[0].title)).toBeInTheDocument();
      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });

    // Find and click the first node circle
    const svg = container.querySelector('svg');
    const circles = svg?.querySelectorAll('circle');
    expect(circles?.length).toBeGreaterThan(0);
    fireEvent.click(circles![0]);

    // Check details panel content
    await waitFor(() => {
      expect(screen.getByText(/selected work item/i)).toBeInTheDocument();
      const statusElement = screen.getByTestId('work-item-status');
      expect(statusElement).toBeInTheDocument();
      expect(statusElement).toHaveTextContent(/not started/i);
    }, {
      timeout: 2000
    });
  });

  it('handles callback when dependencies are updated', async () => {
    const onDependenciesUpdated = vi.fn();

    render(
      <DependencyManager
        workItems={mockWorkItems}
        onDependenciesUpdated={onDependenciesUpdated}
      />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(onDependenciesUpdated).toHaveBeenCalledWith(mockDependencies);
    });
  });
});
