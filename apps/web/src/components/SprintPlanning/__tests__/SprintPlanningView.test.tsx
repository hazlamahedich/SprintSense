import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SprintPlanningView } from '../SprintPlanningView';
import { useSimulationStore } from '@/stores/simulationStore';

// Mock the simulation store
jest.mock('@/stores/simulationStore');
const mockUseSimulationStore = useSimulationStore as jest.Mock;

describe('SprintPlanningView', () => {
  beforeEach(() => {
    mockUseSimulationStore.mockReturnValue({
      results: null,
      isLoading: false,
      error: null,
    });
  });

  it('renders the initial view correctly', () => {
    render(<SprintPlanningView />);

    expect(screen.getByText('Sprint Planning')).toBeInTheDocument();
    expect(screen.getByText(/Plan your sprint using AI-powered predictions/)).toBeInTheDocument();
  });

  it('displays simulation results when available', () => {
    mockUseSimulationStore.mockReturnValue({
      results: {
        distribution: [
          { storyPoints: 10, frequency: 0.2 },
          { storyPoints: 15, frequency: 0.5 },
        ],
        percentiles: {
          p25: 10,
          p50: 15,
          p75: 20,
        },
        confidence: 0.85,
        explanation: 'Based on historical data',
      },
      isLoading: false,
      error: null,
    });

    render(<SprintPlanningView />);

    expect(screen.getByText('Sprint Simulation Results')).toBeInTheDocument();
    expect(screen.getByText(/Based on historical data/)).toBeInTheDocument();
  });

  it('displays error message when an error occurs', () => {
    const errorMessage = 'Failed to run simulation';
    mockUseSimulationStore.mockReturnValue({
      results: null,
      isLoading: false,
      error: errorMessage,
    });

    render(<SprintPlanningView />);

    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('shows loading state in work item list', () => {
    mockUseSimulationStore.mockReturnValue({
      results: null,
      isLoading: true,
      error: null,
    });

    render(<SprintPlanningView />);

    expect(screen.getAllByRole('row')[0]).toBeInTheDocument();
  });
});
