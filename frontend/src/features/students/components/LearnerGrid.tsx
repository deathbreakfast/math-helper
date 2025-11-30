import LearnerCard from './LearnerCard'
import type { User } from '../hooks/useLearners'

type LearnerGridProps = {
  users: User[]
  selectedUser: User | null
  onSelect: (user: User | null) => void
}

const LearnerGrid = ({ users, selectedUser, onSelect }: LearnerGridProps) => (
  <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6" data-testid="testid-student-grid">
    {users.map((user, index) => {
      const isSelected = selectedUser?.id === user.id
      return (
        <LearnerCard
          key={user.id}
          user={user}
          index={index}
          isSelected={isSelected}
          onClick={() => onSelect(isSelected ? null : user)}
          data-testid={`testid-student-card-${user.id}`}
        />
      )
    })}
  </div>
)

export default LearnerGrid

