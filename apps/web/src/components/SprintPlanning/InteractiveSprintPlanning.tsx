import React, { useCallback, useEffect, useState } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { debounce } from 'lodash';
import { Box, Container, Paper } from '@mui/material';
import { SimulationContext } from '../../contexts/SimulationContext';
import { BacklogList } from './BacklogList';
import { SprintPlanningBoard } from './SprintPlanningBoard';
import { SimulationResults } from './SimulationResults';
import { runSimulation } from '../../services/simulationService';
import type { WorkItem, SimulationResult } from '../../types';

interface Props {
  initialItems?: WorkItem[];
}

export const InteractiveSprintPlanning: React.FC<Props> = ({ initialItems = [] }) => {
  const [items, setItems] = useState<WorkItem[]>(initialItems);
  const [results, setResults] = useState<SimulationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const debouncedSimulation = useCallback(
    debounce(async (workItems: WorkItem[]) => {
      try {
        setIsLoading(true);
        setError(null);
        const result = await runSimulation(workItems);
        setResults(result);
      } catch (err) {
        setError(err as Error);
      } finally {
        setIsLoading(false);
      }
    }, 500),
    []
  );

  useEffect(() => {
    if (items.length > 0) {
      debouncedSimulation(items);
    }
  }, [items, debouncedSimulation]);

  const updateItems = useCallback((newItems: WorkItem[]) => {
    setItems(newItems);
  }, []);

  return (
    <DndProvider backend={HTML5Backend}>
      <SimulationContext.Provider value={{ items, updateItems, results, isLoading, error }}>
        <Container maxWidth="xl">
          <Box display="grid" gridTemplateColumns="1fr 2fr" gap={2} p={2}>
            <Paper elevation={2}>
              <BacklogList />
            </Paper>
            <Box display="flex" flexDirection="column" gap={2}>
              <Paper elevation={2}>
                <SprintPlanningBoard />
              </Paper>
              <Paper elevation={2}>
                <SimulationResults />
              </Paper>
            </Box>
          </Box>
        </Container>
      </SimulationContext.Provider>
    </DndProvider>
  );
};
