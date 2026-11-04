import { EventEmitter } from 'node:events'
import { PassThrough } from 'node:stream'

/**
 * A stand-in for the region-picker child process (MEU-40, AC-40.28 / AC-40.29).
 *
 * It is deliberately a real `EventEmitter` with real `PassThrough` pipes rather than a bag of
 * `vi.fn()`s: the lifecycle machine under test subscribes to `exit`, `close` and `error` and
 * drains both pipes, and a stub that only records subscriptions would let a machine that never
 * settles look correct.
 */
export class FakePickerChild extends EventEmitter {
  readonly stdout = new PassThrough()
  readonly stderr = new PassThrough()
  readonly killSignals: (string | undefined)[] = []
  readonly pid = 4242
  killed = false

  kill(signal?: string): boolean {
    this.killed = true
    this.killSignals.push(signal)
    return true
  }

  /** Emits the readiness line the way the helper's `Program.Main` does. */
  ready(marker = 'ready'): void {
    this.stdout.write(`${marker}\n`)
  }

  say(line: string): void {
    this.stdout.write(`${line}\n`)
  }

  complain(line: string): void {
    this.stderr.write(`${line}\n`)
  }

  /**
   * Node guarantees `close` follows `exit`; the plan's §Helper lifecycle relies on that
   * ordering (classification waits for `close` so the stderr tail is complete), so the fake
   * reproduces it rather than emitting one event.
   */
  finish(code: number | null, signal: string | null = null): void {
    this.emit('exit', code, signal)
    this.emit('close', code, signal)
  }

  /** A spawn that never produced a process at all: `error` then `close`. */
  failToSpawn(err: Error): void {
    this.emit('error', err)
    this.emit('close', null, null)
  }
}

export type SpawnCall = {
  exe: string
  args: string[]
  options: Record<string, unknown>
  child: FakePickerChild
}

export type FakeSpawn = {
  calls: SpawnCall[]
  /** The child handed to the Nth spawn; fails loudly if that spawn never happened. */
  child: (index?: number) => FakePickerChild
  fn: (exe: string, args: string[], options: Record<string, unknown>) => FakePickerChild
}

export function createFakeSpawn(): FakeSpawn {
  const calls: SpawnCall[] = []
  const fn = (
    exe: string,
    args: string[],
    options: Record<string, unknown>,
  ): FakePickerChild => {
    const child = new FakePickerChild()
    calls.push({ exe, args, options, child })
    return child
  }
  return {
    calls,
    child: (index = 0) => {
      const call = calls[index]
      if (call === undefined) {
        throw new Error(`no spawn at index ${index}; ${calls.length} spawn(s) recorded`)
      }
      return call.child
    },
    fn,
  }
}
