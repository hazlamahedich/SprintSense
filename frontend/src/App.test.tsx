import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { Routes, Route, Navigate } from 'react-router-dom'
import { HealthPage } from './pages/HealthPage'

// Mock the health API
vi.mock('./services/api', () => ({
  healthApi: {
    checkHealth: vi.fn().mockResolvedValue({
      status: 'OK',
      service: 'SprintSense Backend',
    }),
    checkDetailedHealth: vi.fn().mockResolvedValue({
      status: 'OK',
      service: 'SprintSense Backend',
      database: 'connected',
      version: '0.1.0',
    }),
  },
}))

// Create the same theme as in App
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    h4: {
      fontWeight: 600,
    },
  },
})

// Test component that wraps routes in a MemoryRouter instead of App
function TestApp({ initialEntries }: { initialEntries: string[] }) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <MemoryRouter initialEntries={initialEntries}>
        <Routes>
          <Route path="/health" element={<HealthPage />} />
          <Route path="/" element={<Navigate to="/health" replace />} />
        </Routes>
      </MemoryRouter>
    </ThemeProvider>
  )
}

describe('App', () => {
  it('renders health page by default', async () => {
    render(<TestApp initialEntries={['/']} />)

    // Check if the health check title is rendered
    expect(
      await screen.findByText('SprintSense Health Check')
    ).toBeInTheDocument()
  })

  it('renders health page when navigating to /health', async () => {
    render(<TestApp initialEntries={['/health']} />)

    expect(
      await screen.findByText('SprintSense Health Check')
    ).toBeInTheDocument()
    expect(screen.getByText('Basic Health Status')).toBeInTheDocument()
    expect(screen.getByText('Detailed Health Status')).toBeInTheDocument()
  })
})
