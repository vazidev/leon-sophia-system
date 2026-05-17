import type { LeonEvolutionRow } from '../../types/debate'

interface Props { evolution: LeonEvolutionRow[] }

export function PositionDiff({ evolution }: Props) {
  return (
    <div style={{ fontSize: 12, lineHeight: 1.5 }}>
      {evolution.map((r) => (
        <div key={r.round} style={{ marginBottom: 10, padding: '6px 8px', borderLeft: '3px solid var(--leon)', background: '#eff6ff', borderRadius: '0 var(--radius) var(--radius) 0' }}>
          <div style={{ display: 'flex', gap: 6, marginBottom: 4 }}>
            <span className="chip chip-leon">R{r.round}</span>
            <span style={{ color: 'var(--text-secondary)' }}>Score: {r.qualityScore.toFixed(1)}</span>
          </div>
          <p style={{ fontSize: 11, color: 'var(--text)', margin: 0 }}>
            {r.recommendationSnapshot.slice(0, 120)}{r.recommendationSnapshot.length > 120 ? '…' : ''}
          </p>
          {r.claimsAdded.length > 0 && (
            <div style={{ marginTop: 4 }}>
              {r.claimsAdded.map((c, i) => (
                <span key={i} style={{ fontSize: 10, background: '#dcfce7', color: 'var(--converged)', borderRadius: 4, padding: '1px 4px', marginRight: 3 }}>+{c}</span>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
