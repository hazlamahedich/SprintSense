import { useState, useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';

import { supabase } from '@/lib/supabaseClient';

interface TeamMember {
  id: string;
  availability: number;
  skills: string[];
  timeZone: string;
}

interface WorkItem {
  id: string;
  storyPoints: number;
  requiredSkills: string[];
  assignedTo?: string;
  estimatedHours: number;
}

interface BalanceMetrics {
  overallBalanceScore: number;
  teamUtilization: number;
  skillCoverage: number;
  workloadDistribution: Record<string, number>;
  bottlenecks: string[];
  recommendations: string[];
}

interface UseSprintBalanceOptions {
  refreshInterval?: number;
  onError?: (error: Error) => void;
}

const DEFAULT_REFRESH_INTERVAL = 30000; // 30 seconds

export function useSprintBalance(
  sprintId: string,
  options: UseSprintBalanceOptions = {}
) {
  const {
    refreshInterval = DEFAULT_REFRESH_INTERVAL,
    onError
  } = options;

  const queryClient = useQueryClient();

  // Fetch balance metrics
  const {
    data: balanceMetrics,
    error,
    isLoading,
    isError
  } = useQuery<BalanceMetrics, Error>(
    ['sprintBalance', sprintId],
    async () => {
      try {
        const { data, error } = await supabase
          .from('sprint_balance')
          .select('*')
          .eq('sprint_id', sprintId)
          .single();

        if (error) throw error;
        return data;
      } catch (err) {
        console.error('Error fetching sprint balance:', err);
        throw new Error('Failed to fetch sprint balance data');
      }
    },
    {
      refetchInterval: refreshInterval,
      onError: (err) => {
        toast.error('Failed to load sprint balance data');
        onError?.(err);
      }
    }
  );

  // Force refresh balance metrics
  const refreshBalance = async () => {
    try {
      const { data, error } = await supabase
        .rpc('refresh_sprint_balance', { sprint_id: sprintId });

      if (error) throw error;

      // Invalidate and refetch
      queryClient.invalidateQueries(['sprintBalance', sprintId]);
      toast.success('Sprint balance data refreshed');
      
      return data;
    } catch (err) {
      console.error('Error refreshing sprint balance:', err);
      toast.error('Failed to refresh sprint balance data');
      throw err;
    }
  };

  // Subscribe to real-time updates
  useEffect(() => {
    const subscription = supabase
      .channel('sprint_balance_changes')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'sprint_balance',
          filter: `sprint_id=eq.${sprintId}`
        },
        () => {
          // Invalidate and refetch on any changes
          queryClient.invalidateQueries(['sprintBalance', sprintId]);
        }
      )
      .subscribe();

    return () => {
      subscription.unsubscribe();
    };
  }, [sprintId, queryClient]);

  return {
    balanceMetrics,
    isLoading,
    isError,
    error,
    refreshBalance
  };
}