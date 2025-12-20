import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { EncouragementBanner } from './EncouragementBanner'
import type { LevelUpResult } from '../../types'

describe('EncouragementBanner', () => {
  it('only shows level-up message when leveled_up is true', () => {
    const notLeveled: LevelUpResult = { new_level: 2, previous_level: 1, leveled_up: false }
    render(<EncouragementBanner accuracy={90} totalProblems={10} totalTime={25} levelUp={notLeveled} />)
    expect(screen.queryByText(/leveled up/i)).toBeNull()

    const leveled: LevelUpResult = { new_level: 2, previous_level: 1, leveled_up: true }
    render(<EncouragementBanner accuracy={90} totalProblems={10} totalTime={25} levelUp={leveled} />)
    expect(screen.getByText(/you've leveled up/i)).toBeTruthy()
  })
})

