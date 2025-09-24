import { test, expect } from '@playwright/test'
import { SprintStatus } from '@/types/sprint'
import { login } from './helpers/auth'

// Helper functions to format dates for testing
const formatDate = (date: Date) => date.toISOString().split('T')[0]
const today = new Date()
const tomorrow = new Date(today)
tomorrow.setDate(today.getDate() + 1)
const nextWeek = new Date(today)
nextWeek.setDate(today.getDate() + 7)

import { test, expect } from '@playwright/test';
import { login } from './helpers/auth';

test('completes sprint lifecycle', async ({ page }) => {
  test('completes basic lifecycle', async ({ page }) => {
    await login(page)
    await page.goto('/teams/1/sprints')
    await page.waitForSelector('h4:has-text("Sprint Management")')

    await test.step('Create Sprint', async () => {
      await page.click('button[aria-label="Add Sprint"]')
      await page.waitForSelector('div[role="dialog"]')

      await page.fill('input[name="name"]', 'Test Sprint')
      await page.fill('textarea[name="goal"]', 'Test sprint goal')
      await page.fill('input[name="startDate"]', formatDate(today))
      await page.fill('input[name="endDate"]', formatDate(nextWeek))

      await page.click('button:has-text("Create Sprint")')
      await page.waitForSelector('div:has-text("Test Sprint")')

      await expect(page.locator('text=Test Sprint')).toBeVisible()
      await expect(page.locator('text=Test sprint goal')).toBeVisible()
      await expect(page.locator(`text=${formatDate(today)}`)).toBeVisible()
      await expect(page.locator(`text=${formatDate(nextWeek)}`)).toBeVisible()
      await expect(page.locator('text=Future')).toBeVisible()
    })

    await test.step('Activate Sprint', async () => {
      await page.click('button:has-text("Start Sprint")')
      await expect(page.locator('text=Active')).toBeVisible()

      const startButtons = page.locator('button:has-text("Start Sprint")')
      for (const button of await startButtons.all()) {
        await expect(button).toBeDisabled()
      }
    })

    await test.step('Close Sprint', async () => {
      await page.click('button:has-text("Close Sprint")')
      await expect(page.locator('text=Closed')).toBeVisible()

      const startButtons = page.locator('button:has-text("Start Sprint")')
      for (const button of await startButtons.all()) {
        await expect(button).toBeEnabled()
      }
    })
  })

  test('prevents invalid state transitions', async ({ page }) => {
    await login(page)
    await page.goto('/teams/1/sprints')
    await page.waitForSelector('h4:has-text("Sprint Management")')

    await test.step('Create test sprint', async () => {
      await page.click('button[aria-label="Add Sprint"]')
      await page.fill('input[name="name"]', 'Invalid Transition Test')
      await page.fill('input[name="startDate"]', formatDate(today))
      await page.fill('input[name="endDate"]', formatDate(nextWeek))
      await page.click('button:has-text("Create Sprint")')
    })

    await test.step('Attempt invalid transition', async () => {
      await page.evaluate(() => {
        window.fetch = async (url, options) => {
          if (url.includes('/sprints') && options?.method === 'PATCH') {
            const body = JSON.parse(options.body as string)
            if (body.status === SprintStatus.CLOSED) {
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

      await page.click('button:has-text("Start Sprint")')
      await page.click('button:has-text("Close Sprint")')
      await expect(page.locator('text=Invalid state transition')).toBeVisible()
    })
  })

  test('prevents overlapping sprint dates', async ({ page }) => {
    await login(page)
    await page.goto('/teams/1/sprints')
    await page.waitForSelector('h4:has-text("Sprint Management")')

    await test.step('Create first sprint', async () => {
      await page.click('button[aria-label="Add Sprint"]')
      await page.fill('input[name="name"]', 'Sprint 1')
      await page.fill('input[name="startDate"]', formatDate(today))
      await page.fill('input[name="endDate"]', formatDate(nextWeek))
      await page.click('button:has-text("Create Sprint")')
    })

    await test.step('Attempt overlapping sprint', async () => {
      await page.click('button[aria-label="Add Sprint"]')
      await page.fill('input[name="name"]', 'Sprint 2')
      await page.fill('input[name="startDate"]', formatDate(tomorrow))
      await page.fill('input[name="endDate"]', formatDate(nextWeek))
      await page.click('button:has-text("Create Sprint")')

      await expect(page.locator('text=Sprint dates overlap')).toBeVisible()
    })
  })
})
