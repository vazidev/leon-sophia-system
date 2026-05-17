import type { ConvergenceData } from '../../types/debate'

interface Props { convergence: ConvergenceData }

export function FinalDecision({ convergence }: Props) {
  return (
    <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
        <span style={{ fontSize: 22 }}>⚖️</span>
        <h2 style={{ fontSize: 20, fontWeight: 700 }}>Final Decision</h2>
        <span style={{ marginLeft: 'auto', fontWeight: 700, color: 'var(--converged)', fontSize: 18 }}>
          {convergence.qualityScore.toFixed(1)} / 10
        </span>
      </div>
      <p style={{ fontSize: 16, lineHeight: 1.7, marginBottom: 16 }}>{convergence.finalRecommendation}</p>
      <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
        <span className="chip chip-converged">Ethics ✓</span>
        <span className="chip chip-converged">Bias ✓</span>
        <span className="chip chip-converged">Evidence Tier A</span>
      </div>
      <div style={{ padding: '10px 14px', background: '#fffbeb', borderRadius: 'var(--radius)', borderLeft: '3px solid var(--advisory)', marginBottom: 12 }}>
        <strong style={{ fontSize: 13 }}>Key Trade-off Accepted:</strong>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>{convergence.keyTradeoff}</p>
      </div>
      {convergence.openAdvisories.length > 0 && (
        <div>
          <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 6 }}>Open Advisories</div>
          {convergence.openAdvisories.map((a, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, marginBottom: 4 }}>
              <span style={{ color: 'var(--advisory)' }}>⚠</span>
              <span>{a}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
