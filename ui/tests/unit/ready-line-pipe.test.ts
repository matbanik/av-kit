import { describe, expect, it, vi } from 'vitest'
import type { LiveQuery } from '../../src/main/live-identity'
import * as pm from '../../src/main/python-manager'

const OURS = 'P:\\av-kit\\.venv\\Scripts\\python.exe'
// Writes a ready line in two pieces 80 ms apart, then a second ready line, then exits on its own.
const SCRIPT = [
  "process.stdout.write('INFO boot\\nAVKIT_READY port=139')",
  "setTimeout(() => { process.stdout.write('88 instance=70d5efcc-856f-4f37-b90a-eb2b4c09e72e\\nAVKIT_READY port=14000 instance=x\\n') }, 80)",
].join('\n')

describe('MEU-154 READY_LINES through a real pipe', () => {
  it('AC-154.8 a real pipe splits the ready line and it publishes once', async () => {
    expect(typeof pm.createReadyLineReader).toBe('function')
    expect(pm.READY_LINE_MAX_LENGTH).toBe(4096)
    const queryLive = vi.fn((_pid: number): LiveQuery => ({ ok: true, image: OURS }))
    const published: Array<{ apiBase: string; token: string }> = []
    const reader = pm.createReadyLineReader((line) =>
      pm.publishIfReady({
        chunkText: line,
        ownedPid: 111,
        readDescriptorPid: () => 111,
        queryLive,
        oursExe: OURS,
        token: 'gui-nonce',
        publish: (ready) => {
          published.push(ready)
        },
      }),
    )
    const child = pm.spawnOwned([process.execPath, '-e', SCRIPT], { ...process.env })
    const chunks: string[] = []
    child.stdout?.on('data', (chunk: Buffer) => {
      const text = chunk.toString('utf8')
      chunks.push(text)
      reader.push(text)
    })
    const code = await new Promise<number | null>((done) => {
      child.on('close', (exitCode) => done(exitCode))
    })
    expect(code).toBe(0)
    expect(chunks.length).toBeGreaterThanOrEqual(2)
    expect(chunks[0]?.endsWith('\n')).toBe(false)
    expect(published).toEqual([{ apiBase: 'http://127.0.0.1:13988/api/v1', token: 'gui-nonce' }])
    expect(queryLive).toHaveBeenCalledTimes(1)
  }, 15_000)
})
