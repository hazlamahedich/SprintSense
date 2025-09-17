import React, { useMemo } from 'react';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  ChevronDoubleLeftIcon,
  ChevronDoubleRightIcon
} from '@heroicons/react/24/outline';

interface PaginationProps {
  currentPage: number;
  totalItems: number;
  itemsPerPage: number;
  onPageChange: (page: number) => void;
  onItemsPerPageChange: (itemsPerPage: number) => void;
  className?: string;
  showItemsPerPage?: boolean;
  showPageSizeSelector?: boolean;
  maxVisiblePages?: number;
}

const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalItems,
  itemsPerPage,
  onPageChange,
  onItemsPerPageChange,
  className = '',
  showItemsPerPage = true,
  showPageSizeSelector = true,
  maxVisiblePages = 5
}) => {
  const totalPages = useMemo(() => Math.ceil(totalItems / itemsPerPage), [totalItems, itemsPerPage]);

  const startItem = useMemo(() =>
    totalItems === 0 ? 0 : (currentPage - 1) * itemsPerPage + 1
  , [currentPage, itemsPerPage, totalItems]);

  const endItem = useMemo(() =>
    Math.min(currentPage * itemsPerPage, totalItems)
  , [currentPage, itemsPerPage, totalItems]);

  // Generate visible page numbers
  const visiblePages = useMemo(() => {
    if (totalPages <= maxVisiblePages) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }

    const half = Math.floor(maxVisiblePages / 2);
    let start = Math.max(1, currentPage - half);
    let end = Math.min(totalPages, start + maxVisiblePages - 1);

    // Adjust start if we're near the end
    if (end - start + 1 < maxVisiblePages) {
      start = Math.max(1, end - maxVisiblePages + 1);
    }

    return Array.from({ length: end - start + 1 }, (_, i) => start + i);
  }, [currentPage, totalPages, maxVisiblePages]);

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages && page !== currentPage) {
      onPageChange(page);
    }
  };

  const handleItemsPerPageChange = (value: string) => {
    const newItemsPerPage = parseInt(value, 10);
    if (newItemsPerPage !== itemsPerPage) {
      onItemsPerPageChange(newItemsPerPage);
    }
  };

  // Don't render pagination if there are no items
  if (totalItems === 0) {
    return null;
  }

  return (
    <div className={`flex flex-col sm:flex-row items-center justify-between gap-4 ${className}`}>
      {/* Items Info */}
      {showItemsPerPage && (
        <div className="flex items-center gap-4 text-sm text-gray-600">
          <span>
            Showing {startItem.toLocaleString()} to {endItem.toLocaleString()} of{' '}
            {totalItems.toLocaleString()} items
          </span>

          {showPageSizeSelector && (
            <div className="flex items-center gap-2">
              <span>Show:</span>
              <Select
                value={itemsPerPage.toString()}
                onValueChange={handleItemsPerPageChange}
              >
                <SelectTrigger className="w-20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {PAGE_SIZE_OPTIONS.map(size => (
                    <SelectItem key={size} value={size.toString()}>
                      {size}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <span>per page</span>
            </div>
          )}
        </div>
      )}

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex items-center gap-1">
          {/* First Page */}
          <Button
            onClick={() => handlePageChange(1)}
            disabled={currentPage === 1}
            variant="outline"
            size="sm"
            className="p-2"
            title="First page"
          >
            <ChevronDoubleLeftIcon className="w-4 h-4" />
          </Button>

          {/* Previous Page */}
          <Button
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
            variant="outline"
            size="sm"
            className="p-2"
            title="Previous page"
          >
            <ChevronLeftIcon className="w-4 h-4" />
          </Button>

          {/* Page Numbers */}
          <div className="flex items-center gap-1">
            {visiblePages[0] > 1 && (
              <>
                <Button
                  onClick={() => handlePageChange(1)}
                  variant="outline"
                  size="sm"
                  className="min-w-[36px]"
                >
                  1
                </Button>
                {visiblePages[0] > 2 && (
                  <span className="px-2 text-gray-400">...</span>
                )}
              </>
            )}

            {visiblePages.map(page => (
              <Button
                key={page}
                onClick={() => handlePageChange(page)}
                variant={page === currentPage ? "default" : "outline"}
                size="sm"
                className="min-w-[36px]"
              >
                {page}
              </Button>
            ))}

            {visiblePages[visiblePages.length - 1] < totalPages && (
              <>
                {visiblePages[visiblePages.length - 1] < totalPages - 1 && (
                  <span className="px-2 text-gray-400">...</span>
                )}
                <Button
                  onClick={() => handlePageChange(totalPages)}
                  variant="outline"
                  size="sm"
                  className="min-w-[36px]"
                >
                  {totalPages}
                </Button>
              </>
            )}
          </div>

          {/* Next Page */}
          <Button
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            variant="outline"
            size="sm"
            className="p-2"
            title="Next page"
          >
            <ChevronRightIcon className="w-4 h-4" />
          </Button>

          {/* Last Page */}
          <Button
            onClick={() => handlePageChange(totalPages)}
            disabled={currentPage === totalPages}
            variant="outline"
            size="sm"
            className="p-2"
            title="Last page"
          >
            <ChevronDoubleRightIcon className="w-4 h-4" />
          </Button>
        </div>
      )}
    </div>
  );
};

export default Pagination;
