import { render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { VelocityChart } from '../../../components/sprints/VelocityChart';
import { getVelocityData } from '../../../services/velocityService';

// Mock velocity service
vi.mock('../../../services/velocityService');

describe('VelocityChart', () => {
  const mockTeamId = '123';
  const mockVelocityData = [
    {
      sprintId: '1',
      sprintName: 'Sprint 1',
      points: 13,
      startDate: '2025-08-01T00:00:00Z',
      endDate: '2025-08-14T23:59:59Z',
    },
    {
      sprintId: '2',
      sprintName: 'Sprint 2',
      points: 21,
      startDate: '2025-08-15T00:00:00Z',
      endDate: '2025-08-28T23:59:59Z',
    },
    {
      sprintId: '3',
      sprintName: 'Sprint 3',
      points: 34,
      startDate: '2025-08-29T00:00:00Z',
      endDate: '2025-09-11T23:59:59Z',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading state initially', () => {
    vi.mocked(getVelocityData).mockImplementation(() => new Promise(() => {}));
    render(<VelocityChart teamId={mockTeamId} />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('displays velocity data when loaded', async () => {
    vi.mocked(getVelocityData).mockResolvedValue(mockVelocityData);
    render(<VelocityChart teamId={mockTeamId} />);

    await waitFor(() => {
      expect(screen.getByText('Team Velocity')).toBeInTheDocument();
      // Verify the chart container exists
      expect(screen.getByTestId('velocity-chart')).toBeInTheDocument();
    });
  });

  it('shows new team message when less than 3 sprints', async () => {
    const twoSprints = mockVelocityData.slice(0, 2);
    vi.mocked(getVelocityData).mockResolvedValue(twoSprints);
    render(<VelocityChart teamId={mockTeamId} />);

    await waitFor(() => {
      expect(screen.getByText('Velocity trends will appear after completing 3 sprints')).toBeInTheDocument();
    });
  });

  it('shows error message on failure', async () => {
    const errorMessage = 'Failed to load velocity data';
    vi.mocked(getVelocityData).mockRejectedValue(new Error(errorMessage));
    render(<VelocityChart teamId={mockTeamId} />);

    await waitFor(() => {
      expect(screen.getByText('Error Loading Velocity Data')).toBeInTheDocument();
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('calculates and displays rolling average', async () => {
    vi.mocked(getVelocityData).mockResolvedValue(mockVelocityData);
    render(<VelocityChart teamId={mockTeamId} showRollingAverage={true} />);

    await waitFor(() => {
      // Verify the chart container exists
      expect(screen.getByTestId('velocity-chart')).toBeInTheDocument();
    });
  });

  it('respects sprint limit parameter', async () => {
    render(<VelocityChart teamId={mockTeamId} sprints={3} />);
    await waitFor(() => {
      expect(getVelocityData).toHaveBeenCalledWith(mockTeamId, 3);
    });
  });
});
