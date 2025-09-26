import React from 'react'
import { Button } from '../../ui/button'
import { Edit, Loader2 } from 'lucide-react'

interface EditWorkItemButtonProps {
  onClick: () => void
  isDisabled?: boolean
  isLoading?: boolean
  variant?: 'default' | 'ghost' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  ariaLabel?: string
}

export const EditWorkItemButton: React.FC<EditWorkItemButtonProps> = ({
  onClick,
  isDisabled = false,
  isLoading = false,
  variant = 'outline',
  size = 'sm',
  ariaLabel = 'Edit work item',
}) => {
  return (
    <Button
      variant={variant}
      size={size}
      onClick={onClick}
      disabled={isDisabled || isLoading}
      aria-label={ariaLabel}
      className={`
        transition-all duration-200
        ${
          variant === 'ghost'
            ? 'hover:bg-blue-50 hover:text-blue-700 text-gray-600'
            : 'hover:bg-blue-50 hover:border-blue-300'
        }
        ${isDisabled ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'}
      `}
    >
      {isLoading ? (
        <>
          <Loader2 className="h-4 w-4 animate-spin mr-1" />
          <span className="sr-only">Loading</span>
        </>
      ) : (
        <>
          <Edit className="h-4 w-4" />
          <span className="sr-only md:not-sr-only md:ml-1">Edit</span>
        </>
      )}
    </Button>
  )
}

export default EditWorkItemButton

