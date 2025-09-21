import { Page, expect } from '@playwright/test'

const TEST_USER = {
  email: 'test@example.com',
  password: 'TestPass123',
}

export async function login(
  page: Page,
  email = TEST_USER.email,
  password = TEST_USER.password
) {
  // Navigate to login page
  await page.goto('/login', { waitUntil: 'domcontentloaded' })

  // Wait for and fill login form
  await page.waitForSelector('input[type="email"]')
  await page.waitForSelector('input[type="password"]')

  await page.fill('input[type="email"]', email)
  await page.fill('input[type="password"]', password)

  // Submit login form and wait for response
  try {
    await Promise.all([
      page.waitForResponse(
        (res) =>
          res.url().includes('/api/v1/auth/login') && res.status() === 200,
        { timeout: 15000 }
      ),
      page.click('button[type="submit"]'),
    ])

    // Wait for navigation
    await page.waitForURL('**/dashboard')
    await page.waitForLoadState('domcontentloaded')
  } catch (error) {
    console.error('Login failed:', error)
    throw new Error(`Login failed: ${error.message}`)
  }
}

export async function getAuthCookie(
  page: Page
): Promise<{ name: string; value: string }> {
  // First login to get the cookie
  await login(page)

  // Get all cookies
  const cookies = await page.context().cookies()

  // Find the auth cookie (adjust the name based on your actual cookie name)
  const authCookie = cookies.find((cookie) => cookie.name === 'access_token')
  if (!authCookie) {
    throw new Error('Auth cookie not found after login')
  }

  return {
    name: authCookie.name,
    value: authCookie.value,
    url: 'http://localhost:5173',
    httpOnly: true,
    secure: false,
  }
}
