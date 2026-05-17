import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useDebate } from '../hooks/useDebate'

describe('useDebate', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('starts in idle phase', () => {
    const { result } = renderHook(() => useDebate())
    expect(result.current.state.phase).toBe('idle')
  })

  it('transitions to running phase on startDebate', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      json: async () => ({ session_id: 'test-session-123' })
    }) as unknown as typeof fetch

    const mockListeners: Record<string, ((e: MessageEvent) => void)[]> = {}
    const mockES = {
      addEventListener: vi.fn((event: string, handler: (e: MessageEvent) => void) => {
        mockListeners[event] = mockListeners[event] || []
        mockListeners[event].push(handler)
      }),
      close: vi.fn(),
      onerror: null as ((e: Event) => void) | null,
    }
    global.EventSource = vi.fn(() => mockES) as unknown as typeof EventSource

    const { result } = renderHook(() => useDebate())

    await act(async () => {
      await result.current.startDebate('test topic')
    })

    expect(result.current.state.phase).toBe('running')
    if (result.current.state.phase === 'running') {
      expect(result.current.state.sessionId).toBe('test-session-123')
      expect(result.current.state.topic).toBe('test topic')
    }
  })
})
