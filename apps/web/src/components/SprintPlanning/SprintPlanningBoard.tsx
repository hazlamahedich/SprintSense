import React, { useContext } from 'react';
import { Box, Typography, List, Paper } from '@mui/material';
import { useDrop } from 'react-dnd';
import { DraggableWorkItem } from './DraggableWorkItem';
import { SimulationContext } from '../../contexts/SimulationContext';
import type { WorkItem } from '../../types';

export const SprintPlanningBoard: React.FC = () => {
  const { items = [], updateItems } = useContext(SimulationContext);

  const [{ isOver }, drop] = useDrop({
    accept: 'WORK_ITEM',
    drop: (droppedItem: { id: string }) => {
      if (!items.some(item => item.id === droppedItem.id)) {
        const item = items.find(i => i.id === droppedItem.id);
        if (item) {
          updateItems([...items, item]);
        }
      }
    },
    collect: monitor => ({
      isOver: monitor.isOver(),
    }),
  });

  return (
    <Box
      ref={drop}
      sx={{
        p: 2,
        minHeight: '400px',
        backgroundColor: isOver ? 'action.hover' : 'background.paper',
        transition: 'background-color 0.2s ease',
      }}
    >
      <Typography variant="h6" gutterBottom>
        Sprint Plan
      </Typography>
      <List>
        {items.map((item: WorkItem) => (
          <DraggableWorkItem key={item.id} item={item} />
        ))}
      </List>
    </Box>
  );
};
