import { vi } from 'vitest';
import React from 'react';
import '@testing-library/jest-dom';

// Create the mock icon component
const createMockIcon = (name: string) => {
  const MockIcon: React.FC<{ className?: string }> = ({ className }) => {
    return React.createElement('svg', {
      'data-testid': `heroicon-${name}`,
      className,
      fill: 'none',
      viewBox: '0 0 24 24',
      stroke: 'currentColor',
      'stroke-width': '2'
    });
  };
  return MockIcon;
};

// Mock the HeroIcons
vi.mock('@heroicons/react/24/outline', () => ({
  ExclamationTriangleIcon: createMockIcon('exclamation-triangle'),
  TrashIcon: createMockIcon('trash'),
  MinusIcon: createMockIcon('minus'),
  ArrowUpIcon: createMockIcon('arrow-up')
}));

import { vi } from 'vitest';
import '@testing-library/jest-dom';

vi.mock('@heroicons/react/24/outline', async () => {
  const actual = await vi.importActual('@heroicons/react/24/outline') as Record<string, any>;
  return {
    ...actual,
    ExclamationTriangleIcon: vi.fn().mockImplementation(() => {
      return {
        type: 'svg',
        props: {
          'data-testid': 'exclamation-triangle-icon',
          xmlns: 'http://www.w3.org/2000/svg',
          fill: 'none',
          viewBox: '0 0 24 24',
          strokeWidth: 1.5,
          stroke: 'currentColor'
        }
      };
    }),
    TrashIcon: vi.fn().mockImplementation(() => {
      return {
        type: 'svg',
        props: {
          'data-testid': 'trash-icon',
          xmlns: 'http://www.w3.org/2000/svg',
          fill: 'none',
          viewBox: '0 0 24 24',
          strokeWidth: 1.5,
          stroke: 'currentColor'
        }
      };
    }),
    MinusIcon: vi.fn().mockImplementation(() => {
      return {
        type: 'svg',
        props: {
          'data-testid': 'minus-icon',
          xmlns: 'http://www.w3.org/2000/svg',
          fill: 'none',
          viewBox: '0 0 24 24',
          strokeWidth: 1.5,
          stroke: 'currentColor'
        }
      };
    }),
    ArrowUpIcon: vi.fn().mockImplementation(() => {
      return {
        type: 'svg',
        props: {
          'data-testid': 'arrow-up-icon',
          xmlns: 'http://www.w3.org/2000/svg',
          fill: 'none',
          viewBox: '0 0 24 24',
          strokeWidth: 1.5,
          stroke: 'currentColor'
        }
      };
    })
  };
});

import { vi } from 'vitest';
import '@testing-library/jest-dom';

// Create the mock components
const createMockIcon = (testId: string) => {
  const MockIcon = () => {
    return {
      '$$typeof': Symbol.for('react.element'),
      type: 'svg',
      props: {
        'data-testid': testId,
        xmlns: 'http://www.w3.org/2000/svg',
        fill: 'none',
        viewBox: '0 0 24 24',
        strokeWidth: 1.5,
        stroke: 'currentColor'
      }
    };
  };
  return MockIcon;
};

// Mock the HeroIcons
vi.mock('@heroicons/react/24/outline', () => ({
  ExclamationTriangleIcon: createMockIcon('exclamation-triangle-icon'),
  TrashIcon: createMockIcon('trash-icon'),
  MinusIcon: createMockIcon('minus-icon'),
  ArrowUpIcon: createMockIcon('arrow-up-icon')
}));

import React from 'react';
import { SVGProps } from 'react';

const createIcon = (testId: string) => {
  const Icon = (props: SVGProps<SVGSVGElement>) => {
    return React.createElement('svg', {
      ...props,
      'data-testid': testId,
      xmlns: 'http://www.w3.org/2000/svg',
      fill: 'none',
      viewBox: '0 0 24 24',
      strokeWidth: 1.5,
      stroke: 'currentColor'
    });
  };
  return Icon;
};
import '@testing-library/jest-dom';

vi.hoisted(() => { return React }); // Make React available in the mock scope
import { vi } from 'vitest';

// Mock HeroIcons components
vi.mock('@heroicons/react/24/outline', () => ({
  ExclamationTriangleIcon: createIcon('exclamation-triangle-icon'),
  TrashIcon: createIcon('trash-icon'),
  MinusIcon: createIcon('minus-icon'),
  ArrowUpIcon: createIcon('arrow-up-icon')
}));
