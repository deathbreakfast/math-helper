import PracticeSessionPage from './features/practice/PracticeSessionPage'
import SummaryPage from './features/practice/SummaryPage'
import LearnersDashboard from './features/students/LearnersDashboard'
import { isPracticeRoute, isSummaryRoute } from './utils/routing'

function App() {
  if (isPracticeRoute()) {
    return <PracticeSessionPage />
  }

  if (isSummaryRoute()) {
    return <SummaryPage />
  }

  return <LearnersDashboard />
}

export default App
