import axios from 'axios';
import type { SimulationResult } from '../stores/simulationStore';

const API_BASE = process.env.NEXT_PUBLIC_API_URL;
const SIMULATION_CACHE = new Map<string, SimulationResult>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

interface SimulationRequest {
  teamId: string;
  sprintId: string;
  workItems: Array<{
    id: string;
    storyPoints: number;
  }>;
}

export class SimulationService {
  static async runSimulation(request: SimulationRequest): Promise<SimulationResult> {
    const cacheKey = JSON.stringify(request);
    const cachedResult = SIMULATION_CACHE.get(cacheKey);

    if (cachedResult) {
      return cachedResult;
    }

    try {
      const response = await axios.post<SimulationResult>(
        `${API_BASE}/teams/${request.teamId}/sprints/${request.sprintId}/simulate`,
        request
      );

      SIMULATION_CACHE.set(cacheKey, response.data);
      setTimeout(() => SIMULATION_CACHE.delete(cacheKey), CACHE_TTL);

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.message || 'Failed to run simulation');
      }
      throw error;
    }
  }

  static async saveScenario(teamId: string, sprintId: string, results: SimulationResult): Promise<string> {
    try {
      const response = await axios.post<{ scenarioId: string }>(
        `${API_BASE}/teams/${teamId}/sprints/${sprintId}/scenarios`,
        { results }
      );
      return response.data.scenarioId;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.message || 'Failed to save scenario');
      }
      throw error;
    }
  }

  static clearCache(): void {
    SIMULATION_CACHE.clear();
  }
}
