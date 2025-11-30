import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { AlertCircle, Search, Lock, Unlock, Play } from 'lucide-react'
import type { FrontendTest } from '../../utils/testMapping'
import { TestCard } from './TestCard'
import { TestDetailModal } from './TestDetailModal'

type TestsTabProps = {
  tests: FrontendTest[]
  tierFilter: 'all' | 'B' | 'A' | 'S' | 'SS' | 'SSS'
  statusFilter: 'all' | 'locked' | 'unlocked' | 'attempted'
  textFilter: string
  onTierFilterChange: (filter: 'all' | 'B' | 'A' | 'S' | 'SS' | 'SSS') => void
  onStatusFilterChange: (filter: 'all' | 'locked' | 'unlocked' | 'attempted') => void
  onTextFilterChange: (filter: string) => void
  onStartTest: (test: FrontendTest) => void
  getTestAttempts: (testType: string) => Promise<any[]>
  getTestAttemptDetail: (attemptId: number) => Promise<any>
}

export const TestsTab = ({
  tests,
  tierFilter,
  statusFilter,
  textFilter,
  onTierFilterChange,
  onStatusFilterChange,
  onTextFilterChange,
  onStartTest,
  getTestAttempts,
  getTestAttemptDetail,
}: TestsTabProps) => {
  const [selectedTest, setSelectedTest] = useState<FrontendTest | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  // Filter tests
  const filteredTests = useMemo(() => {
    const lowerTextFilter = textFilter.toLowerCase()
    return tests.filter((test) => {
      // Tier filter (based on best result)
      const tierMatch =
        tierFilter === 'all' ||
        (test.bestResult && test.bestResult.tier === tierFilter) ||
        (tierFilter === 'B' && !test.bestResult)

      // Status filter
      let statusMatch = true
      if (statusFilter !== 'all') {
        if (statusFilter === 'locked') {
          statusMatch = test.isLocked
        } else if (statusFilter === 'unlocked') {
          statusMatch = !test.isLocked && test.attemptCount === 0
        } else if (statusFilter === 'attempted') {
          statusMatch = test.attemptCount > 0
        }
      }

      // Text filter
      const textMatch =
        !textFilter ||
        test.display_name.toLowerCase().includes(lowerTextFilter) ||
        test.test_type.toLowerCase().includes(lowerTextFilter)

      return tierMatch && statusMatch && textMatch
    })
  }, [tests, tierFilter, statusFilter, textFilter])

  const handleTestClick = (test: FrontendTest) => {
    setSelectedTest(test)
    setIsModalOpen(true)
  }

  const handleStartTest = (test: FrontendTest) => {
    setIsModalOpen(false)
    onStartTest(test)
  }

  return (
    <>
      <motion.div
        data-testid="testid-tests-tab"
        key="tests"
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
          <h2 className="mb-2 text-2xl font-bold text-gray-900">Available Tests</h2>
          <p className="text-gray-600">
            Tests are unlocked as you progress through levels. Complete tests to earn tier achievements (B, A, S, SS,
            SSS).
          </p>
        </div>

        {/* Filters */}
        <div className="mb-8 rounded-2xl bg-white p-6 shadow-lg">
          <div className="flex flex-wrap gap-4">
            <div className="min-w-[200px] flex-1">
              <label className="mb-2 block text-sm font-medium text-gray-700">Rank/Tier</label>
              <select
                data-testid="testid-test-filter-tier"
                value={tierFilter}
                onChange={(e) => onTierFilterChange(e.target.value as any)}
                className="w-full rounded-xl border border-gray-300 bg-white px-4 py-2 text-gray-900 outline-none focus:border-transparent focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Ranks</option>
                <option value="B">B Rank</option>
                <option value="A">A Rank</option>
                <option value="S">S Rank</option>
                <option value="SS">SS Rank</option>
                <option value="SSS">SSS Rank</option>
              </select>
            </div>
            <div className="min-w-[200px] flex-1">
              <label className="mb-2 block text-sm font-medium text-gray-700">Status</label>
              <select
                data-testid="testid-test-filter-status"
                value={statusFilter}
                onChange={(e) => onStatusFilterChange(e.target.value as any)}
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
                  data-testid="testid-test-search-input"
                  type="text"
                  value={textFilter}
                  onChange={(e) => onTextFilterChange(e.target.value)}
                  placeholder="Search tests..."
                  className="w-full rounded-xl border border-gray-300 bg-white px-4 py-2 pl-10 text-gray-900 outline-none placeholder:text-gray-400 focus:border-transparent focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Test Grid */}
        <div data-testid="testid-test-achievements-grid" className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredTests.map((test, index) => (
            <TestCard
              key={test.test_type}
              test={test}
              index={index}
              onClick={handleTestClick}
              onStartTest={handleStartTest}
            />
          ))}
        </div>

        {filteredTests.length === 0 && (
          <div className="py-16 text-center">
            <AlertCircle className="mx-auto mb-4 h-16 w-16 text-gray-300" />
            <p className="text-lg text-gray-500">No tests match your filters</p>
          </div>
        )}
      </motion.div>

      {/* Test Detail Modal */}
      <TestDetailModal
        test={selectedTest}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onStartTest={handleStartTest}
        getTestAttempts={getTestAttempts}
        getTestAttemptDetail={getTestAttemptDetail}
      />
    </>
  )
}
