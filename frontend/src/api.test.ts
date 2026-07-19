import { afterEach, describe, expect, it, vi } from 'vitest'

import { authHeaders } from './api'

describe('Mini App authentication headers', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('uses signed Telegram init data when opened inside Telegram', () => {
    vi.stubGlobal('window', { Telegram: { WebApp: { initData: 'signed-data' } } })
    expect(authHeaders()).toEqual({ 'X-Telegram-Init-Data': 'signed-data' })
  })

  it('uses an explicit developer identity outside Telegram', () => {
    vi.stubGlobal('window', {})
    const headers = authHeaders()
    expect(headers).toMatchObject({ 'X-Dev-Telegram-User-Id': expect.any(String) })
    expect(headers['X-Dev-Telegram-Name']).not.toMatch(/[А-Яа-я]/)
  })
})
