import { APIRequestContext, request as playwrightRequest, FullConfig } from '@playwright/test'
import { resetAllData } from './helpers/test-helpers'

/**
 * Global setup hook that runs before all tests
 * Automatically resets all test data to ensure a clean state
 * Can be disabled with RESET_DATA=false environment variable
 */
async function globalSetup(config: FullConfig) {
  // Check if reset is disabled via environment variable
  const shouldSkip = process.env.RESET_DATA === 'false' || process.env.RESET_DATA === '0'
  
  if (shouldSkip) {
    console.log('Global reset skipped (set RESET_DATA=false to disable)')
    return
  }

  console.log('Resetting all test data...')
  
  try {
    // Get base URL from config (frontend URL)
    const baseURL = config.projects[0]?.use?.baseURL || 'http://localhost:5003'

    // Prefer explicit backend URL (matches Vite proxy configuration).
    // This avoids assuming the backend runs on the same host as the frontend.
    const explicitBackendURL = process.env.BACKEND_URL || process.env.VITE_BACKEND_URL

    // Fallback: assume backend runs on same host as frontend with BACKEND_PORT (default 5004)
    const backendPort = process.env.BACKEND_PORT || '5004'
    const url = new URL(baseURL)
    const backendURL = explicitBackendURL || `${url.protocol}//${url.hostname}:${backendPort}`
    console.log(`Global reset target backend: ${backendURL}`)
    
    // Create API request context pointing to backend
    const request = await playwrightRequest.newContext({
      baseURL: backendURL,
    })
    
    await resetAllData(request)
    
    console.log('All test data has been reset successfully')
    
    await request.dispose()
  } catch (error) {
    console.error('Failed to reset test data:', error)
    // Don't throw - allow tests to run even if reset fails
    // This is useful if the backend isn't running yet
  }
}

export default globalSetup

