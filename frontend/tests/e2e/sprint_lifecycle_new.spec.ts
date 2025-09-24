import { test, expect } from '@playwright/test'
import { setupTestTeam } from './helpers/setup'

// Test configuration
const testTimeouts = {
  navigation: { timeout: 30000 },
  assertion: { timeout: 15000 },
  action: { timeout: 10000 },
}

// Helper functions to format dates for testing
const formatDate = (date: Date) => date.toISOString().split('T')[0]
const today = new Date()
const tomorrow = new Date(today)
tomorrow.setDate(today.getDate() + 1)
const nextWeek = new Date(today)
nextWeek.setDate(today.getDate() + 7)

test.describe('Sprint Management', () => {
  test.beforeEach(async ({ page }) => {
    // Enable request/response logging for debugging
    page.on('request', (request) =>
      console.log(`>> ${request.method()} ${request.url()}`)
    )
    page.on('response', (response) =>
      console.log(`<< ${response.status()} ${response.url()}`)
    )
  })
  test('completes basic lifecycle', async ({ page }) => {
    const teamId = await setupTestTeam(page)
    await page.goto(`/teams/${teamId}/sprints`)
    await page.waitForLoadState('networkidle')
    await expect(
      page.getByRole('heading', { name: 'Sprint Management' })
    ).toBeVisible(testTimeouts.navigation)

    await test.step('Create Sprint', async () => {
      // Click Add Sprint and wait for dialog
      const addButton = page.getByRole('button', { name: 'Add Sprint' })
      await expect(addButton).toBeEnabled(testTimeouts.assertion)
      await addButton.click()
      await expect(page.getByRole('dialog')).toBeVisible(testTimeouts.assertion)

      // Fill sprint form
      const nameInput = page.getByLabel('Name')
      await expect(nameInput).toBeVisible(testTimeouts.assertion)
      await nameInput.fill('Test Sprint')

      const goalInput = page.getByLabel('Goal')
      await expect(goalInput).toBeVisible(testTimeouts.assertion)
      await goalInput.fill('Test sprint goal')

      const startDateInput = page.getByLabel('Start Date')
      await expect(startDateInput).toBeVisible(testTimeouts.assertion)
      await startDateInput.fill(formatDate(today))

      const endDateInput = page.getByLabel('End Date')
      await expect(endDateInput).toBeVisible(testTimeouts.assertion)
      await endDateInput.fill(formatDate(nextWeek))

      // Submit and wait for completion
      const createButton = page.getByRole('button', { name: 'Create Sprint' })
      await expect(createButton).toBeEnabled(testTimeouts.assertion)
      await createButton.click()
      await page.waitForLoadState('networkidle')

      // Verify sprint details
      await expect(page.getByText('Test Sprint')).toBeVisible(
        testTimeouts.assertion
      )
      await expect(page.getByText('Test sprint goal')).toBeVisible(
        testTimeouts.assertion
      )
      await expect(page.getByText(formatDate(today))).toBeVisible(
        testTimeouts.assertion
      )
      await expect(page.getByText(formatDate(nextWeek))).toBeVisible(
        testTimeouts.assertion
      )
      await expect(page.getByText('Future')).toBeVisible(testTimeouts.assertion)
    })

    await test.step('Activate Sprint', async () => {
      await page.getByRole('button', { name: 'Start Sprint' }).click()
      await expect(page.getByText('Active')).toBeVisible(testTimeouts.assertion)

      // Verify all Start Sprint buttons are disabled
      const startButtons = page.getByRole('button', { name: 'Start Sprint' })
      await expect(startButtons).toBeDisabled(testTimeouts.assertion)
    })

    await test.step('Close Sprint', async () => {
      await page.getByRole('button', { name: 'Close Sprint' }).click()
      await expect(page.getByText('Closed')).toBeVisible(testTimeouts.assertion)

      // Verify Start Sprint buttons are enabled again
      const startButtons = page.getByRole('button', { name: 'Start Sprint' })
      await expect(startButtons).toBeEnabled(testTimeouts.assertion)
    })
  })

  test('prevents invalid state transitions', async ({ page }) => {
    const teamId = await setupTestTeam(page)
    await page.goto(`/teams/${teamId}/sprints`)
    await expect(
      page.getByRole('heading', { name: 'Sprint Management' })
    ).toBeVisible(testTimeouts.navigation)

    await test.step('Create test sprint', async () => {
      await page.getByRole('button', { name: 'Add Sprint' }).click()
      await page.getByLabel('Name').fill('Invalid Transition Test')
      await page.getByLabel('Start Date').fill(formatDate(today))
      await page.getByLabel('End Date').fill(formatDate(nextWeek))
      await page.getByRole('button', { name: 'Create Sprint' }).click()
    })

    await test.step('Attempt invalid transition', async () => {
      await page.evaluate(() => {
        window.fetch = async (url, options) => {
          if (url.includes('/sprints') && options?.method === 'PATCH') {
            const body = JSON.parse(options.body as string)
            if (body.status === 'closed') {
              return new Response(
                JSON.stringify({
                  detail: 'Invalid state transition from future to closed',
                }),
                { status: 400 }
              )
            }
          }
          return new Response()
        }
      })

      await page.getByRole('button', { name: 'Start Sprint' }).click()
      await page.getByRole('button', { name: 'Close Sprint' }).click()
      await expect(page.getByText('Invalid state transition')).toBeVisible(
        testTimeouts.assertion
      )
    })
  })

  test('prevents overlapping sprint dates', async ({ page }) => {
    const teamId = await setupTestTeam(page)
    await page.goto(`/teams/${teamId}/sprints`)
    await expect(
      page.getByRole('heading', { name: 'Sprint Management' })
    ).toBeVisible(testTimeouts.navigation)

    await test.step('Create first sprint', async () => {
      await page.getByRole('button', { name: 'Add Sprint' }).click()
      await page.getByLabel('Name').fill('Sprint 1')
      await page.getByLabel('Start Date').fill(formatDate(today))
      await page.getByLabel('End Date').fill(formatDate(nextWeek))
      await page.getByRole('button', { name: 'Create Sprint' }).click()
    })

    await test.step('Attempt overlapping sprint', async () => {
      await page.getByRole('button', { name: 'Add Sprint' }).click()
      await page.getByLabel('Name').fill('Sprint 2')
      await page.getByLabel('Start Date').fill(formatDate(tomorrow))
      await page.getByLabel('End Date').fill(formatDate(nextWeek))
      await page.getByRole('button', { name: 'Create Sprint' }).click()

      await expect(page.getByText('Sprint dates overlap')).toBeVisible(
        testTimeouts.assertion
      )
    })
  })
})
