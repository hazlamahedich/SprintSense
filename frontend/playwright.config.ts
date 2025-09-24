import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  globalSetup: './tests/e2e/global-setup.ts',
  // Load test environment variables
  env: {
    NODE_ENV: 'test',
  },

  // Increase timeouts
  timeout: 60000,
  expect: {
    timeout: 30000,
  },
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5175',
    trace: 'retain-on-failure',  // Save trace for failed tests
    screenshot: 'only-on-failure', // Save screenshot for failed tests
    video: 'retain-on-failure',    // Save video for failed tests
    actionTimeout: 30000,
    navigationTimeout: 30000,
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,
    contextOptions: {},
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  // Using existing dev server
  // webServer: {
  //   command: 'npm run dev',
  //   url: 'http://localhost:5175',
  //   reuseExistingServer: !process.env.CI,
  //   timeout: 60000,
  // },
  reporter: [
    ['html'],
    ['list']
  ],
  testDir: './tests/e2e',
  retries: process.env.CI ? 2 : 1,
})
