import React from 'react';

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  loading?: boolean;
}

const Skeleton = React.forwardRef<HTMLDivElement, SkeletonProps>(
  ({ className, loading = true, children, ...props }, ref) => {
    if (!loading) {
      return <>{children}</>;
    }

    return (
      <div
        ref={ref}
        className={`animate-pulse rounded-md bg-gray-200 ${className || ''}`}
        {...props}
      />
    );
  }
);

Skeleton.displayName = 'Skeleton';

export { Skeleton };
