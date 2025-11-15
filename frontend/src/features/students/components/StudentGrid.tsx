import StudentCard from './StudentCard'
import type { User } from '../hooks/useStudents'

type StudentGridProps = {
  users: User[]
  selectedUser: User | null
  onSelect: (user: User | null) => void
}

const StudentGrid = ({ users, selectedUser, onSelect }: StudentGridProps) => (
  <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
    {users.map((user, index) => {
      const isSelected = selectedUser?.id === user.id
      return (
        <StudentCard
          key={user.id}
          user={user}
          index={index}
          isSelected={isSelected}
          onClick={() => onSelect(isSelected ? null : user)}
        />
      )
    })}
  </div>
)

export default StudentGrid

