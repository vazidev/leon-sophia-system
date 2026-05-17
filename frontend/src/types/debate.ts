export type Severity = 'blocking' | 'advisory'

export interface DebateFlag {
  severity: Severity
  claim: string
  description: string
}

export interface RoundEntry {
  round: number
  agent: 'leon' | 'sophia'
  text: string
  flags: DebateFlag[]
  qualityScore?: number
  streaming: boolean
}

export interface AchievementStep {
  title: string
  description: string
  timeline: string
  owner: string
}

export interface PredictedMetric {
  label: string
  value: string
  confidence: number
}

export interface ConvergenceData {
  qualityScore: number
  finalRecommendation: string
  keyTradeoff: string
  openAdvisories: string[]
  achievementSteps: AchievementStep[]
  predictedMetrics: PredictedMetric[]
  predictedNarrative: string
  overallConfidence: number
}

export interface LeonEvolutionRow {
  round: number
  recommendationSnapshot: string
  evidenceCount: number
  claimsAdded: string[]
  scopeKeywords: string[]
  confidenceScore: number
  qualityScore: number
}

export type DebateState =
  | { phase: 'idle' }
  | { phase: 'running'; sessionId: string; topic: string; rounds: RoundEntry[] }
  | { phase: 'converged'; sessionId: string; topic: string; rounds: RoundEntry[]; convergence: ConvergenceData }
