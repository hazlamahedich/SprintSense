/** @jsxImportSource react */
import React from 'react';
import { vi } from 'vitest';

console.log('Loading test-utils mocks');

// Mock function for icon components
export const mockIcon = vi.fn(() => <div role="img" />);

// Common interface for component mocks
export interface MockProps {
  children?: React.ReactNode;
  [key: string]: unknown;
}

// Common mock components
export const mockButton = ({ children, ...props }: MockProps) => (
  <button {...props}>{children}</button>
);

export const mockCard = ({ children, ...props }: MockProps) => (
  <div {...props}>{children}</div>
);

export const mockAlert = ({ children, ...props }: MockProps) => (
  <div role="alert" {...props}>
    {children}
  </div>
);

export const mockAlertDescription = ({ children, ...props }: MockProps) => (
  <div {...props}>{children}</div>
);

// Mock data generators
export const createMockWorkItem = (overrides = {}) => ({
  id: '1',
  teamId: 'team-123',
  title: 'Test Item',
  type: 'TASK',
  status: 'NEW',
  priority: 'MEDIUM',
  createdAt: new Date(),
  updatedAt: new Date(),
  ...overrides,
});
