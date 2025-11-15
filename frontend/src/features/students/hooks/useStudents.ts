import { useEffect, useMemo, useState } from 'react'

import { useLearners } from '../../../lib/learners/hooks'
import { AVATAR_OPTIONS, mapApiLearner } from '../../../lib/learners/api'
import type { Learner, LearnerAchievement, LearnerStats } from '../../../lib/learners/types'

export type UserStats = LearnerStats
export type Achievement = LearnerAchievement
export type User = Learner

const INITIAL_NEW_USER = {
  name: '',
  avatar: AVATAR_OPTIONS[0],
  pin: '',
}

export const useStudents = () => {
  const { learners, isLoading, error, refetch, setLearners } = useLearners()
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [showAddUser, setShowAddUser] = useState(false)
  const [filterCategory, setFilterCategory] = useState<string>('all')
  const [filterLevel, setFilterLevel] = useState<string>('all')
  const [newUser, setNewUser] = useState(INITIAL_NEW_USER)
  const [creationError, setCreationError] = useState<string | null>(null)
  const [isCreatingUser, setIsCreatingUser] = useState(false)

  useEffect(() => {
    if (selectedUser && !learners.some((user) => user.id === selectedUser.id)) {
      setSelectedUser(null)
    }
  }, [selectedUser, learners])

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

      const createdUser = mapApiLearner(result)
      setLearners((prev) => [...prev, createdUser])
      setNewUser(INITIAL_NEW_USER)
      setShowAddUser(false)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unable to create learner.'
      setCreationError(message)
    } finally {
      setIsCreatingUser(false)
    }
  }

  const users = learners
  const isLoadingUsers = isLoading
  const loadError = error

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
      refetchUsers: refetch,
    },
  }
}

