import { BrowserRouter, Routes, Route } from 'react-router-dom'
import PracticeSessionPage from './features/practice/PracticeSessionPage'
import SummaryPage from './features/practice/SummaryPage'
import LearnersDashboard from './features/students/LearnersDashboard'
import JourneyPage from './features/students/pages/JourneyPage'
import { GraphPage } from './features/students/pages/GraphPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LearnersDashboard />} />
        <Route path="/practice" element={<PracticeSessionPage />} />
        <Route path="/summary" element={<SummaryPage />} />
        <Route path="/graph" element={<GraphPage />} />
        <Route path="/journey/:userId" element={<JourneyPage />} />
        <Route path="/journey/:userId/:tab" element={<JourneyPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
