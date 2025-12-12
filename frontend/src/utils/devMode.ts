/**
 * Hook to detect if dev mode is enabled via environment variable
 * Dev mode is enabled when VITE_DEV_MODE=true (default: false)
 *
 * Note: For local development + E2E tests that run against the Vite dev server,
 * we also support the legacy query param `?env=dev` (dev builds only).
 */
export function useDevMode(): boolean {
  return isDevMode()
}

/**
 * Utility function to detect if dev mode is enabled via environment variable
 * Use this when you can't use hooks (e.g., outside React components)
 * Dev mode is enabled when VITE_DEV_MODE=true (default: false)
 */
export function isDevMode(): boolean {
  if (typeof window === 'undefined') {
    return false
  }
  
  // Primary switch: build-time env var (default: false)
  if (import.meta.env.VITE_DEV_MODE === 'true') {
    return true
  }

  // Legacy switch: URL param, but only in Vite dev builds (not production)
  if (import.meta.env.DEV) {
    const params = new URLSearchParams(window.location.search)
    return params.get('env') === 'dev'
  }

  return false
}

