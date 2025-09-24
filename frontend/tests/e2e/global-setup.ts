import { createClient } from '@supabase/supabase-js'
import { FullConfig } from '@playwright/test'

const SUPABASE_URL = 'http://127.0.0.1:54321'
const SUPABASE_ANON_KEY =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

async function cleanupDatabase() {
  try {
    // Clear test data from tables
    await supabase.from('sprints').delete().neq('id', '')
    await supabase.from('teams').delete().neq('id', '')
    await supabase.from('team_members').delete().neq('id', '')

    console.log('Successfully cleaned up test database')
  } catch (error) {
    console.error('Failed to clean up test database:', error)
    throw error
  }
}

async function globalSetup(config: FullConfig) {
  // Ensure clean state before tests
  await cleanupDatabase()
}

export default globalSetup
