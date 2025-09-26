import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SimulationControls } from '../SimulationControls';
import { SimulationService } from '@/services/simulationService';
import { useSimulationStore } from '@/stores/simulationStore';

jest.mock('@/services/simulationService', () => ({
  SimulationService: {
    runSimulation: jest.fn(),
    saveScenario: jest.fn(),
    clearCache: jest.fn(),
  }
}));

jest.mock('@/stores/simulationStore');

const mockUseSimulationStore = useSimulationStore as unknown as jest.Mock;

describe('SimulationControls', () => {
  const mockSetLoading = jest.fn();
  const mockSetError = jest.fn();
  const mockSetResults = jest.fn();
  const mockSetScenarioId = jest.fn();

  const baseStore = {
    results: null,
    isLoading: false,
    setLoading: mockSetLoading,
    setError: mockSetError,
    setResults: mockSetResults,
    setScenarioId: mockSetScenarioId,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseSimulationStore.mockReturnValue({ ...baseStore });
  });

  const renderControls = () => render(<SimulationControls />);

  it('renders all control buttons', () => {
    renderControls();

    expect(screen.getByText('Run Simulation')).toBeInTheDocument();
expect(screen.getByText('Save Scenario')).toBeInTheDocument();
    expect(screen.getByText('Reset')).toBeInTheDocument();
  });

  it('disables Save and Reset buttons when no results', () => {
    renderControls();

expect(screen.getByText('Save Scenario')).toBeDisabled();
    expect(screen.getByText('Reset')).toBeDisabled();
  });

  it('keeps Run enabled but disables Save and Reset during loading', () => {
    mockUseSimulationStore.mockReturnValue({ ...baseStore, isLoading: true });

    renderControls();

    // Run Simulation should stay enabled during loading
    expect(screen.getByText('Run Simulation')).toBeEnabled();
    // Run button should stay enabled even while loading
    expect(screen.getByText('Run Simulation')).toBeEnabled();
    expect(screen.getByText('Reset')).toBeDisabled();
  });

  it('handles simulation success', async () => {
    const user = userEvent.setup();
    const mockResult = {
      distribution: [{ storyPoints: 10, frequency: 0.5 }],
      percentiles: { p25: 8, p50: 10, p75: 12 },
      confidence: 0.8,
      explanation: 'Test',
    };

    (SimulationService.runSimulation as jest.Mock).mockResolvedValue(mockResult);

    renderControls();

    await act(async () => {
      await user.click(screen.getByText('Run Simulation'));
    });

    await waitFor(() => {
      expect(mockSetResults).toHaveBeenCalledWith(mockResult);
    });
  });

  it('handles simulation error', async () => {
    const user = userEvent.setup();
    const error = new Error('Test error');
    const mockError = error instanceof Error ? error : new Error('Failed to run simulation');
    (SimulationService.runSimulation as jest.Mock).mockRejectedValue(error);

    renderControls();

    await act(async () => {
      await user.click(screen.getByText('Run Simulation'));
    });

    await waitFor(() => {
      expect(mockSetError).toHaveBeenCalledWith(mockError);
    });
  });

  it('handles scenario save', async () => {
    const user = userEvent.setup();
    const mockResults = {
      distribution: [{ storyPoints: 10, frequency: 0.5 }],
      percentiles: { p25: 8, p50: 10, p75: 12 },
      confidence: 0.8,
      explanation: 'Test',
    };

    mockUseSimulationStore.mockReturnValue({ ...baseStore, results: mockResults });

    (SimulationService.saveScenario as jest.Mock).mockResolvedValue('scenario-123');

    renderControls();

    await act(async () => {
await user.click(screen.getByText('Save Scenario'));
    });

    await waitFor(() => {
      expect(mockSetScenarioId).toHaveBeenCalledWith('scenario-123');
    });
  });

  it('handles reset', async () => {
    // Ensure results exist so Reset is enabled
    const user = userEvent.setup();
    mockUseSimulationStore.mockReturnValue({ ...baseStore, results: { distribution: [], percentiles: { p25: 0, p50: 0, p75: 0 }, confidence: 0, explanation: '' } });

    renderControls();

    await act(async () => {
      await user.click(screen.getByText('Reset'));
    });

    await waitFor(() => {
      expect(SimulationService.clearCache).toHaveBeenCalled();
      expect(mockSetResults).toHaveBeenCalledWith(null);
      expect(mockSetScenarioId).toHaveBeenCalledWith(null);
      expect(mockSetError).toHaveBeenCalledWith(null);
    });
  });
});
