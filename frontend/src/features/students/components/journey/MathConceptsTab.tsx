import { useState } from 'react'
import { motion } from 'framer-motion'
import { AlertCircle, Loader2 } from 'lucide-react'
import type { UserProgressData } from '../../utils/progressMapping'
import type { User } from '../../hooks/useLearners'
import { useMathConcepts } from '../../hooks/useMathConcepts'
import type { MathConcept } from '../../data/mathConcepts'
import { MathConceptDetailModal } from './MathConceptDetailModal'
import { ConceptTreeView } from './ConceptTreeView'
import PINVerificationModal from '../../modals/PINVerificationModal'
import { useRouter } from '../../../../utils/routing'
import { useConceptRequirements } from '../../../../lib/concepts/hooks'

type MathConceptsTabProps = {
  userData: UserProgressData
  isActive: boolean
  user?: User | null
}

export const MathConceptsTab = ({ userData, isActive, user }: MathConceptsTabProps) => {
  const [selectedConcept, setSelectedConcept] = useState<MathConcept | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isPinModalOpen, setIsPinModalOpen] = useState(false)
  const [pendingConcept, setPendingConcept] = useState<MathConcept | null>(null)
  const router = useRouter()

  const userId = user?.id ? String(user.id) : undefined
  const { concepts, isLoading, error } = useMathConcepts({
    userData,
    isActive,
    userId,
  })

  // Get backend requirements for graph building
  const conceptIds = concepts.map(c => c.conceptId)
  const { requirements: backendRequirements } = useConceptRequirements(conceptIds, isActive, userId)

  const handleConceptClick = (concept: MathConcept) => {
    setSelectedConcept(concept)
    setIsModalOpen(true)
  }

  const handleStartPracticeClick = (concept: MathConcept) => {
    setPendingConcept(concept)
    setIsModalOpen(false)
    setIsPinModalOpen(true)
  }

  const handlePinVerified = (pin: string) => {
    setIsPinModalOpen(false)
    if (pendingConcept) {
      handleStartPractice(pendingConcept)
      setPendingConcept(null)
    }
  }

  const handleStartPractice = (concept: MathConcept) => {
    if (!userData) return

    // Navigate to practice page with concept parameters
    router.navigate('/practice', {
      user: userData.name,
      userId: userData.id,
      avatar: userData.avatar,
      conceptId: concept.conceptId,
      isConcept: 'true',
    })
  }

  return (
    <motion.div
      data-testid="testid-concepts-tab"
      key="concepts"
      initial={{
        opacity: 0,
        y: 20,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      exit={{
        opacity: 0,
        y: -20,
      }}
    >
      {/* Header */}
      <div className="mb-6">
        <h2 className="mb-2 text-2xl font-bold text-gray-900">Math Concepts</h2>
        <p className="text-gray-600">
          Practice specific math concepts. Each concept has its own unlock requirements and can be practiced independently.
        </p>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <span className="ml-3 text-gray-600">Loading concepts...</span>
        </div>
      )}

      {error && (
        <div className="rounded-lg border-2 border-red-300 bg-red-50 p-4 text-red-800">
          <p>Failed to load concepts: {error}</p>
        </div>
      )}

      {!isLoading && !error && (
        <>
          {concepts.length > 0 ? (
            <ConceptTreeView
              concepts={concepts}
              userData={userData}
              backendRequirements={backendRequirements}
              onConceptClick={handleConceptClick}
              onStartPractice={handleStartPracticeClick}
            />
          ) : (
            <div className="py-16 text-center">
              <AlertCircle className="mx-auto mb-4 h-16 w-16 text-gray-300" />
              <p className="text-lg text-gray-500">No concepts available</p>
            </div>
          )}
        </>
      )}

      {/* Concept Detail Modal */}
      <MathConceptDetailModal
        concept={selectedConcept}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onStartPractice={handleStartPractice}
        selectedUser={user || (userData ? {
          id: userData.id,
          name: userData.name,
          avatar: userData.avatar,
          level: userData.level,
          questionsAnswered: userData.totalQuestions,
          averageSpeed: 0,
          achievements: userData.achievements
            .filter(ach => ach.unlockedAt)
            .map(ach => ({
              id: ach.id,
              code: ach.id,
              title: ach.title,
              description: ach.description,
              icon: ach.icon,
              earnedAt: ach.unlockedAt!,
              category: ach.category,
            })),
          stats: {
            additionAccuracy: 0,
            subtractionAccuracy: 0,
            multiplicationAccuracy: 0,
            divisionAccuracy: 0,
            additionSpeed: 0,
            subtractionSpeed: 0,
            multiplicationSpeed: 0,
            divisionSpeed: 0,
            currentStreak: userData.currentStreak,
            bestStreak: userData.bestStreak,
          },
        } : null)}
      />

      {/* PIN Verification Modal */}
      <PINVerificationModal
        isOpen={isPinModalOpen}
        onClose={() => {
          setIsPinModalOpen(false)
          setPendingConcept(null)
        }}
        onVerified={handlePinVerified}
        selectedUser={user || (userData ? {
          id: userData.id,
          name: userData.name,
          avatar: userData.avatar,
          level: userData.level,
          questionsAnswered: userData.totalQuestions,
          averageSpeed: 0,
          achievements: [],
          stats: {
            additionAccuracy: 0,
            subtractionAccuracy: 0,
            multiplicationAccuracy: 0,
            divisionAccuracy: 0,
            additionSpeed: 0,
            subtractionSpeed: 0,
            multiplicationSpeed: 0,
            divisionSpeed: 0,
            currentStreak: userData.currentStreak,
            bestStreak: userData.bestStreak,
          },
        } : null)}
      />
    </motion.div>
  )
}
