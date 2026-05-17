interface Props {
  topic: string
  status: 'idle' | 'running' | 'converged'
}

export function TopBar({ topic, status }: Props) {
  const statusText = status === 'idle' ? 'Ready' : status === 'running' ? 'Debating...' : 'Converged'
  const statusColor = status === 'idle' ? 'var(--text-secondary)' : status === 'running' ? 'var(--leon)' : 'var(--converged)'

  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '12px 20px', background: 'var(--surface)',
      borderBottom: '1px solid var(--border)', flexShrink: 0
    }}>
      <span style={{ fontWeight: 700, fontSize: 18 }}>LEON · SOPHIA</span>
      {topic && (
        <span style={{ fontSize: 14, color: 'var(--text-secondary)', maxWidth: 400, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {topic}
        </span>
      )}
      <span style={{ fontSize: 13, color: statusColor, fontWeight: 500 }}>{statusText}</span>
    </div>
  )
}
