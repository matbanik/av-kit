import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useCallback, useMemo, useSyncExternalStore } from 'react'

import {
  CAPTURE_SETTINGS_KEY,
  committedStyleLeaves,
  fetchCaptureSettings,
  saveCaptureToolStyle,
  styleSaveFailures,
  subscribeCommittedStyleLeaves,
  subscribeStyleSaveFailures,
} from './capture-style-store'
import { readToolStyles, type StyleTool, type ToolStyle, type ToolStyles } from './capture-tool-style'

/**
 * STYLE_STORE (MEU-105, D-720): each tool's persisted style, read from the same query as
 * `useCaptureSettings`, and its save. Until the query has data, the styles come from the leaves committed
 * so far (execution round 1 F1). `failures` counts the style PUTs that failed.
 */
export function useCaptureToolStyles(): {
  styles: ToolStyles
  saveToolStyle: (tool: StyleTool, patch: ToolStyle) => void
  failures: number
} {
  const client = useQueryClient()
  const query = useQuery({ queryKey: CAPTURE_SETTINGS_KEY, queryFn: fetchCaptureSettings })
  const committed = useSyncExternalStore(subscribeCommittedStyleLeaves, committedStyleLeaves)
  const styles = useMemo(() => readToolStyles(query.data ?? committed), [query.data, committed])
  const failures = useSyncExternalStore(subscribeStyleSaveFailures, styleSaveFailures)
  const saveToolStyle = useCallback(
    (tool: StyleTool, patch: ToolStyle) => {
      saveCaptureToolStyle(client, tool, patch)
    },
    [client],
  )
  return { styles, saveToolStyle, failures }
}
