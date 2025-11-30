import { useEffect, useMemo, useState, useRef } from 'react'

import { useLearners as useLearnersHook } from '../../../lib/learners/hooks'
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

export const useLearners = () => {
  const { learners, isLoading, isLoadingFullData, error, refetch, refetchFullData, fetchUserFullData, setLearners } = useLearnersHook()
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [showAddUser, setShowAddUser] = useState(false)
  const [filterCategory, setFilterCategory] = useState<string>('all')
  const [filterLevel, setFilterLevel] = useState<string>('all')
  const [newUser, setNewUser] = useState(INITIAL_NEW_USER)
  const [creationError, setCreationError] = useState<string | null>(null)
  const [isCreatingUser, setIsCreatingUser] = useState(false)
  
  // Track which users we've already fetched full data for to avoid infinite loops
  const fetchedFullDataFor = useRef<Set<string>>(new Set())
  // Track if we're currently fetching to avoid duplicate requests
  const isFetchingFullData = useRef<boolean>(false)

  useEffect(() => {
    if (selectedUser && !learners.some((user) => user.id === selectedUser.id)) {
      setSelectedUser(null)
    } else if (selectedUser) {
      // Update selectedUser to point to the latest data from learners array
      // This ensures selectedUser has full data (including PIN) after refetchFullData
      const updatedUser = learners.find((user) => user.id === selectedUser.id)
      if (updatedUser && updatedUser !== selectedUser) {
        setSelectedUser(updatedUser)
      }
    }
  }, [selectedUser, learners])

  // When a user is selected, fetch full data if we only have minimal data
  // Use single-user endpoint instead of fetching all users (optimized for journey modal)
  // Only fetch once per user to avoid infinite loops
  useEffect(() => {
    if (selectedUser && !isFetchingFullData.current) {
      const currentUser = learners.find(u => u.id === selectedUser.id)
      
      // Only fetch if:
      // 1. User exists in learners list
      // 2. We haven't fetched full data for this user yet
      // 3. We're not currently fetching
      // 4. User has minimal data (no achievements or stats indicate minimal data)
      const hasMinimalData = currentUser && (
        currentUser.achievements.length === 0 || 
        (currentUser.questionsAnswered === 0 && currentUser.averageSpeed === 0)
      )
      
      if (currentUser && !fetchedFullDataFor.current.has(selectedUser.id) && hasMinimalData) {
        isFetchingFullData.current = true
        fetchedFullDataFor.current.add(selectedUser.id)
        
        // Use single-user endpoint instead of fetching all users
        fetchUserFullData(selectedUser.id).finally(() => {
          isFetchingFullData.current = false
        })
      }
    }
  }, [selectedUser?.id, fetchUserFullData, learners]) // Only depend on selectedUser.id, not the whole object

  const handleAddUser = async (userData?: { name: string; avatar: string; pin: string }) => {
    const userToAdd = userData || newUser
    
    if (!userToAdd.name.trim() || userToAdd.pin.length !== 4) {
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
          name: userToAdd.name.trim(),
          avatar: userToAdd.avatar,
          pin: userToAdd.pin,
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
      isLoadingFullData,
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

