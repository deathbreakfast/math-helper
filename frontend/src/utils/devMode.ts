import { useSearchParams } from 'react-router-dom'

/**
 * Hook to detect if dev mode is enabled via URL parameter
 * Dev mode is enabled when ?env=dev is present in the URL
 * Uses React Router's useSearchParams for proper integration
 */
export function useDevMode(): boolean {
  const [searchParams] = useSearchParams()
  return searchParams.get('env') === 'dev'
}

/**
 * Utility function to detect if dev mode is enabled via URL parameter
 * Use this when you can't use hooks (e.g., outside React components)
 * Dev mode is enabled when ?env=dev is present in the URL
 */
export function isDevMode(): boolean {
  if (typeof window === 'undefined') {
    return false
  }
  
  const params = new URLSearchParams(window.location.search)
  return params.get('env') === 'dev'
}

