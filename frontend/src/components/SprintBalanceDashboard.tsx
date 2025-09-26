import React, { useMemo } from 'react'
import { Chart } from 'react-chartjs-2'
import { Card, CardHeader, CardContent } from '@/components/ui/card'
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { RefreshCw, AlertTriangle, CheckCircle } from 'lucide-react'
import { useSprintBalance } from '@/hooks/useSprintBalance'

interface SprintBalanceDashboardProps {
  sprintId: string
  refreshInterval?: number
}

export const SprintBalanceDashboard: React.FC<SprintBalanceDashboardProps> = ({
  sprintId,
  refreshInterval,
}) => {
  const { balanceMetrics, isLoading, isError, error, refreshBalance } =
    useSprintBalance(sprintId, { refreshInterval })

  const chartData = useMemo(() => {
    if (!balanceMetrics?.workloadDistribution) return null

    const data = Object.entries(balanceMetrics.workloadDistribution)
    return {
      labels: data.map(([member]) => member),
      datasets: [
        {
          label: 'Workload (hours)',
          data: data.map(([_, hours]) => hours),
          backgroundColor: 'rgba(59, 130, 246, 0.5)',
          borderColor: 'rgb(59, 130, 246)',
          borderWidth: 1,
        },
      ],
    }
  }, [balanceMetrics?.workloadDistribution])

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Team Workload Distribution',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Hours',
        },
      },
    },
  }

  const getStatusColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-500'
    if (score >= 0.6) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-[300px] w-full" />
        <div className="grid grid-cols-3 gap-4">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>
          Failed to load sprint balance data. {error?.message}
        </AlertDescription>
      </Alert>
    )
  }

  if (!balanceMetrics) {
    return (
      <Alert>
        <AlertTitle>No Data</AlertTitle>
        <AlertDescription>No sprint balance data available.</AlertDescription>
      </Alert>
    )
  }

  return (
    <div
      className="space-y-6"
      role="region"
      aria-label="Sprint balance analysis dashboard"
    >
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold" id="dashboard-title">
          Sprint Balance Analysis
        </h2>
        <Button
          onClick={() => refreshBalance()}
          size="sm"
          variant="outline"
          aria-label="Refresh balance analysis"
        >
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh
        </Button>
      </div>

      <div
        className="grid grid-cols-1 md:grid-cols-3 gap-4"
        role="list"
        aria-label="Balance metrics overview"
      >
        <Card role="listitem">
          <CardHeader className="pb-2">
            <h3 className="text-sm font-medium">Overall Balance</h3>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <div
                className={`h-8 w-8 rounded-full ${getStatusColor(
                  balanceMetrics.overallBalanceScore
                )}`}
                role="img"
                aria-label={`Balance score: ${Math.round(balanceMetrics.overallBalanceScore * 100)}%`}
              />
              <span className="text-2xl font-bold">
                {Math.round(balanceMetrics.overallBalanceScore * 100)}%
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <h3 className="text-sm font-medium">Team Utilization</h3>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <div
                className={`h-8 w-8 rounded-full ${getStatusColor(
                  balanceMetrics.teamUtilization
                )}`}
              />
              <span className="text-2xl font-bold">
                {Math.round(balanceMetrics.teamUtilization * 100)}%
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <h3 className="text-sm font-medium">Skill Coverage</h3>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <div
                className={`h-8 w-8 rounded-full ${getStatusColor(
                  balanceMetrics.skillCoverage
                )}`}
              />
              <span className="text-2xl font-bold">
                {Math.round(balanceMetrics.skillCoverage * 100)}%
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="h-[300px]">
            {chartData && (
              <div
                role="img"
                aria-label="Bar chart showing workload distribution across team members"
              >
                <Chart
                  type="bar"
                  data={chartData}
                  options={{
                    ...chartOptions,
                    plugins: {
                      ...chartOptions.plugins,
                      accessibility: {
                        enabled: true,
                        announceToScreenReader: true,
                      },
                    },
                  }}
                />
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {balanceMetrics.bottlenecks.length > 0 && (
        <Alert role="alert" aria-atomic="true">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Potential Bottlenecks</AlertTitle>
          <AlertDescription>
            <ul
              className="list-disc list-inside"
              aria-label="List of identified bottlenecks"
            >
              {balanceMetrics.bottlenecks.map((bottleneck, index) => (
                <li key={index}>{bottleneck}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold">Recommendations</h3>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2" aria-label="List of recommendations">
            {balanceMetrics.recommendations.map((recommendation, index) => (
              <li key={index} className="flex items-start space-x-2">
                <CheckCircle
                  className="h-5 w-5 text-green-500 mt-0.5"
                  aria-hidden="true"
                />
                <span>{recommendation}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
