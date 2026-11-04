import { describe, expect, it, vi } from 'vitest'

describe('AC-19.9 COPY_MCP_RESULT', () => {
  it('AC-25.8 MCP_COPY_DEFAULT omits AVKIT_API_BASE when pinEndpoint: false', async () => {
    const { handleIpc } = await import('../../src/main/ipc')
    const mcpToken = 'mcp-live-token-should-stay-in-main'
    const sideEffects = { dialog: 0, fs: 0, clipboard: 0, spawn: 0 }
    const deps = {
      appData: 'C:/data/av-kit',
      sideEffects,
      readMcpToken: vi.fn(async () => mcpToken),
      writeClipboard: vi.fn(async () => {
        sideEffects.clipboard += 1
      }),
    }
    const result = await handleIpc('copy-mcp-config', { pinEndpoint: false }, deps)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toEqual({ ok: true })
      expect(JSON.stringify(result.value)).not.toContain(mcpToken)
    }
    expect(deps.writeClipboard).toHaveBeenCalledTimes(1)
    const written = String(deps.writeClipboard.mock.calls.flat()[0] ?? '')
    expect(written).toContain('AVKIT_API_TOKEN')
    expect(written).toContain(mcpToken)
    expect(written).not.toContain('AVKIT_API_BASE')
    expect(sideEffects.clipboard).toBe(1)
  })
})
