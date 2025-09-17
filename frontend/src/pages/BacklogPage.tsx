import React, { useState, useCallback, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useWorkItems } from '../hooks/useWorkItems'
import {
  CreateWorkItemRequest,
  UpdateWorkItemRequest,
  WorkItem,
  WorkItemFilters,
  WorkItemSort,
} from '../types/workItem.types'

// Components
import BacklogList from '../components/common/BacklogList'
import FilterControls from '../components/common/FilterControls'
import SortControls from '../components/common/SortControls'
import ViewModeToggle, { ViewMode } from '../components/common/ViewModeToggle'
import Pagination from '../components/common/Pagination'
import WorkItemForm from '../components/common/WorkItemForm'

import { Button } from '../components/ui/button'
import { Card } from '../components/ui/card'
import { Alert, AlertDescription } from '../components/ui/alert'
import {
  PlusIcon,
  ExclamationTriangleIcon,
  RefreshCwIcon,
} from '@heroicons/react/24/outline'

export const BacklogPage: React.FC = () => {
  const { teamId } = useParams<{ teamId: string }>()

  // State for UI controls
  const [viewMode, setViewMode] = useState<ViewMode>(ViewMode.LIST)
  const [selectedWorkItem, setSelectedWorkItem] = useState<WorkItem | null>(
    null
  )
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Use the work items hook
  const {
    workItems,
    loading,
    error,
    hasMore,
    totalCount,
    filters,
    sort,
    pagination,
    setFilters,
    setSort,
    setPagination,
    loadWorkItems,
    refreshWorkItems,
    createWorkItem,
    updateWorkItem,
    deleteWorkItem,
  } = useWorkItems(teamId || '')

  // Load work items on mount
  useEffect(() => {
    if (teamId) {
      loadWorkItems()
    }
  }, [teamId, loadWorkItems])

  // Event handlers
  const handleCreateClick = useCallback(() => {
    setSelectedWorkItem(null)
    setIsFormOpen(true)
  }, [])

  const handleEditWorkItem = useCallback((workItem: WorkItem) => {
    setSelectedWorkItem(workItem)
    setIsFormOpen(true)
  }, [])

  const handleDeleteWorkItem = useCallback(
    async (workItemId: string) => {
      if (window.confirm('Are you sure you want to delete this work item?')) {
        try {
          await deleteWorkItem(workItemId)
        } catch (error) {
          console.error('Failed to delete work item:', error)
          // Error handling can be improved with toast notifications
        }
      }
    },
    [deleteWorkItem]
  )

  const handleFormSubmit = useCallback(
    async (data: CreateWorkItemRequest | UpdateWorkItemRequest) => {
      if (!teamId) return

      setIsSubmitting(true)
      try {
        if (selectedWorkItem) {
          // Update existing work item
          await updateWorkItem(
            selectedWorkItem.id,
            data as UpdateWorkItemRequest
          )
        } else {
          // Create new work item
          await createWorkItem(data as CreateWorkItemRequest)
        }
        setIsFormOpen(false)
        setSelectedWorkItem(null)
      } catch (error) {
        console.error('Failed to save work item:', error)
        // Error handling can be improved with toast notifications
      } finally {
        setIsSubmitting(false)
      }
    },
    [teamId, selectedWorkItem, createWorkItem, updateWorkItem]
  )

  const handleFormClose = useCallback(() => {
    if (!isSubmitting) {
      setIsFormOpen(false)
      setSelectedWorkItem(null)
    }
  }, [isSubmitting])

  const handleFiltersChange = useCallback(
    (newFilters: WorkItemFilters) => {
      setFilters(newFilters)
      // Reset to first page when filters change
      setPagination((prev) => ({ ...prev, page: 1 }))
    },
    [setFilters, setPagination]
  )

  const handleClearFilters = useCallback(() => {
    setFilters({})
    setPagination((prev) => ({ ...prev, page: 1 }))
  }, [setFilters, setPagination])

  const handleSortChange = useCallback(
    (newSort: WorkItemSort) => {
      setSort(newSort)
      // Reset to first page when sort changes
      setPagination((prev) => ({ ...prev, page: 1 }))
    },
    [setSort, setPagination]
  )

  const handlePageChange = useCallback(
    (page: number) => {
      setPagination((prev) => ({ ...prev, page }))
    },
    [setPagination]
  )

  const handleItemsPerPageChange = useCallback(
    (size: number) => {
      setPagination((prev) => ({
        ...prev,
        size,
        page: 1, // Reset to first page when page size changes
      }))
    },
    [setPagination]
  )

  const handleLoadMore = useCallback(() => {
    if (!loading && hasMore) {
      setPagination((prev) => ({ ...prev, page: prev.page + 1 }))
    }
  }, [loading, hasMore, setPagination])

  const handleRefresh = useCallback(() => {
    refreshWorkItems()
  }, [refreshWorkItems])

  // Don't render if no team ID
  if (!teamId) {
    return (
      <div className="container mx-auto px-6 py-8">
        <Alert>
          <ExclamationTriangleIcon className="w-4 h-4" />
          <AlertDescription>
            No team ID provided. Please navigate from a valid team context.
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-6 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Team Backlog</h1>
          <p className="text-gray-600 mt-1">
            Manage and prioritize your team's work items
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            onClick={handleRefresh}
            variant="outline"
            disabled={loading}
            className="flex items-center gap-2"
          >
            <RefreshCwIcon
              className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`}
            />
            Refresh
          </Button>

          <Button
            onClick={handleCreateClick}
            className="flex items-center gap-2"
          >
            <PlusIcon className="w-4 h-4" />
            Add Work Item
          </Button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <ExclamationTriangleIcon className="w-4 h-4" />
          <AlertDescription>
            {error instanceof Error
              ? error.message
              : 'An error occurred while loading work items'}
          </AlertDescription>
        </Alert>
      )}

      {/* Controls */}
      <Card className="p-6">
        <div className="space-y-4">
          {/* View Mode and Sort Controls */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <ViewModeToggle
              viewMode={viewMode}
              onViewModeChange={setViewMode}
            />

            <SortControls sort={sort} onSortChange={handleSortChange} />
          </div>

          {/* Filters */}
          <FilterControls
            filters={filters}
            onFiltersChange={handleFiltersChange}
            onClearFilters={handleClearFilters}
          />
        </div>
      </Card>

      {/* Work Items List */}
      <div className="space-y-4">
        {viewMode === ViewMode.LIST && (
          <BacklogList
            workItems={workItems}
            loading={loading}
            hasMore={hasMore}
            onLoadMore={handleLoadMore}
            onEdit={handleEditWorkItem}
            onDelete={handleDeleteWorkItem}
            onRefresh={handleRefresh}
            showMoveButtons={false}
            emptyMessage="No work items found"
            emptyDescription="Start by creating your first work item or adjust your search filters."
          />
        )}

        {/* TODO: Implement Kanban and Table views */}
        {viewMode === ViewMode.KANBAN && (
          <div className="text-center py-12 text-gray-500">
            <div className="text-6xl mb-4">🔧</div>
            <h3 className="text-lg font-semibold mb-2">
              Kanban View Coming Soon
            </h3>
            <p>
              This view is under development and will be available in a future
              release.
            </p>
          </div>
        )}

        {viewMode === ViewMode.TABLE && (
          <div className="text-center py-12 text-gray-500">
            <div className="text-6xl mb-4">📊</div>
            <h3 className="text-lg font-semibold mb-2">
              Table View Coming Soon
            </h3>
            <p>
              This view is under development and will be available in a future
              release.
            </p>
          </div>
        )}
      </div>

      {/* Pagination */}
      {viewMode === ViewMode.LIST && totalCount > 0 && (
        <Pagination
          currentPage={pagination.page}
          totalItems={totalCount}
          itemsPerPage={pagination.size}
          onPageChange={handlePageChange}
          onItemsPerPageChange={handleItemsPerPageChange}
        />
      )}

      {/* Work Item Form Dialog */}
      <WorkItemForm
        workItem={selectedWorkItem}
        isOpen={isFormOpen}
        onClose={handleFormClose}
        onSubmit={handleFormSubmit}
        isSubmitting={isSubmitting}
        teamId={teamId}
      />
    </div>
  )
}

export default BacklogPage
