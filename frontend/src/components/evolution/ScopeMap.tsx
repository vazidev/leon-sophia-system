import type { LeonEvolutionRow } from '../../types/debate'

interface Props { evolution: LeonEvolutionRow[] }

export function ScopeMap({ evolution }: Props) {
  const allKeywords = evolution.flatMap(r => r.scopeKeywords.map(kw => ({ kw, round: r.round })))
  const cx = 90, cy = 90, r = 70

  return (
    <svg width={180} height={180} style={{ width: '100%' }}>
      <circle cx={cx} cy={cy} r={20} fill="var(--leon)" />
      <text x={cx} y={cy + 5} textAnchor="middle" fill="#fff" fontSize={9} fontWeight="bold">TOPIC</text>
      {allKeywords.slice(0, 8).map((item, i) => {
        const angle = (i / Math.min(allKeywords.length, 8)) * 2 * Math.PI - Math.PI / 2
        const nx = cx + r * Math.cos(angle)
        const ny = cy + r * Math.sin(angle)
        return (
          <g key={i}>
            <line x1={cx} y1={cy} x2={nx} y2={ny} stroke="var(--border)" strokeWidth={1} />
            <circle cx={nx} cy={ny} r={12} fill="#eff6ff" stroke="var(--leon)" strokeWidth={1} />
            <text x={nx} y={ny + 4} textAnchor="middle" fill="var(--leon)" fontSize={7}>{item.kw.slice(0, 6)}</text>
          </g>
        )
      })}
    </svg>
  )
}
