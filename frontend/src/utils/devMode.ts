/**
 * Hook to detect if dev mode is enabled via environment variable
 * Dev mode is enabled when VITE_DEV_MODE=true (default: false)
 * This replaces the previous URL parameter-based approach for better security
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
  
  // Check environment variable (default: false)
  return import.meta.env.VITE_DEV_MODE === 'true'
}

