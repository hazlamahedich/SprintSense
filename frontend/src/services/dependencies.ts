import { WorkItem, Dependency } from '../types';
import { api } from './api';

/**
 * Analyze dependencies between work items
 * @param workItems List of work items to analyze
 * @returns List of detected dependencies with confidence scores
 */
export const analyzeDependencies = async (workItems: WorkItem[]): Promise<Dependency[]> => {
  try {
    const { data } = await api.post('/dependencies/analyze', { work_items: workItems });
    return data;
  } catch (error) {
    console.error('Failed to analyze dependencies:', error);
    throw error;
  }
};

/**
 * Get suggestions for optimal work item ordering
 * @param workItems Work items to order
 * @param targetDate Target completion date
 * @returns Ordered list of work items with explanations
 */
export const suggestDependencyChain = async (
  workItems: WorkItem[],
  targetDate: string
): Promise<WorkItem[]> => {
  try {
    const { data } = await api.post('/dependencies/chain', {
      work_items: workItems,
      target_date: targetDate,
    });
    return data;
  } catch (error) {
    console.error('Failed to suggest dependency chain:', error);
    throw error;
  }
};
