import { APIRequestContext } from '@playwright/test'
import type { TestUser } from '../types/test-types'

/**
 * Generate a unique test user name with timestamp and random suffix
 * Format: TestUser_{testName}_{timestamp}_{random}
 */
export function generateTestUserName(testName: string): string {
  const timestamp = Date.now()
  const random = Math.random().toString(36).substring(2, 6)
  return `TestUser_${testName}_${timestamp}_${random}`
}

/**
 * Create a test user via API
 */
export async function createTestUser(
  request: APIRequestContext,
  options?: {
    name?: string
    avatar?: string
    pin?: string
  }
): Promise<TestUser> {
  const name = options?.name || generateTestUserName('Test')
  const avatar = options?.avatar || '🐯'
  const pin = options?.pin || '1234'

  const response = await request.post('/api/users', {
    data: {
      name,
      avatar,
      pin,
    },
  })

  if (!response.ok()) {
    // Try to parse as JSON, but handle HTML error pages
    let errorMessage = `Failed to create test user: ${response.status()} ${response.statusText()}`
    try {
      const contentType = response.headers()['content-type'] || ''
      if (contentType.includes('application/json')) {
        const error = await response.json()
        errorMessage = `Failed to create test user: ${JSON.stringify(error)}`
      } else {
        const text = await response.text()
        errorMessage = `Failed to create test user: ${response.status()} ${response.statusText()}. Response: ${text.substring(0, 200)}`
      }
    } catch (e) {
      const text = await response.text().catch(() => 'Unable to read response')
      errorMessage = `Failed to create test user: ${response.status()} ${response.statusText()}. Response: ${text.substring(0, 200)}`
    }
    throw new Error(errorMessage)
  }

  const user = await response.json()
  return {
    id: user.id,
    name: user.name,
    avatar: user.avatar || avatar,
    pin,
    level: user.level || 1,
  }
}

/**
 * Delete a test user via API
 */
export async function deleteTestUser(
  request: APIRequestContext,
  userId: number
): Promise<void> {
  const response = await request.delete(`/api/users/${userId}`)

  if (!response.ok()) {
    // If user doesn't exist, that's okay (might have been deleted already)
    if (response.status() === 404) {
      return
    }
    // Try to parse as JSON, but handle HTML error pages
    let errorMessage = `Failed to delete test user: ${response.status()} ${response.statusText()}`
    try {
      const contentType = response.headers()['content-type'] || ''
      if (contentType.includes('application/json')) {
        const error = await response.json()
        errorMessage = `Failed to delete test user: ${JSON.stringify(error)}`
      } else {
        const text = await response.text()
        errorMessage = `Failed to delete test user: ${response.status()} ${response.statusText()}. Response: ${text.substring(0, 200)}`
      }
    } catch (e) {
      const text = await response.text().catch(() => 'Unable to read response')
      errorMessage = `Failed to delete test user: ${response.status()} ${response.statusText()}. Response: ${text.substring(0, 200)}`
    }
    throw new Error(errorMessage)
  }
}

/**
 * Get a user by ID via API
 */
export async function getUser(
  request: APIRequestContext,
  userId: number
): Promise<TestUser | null> {
  const response = await request.get(`/api/users/${userId}`)

  if (response.status() === 404) {
    return null
  }

  if (!response.ok()) {
    // Try to parse as JSON, but handle HTML error pages
    let errorMessage = `Failed to get user: ${response.status()} ${response.statusText()}`
    try {
      const contentType = response.headers()['content-type'] || ''
      if (contentType.includes('application/json')) {
        const error = await response.json()
        errorMessage = `Failed to get user: ${JSON.stringify(error)}`
      } else {
        const text = await response.text()
        errorMessage = `Failed to get user: ${response.status()} ${response.statusText()}. Response: ${text.substring(0, 200)}`
      }
    } catch (e) {
      const text = await response.text().catch(() => 'Unable to read response')
      errorMessage = `Failed to get user: ${response.status()} ${response.statusText()}. Response: ${text.substring(0, 200)}`
    }
    throw new Error(errorMessage)
  }

  const user = await response.json()
  return {
    id: user.id,
    name: user.name,
    avatar: user.avatar || '🐯',
    pin: user.pin || '1234',
    level: user.level || 1,
  }
}

/**
 * List all users via API
 */
export async function listUsers(request: APIRequestContext): Promise<TestUser[]> {
  const response = await request.get('/api/users')

  if (!response.ok()) {
    // Try to parse as JSON, but handle HTML error pages
    let errorMessage = `Failed to list users: ${response.status()} ${response.statusText()}`
    try {
      const contentType = response.headers()['content-type'] || ''
      if (contentType.includes('application/json')) {
        const error = await response.json()
        errorMessage = `Failed to list users: ${JSON.stringify(error)}`
      } else {
        // Response is HTML or other non-JSON format
        const text = await response.text()
        errorMessage = `Failed to list users: ${response.status()} ${response.statusText()}. Response: ${text.substring(0, 200)}`
      }
    } catch (e) {
      // If parsing fails, use the status and text
      const text = await response.text().catch(() => 'Unable to read response')
      errorMessage = `Failed to list users: ${response.status()} ${response.statusText()}. Response: ${text.substring(0, 200)}`
    }
    throw new Error(errorMessage)
  }

  const data = await response.json()
  return (data.users || []).map((user: any) => ({
    id: user.id,
    name: user.name,
    avatar: user.avatar || '🐯',
    pin: user.pin || '1234',
    level: user.level || 1,
  }))
}

