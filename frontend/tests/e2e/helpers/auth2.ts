import { Page } from '@playwright/test'
import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = 'http://127.0.0.1:54321'
const SUPABASE_ANON_KEY =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

const TEST_USER = {
  email: 'test@example.com',
  password: 'TestPass123!',
  full_name: 'Test User',
}

// Function to create a test user directly in the database
async function createTestUser() {
  try {
    // Create user in auth.users
    const { data: authUser, error: authError } = await supabase.rpc(
      'create_test_user',
      {
        p_email: TEST_USER.email,
        p_password: TEST_USER.password,
        p_full_name: TEST_USER.full_name,
      }
    )

    if (authError) {
      throw authError
    }

    return authUser
  } catch (error) {
    console.error('Failed to create test user:', error)
    throw error
  }
}

// Ensure test user exists and get session
export async function ensureTestUser() {
  try {
    // Try to sign in first
    const { data: signInData, error: signInError } =
      await supabase.auth.signInWithEmailAndPassword({
        email: TEST_USER.email,
        password: TEST_USER.password,
      })

    if (!signInError && signInData?.session) {
      return signInData.session
    }

    // If sign in failed, create user
    await createTestUser()

    // Try signing in again
    const { data, error } = await supabase.auth.signInWithEmailAndPassword({
      email: TEST_USER.email,
      password: TEST_USER.password,
    })

    if (error || !data?.session) {
      throw new Error(error?.message || 'Failed to get session')
    }

    return data.session
  } catch (error) {
    console.error('Failed to ensure test user:', error)
    throw error
  }
}

// Login helper function
export async function login(page: Page) {
  try {
    const session = await ensureTestUser()

    // Set auth state in localStorage
    await page.addInitScript(() => {
      // Clear any existing storage
      localStorage.clear()
      sessionStorage.clear()
    })

    // Navigate to app and set auth state
    await page.goto('/')

    await page.evaluate(
      (authData) => {
        localStorage.setItem('sb-access-token', authData.token)
        localStorage.setItem('sb-user', JSON.stringify(authData.user))
        localStorage.setItem('sb-refresh-token', authData.refresh)
        localStorage.setItem('isAuthenticated', 'true')
      },
      {
        token: session.access_token,
        refresh: session.refresh_token,
        user: session.user,
      }
    )

    // Navigate to dashboard and wait for auth to be recognized
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    const isAuthenticated = await page.evaluate(() => {
      return !!localStorage.getItem('sb-access-token')
    })

    if (!isAuthenticated) {
      throw new Error('Failed to verify authentication state')
    }
  } catch (error) {
    console.error('Login failed:', error)
    throw error
  }
}
