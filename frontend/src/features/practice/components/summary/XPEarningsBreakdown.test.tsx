import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { XPEarningsBreakdown } from './XPEarningsBreakdown'
import type { LevelUpResult } from '../../../types'

// Mock the hooks
vi.mock('../../../../lib/levels/hooks', () => ({
  useAchievementDefinitions: vi.fn(() => ({
    definitions: {
      'first-steps': { title: 'First Steps' },
      'accuracy-ace-gold': { title: 'Accuracy Ace (Gold)' },
      'so-wow-bronze': { title: 'So Wow (Bronze)' },
    },
  })),
}))

vi.mock('../../../students/data/mathConcepts', () => ({
  getConceptDisplayNameByConceptId: vi.fn((id: string) => {
    if (id === 'c_add_1s') return 'Addition by 1s'
    return null
  }),
}))

describe('XPEarningsBreakdown', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders nothing when levelUp is null', () => {
    const { container } = render(<XPEarningsBreakdown levelUp={null} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders nothing when breakdown is missing', () => {
    const levelUp: LevelUpResult = {
      earned_xp: 100,
      leveled_up: false,
    } as LevelUpResult

    const { container } = render(<XPEarningsBreakdown levelUp={levelUp} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders nothing when earned_xp is undefined', () => {
    const levelUp: LevelUpResult = {
      xp_breakdown: {
        base_xp: 100,
        correct_count: 10,
        xp_per_correct: 10,
        concept_id: 'c_add_1s',
      },
    } as LevelUpResult

    const { container } = render(<XPEarningsBreakdown levelUp={levelUp} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders base XP breakdown correctly', () => {
    const levelUp: LevelUpResult = {
      earned_xp: 100,
      leveled_up: false,
      xp_breakdown: {
        base_xp: 100,
        correct_count: 10,
        xp_per_correct: 10,
        concept_id: 'c_add_1s',
        total_multiplier: 1.0,
        bonus_xp: 0,
        multipliers: [],
        bonus_xp_sources: [],
      },
    } as LevelUpResult

    render(<XPEarningsBreakdown levelUp={levelUp} />)

    expect(screen.getByText('XP Earned')).toBeInTheDocument()
    expect(screen.getByText('Base XP')).toBeInTheDocument()
    // "100xp" appears in base XP row
    const baseXpElements = screen.getAllByText('100xp')
    expect(baseXpElements.length).toBeGreaterThan(0)
    expect(screen.getByText(/10 × 10/i)).toBeInTheDocument()
    expect(screen.getByText(/Addition by 1s/i)).toBeInTheDocument()
  })

  it('renders multiplier when present', () => {
    const levelUp: LevelUpResult = {
      earned_xp: 104,
      leveled_up: false,
      xp_breakdown: {
        base_xp: 100,
        correct_count: 10,
        xp_per_correct: 10,
        concept_id: 'c_add_1s',
        total_multiplier: 1.04,
        bonus_xp: 0,
        multipliers: [
          { achievement_code: 'first-steps', multiplier: 0.01 },
          { achievement_code: 'accuracy-ace-gold', multiplier: 0.03 },
        ],
        bonus_xp_sources: [],
      },
    } as LevelUpResult

    render(<XPEarningsBreakdown levelUp={levelUp} />)

    expect(screen.getByText('Multiplier')).toBeInTheDocument()
    expect(screen.getByText('x1.04')).toBeInTheDocument()
    expect(screen.getByText(/2 achievement\(s\)/i)).toBeInTheDocument()
    expect(screen.getByText('First Steps')).toBeInTheDocument()
    expect(screen.getByText('Accuracy Ace (Gold)')).toBeInTheDocument()
  })

  it('renders bonus XP when present', () => {
    const levelUp: LevelUpResult = {
      earned_xp: 112,
      leveled_up: false,
      xp_breakdown: {
        base_xp: 100,
        correct_count: 10,
        xp_per_correct: 10,
        concept_id: 'c_add_1s',
        total_multiplier: 1.0,
        bonus_xp: 12,
        multipliers: [],
        bonus_xp_sources: [
          { achievement_code: 'so-wow-bronze', bonus_xp: 12 },
        ],
      },
    } as LevelUpResult

    render(<XPEarningsBreakdown levelUp={levelUp} />)

    // Check for the main "Bonus XP" label (appears in the summary row)
    const bonusXPElements = screen.getAllByText('Bonus XP')
    expect(bonusXPElements.length).toBeGreaterThan(0)
    
    // Check for the bonus XP value (12xp appears twice - once in summary, once in detail)
    const bonusValues = screen.getAllByText('12xp')
    expect(bonusValues.length).toBeGreaterThan(0)
    
    expect(screen.getByText(/1 achievement\(s\)/i)).toBeInTheDocument()
    expect(screen.getByText('So Wow (Bronze)')).toBeInTheDocument()
  })

  it('renders complete breakdown with multipliers and bonus XP', () => {
    const levelUp: LevelUpResult = {
      earned_xp: 216,
      leveled_up: true,
      xp_breakdown: {
        base_xp: 100,
        correct_count: 10,
        xp_per_correct: 10,
        concept_id: 'c_add_1s',
        total_multiplier: 1.04,
        bonus_xp: 112,
        multiplied_xp: 104,
        multipliers: [
          { achievement_code: 'first-steps', multiplier: 0.01 },
          { achievement_code: 'accuracy-ace-gold', multiplier: 0.03 },
        ],
        bonus_xp_sources: [
          { achievement_code: 'first-steps', bonus_xp: 50 },
          { achievement_code: 'accuracy-ace-gold', bonus_xp: 50 },
          { achievement_code: 'so-wow-bronze', bonus_xp: 12 },
        ],
      },
    } as LevelUpResult

    render(<XPEarningsBreakdown levelUp={levelUp} />)

    // Base XP
    expect(screen.getByText('100xp')).toBeInTheDocument()

    // Multiplier
    expect(screen.getByText('x1.04')).toBeInTheDocument()
    expect(screen.getByText(/2 achievement\(s\)/i)).toBeInTheDocument()

    // Bonus XP
    expect(screen.getByText('112xp')).toBeInTheDocument()
    expect(screen.getByText(/3 achievement\(s\)/i)).toBeInTheDocument()

    // Total
    expect(screen.getByText('216xp')).toBeInTheDocument()
  })

  it('renders "None" when no multipliers or bonus XP', () => {
    const levelUp: LevelUpResult = {
      earned_xp: 100,
      leveled_up: false,
      xp_breakdown: {
        base_xp: 100,
        correct_count: 10,
        xp_per_correct: 10,
        concept_id: 'c_add_1s',
        total_multiplier: 1.0,
        bonus_xp: 0,
        multipliers: [],
        bonus_xp_sources: [],
      },
    } as LevelUpResult

    render(<XPEarningsBreakdown levelUp={levelUp} />)

    expect(screen.getAllByText('None')).toHaveLength(2) // One for multipliers, one for bonus
  })

  it('handles missing achievement definitions gracefully', () => {
    const levelUp: LevelUpResult = {
      earned_xp: 104,
      leveled_up: false,
      xp_breakdown: {
        base_xp: 100,
        correct_count: 10,
        xp_per_correct: 10,
        concept_id: 'c_add_1s',
        total_multiplier: 1.04,
        bonus_xp: 0,
        multipliers: [
          { achievement_code: 'unknown-achievement', multiplier: 0.04 },
        ],
        bonus_xp_sources: [],
      },
    } as LevelUpResult

    render(<XPEarningsBreakdown levelUp={levelUp} />)

    // Should fall back to achievement code if definition not found
    expect(screen.getByText('unknown-achievement')).toBeInTheDocument()
  })

  it('handles missing concept display name gracefully', () => {
    const levelUp: LevelUpResult = {
      earned_xp: 100,
      leveled_up: false,
      xp_breakdown: {
        base_xp: 100,
        correct_count: 10,
        xp_per_correct: 10,
        concept_id: 'unknown-concept',
        total_multiplier: 1.0,
        bonus_xp: 0,
        multipliers: [],
        bonus_xp_sources: [],
      },
    } as LevelUpResult

    render(<XPEarningsBreakdown levelUp={levelUp} />)

    // Should show concept_id if display name not found
    expect(screen.getByText(/unknown-concept/i)).toBeInTheDocument()
  })
})

