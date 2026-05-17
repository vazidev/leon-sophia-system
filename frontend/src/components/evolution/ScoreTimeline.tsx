import type { LeonEvolutionRow } from '../../types/debate'

interface Props { evolution: LeonEvolutionRow[] }

export function ScoreTimeline({ evolution }: Props) {
  if (evolution.length === 0) return <p style={{ color: 'var(--text-secondary)', fontSize: 12 }}>No rounds yet.</p>

  const w = 180, h = 80, pad = 10
  const plotW = w - pad * 2, plotH = h - pad * 2
  const pts = evolution.map((r, i) => ({
    x: pad + (i / Math.max(evolution.length - 1, 1)) * plotW,
    y: pad + plotH - (r.qualityScore / 10) * plotH
  }))
  const polyline = pts.map(p => `${p.x},${p.y}`).join(' ')

  return (
    <svg width={w} height={h} style={{ width: '100%' }}>
      <line x1={pad} y1={pad + plotH - 0.7 * plotH} x2={w - pad} y2={pad + plotH - 0.7 * plotH}
        stroke="var(--converged)" strokeWidth={1} strokeDasharray="3,3" />
      <polyline fill="none" stroke="var(--leon)" strokeWidth={2} points={polyline} />
      {pts.map((p, i) => (
        <circle key={i} cx={p.x} cy={p.y} r={3}
          fill={evolution[i].qualityScore >= 7 ? 'var(--converged)' : 'var(--leon)'} />
      ))}
    </svg>
  )
}
