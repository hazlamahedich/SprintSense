import React, { useEffect, useState, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  CircularProgress,
  Snackbar,
  Alert,
  Typography,
  styled,
  useTheme,
  alpha,
} from '@mui/material';
import { motion } from 'framer-motion';
import {
  CompleteSprintRequest,
  CompleteSprintResponse,
  IncompleteTask,
  MoveType,
} from '../../types/sprint';
import { getIncompleteItems, completeSprint } from '../../api/sprint';

interface Props {
  open: boolean;
  sprintId: string;
  onClose: () => void;
  onCompleted: (result: CompleteSprintResponse) => void;
}

// Styled components for visual flair
const StyledDialog = styled(Dialog)(({ theme }) => ({
  '& .MuiPaper-root': {
    borderRadius: 12,
    boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
  },
}));

const StyledTableRow = styled(TableRow)(({ theme }) => ({
  '&:nth-of-type(odd)': {
    backgroundColor: alpha(theme.palette.primary.main, 0.04),
  },
  transition: 'background-color 0.2s ease',
  '&:hover': {
    backgroundColor: alpha(theme.palette.primary.main, 0.08),
  },
}));

const LoadingWrapper = styled('div')({
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  padding: 32,
});

const ActionButton = styled(Button)(({ theme }) => ({
  minWidth: 160,
  borderRadius: 8,
  textTransform: 'none',
  fontSize: 16,
  padding: '10px 24px',
  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    transform: 'translateY(-1px)',
    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
  },
}));

export const IncompleteWorkDialog: React.FC<Props> = ({
  open,
  sprintId,
  onClose,
  onCompleted,
}) => {
  const theme = useTheme();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [items, setItems] = useState<IncompleteTask[]>([]);
  const [totalPoints, setTotalPoints] = useState(0);

  const loadItems = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getIncompleteItems(sprintId);
      setItems(data);
      setTotalPoints(data.reduce((sum, item) => sum + (item.points || 0), 0));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load incomplete items');
    } finally {
      setLoading(false);
    }
  }, [sprintId]);

  useEffect(() => {
    if (open) {
      loadItems();
    }
  }, [open, loadItems]);

  const handleMove = async (action: MoveType) => {
    try {
      setLoading(true);
      setError(null);
      const payload: CompleteSprintRequest = {
        action,
        item_ids: items.map(i => i.id),
      };
      const result = await completeSprint(sprintId, payload);
      onCompleted(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to move items');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !items.length) {
    return (
      <StyledDialog open={open} onClose={onClose} maxWidth="md" fullWidth>
        <LoadingWrapper>
          <CircularProgress />
        </LoadingWrapper>
      </StyledDialog>
    );
  }

  return (
    <>
      <StyledDialog open={open} onClose={!loading ? onClose : undefined} maxWidth="md" fullWidth>
        <DialogTitle>
          <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }}>
            Handle Incomplete Work
          </Typography>
          <Typography variant="subtitle1" color="text.secondary" sx={{ mt: 1 }}>
            {items.length} incomplete {items.length === 1 ? 'item' : 'items'} ({totalPoints} points)
          </Typography>
        </DialogTitle>

        <DialogContent>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Points</TableCell>
                <TableCell>Assignee</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map(item => (
                <StyledTableRow
                  key={item.id}
                  component={motion.tr}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <TableCell>{item.title}</TableCell>
                  <TableCell>
                    <Typography
                      component="span"
                      sx={{
                        px: 1.5,
                        py: 0.5,
                        borderRadius: 1,
                        fontSize: '0.875rem',
                        backgroundColor:
                          item.status === 'In Progress'
                            ? alpha(theme.palette.warning.main, 0.1)
                            : alpha(theme.palette.info.main, 0.1),
                        color:
                          item.status === 'In Progress'
                            ? theme.palette.warning.dark
                            : theme.palette.info.dark,
                      }}
                    >
                      {item.status}
                    </Typography>
                  </TableCell>
                  <TableCell>{item.points}</TableCell>
                  <TableCell>{item.assignee_name || '-'}</TableCell>
                </StyledTableRow>
              ))}
            </TableBody>
          </Table>
        </DialogContent>

        <DialogActions sx={{ p: 3 }}>
          <ActionButton
            onClick={() => handleMove('backlog')}
            disabled={loading}
            variant="outlined"
            color="primary"
          >
            Move to Backlog
          </ActionButton>
          <ActionButton
            onClick={() => handleMove('next_sprint')}
            disabled={loading}
            variant="contained"
            color="primary"
            endIcon={loading && <CircularProgress size={16} color="inherit" />}
          >
            Move to Next Sprint
          </ActionButton>
        </DialogActions>
      </StyledDialog>

      <Snackbar open={!!error} autoHideDuration={6000} onClose={() => setError(null)}>
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>
    </>
  );
};
