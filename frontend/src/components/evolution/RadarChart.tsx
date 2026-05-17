import type { LeonEvolutionRow } from '../../types/debate'

interface Props { evolution: LeonEvolutionRow[] }

const AXES = ['Evidence', 'Scope', 'Confidence', 'Depth', 'Specificity', 'Risk']

function polarToXY(angle: number, radius: number, cx: number, cy: number) {
  return { x: cx + radius * Math.cos(angle - Math.PI / 2), y: cy + radius * Math.sin(angle - Math.PI / 2) }
}

function getValues(row: LeonEvolutionRow): number[] {
  return [
    row.evidenceCount / 10,
    row.scopeKeywords.length / 5,
    row.confidenceScore,
    row.claimsAdded.length / 5,
    row.qualityScore / 10,
    1 - row.confidenceScore
  ].map(v => Math.min(v, 1))
}

function toPath(values: number[], cx: number, cy: number, R: number): string {
  return values.map((v, i) => {
    const angle = (i / AXES.length) * 2 * Math.PI
    const pt = polarToXY(angle, v * R, cx, cy)
    return `${i === 0 ? 'M' : 'L'}${pt.x},${pt.y}`
  }).join(' ') + 'Z'
}

export function RadarChart({ evolution }: Props) {
  if (evolution.length === 0) return null
  const first = evolution[0]
  const last = evolution[evolution.length - 1]
  const cx = 90, cy = 90, R = 70

  const axisLines = AXES.map((label, i) => {
    const angle = (i / AXES.length) * 2 * Math.PI
    const end = polarToXY(angle, R, cx, cy)
    const labelPt = polarToXY(angle, R + 14, cx, cy)
    return { x1: cx, y1: cy, x2: end.x, y2: end.y, labelPt, label }
  })

  return (
    <svg width={180} height={180} style={{ width: '100%' }}>
      {axisLines.map((a, i) => (
        <g key={i}>
          <line x1={a.x1} y1={a.y1} x2={a.x2} y2={a.y2} stroke="var(--border)" strokeWidth={1} />
          <text x={a.labelPt.x} y={a.labelPt.y + 4} textAnchor="middle" fontSize={8} fill="var(--text-secondary)">{a.label}</text>
        </g>
      ))}
      <path d={toPath(getValues(first), cx, cy, R)} fill="rgba(9,105,218,0.15)" stroke="var(--leon)" strokeWidth={1.5} strokeDasharray="3,2" />
      <path d={toPath(getValues(last), cx, cy, R)} fill="rgba(9,105,218,0.25)" stroke="var(--leon)" strokeWidth={2} />
    </svg>
  )
}
