import React from 'react';
import { Typography, Box } from '@mui/material';

interface StatusProps {
  label: string;
  status: string;
  variant?: 'success' | 'warning' | 'error' | 'info';
}

export const StatusIndicator: React.FC<StatusProps> = ({
  label,
  status,
  variant = 'info'
}) => {
  const getColor = () => {
    switch (variant) {
      case 'success':
        return 'rgb(46, 125, 50)';
      case 'warning':
        return 'rgb(237, 108, 2)';
      case 'error':
        return 'rgb(211, 47, 47)';
      default:
        return 'rgb(25, 118, 210)';
    }
  };

  return (
    <Box display="flex" alignItems="center" gap={1}>
      <Typography component="div" variant="body2">
        {label}:
      </Typography>
      <Box
        component="div"
        sx={{
          display: 'inline-flex',
          alignItems: 'center',
          backgroundColor: `${getColor()}20`,
          color: getColor(),
          borderRadius: 1,
          px: 1,
          py: 0.5,
          fontSize: '0.875rem',
          lineHeight: 1,
        }}
      >
        {status}
      </Box>
    </Box>
  );
};
