import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export async function seedTestUser() {
  try {
    await api.post('/api/v1/users/register', {
      full_name: 'Test User',
      email: 'test@example.com',
      password: 'TestPass123'
    })
  } catch (err: unknown) {
    // Ignore if user already exists
    const error = err as { response?: { status?: number } }
    if (error.response?.status !== 409) {
      throw err
    }
  }
}
