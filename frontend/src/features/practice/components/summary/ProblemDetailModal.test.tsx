import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ProblemDetailModal } from './ProblemDetailModal'
import type { ProblemResult } from '../../../hooks/useSummaryData'

// Mock framer-motion to avoid animation issues in tests
vi.mock('framer-motion', async () => {
  const actual = await vi.importActual('framer-motion')
  return {
    ...actual,
    motion: {
      div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    },
    AnimatePresence: ({ children }: any) => children,
  }
})

describe('ProblemDetailModal', () => {
  const mockProblem: ProblemResult = {
    id: '1',
    operand1: 5,
    operand2: 3,
    operation: 'addition',
    correctAnswer: '8',
    userAnswer: '8',
    isCorrect: true,
    timeSpent: 2.5,
    isMarkedForReview: false,
  }

  it('renders nothing when problem is null', () => {
    const { container } = render(<ProblemDetailModal problem={null} onClose={vi.fn()} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders problem details correctly for correct answer', () => {
    render(<ProblemDetailModal problem={mockProblem} onClose={vi.fn()} />)

    expect(screen.getByText('Problem Details')).toBeInTheDocument()
    expect(screen.getByText('5 + 3')).toBeInTheDocument()
    expect(screen.getByText('Correct Answer')).toBeInTheDocument()
    // "8" appears multiple times (correct answer and user answer), use getAllBy
    const eights = screen.getAllByText('8')
    expect(eights.length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText('Your Answer')).toBeInTheDocument()
    expect(screen.getByText(/2\.5s/i)).toBeInTheDocument()
  })

  it('renders problem details correctly for incorrect answer', () => {
    const incorrectProblem: ProblemResult = {
      ...mockProblem,
      userAnswer: '7',
      isCorrect: false,
    }

    render(<ProblemDetailModal problem={incorrectProblem} onClose={vi.fn()} />)

    expect(screen.getByText('5 + 3')).toBeInTheDocument()
    expect(screen.getByText('8')).toBeInTheDocument() // Correct answer
    expect(screen.getByText('7')).toBeInTheDocument() // User answer
  })

  it('displays correct operation symbols', () => {
    // Test subtraction
    const subtractionProblem: ProblemResult = {
      ...mockProblem,
      operation: 'subtraction',
    }
    const { unmount: unmountSub } = render(<ProblemDetailModal problem={subtractionProblem} onClose={vi.fn()} />)
    expect(screen.getByText('5 - 3')).toBeInTheDocument()
    unmountSub()

    // Test multiplication
    const multiplicationProblem: ProblemResult = {
      ...mockProblem,
      operation: 'multiplication',
    }
    const { unmount: unmountMul } = render(<ProblemDetailModal problem={multiplicationProblem} onClose={vi.fn()} />)
    expect(screen.getByText('5 × 3')).toBeInTheDocument()
    unmountMul()

    // Test division
    const divisionProblem: ProblemResult = {
      ...mockProblem,
      operation: 'division',
    }
    render(<ProblemDetailModal problem={divisionProblem} onClose={vi.fn()} />)
    expect(screen.getByText('5 ÷ 3')).toBeInTheDocument()
  })

  it('shows flagged indicator when problem is marked for review', () => {
    const flaggedProblem: ProblemResult = {
      ...mockProblem,
      isMarkedForReview: true,
    }

    render(<ProblemDetailModal problem={flaggedProblem} onClose={vi.fn()} />)

    expect(screen.getByText(/flagged for review/i)).toBeInTheDocument()
  })

  it('does not show flagged indicator when problem is not marked for review', () => {
    render(<ProblemDetailModal problem={mockProblem} onClose={vi.fn()} />)

    expect(screen.queryByText(/flagged for review/i)).not.toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()

    render(<ProblemDetailModal problem={mockProblem} onClose={onClose} />)

    const closeButton = screen.getByRole('button', { name: /close/i })
    await user.click(closeButton)

    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('handles missing userAnswer gracefully', () => {
    const problemWithoutAnswer: ProblemResult = {
      ...mockProblem,
      userAnswer: null,
      isCorrect: false,
    }

    render(<ProblemDetailModal problem={problemWithoutAnswer} onClose={vi.fn()} />)

    expect(screen.getByText('—')).toBeInTheDocument()
  })

  it('displays time with one decimal place', () => {
    const problemWithDecimalTime: ProblemResult = {
      ...mockProblem,
      timeSpent: 3.456,
    }

    render(<ProblemDetailModal problem={problemWithDecimalTime} onClose={vi.fn()} />)

    expect(screen.getByText(/3\.5s/i)).toBeInTheDocument()
  })
})

