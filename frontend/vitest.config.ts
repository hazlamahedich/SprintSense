/// <reference types="vitest" />
import { defineConfig } from 'vite';
import { resolve } from 'path';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.ts'],
    globals: true,
    include: ['src/**/*.test.{ts,tsx}', 'src/**/__tests__/**/*.{ts,tsx}'],
    exclude: ['node_modules/**', 'tests/e2e/**', 'src/__tests__/test-utils/**'],
    testTimeout: 20000,
    logHeapUsage: true,
    onConsoleLog(log, type) {
      console.log(`[${type}] ${log}`);
      return false;
    },
    coverage: {
      reporter: ['text', 'lcov'],
      exclude: ['node_modules/', 'tests/e2e/**'],
    },
    deps: {
      moduleDirectories: ['node_modules', '__mocks__'],
      inline: [
        '@heroicons/react',
        'test-utils',
        'react-router',
        'react-router-dom'
      ],
    },
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      'test-utils': resolve(__dirname, './src/__mocks__/test-utils.tsx'),
    },
  },
});
