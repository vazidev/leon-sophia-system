import type { RoundEntry } from '../types/debate'

interface Props {
  round: RoundEntry | null
}

export function DetailPanel({ round }: Props) {
  if (!round) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)' }}>
        <p>Select a round or start a debate.</p>
      </div>
    )
  }

  const isLeon = round.agent === 'leon'
  const accentColor = isLeon ? 'var(--leon)' : 'var(--sophia)'

  return (
    <div style={{ padding: 24, maxWidth: 860, margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
        <span className={`chip chip-${round.agent}`}>{round.agent.toUpperCase()}</span>
        <span style={{ fontSize: 16, fontWeight: 600 }}>Round {round.round}</span>
        {round.qualityScore !== undefined && (
          <span style={{ marginLeft: 'auto', fontWeight: 600, color: round.qualityScore >= 7 ? 'var(--converged)' : 'var(--text-secondary)' }}>
            Quality: {round.qualityScore.toFixed(1)} / 10
          </span>
        )}
      </div>

      {round.qualityScore !== undefined && (
        <div style={{ height: 6, background: 'var(--border)', borderRadius: 3, marginBottom: 16 }}>
          <div style={{
            height: '100%', borderRadius: 3,
            width: `${(round.qualityScore / 10) * 100}%`,
            background: round.qualityScore >= 7 ? 'var(--converged)' : accentColor,
            transition: 'width 0.4s ease'
          }} />
        </div>
      )}

      <div style={{ fontSize: 15, lineHeight: 1.7, whiteSpace: 'pre-wrap', marginBottom: 16 }}>
        {round.text}
        {round.streaming && (
          <span style={{
            display: 'inline-block', width: 2, height: '1em',
            background: accentColor, marginLeft: 2,
            animation: 'blink 1s step-end infinite',
            verticalAlign: 'text-bottom'
          }} />
        )}
      </div>

      {round.flags.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8, color: 'var(--text-secondary)' }}>SOPHIA Flags</div>
          {round.flags.map((f, i) => (
            <div key={i} style={{
              padding: '10px 14px', borderRadius: 'var(--radius)', marginBottom: 6,
              borderLeft: `3px solid ${f.severity === 'blocking' ? 'var(--sophia)' : 'var(--advisory)'}`,
              background: f.severity === 'blocking' ? '#fff1f2' : '#fefce8'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                <span className={`chip chip-${f.severity}`}>{f.severity.toUpperCase()}</span>
                <span style={{ fontSize: 13, fontWeight: 500 }}>{f.claim}</span>
              </div>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{f.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
