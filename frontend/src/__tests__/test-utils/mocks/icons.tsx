import React from 'react';
import { vi } from 'vitest';

const MockIcon = ({ testId = 'mock-icon' }: { testId?: string }) => (
  <svg data-testid={testId} />
);

vi.mock('@heroicons/react/24/outline', () => ({
  XMarkIcon: () => <MockIcon testId="xmark-icon" />,
  ChevronDownIcon: () => <MockIcon testId="chevron-down-icon" />,
}));

vi.mock('lucide-react', () => ({
  Check: () => <MockIcon testId="check-icon" />,
  ChevronDown: () => <MockIcon testId="chevron-down-icon" />,
}));
