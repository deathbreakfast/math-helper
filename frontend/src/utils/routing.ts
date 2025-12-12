// Enhanced routing utility with parameter preservation
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useCallback } from 'react'

// Navigate options type (not exported from react-router-dom in some versions)
type NavigateOptions = {
  replace?: boolean
  state?: unknown
  relative?: 'route' | 'path'
}

export type Route = '/' | '/practice' | '/summary'

// Context parameters that should be preserved across navigation
const CONTEXT_PARAMS = ['env'] as const
type ContextParam = typeof CONTEXT_PARAMS[number]

// Parameters that should be explicitly excluded from navigation (not preserved)
const EXCLUDED_PARAMS = ['session', 'sessionId'] as const

/**
 * Extract context parameters from URLSearchParams
 */
export function getContextParams(searchParams: URLSearchParams): Record<string, string> {
  const context: Record<string, string> = {}
  for (const key of CONTEXT_PARAMS) {
    const value = searchParams.get(key)
    if (value) {
      context[key] = value
    }
  }
  return context
}

/**
 * Merge search parameters, preserving context params from existing params
 * Explicitly excludes session-related params to prevent URL bloat
 */
export function mergeSearchParams(
  existing: URLSearchParams,
  newParams?: Record<string, string | null>,
  preserveKeys: readonly string[] = CONTEXT_PARAMS
): URLSearchParams {
  const merged = new URLSearchParams()
  
  // Preserve context params from existing
  for (const key of preserveKeys) {
    const existingValue = existing.get(key)
    if (existingValue) {
      merged.set(key, existingValue)
    }
  }
  
  // Add/update new params (excluding session-related params)
  if (newParams) {
    for (const [key, value] of Object.entries(newParams)) {
      // Skip excluded params (session, sessionId)
      if (EXCLUDED_PARAMS.includes(key as any)) {
        continue
      }
      if (value === null || value === undefined) {
        merged.delete(key)
      } else {
        merged.set(key, value)
      }
    }
  }
  
  // Remove any excluded params that might have been in existing params
  for (const excludedKey of EXCLUDED_PARAMS) {
    merged.delete(excludedKey)
  }
  
  return merged
}

/**
 * Build a URL string with parameters, preserving context params
 */
export function buildUrl(
  path: string,
  params?: Record<string, string | null>,
  existingParams?: URLSearchParams
): string {
  const searchParams = existingParams 
    ? mergeSearchParams(existingParams, params)
    : new URLSearchParams()
  
  // If we have params but no existing params, create new URLSearchParams
  if (params && !existingParams) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== null && value !== undefined) {
        searchParams.set(key, value)
      }
    }
    // Add context params if they exist in current URL (for non-hook usage)
    // This is a fallback - ideally useRouter hook should be used
  }
  
  const queryString = searchParams.toString()
  return queryString ? `${path}?${queryString}` : path
}

/**
 * Enhanced router hook that preserves context parameters
 */
export function useRouter() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  
  /**
   * Navigate to a path with optional parameters, preserving context params
   */
  const navigateWithParams = useCallback(
    (
      path: string,
      params?: Record<string, string | null>,
      options?: NavigateOptions
    ) => {
      const mergedParams = mergeSearchParams(searchParams, params)
      const queryString = mergedParams.toString()
      const url = queryString ? `${path}?${queryString}` : path
      navigate(url, options)
    },
    [navigate, searchParams]
  )
  
  /**
   * Build a URL string with parameters, preserving context params
   */
  const buildUrlWithParams = useCallback(
    (path: string, params?: Record<string, string | null>): string => {
      return buildUrl(path, params, searchParams)
    },
    [searchParams]
  )
  
  /**
   * Get current context parameters
   */
  const getContextParamsValue = useCallback((): Record<string, string> => {
    return getContextParams(searchParams)
  }, [searchParams])
  
  return {
    navigate: navigateWithParams,
    buildUrl: buildUrlWithParams,
    getContextParams: getContextParamsValue,
    searchParams,
  }
}

// Re-export useLocation for convenience
import { useLocation } from 'react-router-dom'
export { useLocation }

// Helper function to build journey route (preserves context params if used with useRouter)
export const buildJourneyRoute = (
  userId: string,
  tab?: string,
  filters?: Record<string, string>,
  existingParams?: URLSearchParams
): string => {
  const base = `/journey/${userId}${tab ? `/${tab}` : ''}`
  const allParams = { ...filters }
  return buildUrl(base, allParams, existingParams)
}
