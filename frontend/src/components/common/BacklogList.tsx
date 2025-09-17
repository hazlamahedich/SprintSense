import React, { useCallback, useEffect, useRef } from 'react'
import { WorkItem } from '../../types/workItem.types'
import BacklogItem from './BacklogItem'
import { Button } from '../ui/button'
import { RefreshCwIcon } from '@heroicons/react/24/outline'

interface BacklogListProps {
  workItems: WorkItem[]
  loading: boolean
  hasMore: boolean
  onLoadMore: () => void
  onEdit: (workItem: WorkItem) => void
  onDelete: (id: string) => void
  onMove?: (id: string, direction: 'up' | 'down') => void
  onRefresh?: () => void
  showMoveButtons?: boolean
  className?: string
  emptyMessage?: string
  emptyDescription?: string
}

export const BacklogList: React.FC<BacklogListProps> = ({
  workItems,
  loading,
  hasMore,
  onLoadMore,
  onEdit,
  onDelete,
  onMove,
  onRefresh,
  showMoveButtons = false,
  className = '',
  emptyMessage = 'No work items found',
  emptyDescription = 'Try adjusting your filters or create a new work item to get started.',
}) => {
  const loadMoreRef = useRef<HTMLDivElement>(null)

  // Intersection Observer for infinite scroll
  useEffect(() => {
    if (!hasMore || loading) return

    const observer = new IntersectionObserver(
      (entries) => {
        const first = entries[0]
        if (first.isIntersecting) {
          onLoadMore()
        }
      },
      {
        threshold: 0.1,
        rootMargin: '100px', // Load more items 100px before reaching the bottom
      }
    )

    const currentRef = loadMoreRef.current
    if (currentRef) {
      observer.observe(currentRef)
    }

    return () => {
      if (currentRef) {
        observer.unobserve(currentRef)
      }
    }
  }, [hasMore, loading, onLoadMore])

  const handleRefresh = useCallback(() => {
    onRefresh?.()
  }, [onRefresh])

  // Show empty state when no items and not loading
  if (!loading && workItems.length === 0) {
    return (
      <div
        className={`flex flex-col items-center justify-center py-12 ${className}`}
      >
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">📋</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {emptyMessage}
          </h3>
          <p className="text-gray-600 mb-6">{emptyDescription}</p>
          {onRefresh && (
            <Button
              onClick={handleRefresh}
              variant="outline"
              className="flex items-center gap-2"
            >
              <RefreshCwIcon className="w-4 h-4" />
              Refresh
            </Button>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Work Items List */}
      <div className="space-y-3">
        {workItems.map((workItem, index) => (
          <BacklogItem
            key={workItem.id}
            workItem={workItem}
            onEdit={onEdit}
            onDelete={onDelete}
            onMove={onMove}
            showMoveButtons={showMoveButtons}
            className={`
              ${index === 0 ? 'border-t-2 border-blue-200' : ''}
              animate-in slide-in-from-left-2 duration-200
            `}
          />
        ))}
      </div>

      {/* Loading States */}
      {loading && workItems.length > 0 && (
        <div className="flex justify-center py-8">
          <div className="flex items-center gap-2 text-gray-600">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
            <span className="text-sm">Loading more items...</span>
          </div>
        </div>
      )}

      {loading && workItems.length === 0 && (
        <div className="space-y-3">
          {/* Skeleton loading states */}
          {Array.from({ length: 5 }).map((_, index) => (
            <div key={index} className="border rounded-lg p-4 animate-pulse">
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-2">
                  <div className="h-6 w-16 bg-gray-200 rounded"></div>
                  <div className="h-6 w-20 bg-gray-200 rounded"></div>
                  <div className="h-6 w-16 bg-gray-200 rounded"></div>
                </div>
                <div className="flex gap-1">
                  <div className="h-8 w-8 bg-gray-200 rounded"></div>
                  <div className="h-8 w-8 bg-gray-200 rounded"></div>
                </div>
              </div>
              <div className="space-y-2 mb-3">
                <div className="h-6 bg-gray-200 rounded w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded w-full"></div>
                <div className="h-4 bg-gray-200 rounded w-2/3"></div>
              </div>
              <div className="flex justify-between text-xs">
                <div className="h-4 w-24 bg-gray-200 rounded"></div>
                <div className="h-4 w-32 bg-gray-200 rounded"></div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Load More Trigger */}
      {hasMore && !loading && (
        <div ref={loadMoreRef} className="flex justify-center py-4">
          <Button
            onClick={onLoadMore}
            variant="outline"
            className="flex items-center gap-2"
            disabled={loading}
          >
            Load More
          </Button>
        </div>
      )}

      {/* End of List Message */}
      {!hasMore && workItems.length > 0 && (
        <div className="text-center py-8 text-gray-500 text-sm border-t">
          <div className="flex items-center justify-center gap-2">
            <div className="h-px bg-gray-300 flex-1"></div>
            <span>You've reached the end of the list</span>
            <div className="h-px bg-gray-300 flex-1"></div>
          </div>
          {onRefresh && (
            <Button
              onClick={handleRefresh}
              variant="ghost"
              size="sm"
              className="mt-3 flex items-center gap-2"
            >
              <RefreshCwIcon className="w-4 h-4" />
              Refresh List
            </Button>
          )}
        </div>
      )}
    </div>
  )
}

export default BacklogList
