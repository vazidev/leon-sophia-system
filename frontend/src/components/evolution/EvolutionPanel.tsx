import type { LeonEvolutionRow } from '../../types/debate'
import { ScoreTimeline } from './ScoreTimeline'
import { PositionDiff } from './PositionDiff'
import { ScopeMap } from './ScopeMap'
import { EvidenceGrowth } from './EvidenceGrowth'
import { RadarChart } from './RadarChart'

interface Props { evolution: LeonEvolutionRow[] }

export function EvolutionPanel({ evolution }: Props) {
  return (
    <div style={{ flex: 1, overflowY: 'auto', padding: 12 }}>
      <section style={{ marginBottom: 16 }}>
        <h4 style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 6 }}>Score Timeline</h4>
        <ScoreTimeline evolution={evolution} />
      </section>
      <section style={{ marginBottom: 16 }}>
        <h4 style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 6 }}>Scope Growth</h4>
        <ScopeMap evolution={evolution} />
      </section>
      <section style={{ marginBottom: 16 }}>
        <h4 style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 6 }}>Evidence Growth</h4>
        <EvidenceGrowth evolution={evolution} />
      </section>
      <section style={{ marginBottom: 16 }}>
        <h4 style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 6 }}>Dimensions (R1 vs Latest)</h4>
        <RadarChart evolution={evolution} />
      </section>
      <section>
        <h4 style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 6 }}>Position Diff</h4>
        <PositionDiff evolution={evolution} />
      </section>
    </div>
  )
}
