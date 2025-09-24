import { test, expect } from '@playwright/test'
import { login } from './helpers/auth'

test.describe('Team Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await login(page)
  })

  test('should create a new team and display it correctly', async ({
    page,
  }) => {
    // Verify we're on the dashboard
    await expect(page.getByRole('heading', { name: 'SprintSense Dashboard' })).toBeVisible()

    // Click create team button
    const createButton = page.getByRole('button', { name: 'Create New Team' })
    await createButton.waitFor({ state: 'visible' })
    await createButton.click()

    // Wait for navigation and form to be ready
    await page.waitForURL('**/teams/create')

    // Fill team name
    const teamName = `Test Team ${Date.now()}`
    const teamNameInput = page.getByLabel('Team Name')
    await teamNameInput.waitFor({ state: 'visible' })
    await teamNameInput.fill(teamName)

    // Submit form and wait for response
    const submitButton = page.getByRole('button', { name: /Create Team$/ })
    await submitButton.waitFor({ state: 'visible' })

    const [response] = await Promise.all([
      page.waitForResponse(
        response => response.url().includes('/api/v1/teams') && response.request().method() === 'POST'
      ),
      submitButton.click()
    ])

    // Log response for debugging
    const responseData = await response.json().catch(() => null)
    console.log('Create team response:', {
      status: response.status(),
      data: responseData
    })

    // Handle success or error
    if (response.ok()) {
      await expect(
        page.getByRole('heading', { name: 'Team Created Successfully!' })
      ).toBeVisible({ timeout: 5000 })
    } else {
      const errorAlert = page.locator('.MuiAlert-error')
      await errorAlert.waitFor({ timeout: 5000 })
      const errorText = await errorAlert.textContent()
      throw new Error(`Team creation failed: ${errorText}`)
    }

    // Verify redirect to team dashboard
    await expect(page.url()).toMatch(/\/teams\/[\w-]+$/)

    // Verify team data is displayed correctly
    await expect(page.getByRole('heading', { name: teamName })).toBeVisible()
    await expect(page.getByText('Team Dashboard')).toBeVisible()
    await expect(page.getByText('Team Information')).toBeVisible()

    // Verify team members section
    await expect(page.getByText('Team Management')).toBeVisible()
    await expect(
      page.getByRole('button', { name: 'Invite User' })
    ).toBeVisible()
  })

  test('should persist team data after page refresh', async ({ page }) => {
    // Go to dashboard and wait for load
    await page.goto('/', { waitUntil: 'domcontentloaded' })

    // Create a team
    await page.getByRole('button', { name: 'Create New Team' }).click()

    const teamName = `Persistence Test Team ${Date.now()}`
    await page.getByLabel('Team Name').fill(teamName)

    // Submit and wait for both UI and network updates
    await Promise.all([
      page.waitForResponse(
        (response) =>
          response.url().includes('/api/v1/teams') && response.status() === 201
      ),
      page.getByRole('button', { name: /Create Team$/ }).click(),
    ])

    // Wait for success message and navigation
    await expect(page.getByText('Team Created Successfully!')).toBeVisible({
      timeout: 10000,
    })
    await page.waitForURL('**/teams/*', { timeout: 10000 })

    // Store URL for comparison
    const teamUrl = page.url()

    // Refresh and wait for load
    await page.reload({ waitUntil: 'domcontentloaded' })

    // Wait for the content to load
    await page.waitForLoadState('domcontentloaded')

    // Verify team header with direct selector
    await expect(page.locator('h4', { hasText: teamName })).toBeVisible({
      timeout: 10000,
    })

    // Verify team info sections
    await expect(page.getByText('Team Dashboard')).toBeVisible({
      timeout: 10000,
    })
    await expect(page.getByText('Team Information')).toBeVisible({
      timeout: 10000,
    })

    // Verify URL hasn't changed
    expect(page.url()).toBe(teamUrl)

    // Verify team functionality
    await expect(page.getByText('Invite User')).toBeVisible({ timeout: 10000 })
  })

  test('should handle non-existent team (404)', async ({ page }) => {
    // Try to access non-existent team
    await page.goto('/teams/12345678-1234-5678-1234-567812345678')

    // Verify error message
    await expect(page.getByText('Team not found')).toBeVisible()
    await expect(
      page.getByRole('button', { name: 'Back to Dashboard' })
    ).toBeVisible()
  })

  test('should handle unauthorized team access (403)', async ({
    page,
    browser,
  }) => {
    // First create a team with current user
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await page.getByRole('button', { name: 'Create New Team' }).click()

    const teamName = `Restricted Team ${Date.now()}`
    await page.getByLabel('Team Name').fill(teamName)

    // Submit and wait for response
    await Promise.all([
      page.waitForResponse(
        (response) =>
          response.url().includes('/api/v1/teams') && response.status() === 201
      ),
      page.getByRole('button', { name: /Create Team$/ }).click(),
    ])

    // Wait for success and navigation
    await expect(page.getByText('Team Created Successfully!')).toBeVisible({
      timeout: 10000,
    })
    await page.waitForURL('**/teams/*', { timeout: 10000 })

    // Get team ID
    const teamId = page.url().split('/').pop()

    // Create new browser context for different user
    const otherContext = await browser.newContext()
    const otherPage = await otherContext.newPage()

    try {
      // Login as different user
      await login(otherPage, 'other@example.com', 'password123')

      // Try to access team page
      await otherPage.goto(`/teams/${teamId}`)

      // Wait for and verify error message
      await expect(otherPage.locator('.MuiAlert-message')).toContainText(
        'You do not have permission to view this team',
        {
          timeout: 10000,
        }
      )

      // Verify back button
      await expect(otherPage.getByText('Back to Dashboard')).toBeVisible({
        timeout: 10000,
      })
    } finally {
      await otherContext.close()
    }
  })

  test('should handle network errors gracefully', async ({ page, context }) => {
    // Create a team first
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await page.getByRole('button', { name: 'Create New Team' }).click()

    const teamName = `Network Test Team ${Date.now()}`
    await page.getByLabel('Team Name').fill(teamName)

    // Submit and wait for response
    await Promise.all([
      page.waitForResponse(
        (response) =>
          response.url().includes('/api/v1/teams') && response.status() === 201
      ),
      page.getByRole('button', { name: /Create Team$/ }).click(),
    ])

    // Wait for success and navigation
    await expect(page.getByText('Team Created Successfully!')).toBeVisible({
      timeout: 10000,
    })
    await page.waitForURL('**/teams/*', { timeout: 10000 })

    // Get team ID
    const teamId = page.url().split('/').pop()

    // Mock API error with proper error response
    await context.route(`**/api/v1/teams/${teamId}`, (route) =>
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Internal Server Error',
          message: 'Failed to load team. Please try again.',
          code: 'INTERNAL_ERROR',
        }),
      })
    )

    // Refresh and wait for error state
    await page.reload({ waitUntil: 'domcontentloaded' })

    // Wait for and verify error message
    await expect(page.locator('.MuiAlert-message')).toContainText(
      'Failed to load team. Please try again.',
      {
        timeout: 10000,
      }
    )

    // Verify back button
    await expect(page.getByText('Back to Dashboard')).toBeVisible({
      timeout: 10000,
    })
  })
})
