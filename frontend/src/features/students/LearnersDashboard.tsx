import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { Plus, RotateCcw, X } from 'lucide-react'
import PageLayout from '../../layouts/PageLayout'
import LearnerDetailLayout from '../../layouts/LearnerDetailLayout'
import LearnerGrid from './components/LearnerGrid'
import LearnerStatsCards from './components/LearnerStatsCards'
import AccuracyChart from './components/AccuracyChart'
import SpeedChart from './components/SpeedChart'
import AchievementsList from './components/AchievementsList'
import AddLearnerModal from './modals/AddLearnerModal'
import PINVerificationModal from './modals/PINVerificationModal'
import JourneyModal from './modals/JourneyModal'
import { useLearners } from './hooks/useLearners'
import { PillButton } from '../../components/ui'

const LearnersDashboard = () => {
  const {
    state: {
      users,
      selectedUser,
      showAddUser,
      filterCategory,
      filterLevel,
      newUser,
      isLoadingUsers,
      isLoadingFullData,
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
  } = useLearners()

  const [showPinModal, setShowPinModal] = useState(false)
  const [showJourneyModal, setShowJourneyModal] = useState(false)
  const [isResetting, setIsResetting] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  // Check if dev mode is enabled via URL parameter
  const isDevMode = useMemo(() => {
    const params = new URLSearchParams(window.location.search)
    return params.get('env') === 'dev'
  }, [])

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

  const handleResetUser = async () => {
    if (!selectedUser || !isDevMode) return
    
    const confirmed = window.confirm(
      `⚠️ DEV MODE: This will permanently delete ALL data for ${selectedUser.name}:\n\n` +
      `- All achievements\n` +
      `- All practice sessions\n` +
      `- All answered questions\n` +
      `- All daily stats\n` +
      `- Reset level to 1\n\n` +
      `This cannot be undone. Continue?`
    )
    
    if (!confirmed) return

    setIsResetting(true)
    try {
      const response = await fetch(`/api/users/${selectedUser.id}/reset`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Failed to reset user data')
      }

      // Refresh user data
      await refetchUsers()
      
      // Show success message
      alert(`✅ User data reset successfully! ${selectedUser.name} has been reset to level 1.`)
    } catch (error) {
      console.error('Error resetting user:', error)
      alert(`❌ Failed to reset user data: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsResetting(false)
    }
  }

  const handleDeleteUser = async () => {
    if (!selectedUser || !isDevMode) return
    
    const confirmed = window.confirm(
      `⚠️ DEV MODE: This will PERMANENTLY DELETE ${selectedUser.name}:\n\n` +
      `- The user account will be completely removed\n` +
      `- All achievements will be deleted\n` +
      `- All practice sessions will be deleted\n` +
      `- All answered questions will be deleted\n` +
      `- All daily stats will be deleted\n\n` +
      `This cannot be undone. Continue?`
    )
    
    if (!confirmed) return

    setIsDeleting(true)
    try {
      const response = await fetch(`/api/users/${selectedUser.id}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Failed to delete user')
      }

      // Clear selected user and refresh user data
      setSelectedUser(null)
      await refetchUsers()
      
      // Show success message
      alert(`✅ User ${selectedUser.name} has been permanently deleted.`)
    } catch (error) {
      console.error('Error deleting user:', error)
      alert(`❌ Failed to delete user: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <>
      <PageLayout
        title="Math Helper"
        subtitle="Choose your learner to begin practice"
        cta={
          <PillButton 
            onClick={handleOpenModal} 
            className="ml-auto" 
            tone="indigo" 
            leftIcon={<Plus className="h-4 w-4" />}
            data-testid="testid-add-learner-button"
          >
            Add Learner
          </PillButton>
        }
      >
        <motion.h2 
          initial={{ opacity: 0, y: -8 }} 
          animate={{ opacity: 1, y: 0 }} 
          className="mb-4 text-xl font-semibold text-slate-900"
          data-testid="testid-select-learner-header"
        >
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
            <p>No learners yet. Use "Add Learner" to create the first one.</p>
          </div>
        )}

        {!isLoadingUsers && !loadError && users.length > 0 && (
          <LearnerGrid users={users} selectedUser={selectedUser} onSelect={setSelectedUser} />
        )}

        {selectedUser && (
          <LearnerDetailLayout
            title={`${selectedUser.name}'s progress`}
            action={
              <div className="flex items-center gap-3">
                {isDevMode && (
                  <>
                    <PillButton
                      onClick={handleResetUser}
                      tone="red"
                      disabled={isResetting || isDeleting}
                      leftIcon={<RotateCcw className="h-4 w-4" />}
                    >
                      {isResetting ? 'Resetting...' : 'Reset User (Dev)'}
                    </PillButton>
                    <PillButton
                      onClick={handleDeleteUser}
                      tone="red"
                      disabled={isResetting || isDeleting}
                      leftIcon={<X className="h-4 w-4" />}
                    >
                      {isDeleting ? 'Deleting...' : 'Delete User (Dev)'}
                    </PillButton>
                  </>
                )}
                <PillButton 
                  onClick={handleStartPractice} 
                  tone="emerald"
                  data-testid="testid-start-practice-button"
                >
                  Start Practice
                </PillButton>
              </div>
            }
          >
            <LearnerStatsCards user={selectedUser} onLevelCardClick={() => setShowJourneyModal(true)} />

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
          </LearnerDetailLayout>
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

      <AddLearnerModal
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

      <JourneyModal 
        isOpen={showJourneyModal} 
        onClose={() => setShowJourneyModal(false)} 
        user={selectedUser}
        isLoadingFullData={isLoadingFullData}
      />
    </>
  )
}

export default LearnersDashboard

