import { describe, expect, it, vi } from 'vitest'

import { bootstrapSession } from './bootstrap'

describe('session bootstrap', () => {
  it('leaves loading state and exposes the error when the API is unavailable', async () => {
    const setBusy = vi.fn()
    const setError = vi.fn()

    await bootstrapSession(
      async () => { throw new Error('API unavailable') },
      async () => undefined,
      vi.fn(),
      setError,
      setBusy,
    )

    expect(setError).toHaveBeenCalledWith('API unavailable')
    expect(setBusy).toHaveBeenLastCalledWith(false)
  })
})
