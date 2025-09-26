export interface WorkItem {
  id: string;
  title: string;
  storyPoints: number;
  description?: string;
}

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
