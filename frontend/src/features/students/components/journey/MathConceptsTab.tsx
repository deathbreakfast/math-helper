import { useMemo, useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { AlertCircle, Search, Loader2 } from 'lucide-react'
import type { UserProgressData } from '../../utils/progressMapping'
import type { User } from '../../hooks/useLearners'
import { useMathConcepts } from '../../hooks/useMathConcepts'
import type { MathConcept } from '../../data/mathConcepts'
import { MathConceptCard } from './MathConceptCard'
import { MathConceptDetailModal } from './MathConceptDetailModal'
import PINVerificationModal from '../../modals/PINVerificationModal'
import { useRouter } from '../../../../utils/routing'

type MathConceptsTabProps = {
  userData: UserProgressData
  isActive: boolean
  user?: User | null
}

export const MathConceptsTab = ({ userData, isActive, user }: MathConceptsTabProps) => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [textFilter, setTextFilter] = useState('')
  
  // Read status filter from URL query params, default to 'unlocked' for better first-time experience
  const statusParam = searchParams.get('status') as 'all' | 'locked' | 'unlocked' | 'attempted' | null
  const [statusFilter, setStatusFilter] = useState<'all' | 'locked' | 'unlocked' | 'attempted'>(
    statusParam || 'unlocked'
  )
  
  // Sync status filter with URL query params when component mounts or URL changes
  useEffect(() => {
    if (statusParam && statusParam !== statusFilter) {
      setStatusFilter(statusParam)
    }
  }, [statusParam])
  
  // Update URL when status filter changes
  const handleStatusFilterChange = (newStatus: 'all' | 'locked' | 'unlocked' | 'attempted') => {
    setStatusFilter(newStatus)
    const newParams = new URLSearchParams(searchParams)
    if (newStatus !== 'unlocked') {
      // Only set param if not default 'unlocked' to keep URLs clean
      newParams.set('status', newStatus)
    } else {
      newParams.delete('status')
    }
    setSearchParams(newParams, { replace: true })
  }
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

  // Filter concepts
  const filteredConcepts = useMemo(() => {
    const lowerTextFilter = textFilter.toLowerCase()
    const visible = concepts.filter((concept) => {
      // Status filter
      let statusMatch = true
      if (statusFilter !== 'all') {
        if (statusFilter === 'locked') {
          statusMatch = concept.isLocked
        } else if (statusFilter === 'unlocked') {
          statusMatch = !concept.isLocked && concept.attemptCount === 0
        } else if (statusFilter === 'attempted') {
          statusMatch = concept.attemptCount > 0
        }
      }

      // Text filter
      const textMatch =
        !textFilter ||
        concept.displayName.toLowerCase().includes(lowerTextFilter) ||
        concept.conceptId.toLowerCase().includes(lowerTextFilter)

      return statusMatch && textMatch
    })

    // Sort: unlocked (including attempted) first, locked last; within each bucket keep attempted first then alphabetical.
    const sorted = [...visible].sort((a, b) => {
      const aLocked = a.isLocked ? 1 : 0
      const bLocked = b.isLocked ? 1 : 0
      if (aLocked !== bLocked) return aLocked - bLocked

      const aAttempted = a.attemptCount > 0 ? 0 : 1
      const bAttempted = b.attemptCount > 0 ? 0 : 1
      if (aAttempted !== bAttempted) return aAttempted - bAttempted

      return a.displayName.localeCompare(b.displayName)
    })

    return sorted.map((concept) => ({ concept, matchesFilter: true }))
  }, [concepts, statusFilter, textFilter])

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

      {/* Filters */}
      <div className="mb-8 rounded-2xl bg-white p-6 shadow-lg">
        <div className="flex flex-wrap gap-4">
          <div className="min-w-[200px] flex-1">
            <label className="mb-2 block text-sm font-medium text-gray-700">Status</label>
            <select
              data-testid="testid-concept-filter-status"
              value={statusFilter}
              onChange={(e) => handleStatusFilterChange(e.target.value as any)}
              className="w-full rounded-xl border border-gray-300 bg-white px-4 py-2 text-gray-900 outline-none focus:border-transparent focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="unlocked">Unlocked</option>
              <option value="attempted">Attempted</option>
              <option value="locked">Locked</option>
            </select>
          </div>
          <div className="min-w-[200px] flex-1">
            <label className="mb-2 block text-sm font-medium text-gray-700">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
              <input
                data-testid="testid-concept-search-input"
                type="text"
                value={textFilter}
                onChange={(e) => setTextFilter(e.target.value)}
                placeholder="Search concepts..."
                className="w-full rounded-xl border border-gray-300 bg-white px-4 py-2 pl-10 text-gray-900 outline-none placeholder:text-gray-400 focus:border-transparent focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
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
          {/* Concept Grid */}
          <div data-testid="testid-concept-grid" className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {filteredConcepts.map(({ concept, matchesFilter }, index) => (
              <MathConceptCard
                key={concept.id}
                concept={concept}
                index={index}
                onClick={handleConceptClick}
                onStartPractice={handleStartPracticeClick}
                matchesFilter={matchesFilter}
              />
            ))}
          </div>

          {filteredConcepts.length === 0 && (
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
