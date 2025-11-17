import PracticeSessionPage from './features/practice/PracticeSessionPage'
import SummaryPage from './features/practice/SummaryPage'
import StudentsDashboard from './features/students/StudentsDashboard'
import { isPracticeRoute, isSummaryRoute } from './utils/routing'

function App() {
  if (isPracticeRoute()) {
    return <PracticeSessionPage />
  }

  if (isSummaryRoute()) {
    return <SummaryPage />
  }

  return <StudentsDashboard />
}

export default App
