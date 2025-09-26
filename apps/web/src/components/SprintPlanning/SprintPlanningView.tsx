import React from 'react';
import { Container, Box, Typography } from '@mui/material';
import { useSimulationStore } from '@/stores/simulationStore';
import { SimulationControls } from './SimulationControls';
import { SimulationVisualization } from './SimulationVisualization';
import { WorkItemList } from './WorkItemList';
import { ErrorBoundary } from '../ErrorBoundary';

export const SprintPlanningView: React.FC = () => {
  const { results, isLoading, error } = useSimulationStore();

  return (
    <ErrorBoundary>
      <Container maxWidth="lg">
        <Box mb={4}>
          <Typography variant="h4" component="h1" gutterBottom>
            Sprint Planning
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            Plan your sprint using AI-powered predictions to optimize team capacity
            and increase sprint success rates.
          </Typography>
        </Box>

        <Box mb={4}>
          <SimulationControls />
        </Box>

        {error && (
          <Box mb={4} p={2} bgcolor="error.light" borderRadius={1}>
            <Typography color="error">{error}</Typography>
          </Box>
        )}

        {results && !error && (
          <Box mb={4}>
            <SimulationVisualization data={results} />
          </Box>
        )}

        <Box>
          <WorkItemList isLoading={isLoading} />
        </Box>
      </Container>
    </ErrorBoundary>
  );
};
