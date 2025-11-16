import { useEffect, useMemo, useState } from 'react'

import type { PracticeMode, User } from '../types'

type UsePracticeRoutingResult = {
  selectedUser: User | null
  setSelectedUser: (user: User | null) => void
  practiceMode: PracticeMode
  setPracticeMode: (mode: PracticeMode) => void
}

export const usePracticeRouting = (users: User[]): UsePracticeRoutingResult => {
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [hasAppliedShareLink, setHasAppliedShareLink] = useState(false)

  const [practiceMode, setPracticeMode] = useState<PracticeMode>(() => {
    const modeParam = new URLSearchParams(window.location.search).get('mode')
    if (modeParam === 'multiplication' || modeParam === 'division') {
      return modeParam
    }
    return 'standard'
  })

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

  // Keep the mode reflected in the URL so it can be shared / refreshed
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    if (practiceMode === 'multiplication' || practiceMode === 'division') {
      params.set('mode', practiceMode)
    } else {
      params.delete('mode')
    }
    const nextQuery = params.toString()
    const nextUrl = `${window.location.pathname}${nextQuery ? `?${nextQuery}` : ''}`
    window.history.replaceState({}, '', nextUrl)
  }, [practiceMode])

  return {
    selectedUser,
    setSelectedUser,
    practiceMode,
    setPracticeMode,
  }
}


