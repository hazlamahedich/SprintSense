import { Page, expect } from '@playwright/test'
import { login } from './auth'

export async function setupTestTeam(page: Page): Promise<string> {
  // Enable request/response logging
  page.on('request', request => 
    console.log(`>> ${request.method()} ${request.url()}`))
  page.on('response', response => 
    console.log(`<< ${response.status()} ${response.url()}`))

  // Login first
  await login(page)

  // Navigate to dashboard and wait for content
  await page.goto('/dashboard')
  await page.waitForLoadState('networkidle')
  await expect(
    page.getByRole('heading', { name: 'SprintSense Dashboard' })
  ).toBeVisible({ timeout: 30000 })

  // Create team
  await page.getByRole('button', { name: 'Create New Team' }).click()
  await page.waitForLoadState('networkidle')
  
  const teamName = `Test Team ${Date.now()}`
  await page.getByLabel('Team Name').fill(teamName)

  // Click create and wait for navigation
  const createButton = page.getByRole('button', { name: /Create Team$/ })
  await expect(createButton).toBeEnabled()
  await createButton.click()

  // Wait for success UI feedback
  await expect(
    page.getByText('Team Created Successfully!', { exact: true })
  ).toBeVisible({ timeout: 10000 })

  // Wait for navigation and get team ID
  await page.waitForURL('**/teams/**', { timeout: 10000 })
  const teamId = page.url().split('/').pop()
  
  if (!teamId) {
    throw new Error('Failed to obtain teamId from URL')
  }

  // Verify we landed on team dashboard
  await expect(
    page.getByRole('heading', { name: new RegExp(teamName, 'i') })
  ).toBeVisible({ timeout: 10000 })

  return teamId
}

export async function cleanupTestData() {
  // UI-based tests; rely on a clean DB between runs
}
