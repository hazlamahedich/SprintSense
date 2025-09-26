import { test, expect } from '@playwright/test';
import { startSupabase, resetTestData } from '../helpers/supabase';

test.describe('Sprint Completion', () => {
  test.beforeEach(async ({ page }) => {
    await startSupabase();
    await resetTestData();
  });

  test('handles incomplete items when ending sprint', async ({ page }) => {
    // Log in (implement based on your auth flow)
    await page.goto('/login');
    await page.fill('[data-testid=email]', 'test@example.com');
    await page.fill('[data-testid=password]', 'password123');
    await page.click('button[type="submit"]');

    // Navigate to active sprint
    await page.goto('/sprints/current');
    await expect(page).toHaveTitle(/Current Sprint/);

    // Verify incomplete items exist
    await expect(page.locator('[data-testid=incomplete-task]')).toHaveCount(3);

    // Click end sprint
    await page.click('button:text("End Sprint")');

    // Verify incomplete items dialog appears
    await expect(page.locator('text=Handle Incomplete Work')).toBeVisible();
    await expect(page.locator('text=3 incomplete items')).toBeVisible();

    // Choose move to backlog
    await page.click('button:text("Move to Backlog")');

    // Verify success message and navigation prompt
    await expect(page.locator('text=Items moved successfully')).toBeVisible();
    await expect(page.locator('text=View in Backlog')).toBeVisible();

    // Check items moved to backlog (navigate and verify)
    await page.click('text=View in Backlog');
    await expect(page).toHaveURL(/.*backlog/);
    await expect(page.locator('[data-testid=backlog-item]')).toHaveCount(3);
  });

  test('moves items to next sprint', async ({ page }) => {
    // Log in
    await page.goto('/login');
    await page.fill('[data-testid=email]', 'test@example.com');
    await page.fill('[data-testid=password]', 'password123');
    await page.click('button[type="submit"]');

    // Navigate to active sprint
    await page.goto('/sprints/current');

    // End sprint and move to next
    await page.click('button:text("End Sprint")');
    await page.click('button:text("Move to Next Sprint")');

    // Verify items moved
    await expect(page.locator('text=Items moved to next sprint')).toBeVisible();

    // Navigate to next sprint and verify
    await page.click('text=View Next Sprint');
    await expect(page.locator('[data-testid=sprint-item]')).toHaveCount(3);
  });

  test('handles edge case: no incomplete items', async ({ page }) => {
    // Log in
    await page.goto('/login');
    await page.fill('[data-testid=email]', 'test@example.com');
    await page.fill('[data-testid=password]', 'password123');
    await page.click('button[type="submit"]');

    // Navigate to sprint with all items complete
    await page.goto('/sprints/completed');

    // Try to end sprint
    await page.click('button:text("End Sprint")');

    // Should not show incomplete items dialog
    await expect(page.locator('text=Handle Incomplete Work')).not.toBeVisible();
    await expect(page.locator('text=Sprint completed successfully')).toBeVisible();
  });

  test('handles error: no next sprint exists', async ({ page }) => {
    // Log in
    await page.goto('/login');
    await page.fill('[data-testid=email]', 'test@example.com');
    await page.fill('[data-testid=password]', 'password123');
    await page.click('button[type="submit"]');

    // Navigate to last sprint
    await page.goto('/sprints/last');

    // End sprint and try to move to next
    await page.click('button:text("End Sprint")');
    await page.click('button:text("Move to Next Sprint")');

    // Should show error
    await expect(page.locator('text=No next sprint available')).toBeVisible();
    await expect(page.locator('text=Please create a planned sprint first')).toBeVisible();

    // Dialog should stay open
    await expect(page.locator('text=Handle Incomplete Work')).toBeVisible();
  });

  test('handles network errors gracefully', async ({ page }) => {
    // Log in
    await page.goto('/login');
    await page.fill('[data-testid=email]', 'test@example.com');
    await page.fill('[data-testid=password]', 'password123');
    await page.click('button[type="submit"]');

    // Navigate to active sprint
    await page.goto('/sprints/current');

    // Simulate offline
    await page.context().setOffline(true);

    // Try to end sprint
    await page.click('button:text("End Sprint")');

    // Should show error
    await expect(page.locator('text=Failed to load incomplete items')).toBeVisible();

    // Restore online and retry
    await page.context().setOffline(false);
    await page.click('button:text("Retry")');

    // Dialog should now show items
    await expect(page.locator('text=Handle Incomplete Work')).toBeVisible();
    await expect(page.locator('[data-testid=incomplete-task]')).toBeVisible();
  });
});
