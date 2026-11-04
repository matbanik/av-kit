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

export const CAPTURE_SETTINGS_KEY = ['settings', 'capture'] as const

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
    queryFn: async () => apiFetch<CapturePut>('/settings/capture'),
  })
  const [draft, setDraft] = useState<CaptureForm | null>(null)
  const baseline = useMemo(() => asForm(query.data), [query.data])
  const form = draft ?? baseline
  const isDirty = query.data !== undefined && !sameForm(form, baseline)

  const patchForm = useCallback(
    (patch: Partial<CaptureForm>) => {
      setDraft((current) => ({ ...(current ?? baseline), ...patch }))
    },
    [baseline],
  )

  const save = useCallback(async () => {
    const body = parseSettingsPut('capture', form)
    await apiFetch('/settings/capture', {
      method: 'PUT',
      body: JSON.stringify(body),
    })
    setDraft(null)
    await queryClient.invalidateQueries({ queryKey: CAPTURE_SETTINGS_KEY })
  }, [form, queryClient])

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
