import { describe, expect, it, vi } from 'vitest'

describe('AC-19.14 STARTUP_METRIC_KEYS', () => {
  it('posts startup metrics with the GUI nonce, never the MCP token', async () => {
    const { handleIpc, publishBackendReady, resetBackendIpcState } = await import('../../src/main/ipc')
    resetBackendIpcState()
    publishBackendReady({
      apiBase: 'http://127.0.0.1:51234/api/v1',
      token: 'gui-nonce-metric',
    })
    const posts: Array<{ url: string; auth: string; key?: string; value?: number }> = []
    const deps = {
      sideEffects: { dialog: 0, fs: 0, clipboard: 0, spawn: 0 },
      guiNonce: 'gui-nonce-metric',
      mcpToken: 'mcp-token-must-not-be-used',
      postStartupMetric: vi.fn(
        async (input: { url: string; authorization: string; key: string; value: number }) => {
          posts.push({ url: input.url, auth: input.authorization, key: input.key, value: input.value })
        },
      ),
    }
    const result = await handleIpc(
      'startup-metric',
      { key: 'startup.python_spawn_ms', value: 120, timestamp: 1 },
      deps,
    )
    expect(result.ok).toBe(true)
    expect(deps.postStartupMetric).toHaveBeenCalledTimes(1)
    expect(posts[0]?.auth).toBe('Bearer gui-nonce-metric')
    expect(posts[0]?.auth).not.toContain('mcp-token-must-not-be-used')
    expect(posts[0]?.url).toContain('/health/startup-metrics')
    expect(posts[0]?.url).toBe('http://127.0.0.1:51234/api/v1/health/startup-metrics')
    expect(posts[0]?.key).toBe('startup.python_spawn_ms')
    expect(posts[0]?.value).toBe(120)
  })
})
