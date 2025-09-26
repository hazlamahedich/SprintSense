import React from 'react';
import { useDrag } from 'react-dnd';
import { ListItem, ListItemText, Paper } from '@mui/material';
import type { WorkItem } from '../../types';

interface Props {
  item: WorkItem;
}

export const DraggableWorkItem: React.FC<Props> = ({ item }) => {
  const [{ isDragging }, drag] = useDrag({
    type: 'WORK_ITEM',
    item: { id: item.id },
    collect: monitor => ({
      isDragging: monitor.isDragging(),
    }),
  });

  return (
    <Paper
      ref={drag}
      elevation={isDragging ? 3 : 1}
      sx={{
        my: 1,
        cursor: 'grab',
        opacity: isDragging ? 0.5 : 1,
        transition: 'all 0.2s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
        },
      }}
    >
      <ListItem>
        <ListItemText
          primary={item.title}
          secondary={`Story Points: ${item.storyPoints}`}
        />
      </ListItem>
    </Paper>
  );
};
