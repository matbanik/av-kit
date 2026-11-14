import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useCallback, useMemo, useSyncExternalStore } from 'react'

import {
  CAPTURE_SETTINGS_KEY,
  committedStyleLeaves,
  fetchCaptureSettings,
  lockSaveFailures,
  saveCaptureToolLock,
  subscribeCommittedStyleLeaves,
  subscribeLockSaveFailures,
} from './capture-style-store'
import { readToolLock } from './capture-tool-lock'

/**
 * LOCK_STORE (MEU-143, D-746): the persisted tool lock, read from the same query as `useCaptureToolStyles`,
 * and its save. Until the query has data, it comes from the leaves committed so far, and with nothing
 * committed it is on. `failures` counts the lock PUTs that failed.
 */
export function useCaptureToolLock(): { locked: boolean; setLocked(next: boolean): void; failures: number } {
  const client = useQueryClient()
  const query = useQuery({ queryKey: CAPTURE_SETTINGS_KEY, queryFn: fetchCaptureSettings })
  const committed = useSyncExternalStore(subscribeCommittedStyleLeaves, committedStyleLeaves)
  const locked = useMemo(() => readToolLock(query.data ?? committed), [query.data, committed])
  const failures = useSyncExternalStore(subscribeLockSaveFailures, lockSaveFailures)
  const setLocked = useCallback(
    (next: boolean) => {
      saveCaptureToolLock(client, next)
    },
    [client],
  )
  return { locked, setLocked, failures }
}
