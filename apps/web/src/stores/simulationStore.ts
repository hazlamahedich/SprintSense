import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface DistributionPoint {
  storyPoints: number;
  frequency: number;
}

export interface SimulationResult {
  distribution: DistributionPoint[];
  percentiles: {
    p25: number;
    p50: number;
    p75: number;
  };
  confidence: number;
  explanation: string;
}

interface SimulationState {
  results: SimulationResult | null;
  isLoading: boolean;
  error: string | null;
  scenarioId: string | null;
  setResults: (results: SimulationResult | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setScenarioId: (id: string | null) => void;
  reset: () => void;
}

const initialState = {
  results: null,
  isLoading: false,
  error: null,
  scenarioId: null,
};

export const useSimulationStore = create<SimulationState>()(
  devtools(
    (set) => ({
      ...initialState,
      setResults: (results) => set({ results, error: null }),
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error, results: null }),
      setScenarioId: (scenarioId) => set({ scenarioId }),
      reset: () => set(initialState),
    }),
    {
      name: 'SimulationStore',
    }
  )
);
