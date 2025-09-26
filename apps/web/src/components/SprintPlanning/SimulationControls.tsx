import React, { useCallback } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Stack,
  Typography,
  Tooltip,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import SaveIcon from '@mui/icons-material/Save';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useSimulationStore } from '@/stores/simulationStore';
import { SimulationService } from '@/services/simulationService';

export const SimulationControls: React.FC = () => {
  const { results, isLoading, setLoading, setError, setResults, setScenarioId } =
    useSimulationStore();

  const handleRunSimulation = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Mock data for now - would come from props/context in real implementation
      const result = await SimulationService.runSimulation({
        teamId: '123',
        sprintId: '456',
        workItems: [
          { id: '1', storyPoints: 3 },
          { id: '2', storyPoints: 5 },
        ],
      });

      setResults(result);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to run simulation');
    } finally {
      setLoading(false);
    }
  }, [setLoading, setError, setResults]);

  const handleSaveScenario = useCallback(async () => {
    if (!results) return;

    try {
      setLoading(true);
      setError(null);

      const scenarioId = await SimulationService.saveScenario('123', '456', results);
      setScenarioId(scenarioId);

    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to save scenario');
    } finally {
      setLoading(false);
    }
  }, [results, setLoading, setError, setScenarioId]);

  const handleReset = useCallback(() => {
    SimulationService.clearCache();
    setResults(null);
    setScenarioId(null);
    setError(null);
  }, [setResults, setScenarioId, setError]);

  return (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Simulation Controls
        </Typography>
        <Stack direction="row" spacing={2}>
          <Tooltip title="Run the sprint simulation">
            <span>
              <Button
                variant="contained"
                color="primary"
                startIcon={<PlayArrowIcon />}
                onClick={handleRunSimulation}
                disabled={isLoading}
              >
                Run Simulation
              </Button>
            </span>
          </Tooltip>

          <Tooltip title="Save current scenario">
            <span>
              <Button
                variant="outlined"
                startIcon={<SaveIcon />}
                onClick={handleSaveScenario}
                disabled={isLoading || !results}
              >
                Save Scenario
              </Button>
            </span>
          </Tooltip>

          <Tooltip title="Reset simulation">
            <span>
              <Button
                variant="outlined"
                color="secondary"
                startIcon={<RefreshIcon />}
                onClick={handleReset}
                disabled={isLoading || !results}
              >
                Reset
              </Button>
            </span>
          </Tooltip>
        </Stack>
      </CardContent>
    </Card>
  );
};
