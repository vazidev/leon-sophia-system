import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ConvergenceScreen } from '../components/convergence/ConvergenceScreen'
import type { ConvergenceData } from '../types/debate'

const mockData: ConvergenceData = {
  qualityScore: 8.2,
  finalRecommendation: 'Adopt microservices for the data pipeline.',
  keyTradeoff: 'Complexity vs. scalability — accepted.',
  openAdvisories: ['Monitor latency after rollout'],
  achievementSteps: [{ title: 'Phase 1', description: 'Set up services', timeline: '2 weeks', owner: 'Platform team' }],
  predictedMetrics: [{ label: 'Latency', value: '50ms', confidence: 0.8 }],
  predictedNarrative: 'The migration will reduce latency by 40% within 3 months.',
  overallConfidence: 0.82
}

describe('ConvergenceScreen', () => {
  it('renders the final recommendation', () => {
    render(<ConvergenceScreen convergence={mockData} onViewDebate={vi.fn()} onNewDebate={vi.fn()} />)
    expect(screen.getByText('Adopt microservices for the data pipeline.')).toBeInTheDocument()
  })

  it('renders quality score', () => {
    render(<ConvergenceScreen convergence={mockData} onViewDebate={vi.fn()} onNewDebate={vi.fn()} />)
    expect(screen.getAllByText(/8\.2/).length).toBeGreaterThan(0)
  })
})
