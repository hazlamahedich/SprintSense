import React from 'react';
import { render, screen } from '@testing-library/react';
import { SimulationVisualization } from '../SimulationVisualization';
import type { SimulationResult } from '@/stores/simulationStore';

// Mock Recharts as it's causing issues with Jest
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => children,
  BarChart: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Bar: () => null,
  XAxis: () => null,
  YAxis: () => null,
  Tooltip: () => null,
  ReferenceLine: () => null,
}));

describe('SimulationVisualization', () => {
  const mockData: SimulationResult = {
    distribution: [
      { storyPoints: 10, frequency: 0.2 },
      { storyPoints: 15, frequency: 0.5 },
      { storyPoints: 20, frequency: 0.3 },
    ],
    percentiles: {
      p25: 10,
      p50: 15,
      p75: 20,
    },
    confidence: 0.85,
    explanation: 'Based on historical velocity data and current team capacity.',
  };

  it('renders simulation results correctly', () => {
    render(<SimulationVisualization data={mockData} />);

    expect(screen.getByText('Sprint Simulation Results')).toBeInTheDocument();
    expect(screen.getByText((content, element) => content.includes('85.0'))).toBeInTheDocument();
    expect(screen.getByText(mockData.explanation)).toBeInTheDocument();
  });

  it('displays percentile information', () => {
    render(<SimulationVisualization data={mockData} />);

    expect(screen.getByText('Sprint Capacity Percentiles')).toBeInTheDocument();
    expect(screen.getByText(/25th Percentile: 10 story points/)).toBeInTheDocument();
    expect(screen.getByText(/50th Percentile \(Median\): 15 story points/)).toBeInTheDocument();
    expect(screen.getByText(/75th Percentile: 20 story points/)).toBeInTheDocument();
  });

  it('formats confidence score correctly', () => {
    const dataWithLowConfidence = {
      ...mockData,
      confidence: 0.456789,
    };

    render(<SimulationVisualization data={dataWithLowConfidence} />);

    expect(screen.getByText((content, element) => content.includes('45.7'))).toBeInTheDocument();
  });

  it('renders chart components', () => {
    const { container } = render(<SimulationVisualization data={mockData} />);

    // Renders without crashing when chart is present (recharts mocked)
    expect(container).toBeTruthy();
  });
});
