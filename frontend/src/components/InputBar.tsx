import React, { useState } from 'react'

interface Props {
  onStart: (topic: string) => void
  onReset: () => void
  disabled: boolean
}

export function InputBar({ onStart, onReset, disabled }: Props) {
  const [topic, setTopic] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (topic.trim()) onStart(topic.trim())
  }

  return (
    <form onSubmit={handleSubmit} style={{
      display: 'flex', gap: 8, padding: '12px 20px',
      background: 'var(--surface)', borderTop: '1px solid var(--border)', flexShrink: 0
    }}>
      <input
        value={topic}
        onChange={e => setTopic(e.target.value)}
        placeholder="Enter debate topic..."
        disabled={disabled}
        style={{
          flex: 1, padding: '8px 12px', borderRadius: 'var(--radius)',
          border: '1px solid var(--border)', fontSize: 14, outline: 'none',
          background: disabled ? 'var(--bg)' : 'var(--surface)'
        }}
      />
      <button type="submit" disabled={disabled || !topic.trim()} style={{
        padding: '8px 16px', borderRadius: 'var(--radius)',
        background: 'var(--leon)', color: '#fff', border: 'none',
        cursor: disabled ? 'not-allowed' : 'pointer', fontWeight: 600
      }}>
        Start Debate
      </button>
      <button type="button" onClick={onReset} style={{
        padding: '8px 16px', borderRadius: 'var(--radius)',
        background: 'var(--bg)', border: '1px solid var(--border)',
        cursor: 'pointer', fontWeight: 500
      }}>
        New Debate
      </button>
    </form>
  )
}
