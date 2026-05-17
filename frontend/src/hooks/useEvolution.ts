import { useState, useEffect } from 'react'
import type { LeonEvolutionRow } from '../types/debate'

export function useEvolution(sessionId: string | null) {
  const [evolution, setEvolution] = useState<LeonEvolutionRow[]>([])

  useEffect(() => {
    if (!sessionId) return
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/debate/${sessionId}/evolution`)
        if (res.ok) {
          const data = await res.json() as LeonEvolutionRow[]
          setEvolution(data)
        }
      } catch {
        // network error — retry next interval
      }
    }, 2000)
    return () => clearInterval(interval)
  }, [sessionId])

  return evolution
}
