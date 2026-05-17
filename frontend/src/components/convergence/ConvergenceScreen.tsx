import type { ConvergenceData } from '../../types/debate'
import { FinalDecision } from './FinalDecision'
import { AchievementGuide } from './AchievementGuide'
import { PredictedOutcome } from './PredictedOutcome'

interface Props {
  convergence: ConvergenceData
  onViewDebate: () => void
  onNewDebate: () => void
}

export function ConvergenceScreen({ convergence, onViewDebate, onNewDebate }: Props) {
  const exportDecision = () => {
    const content = [
      '# Decision Log',
      `\n**Date:** ${new Date().toISOString()}`,
      '\n## Final Decision',
      convergence.finalRecommendation,
      '\n## Key Trade-off',
      convergence.keyTradeoff,
      '\n## Achievement Steps',
      ...convergence.achievementSteps.map((s, i) => `${i + 1}. **${s.title}** (${s.timeline}, ${s.owner}): ${s.description}`),
      '\n## Predicted Outcomes',
      ...convergence.predictedMetrics.map(m => `- ${m.label}: ${m.value} (${Math.round(m.confidence * 100)}% confidence)`),
      '',
      convergence.predictedNarrative,
    ].join('\n')
    const blob = new Blob([content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = 'decision-log.md'; a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div style={{ height: '100%', overflowY: 'auto' }}>
      <div style={{ background: 'linear-gradient(135deg, #dcfce7, #eff6ff)', padding: '16px 24px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 24 }}>✅</span>
        <div>
          <div style={{ fontWeight: 700, fontSize: 16, color: 'var(--converged)' }}>Analysis Converged</div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
            Quality score {convergence.qualityScore.toFixed(1)}/10 — LEON and SOPHIA reached consensus
          </div>
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
          <button onClick={exportDecision} style={{ padding: '8px 14px', borderRadius: 'var(--radius)', background: 'var(--converged)', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: 13 }}>
            Export Decision
          </button>
          <button onClick={onViewDebate} style={{ padding: '8px 14px', borderRadius: 'var(--radius)', background: 'var(--surface)', border: '1px solid var(--border)', cursor: 'pointer', fontSize: 13 }}>
            View Full Debate
          </button>
          <button onClick={onNewDebate} style={{ padding: '8px 14px', borderRadius: 'var(--radius)', background: 'var(--bg)', border: '1px solid var(--border)', cursor: 'pointer', fontSize: 13 }}>
            New Debate
          </button>
        </div>
      </div>
      <div style={{ maxWidth: 860, margin: '0 auto' }}>
        <FinalDecision convergence={convergence} />
        <AchievementGuide convergence={convergence} />
        <PredictedOutcome convergence={convergence} />
      </div>
    </div>
  )
}
