import { createContext } from 'react';
import type { WorkItem, SimulationResult } from '../types';

interface SimulationContextType {
  items: WorkItem[];
  updateItems: (items: WorkItem[]) => void;
  results: SimulationResult | null;
  isLoading: boolean;
  error: Error | null;
}

export const SimulationContext = createContext<SimulationContextType>({
  items: [],
  updateItems: () => {},
  results: null,
  isLoading: false,
  error: null,
});
