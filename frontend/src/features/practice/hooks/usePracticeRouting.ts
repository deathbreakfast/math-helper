import { useEffect, useMemo, useState } from 'react'

import type { PracticeMode, User } from '../types'

type UsePracticeRoutingResult = {
  selectedUser: User | null
  setSelectedUser: (user: User | null) => void
  practiceMode: PracticeMode
}

export const usePracticeRouting = (users: User[]): UsePracticeRoutingResult => {
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [hasAppliedShareLink, setHasAppliedShareLink] = useState(false)

  // Mode is now determined by the session service based on user level
  // Default to 'standard' and let the backend decide operations
  const [practiceMode] = useState<PracticeMode>('standard')

  const searchParams = useMemo(() => new URLSearchParams(window.location.search), [])

  // Default to the first learner when data loads
  useEffect(() => {
    if (!selectedUser && users.length > 0) {
      setSelectedUser(users[0])
    }
  }, [users, selectedUser])

  // Clear selection if the user disappears from the list
  useEffect(() => {
    if (selectedUser && !users.some((user) => user.id === selectedUser.id)) {
      setSelectedUser(null)
    }
  }, [selectedUser, users])

  // Apply share-link parameters once when learners are available
  useEffect(() => {
    if (hasAppliedShareLink || users.length === 0) return

    const sharedUserId = searchParams.get('userId')
    const sharedName = searchParams.get('user')
    let match: User | null = null

    if (sharedUserId) {
      match = users.find((user) => user.id === sharedUserId) ?? null
    }

    if (!match && sharedName) {
      match =
        users.find((user) => user.name.toLowerCase() === sharedName.toLowerCase()) ??
        null
    }

    if (match) {
      setSelectedUser(match)
    }

    setHasAppliedShareLink(true)
  }, [hasAppliedShareLink, searchParams, users, selectedUser])

  return {
    selectedUser,
    setSelectedUser,
    practiceMode,
  }
}


