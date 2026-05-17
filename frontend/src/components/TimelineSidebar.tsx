import type { RoundEntry } from '../types/debate'

interface Props {
  rounds: RoundEntry[]
  selectedRound: RoundEntry | null
  onSelect: (round: RoundEntry) => void
}

export function TimelineSidebar({ rounds, selectedRound, onSelect }: Props) {
  return (
    <div style={{ flex: 1, overflowY: 'auto', padding: 8 }}>
      {rounds.length === 0 && (
        <p style={{ color: 'var(--text-secondary)', fontSize: 13, padding: 8 }}>
          Debate rounds will appear here.
        </p>
      )}
      {rounds.map((r, i) => {
        const isSelected = selectedRound === r
        const isLeon = r.agent === 'leon'
        return (
          <div
            key={i}
            onClick={() => onSelect(r)}
            style={{
              padding: '8px 10px', marginBottom: 4, borderRadius: 'var(--radius)',
              cursor: 'pointer',
              border: isSelected
                ? `2px solid ${isLeon ? 'var(--leon)' : 'var(--sophia)'}`
                : '1px solid var(--border)',
              background: isSelected ? (isLeon ? '#eff6ff' : '#fff1f2') : 'var(--surface)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span className={`chip chip-${r.agent}`}>{r.agent.toUpperCase()}</span>
              <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>R{r.round}</span>
              {r.streaming && (
                <span style={{ fontSize: 11, color: 'var(--leon)' }}>●</span>
              )}
            </div>
            {r.qualityScore !== undefined && (
              <div style={{ fontSize: 12, marginTop: 4, color: r.qualityScore >= 7 ? 'var(--converged)' : 'var(--text-secondary)' }}>
                Score: {r.qualityScore.toFixed(1)}
              </div>
            )}
            {r.flags.length > 0 && (
              <div style={{ fontSize: 11, marginTop: 3, color: r.flags.some(f => f.severity === 'blocking') ? 'var(--sophia)' : 'var(--advisory)' }}>
                {r.flags.length} flag{r.flags.length > 1 ? 's' : ''}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
