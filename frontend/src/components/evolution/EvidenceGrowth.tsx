import type { LeonEvolutionRow } from '../../types/debate'

interface Props { evolution: LeonEvolutionRow[] }

export function EvidenceGrowth({ evolution }: Props) {
  if (evolution.length === 0) return null
  const maxEvidence = Math.max(...evolution.map(r => r.evidenceCount), 1)

  return (
    <div>
      {evolution.map(r => (
        <div key={r.round} style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4, fontSize: 11 }}>
          <span style={{ width: 24, color: 'var(--text-secondary)', textAlign: 'right' }}>R{r.round}</span>
          <div style={{ flex: 1, height: 12, background: 'var(--bg)', borderRadius: 6, overflow: 'hidden' }}>
            <div style={{ height: '100%', background: 'var(--leon)', width: `${(r.evidenceCount / maxEvidence) * 100}%`, borderRadius: 6 }} />
          </div>
          <span style={{ width: 20, color: 'var(--text-secondary)' }}>{r.evidenceCount}</span>
        </div>
      ))}
    </div>
  )
}
