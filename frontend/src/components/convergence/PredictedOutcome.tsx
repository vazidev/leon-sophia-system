import type { ConvergenceData } from '../../types/debate'

interface Props { convergence: ConvergenceData }

export function PredictedOutcome({ convergence }: Props) {
  return (
    <div style={{ padding: '20px 24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
        <span style={{ fontSize: 22 }}>🔭</span>
        <h2 style={{ fontSize: 20, fontWeight: 700 }}>Best Predicted Outcome</h2>
      </div>
      <div style={{ display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap' }}>
        {convergence.predictedMetrics.map((m, i) => (
          <div key={i} style={{ padding: '12px 16px', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', minWidth: 120, textAlign: 'center' }}>
            <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--leon)' }}>{m.value}</div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 4 }}>{m.label}</div>
            <div style={{ fontSize: 11, color: 'var(--converged)' }}>{Math.round(m.confidence * 100)}% confidence</div>
          </div>
        ))}
      </div>
      <p style={{ fontSize: 14, lineHeight: 1.7, marginBottom: 16 }}>{convergence.predictedNarrative}</p>
      <div style={{ padding: '10px 14px', background: 'var(--bg)', borderRadius: 'var(--radius)', fontSize: 13, color: 'var(--text-secondary)' }}>
        Overall prediction confidence: <strong style={{ color: 'var(--text)' }}>{Math.round(convergence.overallConfidence * 100)}%</strong>
      </div>
    </div>
  )
}
