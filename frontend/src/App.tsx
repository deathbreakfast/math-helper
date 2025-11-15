import PracticeSessionPage from './features/practice/PracticeSessionPage'
import StudentsDashboard from './features/students/StudentsDashboard'

function App() {
  const isBrowser = typeof window !== 'undefined'
  const isPracticeRoute = isBrowser && window.location.pathname.startsWith('/practice')

  if (isPracticeRoute) {
    return <PracticeSessionPage />
  }

  return <StudentsDashboard />
}

export default App
