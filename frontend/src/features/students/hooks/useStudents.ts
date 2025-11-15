import { useCallback, useEffect, useMemo, useState } from 'react'

export type UserStats = {
  additionAccuracy: number
  subtractionAccuracy: number
  multiplicationAccuracy: number
  divisionAccuracy: number
  additionSpeed: number
  subtractionSpeed: number
  multiplicationSpeed: number
  divisionSpeed: number
  currentStreak: number
  bestStreak: number
}

export type Achievement = {
  id: string
  title: string
  description: string
  icon: string
  earnedAt: Date
  category: string
}

export type User = {
  id: string
  name: string
  avatar: string
  pin: string
  level: number
  questionsAnswered: number
  weeklyGain?: number
  averageSpeed: number
  achievements: Achievement[]
  stats: UserStats
}

type ApiAchievement = Omit<Achievement, 'earnedAt'> & {
  earnedAt: string
}

type ApiUser = {
  id: number
  name: string
  avatar: string
  pin: string
  level: number
  questionsAnswered: number
  averageSpeed: number
  stats: Partial<UserStats>
  achievements: ApiAchievement[]
}

export const AVATAR_OPTIONS = ['👧', '👦', '🧒', '👨', '👩', '🧑', '👶', '🦸', '🦹', '🧙', '🧚', '🦄']

const INITIAL_NEW_USER = {
  name: '',
  avatar: AVATAR_OPTIONS[0],
  pin: '',
}

const sanitizeStats = (stats: Partial<UserStats> | undefined): UserStats => ({
  additionAccuracy: stats?.additionAccuracy ?? 0,
  subtractionAccuracy: stats?.subtractionAccuracy ?? 0,
  multiplicationAccuracy: stats?.multiplicationAccuracy ?? 0,
  divisionAccuracy: stats?.divisionAccuracy ?? 0,
  additionSpeed: stats?.additionSpeed ?? 0,
  subtractionSpeed: stats?.subtractionSpeed ?? 0,
  multiplicationSpeed: stats?.multiplicationSpeed ?? 0,
  divisionSpeed: stats?.divisionSpeed ?? 0,
  currentStreak: stats?.currentStreak ?? 0,
  bestStreak: stats?.bestStreak ?? 0,
})

const mapAchievement = (achievement: ApiAchievement): Achievement => ({
  ...achievement,
  earnedAt: achievement.earnedAt ? new Date(achievement.earnedAt) : new Date(),
})

const mapUser = (payload: ApiUser): User => ({
  id: String(payload.id),
  name: payload.name,
  avatar: payload.avatar || AVATAR_OPTIONS[0],
  pin: payload.pin,
  level: payload.level ?? 1,
  questionsAnswered: payload.questionsAnswered ?? 0,
  weeklyGain: 0,
  averageSpeed: payload.averageSpeed ?? 0,
  achievements: (payload.achievements || []).map(mapAchievement),
  stats: sanitizeStats(payload.stats),
})

export const useStudents = () => {
  const [users, setUsers] = useState<User[]>([])
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [showAddUser, setShowAddUser] = useState(false)
  const [filterCategory, setFilterCategory] = useState<string>('all')
  const [filterLevel, setFilterLevel] = useState<string>('all')
  const [newUser, setNewUser] = useState(INITIAL_NEW_USER)
  const [isLoadingUsers, setIsLoadingUsers] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [creationError, setCreationError] = useState<string | null>(null)
  const [isCreatingUser, setIsCreatingUser] = useState(false)

  const fetchUsers = useCallback(async () => {
    setIsLoadingUsers(true)
    setLoadError(null)
    try {
      const response = await fetch('/api/users')
      if (!response.ok) {
        throw new Error('Unable to load learners. Please try again.')
      }
      const data = await response.json()
      const parsedUsers = Array.isArray(data.users) ? data.users.map(mapUser) : []
      setUsers(parsedUsers)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unable to load learners.'
      setLoadError(message)
      setUsers([])
    } finally {
      setIsLoadingUsers(false)
    }
  }, [])

  useEffect(() => {
    fetchUsers()
  }, [fetchUsers])

  useEffect(() => {
    if (selectedUser && !users.some((user) => user.id === selectedUser.id)) {
      setSelectedUser(null)
    }
  }, [selectedUser, users])

  const handleAddUser = async () => {
    if (!newUser.name.trim() || newUser.pin.length !== 4) {
      return
    }

    setCreationError(null)
    setIsCreatingUser(true)

    try {
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newUser.name.trim(),
          avatar: newUser.avatar,
          pin: newUser.pin,
        }),
      })

      const result = await response.json()

      if (!response.ok) {
        const apiErrors = Array.isArray(result.errors) ? result.errors.join(' ') : 'Unable to create learner.'
        setCreationError(apiErrors)
        return
      }

      const createdUser = mapUser(result)
      setUsers((prev) => [...prev, createdUser])
      setNewUser(INITIAL_NEW_USER)
      setShowAddUser(false)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unable to create learner.'
      setCreationError(message)
    } finally {
      setIsCreatingUser(false)
    }
  }

  const allAchievements = useMemo(
    () =>
      users
        .flatMap((user) =>
          user.achievements.map((achievement) => ({
            ...achievement,
            userName: user.name,
          })),
        )
        .sort((a, b) => b.earnedAt.getTime() - a.earnedAt.getTime()),
    [users],
  )

  const filteredAchievements = useMemo(
    () =>
      selectedUser?.achievements.filter(
        (achievement) => filterCategory === 'all' || achievement.category === filterCategory,
      ) || [],
    [selectedUser, filterCategory],
  )

  const displayAchievements = selectedUser ? filteredAchievements : allAchievements.slice(0, 6)

  return {
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
      filteredAchievements,
      allAchievements,
      displayAchievements,
    },
    actions: {
      setSelectedUser,
      setShowAddUser,
      setFilterCategory,
      setFilterLevel,
      setNewUser,
      setCreationError,
      handleAddUser,
      refetchUsers: fetchUsers,
    },
  }
}

