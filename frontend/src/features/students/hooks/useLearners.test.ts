import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { useLearners } from './useLearners'
import * as learnersHook from '../../../lib/learners/hooks'
import * as learnersAPI from '../../../lib/learners/api'

// Mock dependencies
vi.mock('../../../lib/learners/hooks')
vi.mock('../../../lib/learners/api')

const mockUser = {
  id: '1',
  name: 'Test User',
  avatar: '👧',
  level: 1,
  questionsAnswered: 0,
  averageSpeed: 0,
  stats: {
    currentStreak: 0,
    bestStreak: 0,
    additionAccuracy: 0,
    subtractionAccuracy: 0,
    multiplicationAccuracy: 0,
    divisionAccuracy: 0,
    additionSpeed: 0,
    subtractionSpeed: 0,
    multiplicationSpeed: 0,
    divisionSpeed: 0,
  },
  achievements: [],
}

describe('useLearners', () => {
  const mockRefetch = vi.fn()
  const mockRefetchFullData = vi.fn()
  const mockFetchUserFullData = vi.fn()
  const mockSetLearners = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()

    vi.mocked(learnersHook.useLearners).mockReturnValue({
      learners: [mockUser],
      isLoading: false,
      isLoadingFullData: false,
      error: null,
      refetch: mockRefetch,
      refetchFullData: mockRefetchFullData,
      fetchUserFullData: vi.fn().mockResolvedValue(mockUser),
      setLearners: mockSetLearners,
    })

    vi.mocked(learnersAPI.mapApiLearner).mockImplementation((user: any) => user)
  })

  it('should initialize with default state', () => {
    const { result } = renderHook(() => useLearners())

    expect(result.current.state.users).toEqual([mockUser])
    expect(result.current.state.selectedUser).toBeNull()
    expect(result.current.state.showAddUser).toBe(false)
    expect(result.current.state.filterCategory).toBe('all')
    expect(result.current.state.filterLevel).toBe('all')
    expect(result.current.state.isLoadingUsers).toBe(false)
    expect(result.current.state.loadError).toBeNull()
  })

  it('should set selected user', () => {
    const { result } = renderHook(() => useLearners())

    act(() => {
      result.current.actions.setSelectedUser(mockUser)
    })

    expect(result.current.state.selectedUser).toEqual(mockUser)
  })

  it('should clear selected user if user is removed from learners list', () => {
    const { result, rerender } = renderHook(() => useLearners())

    act(() => {
      result.current.actions.setSelectedUser(mockUser)
    })

    // Update mock to return empty learners
    vi.mocked(learnersHook.useLearners).mockReturnValue({
      learners: [],
      isLoading: false,
      isLoadingFullData: false,
      error: null,
      refetch: mockRefetch,
      refetchFullData: mockRefetchFullData,
      fetchUserFullData: vi.fn().mockResolvedValue(mockUser),
      setLearners: mockSetLearners,
    })

    rerender()

    expect(result.current.state.selectedUser).toBeNull()
  })

  it('should update selected user when learners list updates', () => {
    const { result, rerender } = renderHook(() => useLearners())

    act(() => {
      result.current.actions.setSelectedUser(mockUser)
    })

    const updatedUser = { ...mockUser, name: 'Updated User' }

    vi.mocked(learnersHook.useLearners).mockReturnValue({
      learners: [updatedUser],
      isLoading: false,
      isLoadingFullData: false,
      error: null,
      refetch: mockRefetch,
      refetchFullData: mockRefetchFullData,
      fetchUserFullData: vi.fn().mockResolvedValue(updatedUser),
      setLearners: mockSetLearners,
    })

    rerender()

    expect(result.current.state.selectedUser?.name).toBe('Updated User')
  })

  it('should toggle showAddUser', () => {
    const { result } = renderHook(() => useLearners())

    act(() => {
      result.current.actions.setShowAddUser(true)
    })

    expect(result.current.state.showAddUser).toBe(true)

    act(() => {
      result.current.actions.setShowAddUser(false)
    })

    expect(result.current.state.showAddUser).toBe(false)
  })

  it('should set filter category', () => {
    const { result } = renderHook(() => useLearners())

    act(() => {
      result.current.actions.setFilterCategory('speed')
    })

    expect(result.current.state.filterCategory).toBe('speed')
  })

  it('should set filter level', () => {
    const { result } = renderHook(() => useLearners())

    act(() => {
      result.current.actions.setFilterLevel('2')
    })

    expect(result.current.state.filterLevel).toBe('2')
  })

  it('should update new user state', () => {
    const { result } = renderHook(() => useLearners())

    act(() => {
      result.current.actions.setNewUser({
        name: 'New User',
        avatar: '👦',
        pin: '1234',
      })
    })

    expect(result.current.state.newUser.name).toBe('New User')
    expect(result.current.state.newUser.avatar).toBe('👦')
    expect(result.current.state.newUser.pin).toBe('1234')
  })

  it('should create user successfully', async () => {
    const newUserData = {
      name: 'New User',
      avatar: '👦',
      pin: '1234',
    }

    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ...mockUser, ...newUserData, id: '2' }),
    } as Response)

    const { result } = renderHook(() => useLearners())

    act(() => {
      result.current.actions.setNewUser(newUserData)
    })

    await act(async () => {
      await result.current.actions.handleAddUser()
    })

    expect(mockSetLearners).toHaveBeenCalled()
    expect(result.current.state.newUser.name).toBe('')
    expect(result.current.state.showAddUser).toBe(false)
  })

  it('should not create user with invalid data', async () => {
    const { result } = renderHook(() => useLearners())

    act(() => {
      result.current.actions.setNewUser({
        name: '',
        avatar: '👦',
        pin: '1234',
      })
    })

    await act(async () => {
      await result.current.actions.handleAddUser()
    })

    expect(mockSetLearners).not.toHaveBeenCalled()
  })

  it('should handle creation errors', async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: false,
      json: async () => ({ errors: ['User already exists'] }),
    } as Response)

    const { result } = renderHook(() => useLearners())

    act(() => {
      result.current.actions.setNewUser({
        name: 'Duplicate User',
        avatar: '👦',
        pin: '1234',
      })
    })

    await act(async () => {
      await result.current.actions.handleAddUser()
    })

    expect(result.current.state.creationError).toBe('User already exists')
    expect(result.current.state.isCreatingUser).toBe(false)
  })

  it('should filter achievements by category', () => {
    const userWithAchievements = {
      ...mockUser,
      achievements: [
        { id: '1', category: 'speed', earnedAt: new Date() },
        { id: '2', category: 'accuracy', earnedAt: new Date() },
      ],
    }

    vi.mocked(learnersHook.useLearners).mockReturnValue({
      learners: [userWithAchievements],
      isLoading: false,
      isLoadingFullData: false,
      error: null,
      refetch: mockRefetch,
      refetchFullData: mockRefetchFullData,
      fetchUserFullData: vi.fn().mockResolvedValue(userWithAchievements),
      setLearners: mockSetLearners,
    })

    const { result } = renderHook(() => useLearners())

    act(() => {
      result.current.actions.setSelectedUser(userWithAchievements)
      result.current.actions.setFilterCategory('speed')
    })

    expect(result.current.state.filteredAchievements).toHaveLength(1)
    expect(result.current.state.filteredAchievements[0].category).toBe('speed')
  })

  it('should calculate all achievements correctly', () => {
    const user1 = {
      ...mockUser,
      id: '1',
      name: 'User 1',
      achievements: [{ id: 'a1', category: 'speed', earnedAt: new Date('2024-01-01') }],
    }

    const user2 = {
      ...mockUser,
      id: '2',
      name: 'User 2',
      achievements: [{ id: 'a2', category: 'accuracy', earnedAt: new Date('2024-01-02') }],
    }

    vi.mocked(learnersHook.useLearners).mockReturnValue({
      learners: [user1, user2],
      isLoading: false,
      isLoadingFullData: false,
      error: null,
      refetch: mockRefetch,
      refetchFullData: mockRefetchFullData,
      fetchUserFullData: mockFetchUserFullData,
      setLearners: mockSetLearners,
    })

    const { result } = renderHook(() => useLearners())

    expect(result.current.state.allAchievements).toHaveLength(2)
    expect(result.current.state.allAchievements[0].userName).toBe('User 2') // Sorted by date
  })

  it('should refetch users', async () => {
    const { result } = renderHook(() => useLearners())

    await act(async () => {
      await result.current.actions.refetchUsers()
    })

    expect(mockRefetch).toHaveBeenCalled()
  })

  it('should refetch full data', async () => {
    const { result } = renderHook(() => useLearners())

    await act(async () => {
      await result.current.actions.refetchFullData()
    })

    expect(mockRefetchFullData).toHaveBeenCalled()
  })
})
