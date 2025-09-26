import type { VelocityData } from "../types/sprint.types";
import { api } from "../lib/api";

export async function getVelocityData(
  teamId: string,
  limit: number = 5
): Promise<VelocityData[]> {
  try {
    const response = await api.get(`/teams/${teamId}/velocity?limit=${limit}`);
    return response.data;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to fetch velocity data: ${error.message}`);
    }
    throw new Error("Failed to fetch velocity data");
  }
}
