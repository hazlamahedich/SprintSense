import React, { useEffect, useState, useCallback } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Alert,
  CircularProgress,
  Grid,
  Container,
} from '@mui/material'
import { Refresh as RefreshIcon, CheckCircle, Error } from '@mui/icons-material'
import { healthApi } from '../services/api'
import { useAppStore } from '../store/appStore'

interface HealthStatus {
  status: string
  service: string
  database?: string
  version?: string
  lastChecked?: Date
}

export const HealthPage: React.FC = () => {
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null)
  const [detailedHealth, setDetailedHealth] = useState<HealthStatus | null>(
    null
  )
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { setHealthStatus: setGlobalHealthStatus } = useAppStore()

  const checkBasicHealth = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const data = await healthApi.checkHealth()
      const status = { ...data, lastChecked: new Date() }

      setHealthStatus(status)
      setGlobalHealthStatus(status)
    } catch (err) {
      const errorMsg = (err as Error)?.message || 'Health check failed'
      setError(errorMsg)
      setHealthStatus(null)
    } finally {
      setLoading(false)
    }
  }, [setGlobalHealthStatus])

  const checkDetailedHealth = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const data = await healthApi.checkDetailedHealth()
      const status = { ...data, lastChecked: new Date() }

      setDetailedHealth(status)
    } catch (err) {
      const errorMsg = (err as Error)?.message || 'Detailed health check failed'
      setError(errorMsg)
      setDetailedHealth(null)
    } finally {
      setLoading(false)
    }
  }, [])

  const checkAllHealth = useCallback(async () => {
    await Promise.all([checkBasicHealth(), checkDetailedHealth()])
  }, [checkBasicHealth, checkDetailedHealth])

  useEffect(() => {
    checkAllHealth()
  }, [checkAllHealth])

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          SprintSense Health Check
        </Typography>

        <Box sx={{ mb: 3 }}>
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={checkAllHealth}
            disabled={loading}
          >
            {loading ? 'Checking...' : 'Refresh Status'}
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Basic Health Status */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" component="h2">
                    Basic Health Status
                  </Typography>
                  {loading && <CircularProgress size={20} sx={{ ml: 2 }} />}
                </Box>

                {healthStatus ? (
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <CheckCircle color="success" sx={{ mr: 1 }} />
                      <Chip
                        label={healthStatus.status}
                        color={
                          healthStatus.status === 'OK' ? 'success' : 'error'
                        }
                        variant="outlined"
                      />
                    </Box>

                    <Typography variant="body1" sx={{ mb: 1 }}>
                      <strong>Service:</strong> {healthStatus.service}
                    </Typography>

                    {healthStatus.lastChecked && (
                      <Typography variant="body2" color="text.secondary">
                        Last checked:{' '}
                        {healthStatus.lastChecked.toLocaleTimeString()}
                      </Typography>
                    )}
                  </Box>
                ) : (
                  !loading && (
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Error color="error" sx={{ mr: 1 }} />
                      <Typography variant="body1" color="error">
                        Health check failed
                      </Typography>
                    </Box>
                  )
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Detailed Health Status */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" component="h2" sx={{ mb: 2 }}>
                  Detailed Health Status
                </Typography>

                {detailedHealth ? (
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <CheckCircle color="success" sx={{ mr: 1 }} />
                      <Chip
                        label={detailedHealth.status}
                        color={
                          detailedHealth.status === 'OK' ? 'success' : 'error'
                        }
                        variant="outlined"
                      />
                    </Box>

                    <Typography variant="body1" sx={{ mb: 1 }}>
                      <strong>Service:</strong> {detailedHealth.service}
                    </Typography>

                    {detailedHealth.version && (
                      <Typography variant="body1" sx={{ mb: 1 }}>
                        <strong>Version:</strong> {detailedHealth.version}
                      </Typography>
                    )}

                    {detailedHealth.database && (
                      <Typography variant="body1" sx={{ mb: 1 }}>
                        <strong>Database:</strong>
                        <Chip
                          label={detailedHealth.database}
                          color={
                            detailedHealth.database === 'connected'
                              ? 'success'
                              : 'error'
                          }
                          size="small"
                          sx={{ ml: 1 }}
                        />
                      </Typography>
                    )}

                    {detailedHealth.lastChecked && (
                      <Typography variant="body2" color="text.secondary">
                        Last checked:{' '}
                        {detailedHealth.lastChecked.toLocaleTimeString()}
                      </Typography>
                    )}
                  </Box>
                ) : (
                  !loading && (
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Error color="error" sx={{ mr: 1 }} />
                      <Typography variant="body1" color="error">
                        Detailed health check failed
                      </Typography>
                    </Box>
                  )
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Box sx={{ mt: 4, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="body2" color="text.secondary">
            This page demonstrates the connectivity between the frontend and
            backend services. The basic health check tests the API endpoint,
            while the detailed health check also verifies database connectivity.
          </Typography>
        </Box>
      </Box>
    </Container>
  )
}
