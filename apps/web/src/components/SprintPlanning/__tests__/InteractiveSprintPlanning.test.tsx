import * as React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { InteractiveSprintPlanning } from '../InteractiveSprintPlanning';
import { runSimulation } from '../../../services/simulationService';

// Mock the simulation service
jest.mock('../../../services/simulationService');

const mockSimulationResult = {
  distribution: [{ storyPoints: 5, frequency: 10 }],
  percentiles: { p25: 3, p50: 5, p75: 7 },
  confidence: 0.8,
  explanation: 'Test explanation',
};

describe('InteractiveSprintPlanning', () => {
  beforeEach(() => {
    jest.useFakeTimers({ doNotFake: ['nextTick', 'setImmediate'] });
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });
  beforeEach(() => {
    (runSimulation as jest.Mock).mockResolvedValue(mockSimulationResult);
  });

  it('renders without crashing', () => {
    render(<InteractiveSprintPlanning />);
    expect(screen.getByText('Backlog Items')).toBeInTheDocument();
    expect(screen.getByText('Sprint Plan')).toBeInTheDocument();
  });

  it('shows empty state initially', () => {
    render(<InteractiveSprintPlanning />);
    expect(screen.getByText('Add items to the sprint to see simulation results')).toBeInTheDocument();
  });

  it('shows error message when simulation fails', async () => {
    // Mock console.error to avoid React warning logs
    const originalError = console.error;
    console.error = jest.fn();
    const mockItem = { id: '1', title: 'Test Item', storyPoints: 3 };
    const errorMessage = 'Simulation failed';
    (runSimulation as jest.Mock).mockRejectedValue(new Error(errorMessage));

    render(<InteractiveSprintPlanning initialItems={[mockItem]} />);

    // Fast forward past debounce
    await act(async () => {
      jest.advanceTimersByTime(500);
    });

    // Wait until the mocked rejection is processed and error UI appears
    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent(errorMessage));

    // Restore console.error
    console.error = originalError;
  });
});
