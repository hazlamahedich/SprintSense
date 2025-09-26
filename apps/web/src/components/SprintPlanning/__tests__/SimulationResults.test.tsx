import * as React from 'react';
import { render, screen } from '@testing-library/react';
import { SimulationContext } from '../../../contexts/SimulationContext';
import { SimulationResults } from '../SimulationResults';

const mockResults = {
  distribution: [{ storyPoints: 5, frequency: 10 }],
  percentiles: { p25: 3, p50: 5, p75: 7 },
  confidence: 0.8,
  explanation: 'Test explanation',
};

describe('SimulationResults', () => {
  it('shows loading state', () => {
    render(
      <SimulationContext.Provider
        value={{
          items: [],
          updateItems: jest.fn(),
          results: null,
          isLoading: true,
          error: null,
        }}
      >
        <SimulationResults />
      </SimulationContext.Provider>
    );

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('shows error message', () => {
    const errorMessage = 'Test error';
    render(
      <SimulationContext.Provider
        value={{
          items: [],
          updateItems: jest.fn(),
          results: null,
          isLoading: false,
          error: new Error(errorMessage),
        }}
      >
        <SimulationResults />
      </SimulationContext.Provider>
    );

    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('shows empty state when no results', () => {
    render(
      <SimulationContext.Provider
        value={{
          items: [],
          updateItems: jest.fn(),
          results: null,
          isLoading: false,
          error: null,
        }}
      >
        <SimulationResults />
      </SimulationContext.Provider>
    );

    expect(
      screen.getByText('Add items to the sprint to see simulation results')
    ).toBeInTheDocument();
  });

  it('shows simulation results', () => {
    render(
      <SimulationContext.Provider
        value={{
          items: [],
          updateItems: jest.fn(),
          results: mockResults,
          isLoading: false,
          error: null,
        }}
      >
        <SimulationResults />
      </SimulationContext.Provider>
    );

    expect(screen.getByText('Simulation Results')).toBeInTheDocument();
    expect(screen.getByText('50th Percentile: 5 Story Points')).toBeInTheDocument();
    expect(screen.getByText('75th Percentile: 7 Story Points')).toBeInTheDocument();
    expect(screen.getByText('Confidence Score: 80.0%')).toBeInTheDocument();
  });
});
