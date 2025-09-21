import { test, expect } from '@playwright/test';
import { SprintStatus } from '@/types/sprint';

// Helper functions to format dates for testing
const formatDate = (date: Date) => date.toISOString().split('T')[0];
const today = new Date();
const tomorrow = new Date(today);
tomorrow.setDate(today.getDate() + 1);
const nextWeek = new Date(today);
nextWeek.setDate(today.getDate() + 7);

test.describe('Sprint Lifecycle', () => {
  test.beforeEach(async ({ page }) => {
    // Log in and navigate to sprints page
    await page.goto('/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');

    // Navigate to team's sprint page
    await page.goto('/teams/1/sprints');
    await page.waitForSelector('h4:has-text("Sprint Management")');
  });

  test('completes full sprint lifecycle', async ({ page }) => {
    // Test creating a sprint
    await test.step('Create Sprint', async () => {
      await page.click('button[aria-label="Add Sprint"]');
      await page.waitForSelector('div[role="dialog"]');

      // Fill sprint form
      await page.fill('input[name="name"]', 'Test Sprint');
      await page.fill('textarea[name="goal"]', 'Test sprint goal');
      await page.fill('input[name="startDate"]', formatDate(today));
      await page.fill('input[name="endDate"]', formatDate(nextWeek));

      await page.click('button:has-text("Create Sprint")');
      await page.waitForSelector('div:has-text("Test Sprint")');

      // Verify sprint was created
      await expect(page.locator('text=Test Sprint')).toBeVisible();
      await expect(page.locator('text=Test sprint goal')).toBeVisible();
      await expect(page.locator(`text=${formatDate(today)}`)).toBeVisible();
      await expect(page.locator(`text=${formatDate(nextWeek)}`)).toBeVisible();
      await expect(page.locator('text=Future')).toBeVisible();
    });

    // Test activating sprint
    await test.step('Activate Sprint', async () => {
      await page.click('button:has-text("Start Sprint")');
      await expect(page.locator('text=Active')).toBeVisible();

      // Verify "Start Sprint" button is disabled for other sprints
      const startButtons = page.locator('button:has-text("Start Sprint")');
      for (const button of await startButtons.all()) {
        await expect(button).toBeDisabled();
      }
    });

    // Test closing sprint
    await test.step('Close Sprint', async () => {
      await page.click('button:has-text("Close Sprint")');
      await expect(page.locator('text=Closed')).toBeVisible();

      // Verify other sprints can now be activated
      const startButtons = page.locator('button:has-text("Start Sprint")');
      for (const button of await startButtons.all()) {
        await expect(button).toBeEnabled();
      }
    });
  });

  test('prevents invalid state transitions', async ({ page }) => {
    // Create test sprint
    await page.click('button[aria-label="Add Sprint"]');
    await page.fill('input[name="name"]', 'Invalid Transition Test');
    await page.fill('input[name="startDate"]', formatDate(today));
    await page.fill('input[name="endDate"]', formatDate(nextWeek));
    await page.click('button:has-text("Create Sprint")');

    // Verify we can't close a future sprint
    await page.evaluate(() => {
      // Mock the API to attempt an invalid transition
      window.fetch = async (url, options) => {
        if (url.includes('/sprints') && options?.method === 'PATCH') {
          const body = JSON.parse(options.body as string);
          if (body.status === SprintStatus.CLOSED) {
            return new Response(JSON.stringify({
              detail: 'Invalid state transition from future to closed'
            }), { status: 400 });
          }
        }
        return new Response();
      };
    });

    // Attempt invalid transition and verify error
    await page.click('button:has-text("Start Sprint")');
    await page.click('button:has-text("Close Sprint")');
    await expect(page.locator('text=Invalid state transition')).toBeVisible();
  });

  test('prevents overlapping sprint dates', async ({ page }) => {
    // Create first sprint
    await page.click('button[aria-label="Add Sprint"]');
    await page.fill('input[name="name"]', 'Sprint 1');
    await page.fill('input[name="startDate"]', formatDate(today));
    await page.fill('input[name="endDate"]', formatDate(nextWeek));
    await page.click('button:has-text("Create Sprint")');

    // Attempt to create overlapping sprint
    await page.click('button[aria-label="Add Sprint"]');
    await page.fill('input[name="name"]', 'Sprint 2');
    await page.fill('input[name="startDate"]', formatDate(tomorrow));
    await page.fill('input[name="endDate"]', formatDate(nextWeek));
    await page.click('button:has-text("Create Sprint")');

    // Verify error message
    await expect(page.locator('text=Sprint dates overlap')).toBeVisible();
  });
});
