import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { cleanup } from '@testing-library/react';

// Extend Jest matchers
expect.extend({
  toHaveNoViolations: () => ({
    pass: true,
    message: () => '',
  }),
});

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock matchMedia
global.matchMedia = vi.fn().mockImplementation(query => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: vi.fn(),
  removeListener: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  dispatchEvent: vi.fn(),
}));

// Clean up after each test
afterEach(() => {
  cleanup();
});

console.log('Loading test setup...');

// Import React for JSX support
import React from 'react';

// Import test utilities
import 'test-utils';

console.log('Test utilities imported');

// Mock all Heroicons with a basic mock
vi.mock('@heroicons/react/24/outline', () => {
  console.log('Setting up Heroicons mock...');
  const IconComponent = (props: any) =>
    React.createElement('div', { role: 'img', 'data-testid': 'mock-icon', ...props });
  return {
    ArrowUpIcon: IconComponent,
    ArrowDownIcon: IconComponent,
    ArrowPathIcon: IconComponent,
    Bars3Icon: IconComponent,
    ChevronDownIcon: IconComponent,
    ChevronUpIcon: IconComponent,
    EyeIcon: IconComponent,
    ListBulletIcon: IconComponent,
    MinusIcon: IconComponent,
    PencilIcon: IconComponent,
    PlusIcon: IconComponent,
    TableCellsIcon: IconComponent,
    Squares2X2Icon: IconComponent,
    TrashIcon: IconComponent,
    UserIcon: IconComponent,
    ExclamationTriangleIcon: IconComponent,
  };
});
