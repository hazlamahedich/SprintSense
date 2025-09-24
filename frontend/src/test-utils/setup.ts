import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import matchers from '@testing-library/jest-dom/matchers';
import './mocks';

console.log('Loading test setup...');

expect.extend(matchers);

// Cleanup after each test
afterEach(() => {
  cleanup();
});
