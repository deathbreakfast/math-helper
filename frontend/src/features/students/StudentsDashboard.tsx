import { useState } from 'react'
import { motion } from 'framer-motion'
import { Plus } from 'lucide-react'
import PageLayout from '../../layouts/PageLayout'
import StudentDetailLayout from '../../layouts/StudentDetailLayout'
import StudentGrid from './components/StudentGrid'
import StudentStatsCards from './components/StudentStatsCards'
import AccuracyChart from './components/AccuracyChart'
import SpeedChart from './components/SpeedChart'
import AchievementsList from './components/AchievementsList'
import AddStudentModal from './modals/AddStudentModal'
import PINVerificationModal from './modals/PINVerificationModal'
import JourneyModal from './modals/JourneyModal'
import { useStudents } from './hooks/useStudents'
import { PillButton } from '../../components/ui'

const StudentsDashboard = () => {
  const {
    state: {
      users,
      selectedUser,
      showAddUser,
      filterCategory,
      filterLevel,
      newUser,
      isLoadingUsers,
      loadError,
      creationError,
      isCreatingUser,
      displayAchievements,
      allAchievements,
    },
    actions: {
      setSelectedUser,
      setShowAddUser,
      setFilterCategory,
      setFilterLevel,
      setNewUser,
      setCreationError,
      handleAddUser,
      refetchUsers,
    },
  } = useStudents()

  const [showPinModal, setShowPinModal] = useState(false)
  const [showJourneyModal, setShowJourneyModal] = useState(false)

  const handleOpenModal = () => {
    setCreationError(null)
    setShowAddUser(true)
  }

  const handleCloseModal = () => {
    setCreationError(null)
    setShowAddUser(false)
  }

  const showEmptyState = !isLoadingUsers && !loadError && users.length === 0

  const handleStartPractice = () => {
    if (!selectedUser) return
    setShowPinModal(true)
  }

  const handleClosePinModal = () => {
    setShowPinModal(false)
  }

  const handlePinVerified = (pin: string) => {
    if (!selectedUser) return
    setShowPinModal(false)

    const params = new URLSearchParams({
      user: selectedUser.name,
      pin,
      userId: selectedUser.id,
      avatar: selectedUser.avatar,
    })

    window.location.assign(`/practice?${params.toString()}`)
  }

  return (
    <>
      <PageLayout
        title="Math Helper"
        subtitle="Choose your learner to begin practice"
        cta={
          <PillButton onClick={handleOpenModal} className="ml-auto" tone="indigo" leftIcon={<Plus className="h-4 w-4" />}>
            Add Learner
          </PillButton>
        }
      >
        <motion.h2 initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className="mb-4 text-xl font-semibold text-slate-900">
          Select Learner
        </motion.h2>

        {isLoadingUsers && (
          <div className="rounded-2xl bg-white p-6 text-center text-slate-500 shadow-card">Loading learners…</div>
        )}

        {!isLoadingUsers && loadError && (
          <div className="rounded-2xl border border-red-100 bg-red-50 p-6 text-center text-red-700 shadow-card">
            <p>{loadError}</p>
            <button
              onClick={refetchUsers}
              className="mt-4 rounded-xl bg-red-600 px-4 py-2 text-sm font-semibold text-white shadow transition hover:bg-red-700"
            >
              Try again
            </button>
          </div>
        )}

        {!isLoadingUsers && !loadError && users.length === 0 && (
          <div className="rounded-2xl bg-white p-8 text-center text-slate-500 shadow-card">
            <p>No learners yet. Use “Add Learner” to create the first one.</p>
          </div>
        )}

        {!isLoadingUsers && !loadError && users.length > 0 && (
          <StudentGrid users={users} selectedUser={selectedUser} onSelect={setSelectedUser} />
        )}

        {selectedUser && (
          <StudentDetailLayout
            title={`${selectedUser.name}'s progress`}
            action={
              <PillButton onClick={handleStartPractice} tone="emerald">
                Start Practice
              </PillButton>
            }
          >
            <StudentStatsCards user={selectedUser} onLevelCardClick={() => setShowJourneyModal(true)} />

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3 xl:grid-cols-6">
              <div className="lg:col-span-2 xl:col-span-4">
                <AccuracyChart user={selectedUser} filterLevel={filterLevel} onFilterChange={setFilterLevel} />
              </div>
              <div className="lg:col-span-1 xl:col-span-4">
                <SpeedChart user={selectedUser} filterLevel={filterLevel} onFilterChange={setFilterLevel} />
              </div>
              <div className="lg:col-span-3 xl:col-span-4">
                <AchievementsList
                  title="Recent achievements"
                  achievements={displayAchievements}
                  filterCategory={filterCategory}
                  onFilterChange={setFilterCategory}
                  filterOptions={['all', 'speed', 'consistency', 'milestone']}
                  isLoading={isLoadingUsers}
                />
              </div>
            </div>
          </StudentDetailLayout>
        )}

        {!selectedUser && (
          <AchievementsList
            title="Recent achievements (all learners)"
            achievements={allAchievements.slice(0, 6)}
            layout="grid"
            isLoading={isLoadingUsers || Boolean(loadError) || showEmptyState}
            emptyMessage={loadError || 'No achievements yet. Keep practicing!'}
          />
        )}
      </PageLayout>

      <AddStudentModal
        isOpen={showAddUser}
        onClose={handleCloseModal}
        newUser={newUser}
        setNewUser={setNewUser}
        onAddUser={handleAddUser}
        isSubmitting={isCreatingUser}
        errorMessage={creationError}
      />

      <PINVerificationModal
        isOpen={showPinModal}
        onClose={handleClosePinModal}
        onVerified={handlePinVerified}
        selectedUser={selectedUser}
      />

      <JourneyModal isOpen={showJourneyModal} onClose={() => setShowJourneyModal(false)} user={selectedUser} />
    </>
  )
}

export default StudentsDashboard

