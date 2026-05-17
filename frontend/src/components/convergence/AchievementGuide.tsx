import type { ConvergenceData } from '../../types/debate'

interface Props { convergence: ConvergenceData }

export function AchievementGuide({ convergence }: Props) {
  return (
    <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
        <span style={{ fontSize: 22 }}>🗺️</span>
        <h2 style={{ fontSize: 20, fontWeight: 700 }}>How to Achieve This</h2>
      </div>
      {convergence.achievementSteps.map((step, i) => (
        <div key={i} style={{ display: 'flex', gap: 14, marginBottom: 14 }}>
          <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'var(--leon)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 13, flexShrink: 0, marginTop: 2 }}>
            {i + 1}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <span style={{ fontWeight: 600, fontSize: 14 }}>{step.title}</span>
              <span className="chip" style={{ background: '#eff6ff', color: 'var(--leon)', fontSize: 11 }}>{step.timeline}</span>
              <span className="chip" style={{ background: 'var(--bg)', color: 'var(--text-secondary)', fontSize: 11 }}>{step.owner}</span>
            </div>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{step.description}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
