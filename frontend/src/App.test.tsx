import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import App from './App'

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

describe('App', () => {
  it('renders health page by default', async () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    )

    // Check if the health check title is rendered
    expect(
      await screen.findByText('SprintSense Health Check')
    ).toBeInTheDocument()
  })

  it('renders health page when navigating to /health', async () => {
    render(
      <MemoryRouter initialEntries={['/health']}>
        <App />
      </MemoryRouter>
    )

    expect(
      await screen.findByText('SprintSense Health Check')
    ).toBeInTheDocument()
    expect(screen.getByText('Basic Health Status')).toBeInTheDocument()
    expect(screen.getByText('Detailed Health Status')).toBeInTheDocument()
  })
})
