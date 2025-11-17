import ModalShell from '../../../components/ModalShell'
import { LevelProgressionSystem } from '../components/LevelProgressionSystem'
import { mapUserToProgressData } from '../utils/progressMapping'
import type { User } from '../hooks/useStudents'

type JourneyModalProps = {
  isOpen: boolean
  onClose: () => void
  user: User | null
}

const JourneyModal = ({ isOpen, onClose, user }: JourneyModalProps) => {
  const userProgressData = user ? mapUserToProgressData(user) : undefined

  return (
    <ModalShell
      isOpen={isOpen}
      onClose={onClose}
      maxWidth="xl"
      paddingClassName="p-0"
      showCloseButton={false}
      cardClassName="max-h-[90vh] overflow-hidden"
      overlayClassName="bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50"
    >
      <div className="max-h-[90vh] overflow-y-auto">
        <LevelProgressionSystem userData={userProgressData} onBack={onClose} />
      </div>
    </ModalShell>
  )
}

export default JourneyModal

