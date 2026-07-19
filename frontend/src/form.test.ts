import { describe, expect, it, vi } from 'vitest'

import { runFormAction } from './form'

describe('async form submission', () => {
  it('resets the captured form after the asynchronous action succeeds', async () => {
    const reset = vi.fn()
    const action = vi.fn(async () => undefined)

    await runFormAction({ reset }, action)

    expect(action).toHaveBeenCalledOnce()
    expect(reset).toHaveBeenCalledOnce()
    expect(action.mock.invocationCallOrder[0]).toBeLessThan(reset.mock.invocationCallOrder[0])
  })
})
