import React from 'react';
import { Box, Card, CardContent, Typography, Divider } from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { SimulationResult } from '@/stores/simulationStore';

interface Props {
  data: SimulationResult;
}

export const SimulationVisualization: React.FC<Props> = ({ data }) => {
  const chartData = data.distribution.map((point) => ({
    storyPoints: point.storyPoints,
    frequency: point.frequency,
  }));

  return (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Sprint Simulation Results
        </Typography>

        <Box mb={3}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Confidence Score: {(data.confidence * 100).toFixed(1)}%
          </Typography>
          <Typography variant="body2" paragraph>
            {data.explanation}
          </Typography>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Box height={300}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <XAxis
                dataKey="storyPoints"
                label={{ value: 'Story Points', position: 'bottom' }}
              />
              <YAxis
                label={{
                  value: 'Frequency',
                  angle: -90,
                  position: 'insideLeft',
                }}
              />
              <Tooltip
                formatter={(value: number, name: string) => {
                  if (name === 'frequency') {
                    return [`${(value * 100).toFixed(1)}%`, 'Probability'];
                  }
                  return [value, name];
                }}
              />
              <Bar dataKey="frequency" fill="#2196f3" />
              <ReferenceLine
                x={data.percentiles.p25}
                stroke="#ff9800"
                strokeDasharray="3 3"
                label="25th"
              />
              <ReferenceLine
                x={data.percentiles.p50}
                stroke="#4caf50"
                strokeDasharray="3 3"
                label="50th"
              />
              <ReferenceLine
                x={data.percentiles.p75}
                stroke="#f44336"
                strokeDasharray="3 3"
                label="75th"
              />
            </BarChart>
          </ResponsiveContainer>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Sprint Capacity Percentiles
          </Typography>
          <Typography variant="body2">
            • 25th Percentile: {data.percentiles.p25} story points
            <br />
            • 50th Percentile (Median): {data.percentiles.p50} story points
            <br />
            • 75th Percentile: {data.percentiles.p75} story points
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};
