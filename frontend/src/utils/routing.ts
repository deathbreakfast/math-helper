export type Route = '/' | '/practice' | '/summary'

export const getCurrentRoute = (): Route => {
  if (typeof window === 'undefined') return '/'
  const pathname = window.location.pathname
  if (pathname.startsWith('/practice')) {
    return '/practice'
  }
  if (pathname.startsWith('/summary')) {
    return '/summary'
  }
  return '/'
}

export const isPracticeRoute = (): boolean => {
  return getCurrentRoute() === '/practice'
}

export const isSummaryRoute = (): boolean => {
  return getCurrentRoute() === '/summary'
}

