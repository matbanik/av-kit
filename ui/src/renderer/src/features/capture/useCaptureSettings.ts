import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useCallback, useMemo, useState } from 'react'

import { ApiError, apiFetch } from '../../lib/api'
import {
  ANNOTATED_FORMATS,
  parseSettingsPut,
  SettingsValidationError,
  type AnnotatedFormat,
  type CapturePut,
} from '../settings/settings-schemas'
import { CAPTURE_SETTINGS_KEY, fetchCaptureSettings } from './capture-style-store'

export { CAPTURE_SETTINGS_KEY }

export type CaptureForm = {
  inbox_dir: string
  hotkey: string
  copy_to_clipboard: boolean
  close_to_tray: boolean
  flatten_backup: boolean
  backup_dir: string
  annotated_format: AnnotatedFormat
}

export const CAPTURE_DEFAULTS: CaptureForm = {
  inbox_dir: '~/Pictures/av-kit',
  hotkey: 'F2',
  copy_to_clipboard: false,
  close_to_tray: true,
  flatten_backup: true,
  backup_dir: '',
  annotated_format: 'png',
}

/** The seven leaves in `CaptureForm` order, the order a partial Save body keeps. */
const CAPTURE_KEYS: readonly (keyof CaptureForm)[] = [
  'inbox_dir',
  'hotkey',
  'copy_to_clipboard',
  'close_to_tray',
  'flatten_backup',
  'backup_dir',
  'annotated_format',
]

/** The leaves of `form` named in `keys`, in `CaptureForm` order. */
function pickLeaves(form: Partial<CaptureForm>, keys: readonly (keyof CaptureForm)[]): Partial<CaptureForm> {
  return Object.fromEntries(keys.map((key) => [key, form[key]])) as Partial<CaptureForm>
}

/**
 * CAPTURE_DRAFT_CHANGED_ONLY (MEU-151, D-966): the draft keeps only the leaves that differ from the
 * saved answer, so a refetch still reaches every other leaf. An empty draft is `null`.
 */
function changedOnly(draft: Partial<CaptureForm>, baseline: CaptureForm): Partial<CaptureForm> | null {
  const kept = CAPTURE_KEYS.filter((key) => key in draft && draft[key] !== baseline[key])
  return kept.length === 0 ? null : pickLeaves(draft, kept)
}

function isAnnotatedFormat(value: unknown): value is AnnotatedFormat {
  return typeof value === 'string' && (ANNOTATED_FORMATS as readonly string[]).includes(value)
}

function asForm(data: CapturePut | undefined): CaptureForm {
  return {
    inbox_dir: typeof data?.inbox_dir === 'string' ? data.inbox_dir : CAPTURE_DEFAULTS.inbox_dir,
    hotkey: typeof data?.hotkey === 'string' ? data.hotkey : CAPTURE_DEFAULTS.hotkey,
    copy_to_clipboard:
      typeof data?.copy_to_clipboard === 'boolean'
        ? data.copy_to_clipboard
        : CAPTURE_DEFAULTS.copy_to_clipboard,
    close_to_tray:
      typeof data?.close_to_tray === 'boolean' ? data.close_to_tray : CAPTURE_DEFAULTS.close_to_tray,
    flatten_backup:
      typeof data?.flatten_backup === 'boolean' ? data.flatten_backup : CAPTURE_DEFAULTS.flatten_backup,
    backup_dir: typeof data?.backup_dir === 'string' ? data.backup_dir : CAPTURE_DEFAULTS.backup_dir,
    annotated_format: isAnnotatedFormat(data?.annotated_format)
      ? data.annotated_format
      : CAPTURE_DEFAULTS.annotated_format,
  }
}

function sameForm(a: CaptureForm, b: CaptureForm): boolean {
  return (
    a.inbox_dir === b.inbox_dir &&
    a.hotkey === b.hotkey &&
    a.copy_to_clipboard === b.copy_to_clipboard &&
    a.close_to_tray === b.close_to_tray &&
    a.flatten_backup === b.flatten_backup &&
    a.backup_dir === b.backup_dir &&
    a.annotated_format === b.annotated_format
  )
}

export function useCaptureSettings() {
  const queryClient = useQueryClient()
  const query = useQuery({
    queryKey: CAPTURE_SETTINGS_KEY,
    // STYLE_STORE (round 2 F3): the shared GET, which keeps a style commit its answer did not see.
    queryFn: fetchCaptureSettings,
  })
  // CAPTURE_DRAFT_CHANGED_ONLY (MEU-151, D-966): only the edited leaves; the rest come from the latest answer.
  const [draft, setDraft] = useState<Partial<CaptureForm> | null>(null)
  const baseline = useMemo(() => asForm(query.data), [query.data])
  // CS81-R1-F1, D-1067: when the saved answer changes, a draft leaf that now equals it leaves the draft for
  // good, so a later answer reaches that leaf again. The prune runs during render (React's adjust-state-
  // on-change pattern), so React discards this render and renders again before committing: no committed
  // render shows the stale leaf, which an effect would for one frame.
  const [prunedFor, setPrunedFor] = useState(baseline)
  if (prunedFor !== baseline) {
    setPrunedFor(baseline)
    if (draft !== null) {
      setDraft(changedOnly(draft, baseline))
    }
  }
  const form = useMemo<CaptureForm>(() => (draft === null ? baseline : { ...baseline, ...draft }), [baseline, draft])
  const isDirty = query.data !== undefined && !sameForm(form, baseline)

  const patchForm = useCallback(
    (patch: Partial<CaptureForm>) => {
      setDraft((current) => changedOnly({ ...(current ?? {}), ...patch }, baseline))
    },
    [baseline],
  )

  // CAPTURE_SAVE_CHANGED_ONLY (MEU-151, D-966): the merged form is validated whole, and the PUT carries
  // only the draft leaves that still differ from the saved answer; none left means no PUT.
  const save = useCallback(async () => {
    parseSettingsPut('capture', form)
    const changed = CAPTURE_KEYS.filter((key) => draft !== null && key in draft && form[key] !== baseline[key])
    if (changed.length > 0) {
      await apiFetch('/settings/capture', {
        method: 'PUT',
        body: JSON.stringify(pickLeaves(form, changed)),
      })
    }
    setDraft(null)
    await queryClient.invalidateQueries({ queryKey: CAPTURE_SETTINGS_KEY })
  }, [baseline, draft, form, queryClient])

  return {
    form,
    isDirty,
    ready: query.isSuccess,
    patchForm,
    save,
    saveClass: isDirty ? 'btn-save-dirty' : undefined,
    saveLabel: isDirty ? 'Save Changes •' : 'Save',
    SettingsValidationError,
    ApiError,
  }
}
