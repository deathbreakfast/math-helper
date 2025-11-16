import PracticeSessionPage from './features/practice/PracticeSessionPage'
import StudentsDashboard from './features/students/StudentsDashboard'
import { isPracticeRoute } from './utils/routing'

function App() {
  if (isPracticeRoute()) {
    return <PracticeSessionPage />
  }

  return <StudentsDashboard />
}

export default App
