import { useState } from 'react'
import { TopBar } from './components/TopBar'
import { InputBar } from './components/InputBar'
import { TimelineSidebar } from './components/TimelineSidebar'
import { DetailPanel } from './components/DetailPanel'
import { useDebate } from './hooks/useDebate'
import { useEvolution } from './hooks/useEvolution'
import { EvolutionPanel } from './components/evolution/EvolutionPanel'
import { ConvergenceScreen } from './components/convergence/ConvergenceScreen'
import type { RoundEntry } from './types/debate'

export default function App() {
  const { state, startDebate, reset } = useDebate()
  const [selectedRound, setSelectedRound] = useState<RoundEntry | null>(null)
  const [activeTab, setActiveTab] = useState<'debate' | 'evolution'>('debate')

  const sessionId = state.phase !== 'idle' ? state.sessionId : null
  const evolution = useEvolution(sessionId)
  const rounds = state.phase !== 'idle' ? state.rounds : []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100dvh' }}>
      <TopBar
        topic={state.phase !== 'idle' ? state.topic : ''}
        status={state.phase}
      />

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <div style={{ width: 220, borderRight: '1px solid var(--border)', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', borderBottom: '1px solid var(--border)' }}>
            {(['debate', 'evolution'] as const).map(tab => (
              <button key={tab} onClick={() => setActiveTab(tab)} style={{
                flex: 1, padding: '8px', border: 'none', cursor: 'pointer',
                background: activeTab === tab ? 'var(--surface)' : 'var(--bg)',
                fontWeight: activeTab === tab ? 600 : 400,
                borderBottom: activeTab === tab ? '2px solid var(--leon)' : '2px solid transparent',
                fontSize: 13
              }}>
                {tab === 'debate' ? 'Timeline' : 'Evolution'}
              </button>
            ))}
          </div>
          {activeTab === 'debate' ? (
            <TimelineSidebar
              rounds={rounds}
              selectedRound={selectedRound}
              onSelect={setSelectedRound}
            />
          ) : (
            <EvolutionPanel evolution={evolution} />
          )}
        </div>

        <div style={{ flex: 1, overflow: 'auto' }}>
          {state.phase === 'converged' && !selectedRound ? (
            <ConvergenceScreen
              convergence={state.convergence}
              onViewDebate={() => rounds.length > 0 && setSelectedRound(rounds[0])}
              onNewDebate={reset}
            />
          ) : (
            <DetailPanel round={selectedRound || rounds[rounds.length - 1] || null} />
          )}
        </div>
      </div>

      <InputBar
        onStart={startDebate}
        onReset={reset}
        disabled={state.phase === 'running'}
      />
    </div>
  )
}
