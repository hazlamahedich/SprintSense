import React, { useContext } from 'react';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  Paper,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { SimulationContext } from '../../contexts/SimulationContext';

export const SimulationResults: React.FC = () => {
  const { results, isLoading, error } = useContext(SimulationContext);

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={2}>
        <Alert severity="error" role="alert">
          {error.message || 'An error occurred while running the simulation'}
        </Alert>
      </Box>
    );
  }

  if (!results) {
    return (
      <Box p={2}>
        <Typography variant="body1" color="textSecondary">
          Add items to the sprint to see simulation results
        </Typography>
      </Box>
    );
  }

  return (
    <Box p={2}>
      <Typography variant="h6" gutterBottom>
        Simulation Results
      </Typography>
      <Box height={300}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={results.distribution}>
            <XAxis dataKey="storyPoints" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="frequency" fill="#2196f3" />
          </BarChart>
        </ResponsiveContainer>
      </Box>
      <Box mt={2}>
        <Typography variant="body1">
          50th Percentile: {results.percentiles.p50} Story Points
        </Typography>
        <Typography variant="body1">
          75th Percentile: {results.percentiles.p75} Story Points
        </Typography>
        <Typography variant="body2" color="textSecondary" mt={1}>
          Confidence Score: {(results.confidence * 100).toFixed(1)}%
        </Typography>
      </Box>
    </Box>
  );
};
