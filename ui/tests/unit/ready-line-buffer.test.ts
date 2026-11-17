import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it, vi } from 'vitest'
import type { LiveQuery } from '../../src/main/live-identity'
import * as pm from '../../src/main/python-manager'

const here = dirname(fileURLToPath(import.meta.url))
const OURS = 'P:\\av-kit\\.venv\\Scripts\\python.exe'
const READY = 'AVKIT_READY port=13988 instance=70d5efcc-856f-4f37-b90a-eb2b4c09e72e'
const API_BASE = 'http://127.0.0.1:13988/api/v1'

// Red must fail by assertion, never by calling a missing export (Session 52 RULE-4).
function expectNewNames(): void {
  expect(typeof pm.createReadyLineReader).toBe('function')
  expect(pm.READY_LINE_MAX_LENGTH).toBe(4096)
}

function harness(options: { live?: LiveQuery; descriptorPid?: number | null } = {}) {
  const live = options.live ?? { ok: true, image: OURS }
  const descriptorPid = options.descriptorPid === undefined ? 111 : options.descriptorPid
  const queryLive = vi.fn((_pid: number): LiveQuery => live)
  const published: Array<{ apiBase: string; token: string }> = []
  const seen: string[] = []
  const reader = pm.createReadyLineReader((line) => {
    seen.push(line)
    return pm.publishIfReady({
      chunkText: line,
      ownedPid: 111,
      readDescriptorPid: () => descriptorPid,
      queryLive,
      oursExe: OURS,
      token: 'gui-nonce',
      publish: (ready) => {
        published.push(ready)
      },
    })
  })
  return { reader, queryLive, published, seen }
}

function count(text: string, needle: string): number {
  return text.split(needle).length - 1
}

describe('MEU-154 READY_LINES, READY_ONCE, READY_BOUND', () => {
  it('AC-154.1 a ready line split in two publishes once, at each of four split points', () => {
    expectNewNames()
    const splits = [
      READY.indexOf('_READY'),
      READY.indexOf('988'),
      READY.indexOf('ance='),
      READY.indexOf('-4f37'),
    ]
    for (const at of splits) {
      expect(at).toBeGreaterThan(0)
      const { reader, queryLive, published } = harness()
      expect(reader.push(`INFO boot\n${READY.slice(0, at)}`)).toBe(false)
      expect(queryLive).toHaveBeenCalledTimes(0)
      expect(published).toEqual([])
      expect(reader.push(`${READY.slice(at)}\n`)).toBe(true)
      expect(published).toEqual([{ apiBase: API_BASE, token: 'gui-nonce' }])
      expect(queryLive).toHaveBeenCalledTimes(1)
      expect(queryLive).toHaveBeenCalledWith(111)
    }
  })

  it('AC-154.2 two lines in one chunk: lines reach publishLine in order and publish once', () => {
    expectNewNames()
    const first = harness()
    expect(first.reader.push(`INFO a\n${READY}\nINFO b\n`)).toBe(true)
    expect(first.seen).toEqual(['INFO a', READY])
    expect(first.published).toEqual([{ apiBase: API_BASE, token: 'gui-nonce' }])

    const other = 'AVKIT_READY port=14001 instance=70d5efcc-856f-4f37-b90a-eb2b4c09e72e'
    const second = harness()
    expect(second.reader.push(`INFO c\nINFO d\n${other}`)).toBe(false)
    expect(second.published).toEqual([])
    expect(second.reader.push('\n')).toBe(true)
    expect(second.seen).toEqual(['INFO c', 'INFO d', other])
    expect(second.published).toEqual([{ apiBase: 'http://127.0.0.1:14001/api/v1', token: 'gui-nonce' }])
  })

  it('AC-154.3 a repeated ready line publishes once and the reader latches', () => {
    expectNewNames()
    const { reader, queryLive, published, seen } = harness()
    expect(reader.push(`${READY}\n${READY}\n`)).toBe(true)
    expect(reader.push(`${READY}\n`)).toBe(false)
    expect(reader.push('AVKIT_READY port=14000 instance=70d5efcc-856f-4f37-b90a-eb2b4c09e72e\n')).toBe(false)
    expect(reader.push('AVKIT_READY port=1')).toBe(false)
    expect(published).toEqual([{ apiBase: API_BASE, token: 'gui-nonce' }])
    expect(queryLive).toHaveBeenCalledTimes(1)
    expect(seen).toEqual([READY])
    expect(reader.state.published).toBe(true)
    expect(reader.state.pendingLength).toBe(0)
  })

  it('AC-154.4 no veto: a failed or foreign live query still publishes a usable ready line once', () => {
    expectNewNames()
    const failed = harness({ live: { ok: false }, descriptorPid: null })
    expect(failed.reader.push(`${READY}\n`)).toBe(true)
    expect(failed.published).toEqual([{ apiBase: API_BASE, token: 'gui-nonce' }])
    expect(failed.queryLive).toHaveBeenCalledTimes(1)

    const foreign = harness({ live: { ok: true, image: 'C:\\other\\python.exe' } })
    expect(foreign.reader.push(`${READY}\n`)).toBe(true)
    expect(foreign.published).toEqual([{ apiBase: API_BASE, token: 'gui-nonce' }])
    expect(foreign.queryLive).toHaveBeenCalledTimes(1)
  })

  it('AC-154.5 a line longer than the bound is dropped whole; one trailing CR is stripped', () => {
    expectNewNames()
    const { reader, published, seen } = harness()
    expect(reader.push('x'.repeat(5000))).toBe(false)
    expect(reader.state.discarded).toBe(true)
    expect(reader.state.pendingLength).toBeLessThanOrEqual(4096)
    expect(reader.push('end of the long line\n')).toBe(false)
    expect(reader.state.discarded).toBe(false)
    expect(seen).toEqual([])
    expect(reader.push(`${READY}\n`)).toBe(true)
    expect(seen).toEqual([READY])
    expect(published).toEqual([{ apiBase: API_BASE, token: 'gui-nonce' }])

    const crlf = harness()
    expect(crlf.reader.push(`INFO boot\r\n${READY}\r\n`)).toBe(true)
    expect(crlf.seen).toEqual(['INFO boot', READY])
    expect(crlf.published).toEqual([{ apiBase: API_BASE, token: 'gui-nonce' }])
  })

  it('AC-154.6 port=0 and an unterminated ready line do not publish or query; a later usable line does', () => {
    expectNewNames()
    const zero = harness()
    expect(zero.reader.push('AVKIT_READY port=0 instance=x\n')).toBe(false)
    expect(zero.queryLive).toHaveBeenCalledTimes(0)
    expect(zero.published).toEqual([])
    expect(zero.reader.push(`${READY}\n`)).toBe(true)
    expect(zero.queryLive).toHaveBeenCalledTimes(1)
    expect(zero.published).toEqual([{ apiBase: API_BASE, token: 'gui-nonce' }])

    const unterminated = harness()
    expect(unterminated.reader.push(`INFO boot\n${READY}`)).toBe(false)
    expect(unterminated.queryLive).toHaveBeenCalledTimes(0)
    expect(unterminated.published).toEqual([])
    expect(unterminated.seen).toEqual(['INFO boot'])
    expect(unterminated.reader.state.pendingLength).toBe(READY.length)
    expect(unterminated.reader.state.published).toBe(false)
  })

  it('AC-154.7 index.ts feeds only the child stdout to the reader, and onChildOutput no longer publishes', () => {
    expectNewNames()
    const src = readFileSync(resolve(here, '../../src/main/index.ts'), 'utf8').replace(/\r/g, '')
    expect(count(src, "child.stdout?.on('data', onReadyOutput)")).toBe(1)
    expect(src).not.toContain("child.stderr?.on('data', onReadyOutput)")
    const handler = src.indexOf('const onChildOutput')
    const reader = src.indexOf('const readyReader')
    const hookup = src.indexOf("child.stdout?.on('data', onChildOutput)")
    expect(handler).toBeGreaterThan(-1)
    expect(reader).toBeGreaterThan(handler)
    expect(hookup).toBeGreaterThan(reader)
    expect(src.slice(handler, reader)).not.toContain('publishIfReady(')
    const tail = src.slice(reader, hookup)
    expect(count(tail, 'publishIfReady(')).toBe(1)
    expect(count(tail, 'createReadyLineReader(')).toBe(1)
  })
})
