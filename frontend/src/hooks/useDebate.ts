import { useState, useRef, useCallback } from 'react'
import type { DebateState, RoundEntry, DebateFlag, ConvergenceData } from '../types/debate'

export function useDebate() {
  const [state, setState] = useState<DebateState>({ phase: 'idle' })
  const esRef = useRef<EventSource | null>(null)

  const startDebate = useCallback(async (topic: string) => {
    const res = await fetch('/api/debate/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic }),
    })
    const { session_id } = await res.json() as { session_id: string }

    setState({ phase: 'running', sessionId: session_id, topic, rounds: [] })

    const es = new EventSource(
      `/api/debate/${session_id}/stream?topic=${encodeURIComponent(topic)}`
    )
    esRef.current = es

    es.addEventListener('round_start', (e) => {
      const { round, agent } = JSON.parse((e as MessageEvent).data) as {
        round: number
        agent: 'leon' | 'sophia'
      }
      setState((s) => {
        if (s.phase !== 'running') return s
        const newRound: RoundEntry = {
          round,
          agent,
          text: '',
          flags: [],
          streaming: true,
        }
        return { ...s, rounds: [...s.rounds, newRound] }
      })
    })

    es.addEventListener('token', (e) => {
      const { text } = JSON.parse((e as MessageEvent).data) as { text: string }
      setState((s) => {
        if (s.phase !== 'running') return s
        const rounds = [...s.rounds]
        if (rounds.length === 0) return s
        const last = { ...rounds[rounds.length - 1], text: rounds[rounds.length - 1].text + text }
        rounds[rounds.length - 1] = last
        return { ...s, rounds }
      })
    })

    es.addEventListener('flag', (e) => {
      const flag = JSON.parse((e as MessageEvent).data) as DebateFlag
      setState((s) => {
        if (s.phase !== 'running') return s
        const rounds = [...s.rounds]
        if (rounds.length === 0) return s
        const last = { ...rounds[rounds.length - 1] }
        last.flags = [...last.flags, flag]
        rounds[rounds.length - 1] = last
        return { ...s, rounds }
      })
    })

    es.addEventListener('quality_score', (e) => {
      const { score } = JSON.parse((e as MessageEvent).data) as { score: number }
      setState((s) => {
        if (s.phase !== 'running') return s
        const rounds = [...s.rounds]
        if (rounds.length === 0) return s
        const last = { ...rounds[rounds.length - 1], qualityScore: score, streaming: false }
        rounds[rounds.length - 1] = last
        return { ...s, rounds }
      })
    })

    es.addEventListener('convergence', (e) => {
      const convergence = JSON.parse((e as MessageEvent).data) as ConvergenceData
      es.close()
      setState((s) => {
        if (s.phase !== 'running') return s
        return {
          phase: 'converged',
          sessionId: s.sessionId,
          topic: s.topic,
          rounds: s.rounds,
          convergence,
        }
      })
    })

    es.onerror = () => {
      es.close()
    }
  }, [])

  const reset = useCallback(() => {
    esRef.current?.close()
    setState({ phase: 'idle' })
  }, [])

  return { state, startDebate, reset }
}
