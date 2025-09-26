import React, { useState, useCallback, useEffect } from 'react';
import {
  Box,
  Button,
  CircularProgress,
  TextField,
  Typography,
  Alert,
  Snackbar,
  Tooltip
} from '@mui/material';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import { TitleGenerationRequest, TitleGenerationResponse } from '../../domains/llm/title/types';
import { useTitleGeneration } from '../../hooks/useTitleGeneration';

interface TitleGeneratorProps {
  description: string;
  onTitleGenerated?: (title: string) => void;
  onTitleUpdated?: (title: string) => void;
  teamId: string;
  category?: string;
}

export const TitleGenerator: React.FC<TitleGeneratorProps> = ({
  description,
  onTitleGenerated,
  onTitleUpdated,
  teamId,
  category
}) => {
  const [title, setTitle] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const { generateTitle, isLoading } = useTitleGeneration();

  const handleGenerate = useCallback(async () => {
    try {
      setError(null);
      const request: TitleGenerationRequest = {
        description,
        context: {
          teamId,
          category
        },
        options: {
          style: 'concise',
          maxLength: 100
        }
      };

      const response = await generateTitle(request);
      setTitle(response.title);
      onTitleGenerated?.(response.title);
      setSnackbarOpen(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate title');
    }
  }, [description, teamId, category, generateTitle, onTitleGenerated]);

  const handleTitleChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const newTitle = event.target.value;
    setTitle(newTitle);
    onTitleUpdated?.(newTitle);
  }, [onTitleUpdated]);

  useEffect(() => {
    // Clear title when description changes
    setTitle('');
  }, [description]);

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
        width: '100%'
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 2
        }}
      >
        <TextField
          fullWidth
          label="Epic Title"
          value={title}
          onChange={handleTitleChange}
          placeholder="Generate or enter epic title"
          variant="outlined"
          size="medium"
          disabled={isLoading}
          inputProps={{
            'aria-label': 'Epic title input',
            'data-testid': 'epic-title-input'
          }}
        />
        <Tooltip title="Generate title from description">
          <span>
            <Button
              variant="contained"
              onClick={handleGenerate}
              disabled={isLoading || !description}
              startIcon={isLoading ? <CircularProgress size={20} /> : <AutorenewIcon />}
              aria-label="Generate title"
              data-testid="generate-title-button"
            >
              Generate
            </Button>
          </span>
        </Tooltip>
      </Box>

      {error && (
        <Typography
          color="error"
          variant="body2"
          role="alert"
          data-testid="error-message"
        >
          {error}
        </Typography>
      )}

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setSnackbarOpen(false)}
          severity="success"
          sx={{ width: '100%' }}
        >
          Title generated successfully
        </Alert>
      </Snackbar>
    </Box>
  );
};
