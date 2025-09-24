import { test, expect } from '@playwright/test'
import { loginAsTeamMember } from './helpers/auth'

test.describe('Work Item Sprint Assignment', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsTeamMember(page)
    await page.goto('/work-items')
  })

  test('can assign work item to a future sprint', async ({ page }) => {
    // Create a test work item
    const workItemTitle = `Test Item ${Date.now()}`
    await page.click('button:has-text("New Work Item")')
    await page.fill('input[placeholder="Enter title"]', workItemTitle)
    await page.click('button:has-text("Create")')

    // Wait for the work item to be created
    await expect(page.locator(`text=${workItemTitle}`)).toBeVisible()

    // Open sprint assignment dropdown
    const workItemCard = page
      .locator(`div:has-text("${workItemTitle}")`)
      .first()
    await workItemCard.click()

    const sprintSelect = workItemCard.locator('select#sprint-select')
    await expect(sprintSelect).toBeVisible()

    // Select a future sprint
    await sprintSelect.selectOption({ label: /Sprint \d+ \(Future\)/ })

    // Wait for success message
    await expect(
      page.locator('text=Work item assigned to sprint')
    ).toBeVisible()

    // Verify real-time update
    const otherBrowser = await page.context().newPage()
    await otherBrowser.goto('/work-items')
    await expect(
      otherBrowser.locator(`div:has-text("${workItemTitle}") select`)
    ).toHaveValue(/Sprint \d+/)
  })

  test('cannot assign work item to non-future sprint', async ({ page }) => {
    // Create a test work item
    const workItemTitle = `Test Item ${Date.now()}`
    await page.click('button:has-text("New Work Item")')
    await page.fill('input[placeholder="Enter title"]', workItemTitle)
    await page.click('button:has-text("Create")')

    // Wait for the work item to be created
    await expect(page.locator(`text=${workItemTitle}`)).toBeVisible()

    // Open sprint assignment dropdown
    const workItemCard = page
      .locator(`div:has-text("${workItemTitle}")`)
      .first()
    await workItemCard.click()

    const sprintSelect = workItemCard.locator('select#sprint-select')
    await expect(sprintSelect).toBeVisible()

    // Verify active sprints are not in dropdown
    const options = await sprintSelect.locator('option').all()
    for (const option of options) {
      const text = await option.textContent()
      if (text !== 'No Sprint') {
        expect(text).toContain('Future')
      }
    }
  })

  test('handles concurrent modifications', async ({ page, browser }) => {
    // Create a test work item
    const workItemTitle = `Test Item ${Date.now()}`
    await page.click('button:has-text("New Work Item")')
    await page.fill('input[placeholder="Enter title"]', workItemTitle)
    await page.click('button:has-text("Create")')

    // Open the same work item in two browsers
    const browser1 = page
    const browser2 = await browser.newPage()
    await loginAsTeamMember(browser2)
    await browser2.goto('/work-items')

    // Make changes in both browsers
    const workItemCard1 = browser1
      .locator(`div:has-text("${workItemTitle}")`)
      .first()
    const workItemCard2 = browser2
      .locator(`div:has-text("${workItemTitle}")`)
      .first()

    await workItemCard1.click()
    await workItemCard2.click()

    // Try to assign sprint in both browsers
    const sprintSelect1 = workItemCard1.locator('select#sprint-select')
    const sprintSelect2 = workItemCard2.locator('select#sprint-select')

    await sprintSelect1.selectOption({ label: /Sprint \d+ \(Future\)/ })
    await expect(
      browser1.locator('text=Work item assigned to sprint')
    ).toBeVisible()

    await sprintSelect2.selectOption({ label: /Sprint \d+ \(Future\)/ })
    await expect(
      browser2.locator('text=Work item has been modified by another user')
    ).toBeVisible()
  })

  test('removing work item from sprint', async ({ page }) => {
    // Create a test work item and assign it to a sprint
    const workItemTitle = `Test Item ${Date.now()}`
    await page.click('button:has-text("New Work Item")')
    await page.fill('input[placeholder="Enter title"]', workItemTitle)
    await page.click('button:has-text("Create")')

    const workItemCard = page
      .locator(`div:has-text("${workItemTitle}")`)
      .first()
    await workItemCard.click()

    const sprintSelect = workItemCard.locator('select#sprint-select')
    await sprintSelect.selectOption({ label: /Sprint \d+ \(Future\)/ })
    await expect(
      page.locator('text=Work item assigned to sprint')
    ).toBeVisible()

    // Now remove it from the sprint
    await sprintSelect.selectOption({ value: '' })
    await expect(
      page.locator('text=Work item removed from sprint')
    ).toBeVisible()

    // Verify the removal
    await expect(sprintSelect).toHaveValue('')
  })
})
