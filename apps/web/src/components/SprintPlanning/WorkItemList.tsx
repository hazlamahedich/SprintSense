import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Skeleton,
  Paper,
} from '@mui/material';

interface Props {
  isLoading: boolean;
}

const mockData = [
  { id: '1', title: 'Implement user authentication', points: 3, assignee: 'John' },
  { id: '2', title: 'Add error handling', points: 5, assignee: 'Sarah' },
  { id: '3', title: 'Create documentation', points: 2, assignee: 'Mike' },
];

export const WorkItemList: React.FC<Props> = ({ isLoading }) => {
  return (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Sprint Work Items
        </Typography>

        <TableContainer component={Paper} variant="outlined">
          <Table aria-label="work items table">
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell align="right">Story Points</TableCell>
                <TableCell>Assignee</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {isLoading
                ? Array.from({ length: 3 }).map((_, index) => (
                    <TableRow key={`skeleton-${index}`}>
                      <TableCell>
                        <Skeleton animation="wave" width="80%" />
                      </TableCell>
                      <TableCell align="right">
                        <Skeleton animation="wave" width={30} />
                      </TableCell>
                      <TableCell>
                        <Skeleton animation="wave" width={100} />
                      </TableCell>
                    </TableRow>
                  ))
                : mockData.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>{item.title}</TableCell>
                      <TableCell align="right">{item.points}</TableCell>
                      <TableCell>{item.assignee}</TableCell>
                    </TableRow>
                  ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
};
