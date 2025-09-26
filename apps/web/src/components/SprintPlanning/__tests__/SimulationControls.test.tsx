import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SimulationControls } from '../SimulationControls';
import { useSimulationStore } from '@/stores/simulationStore';
import { SimulationService } from '@/services/simulationService';

jest.mock('@/stores/simulationStore');
jest.mock('@/services/simulationService');

const mockUseSimulationStore = useSimulationStore as jest.Mock;
const mockSimulationService = SimulationService as jest.Mocked<typeof SimulationService>;

describe('SimulationControls', () => {
  const mockSetLoading = jest.fn();
  const mockSetError = jest.fn();
  const mockSetResults = jest.fn();
  const mockSetScenarioId = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseSimulationStore.mockReturnValue({
      results: null,
      isLoading: false,
      setLoading: mockSetLoading,
      setError: mockSetError,
      setResults: mockSetResults,
      setScenarioId: mockSetScenarioId,
    });
  });

  it('renders all control buttons', () => {
    render(<SimulationControls />);

    expect(screen.getByText('Run Simulation')).toBeInTheDocument();
    expect(screen.getByText('Save Scenario')).toBeInTheDocument();
    expect(screen.getByText('Reset')).toBeInTheDocument();
  });

  it('disables Save and Reset buttons when no results', () => {
    render(<SimulationControls />);

    expect(screen.getByText('Save Scenario')).toBeDisabled();
    expect(screen.getByText('Reset')).toBeDisabled();
  });

  it('disables all buttons while loading', () => {
    mockUseSimulationStore.mockReturnValue({
      results: null,
      isLoading: true,
      setLoading: mockSetLoading,
      setError: mockSetError,
      setResults: mockSetResults,
      setScenarioId: mockSetScenarioId,
    });

    render(<SimulationControls />);

    expect(screen.getByText('Run Simulation')).toBeDisabled();
    expect(screen.getByText('Save Scenario')).toBeDisabled();
    expect(screen.getByText('Reset')).toBeDisabled();
  });

  it('handles simulation success', async () => {
    const mockResult = {
      distribution: [{ storyPoints: 10, frequency: 0.5 }],
      percentiles: { p25: 8, p50: 10, p75: 12 },
      confidence: 0.8,
      explanation: 'Test',
    };

    mockSimulationService.runSimulation.mockResolvedValue(mockResult);

    render(<SimulationControls />);

    await userEvent.click(screen.getByText('Run Simulation'));

    expect(mockSetLoading).toHaveBeenCalledWith(true);
    await waitFor(() => {
      expect(mockSetResults).toHaveBeenCalledWith(mockResult);
    });
    expect(mockSetLoading).toHaveBeenCalledWith(false);
  });

  it('handles simulation error', async () => {
    const error = new Error('Test error');
    mockSimulationService.runSimulation.mockRejectedValue(error);

    render(<SimulationControls />);

    await userEvent.click(screen.getByText('Run Simulation'));

    expect(mockSetLoading).toHaveBeenCalledWith(true);
    await waitFor(() => {
      expect(mockSetError).toHaveBeenCalledWith('Test error');
    });
    expect(mockSetLoading).toHaveBeenCalledWith(false);
  });

  it('handles scenario save', async () => {
    const mockResults = {
      distribution: [{ storyPoints: 10, frequency: 0.5 }],
      percentiles: { p25: 8, p50: 10, p75: 12 },
      confidence: 0.8,
      explanation: 'Test',
    };

    mockUseSimulationStore.mockReturnValue({
      results: mockResults,
      isLoading: false,
      setLoading: mockSetLoading,
      setError: mockSetError,
      setResults: mockSetResults,
      setScenarioId: mockSetScenarioId,
    });

    mockSimulationService.saveScenario.mockResolvedValue('scenario-123');

    render(<SimulationControls />);

    await userEvent.click(screen.getByText('Save Scenario'));

    expect(mockSetLoading).toHaveBeenCalledWith(true);
    await waitFor(() => {
      expect(mockSetScenarioId).toHaveBeenCalledWith('scenario-123');
    });
    expect(mockSetLoading).toHaveBeenCalledWith(false);
  });

  it('handles reset', () => {
    mockUseSimulationStore.mockReturnValue({
      results: { distribution: [], percentiles: { p25: 0, p50: 0, p75: 0 }, confidence: 0, explanation: '' },
      isLoading: false,
      setLoading: mockSetLoading,
      setError: mockSetError,
      setResults: mockSetResults,
      setScenarioId: mockSetScenarioId,
    });

    render(<SimulationControls />);

    userEvent.click(screen.getByText('Reset'));

    expect(mockSetResults).toHaveBeenCalledWith(null);
    expect(mockSetScenarioId).toHaveBeenCalledWith(null);
    expect(mockSetError).toHaveBeenCalledWith(null);
  });
});
