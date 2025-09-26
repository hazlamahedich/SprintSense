import React, { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
  AlertTitle,
} from "@mui/material";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { motion, AnimatePresence } from "framer-motion";
// import { useUserStore } from "../../stores/userStore";
import { getVelocityData } from "../../services/velocityService";
import type { VelocityData } from "../../types/sprint.types";

interface VelocityChartProps {
  teamId: string;
  sprints?: number;
  showRollingAverage?: boolean;
}

export const VelocityChart: React.FC<VelocityChartProps> = ({
  teamId,
  sprints = 5,
  showRollingAverage = true,
}) => {
  const [data, setData] = useState<VelocityData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rollingAverage, setRollingAverage] = useState<number | null>(null);

  const calculateRollingAverage = (data: VelocityData[]): number | null => {
    if (data.length < 3) return null;
    const last3Sprints = data.slice(-3);
    const sum = last3Sprints.reduce((acc, sprint) => acc + sprint.points, 0);
    return Math.round(sum / 3);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const velocityData = await getVelocityData(teamId, sprints);
        setData(velocityData);

        if (showRollingAverage) {
          const avg = calculateRollingAverage(velocityData);
          setRollingAverage(avg);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load velocity data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [teamId, sprints, showRollingAverage]);

  const NewTeamMessage = () => (
    <Box sx={{ p: 2, textAlign: "center" }}>
      <Typography variant="h6" gutterBottom>
        Velocity trends will appear after completing 3 sprints
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Velocity is most reliable with more historical data
      </Typography>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Alert severity="info">
          <AlertTitle>Getting Started</AlertTitle>
          Complete your first few sprints to start seeing velocity trends.
          This will help in:
          <ul>
            <li>Understanding team capacity</li>
            <li>Planning future sprints</li>
            <li>Tracking productivity improvements</li>
          </ul>
        </Alert>
      </motion.div>
    </Box>
  );

  if (loading) {
    return (
      <Card>
        <CardContent sx={{ minHeight: 300, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <CircularProgress />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error">
            <AlertTitle>Error Loading Velocity Data</AlertTitle>
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (data.length < 3) {
    return (
      <Card>
        <CardContent>
          <NewTeamMessage />
        </CardContent>
      </Card>
    );
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
      >
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Team Velocity
            </Typography>
            <Box data-testid="velocity-chart" sx={{ height: 300, width: "100%" }}>
              <ResponsiveContainer>
                <AreaChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                  <XAxis
                    dataKey="sprintName"
                    stroke="#64748b"
                    tickLine={false}
                  />
                  <YAxis
                    stroke="#64748b"
                    tickLine={false}
                    tickFormatter={(value) => `${value} pts`}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "rgba(255, 255, 255, 0.9)",
                      borderRadius: 8,
                      border: "none",
                      boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
                    }}
                  />
                  <defs>
                    <linearGradient id="velocityGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <Area
                    type="monotone"
                    dataKey="points"
                    stroke="#6366f1"
                    strokeWidth={2}
                    fill="url(#velocityGradient)"
                    animationDuration={300}
                  />
                  {showRollingAverage && rollingAverage && (
                    <ReferenceLine
                      y={rollingAverage}
                      stroke="#f59e0b"
                      strokeDasharray="3 3"
                      label={{
                        value: `3-Sprint Avg: ${rollingAverage} pts`,
                        fill: "#f59e0b",
                        fontSize: 12,
                      }}
                    />
                  )}
                </AreaChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      </motion.div>
    </AnimatePresence>
  );
};
