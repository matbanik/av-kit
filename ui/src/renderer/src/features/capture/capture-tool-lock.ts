/**
 * LOCK_DECODE (MEU-143, D-746, D-747): the persisted tool lock from a `/settings/capture` answer. Only an
 * object whose `tool_lock` is exactly `false` turns the lock off; anything else, a missing key, a string,
 * a number or text that is not a boolean, keeps it on, its default.
 */
export function readToolLock(data: unknown): boolean {
  if (typeof data !== 'object' || data === null) {
    return true
  }
  return (data as Record<string, unknown>).tool_lock !== false
}
