export type Route = '/' | '/practice'

export const getCurrentRoute = (): Route => {
  if (typeof window === 'undefined') return '/'
  const pathname = window.location.pathname
  if (pathname.startsWith('/practice')) {
    return '/practice'
  }
  return '/'
}

export const isPracticeRoute = (): boolean => {
  return getCurrentRoute() === '/practice'
}

