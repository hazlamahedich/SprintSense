import React, { useState, useEffect } from 'react';
import { DependencyGraph } from './DependencyGraph';
import { CircularProgress, Alert, Button, Typography, Box } from '@mui/material';
import { useQuery, useMutation } from '@tanstack/react-query';
import { analyzeDependencies, suggestDependencyChain } from '../../services/dependencies';
import { WorkItem, Dependency } from '../../types';

interface DependencyManagerProps {
  workItems: WorkItem[];
  onDependenciesUpdated?: (dependencies: Dependency[]) => void;
}

export const DependencyManager: React.FC<DependencyManagerProps> = ({
  workItems,
  onDependenciesUpdated,
}) => {
  // State
  const [selectedWorkItem, setSelectedWorkItem] = useState<WorkItem | null>(null);
  const [selectedDependency, setSelectedDependency] = useState<Dependency | null>(null);

  // Queries
  const {
    data: dependencies,
    isLoading: isAnalyzing,
    isError: analysisError,
    refetch: refetchDependencies,
  } = useQuery({
    queryKey: ['dependencies', workItems.map(item => item.id)],
    queryFn: () => analyzeDependencies(workItems),
    enabled: workItems.length > 0,
    staleTime: 30000, // 30 seconds
  });

  // Chain suggestion mutation
  const {
    mutate: suggestChain,
    data: suggestedChain,
    isLoading: isSuggestingChain,
    reset: resetChain,
  } = useMutation({
    mutationFn: (targetDate: string) => suggestDependencyChain(workItems, targetDate)
  });

  // Effects
  useEffect(() => {
    if (dependencies && onDependenciesUpdated) {
      onDependenciesUpdated(dependencies);
    }
  }, [dependencies, onDependenciesUpdated]);

  // Handlers
  const handleWorkItemClick = (workItem: WorkItem) => {
    console.log('Work item clicked:', workItem);
    setSelectedWorkItem(workItem);
    resetChain();
  };

  const handleDependencyClick = (dependency: Dependency) => {
    setSelectedDependency(dependency);
  };

  const handleRefresh = () => {
    refetchDependencies();
  };

  const handleSuggestChain = () => {
    const targetDate = new Date();
    targetDate.setDate(targetDate.getDate() + 30); // 30 days from now
    suggestChain(targetDate.toISOString());
  };

  if (workItems.length === 0) {
    return (
      <Box p={3} textAlign="center">
        <Typography variant="h6">
          No work items available for dependency analysis
        </Typography>
      </Box>
    );
  }

  if (isAnalyzing) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="400px"
      >
        <CircularProgress />
      </Box>
    );
  }

  if (analysisError) {
    return (
      <Box p={3}>
        <Alert
          severity="error"
          action={
            <Button color="inherit" size="small" onClick={handleRefresh}>
              Retry
            </Button>
          }
        >
          Failed to analyze dependencies. Please try again.
        </Alert>
      </Box>
    );
  }

  return (
    <Box className="dependency-manager">
      {/* Controls */}
      <Box mb={2} display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h6">
          Dependency Analysis
        </Typography>
        <Box>
          <Button
            variant="outlined"
            onClick={handleRefresh}
            sx={{ mr: 1 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            onClick={handleSuggestChain}
            disabled={isSuggestingChain}
          >
            Suggest Chain
          </Button>
        </Box>
      </Box>

      {/* Graph */}
      {dependencies && (
        <Box mb={2} height="500px" border="1px solid #e0e0e0" borderRadius={1}>
          <DependencyGraph
            workItems={workItems}
            dependencies={dependencies}
            onWorkItemClick={handleWorkItemClick}
            onDependencyClick={handleDependencyClick}
          />
        </Box>
      )}

      {/* Suggestions */}
      {suggestedChain && (
        <Box mt={2}>
          <Typography variant="h6" gutterBottom>
            Suggested Work Order
          </Typography>
          <Box
            p={2}
            bgcolor="#f5f5f5"
            borderRadius={1}
            maxHeight="200px"
            overflow="auto"
          >
            {suggestedChain.map((item, index) => (
              <Box
                key={item.id}
                py={1}
                display="flex"
                alignItems="center"
              >
                <Typography variant="body2" color="textSecondary" sx={{ mr: 2 }}>
                  {index + 1}.
                </Typography>
                <Typography>{item.title}</Typography>
              </Box>
            ))}
          </Box>
        </Box>
      )}

      {/* Selected Item Details */}
      {selectedWorkItem && (
        <Box mt={2} p={2} bgcolor="#f5f5f5" borderRadius={1}>
          <Typography variant="subtitle1" gutterBottom>
            Selected Work Item
          </Typography>
          <Typography variant="body2">
            Title: {selectedWorkItem.title}
          </Typography>
          <Typography variant="body2" data-testid="work-item-status">
            Status: {selectedWorkItem.status.replace(/_/g, ' ').toLowerCase()}
          </Typography>
          <Typography variant="body2">
            Dependencies: {
              dependencies?.filter(d =>
                d.source.id === selectedWorkItem.id ||
                d.target.id === selectedWorkItem.id
              ).length || 0
            }
          </Typography>
        </Box>
      )}
    </Box>
  );
};

