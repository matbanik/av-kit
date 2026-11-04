import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useCallback, useMemo, useState } from 'react'

import { ApiError, apiFetch } from '../../lib/api'
import { converterPutSchema, SettingsValidationError, type ConverterPut } from '../settings/settings-schemas'
import { PRESET_DEFAULT, type GpuPrefWire, type PresetWire } from './convert-presets'

export const CONVERTER_SETTINGS_KEY = ['settings', 'converter'] as const

export type ConverterForm = {
  output_dir: string
  default_preset: PresetWire
  skip_existing: boolean
  gpu_preference: GpuPrefWire
}

export const CONVERTER_DEFAULTS: ConverterForm = {
  output_dir: '~/Videos/av-kit',
  default_preset: PRESET_DEFAULT,
  skip_existing: true,
  gpu_preference: 'auto',
}

function asForm(data: ConverterPut | undefined): ConverterForm {
  return {
    output_dir: typeof data?.output_dir === 'string' ? data.output_dir : CONVERTER_DEFAULTS.output_dir,
    default_preset:
      data?.default_preset === 'archival' ||
      data?.default_preset === 'high_quality' ||
      data?.default_preset === 'balanced' ||
      data?.default_preset === 'sharing' ||
      data?.default_preset === 'mobile'
        ? data.default_preset
        : CONVERTER_DEFAULTS.default_preset,
    skip_existing:
      typeof data?.skip_existing === 'boolean' ? data.skip_existing : CONVERTER_DEFAULTS.skip_existing,
    gpu_preference:
      data?.gpu_preference === 'auto' ||
      data?.gpu_preference === 'nvidia' ||
      data?.gpu_preference === 'amd' ||
      data?.gpu_preference === 'intel' ||
      data?.gpu_preference === 'software'
        ? data.gpu_preference
        : CONVERTER_DEFAULTS.gpu_preference,
  }
}

function sameForm(a: ConverterForm, b: ConverterForm): boolean {
  return (
    a.output_dir === b.output_dir &&
    a.default_preset === b.default_preset &&
    a.skip_existing === b.skip_existing &&
    a.gpu_preference === b.gpu_preference
  )
}

export function useConverterSettings() {
  const queryClient = useQueryClient()
  const query = useQuery({
    queryKey: CONVERTER_SETTINGS_KEY,
    queryFn: async () => apiFetch<ConverterPut>('/settings/converter'),
  })
  const [draft, setDraft] = useState<ConverterForm | null>(null)
  const baseline = useMemo(() => asForm(query.data), [query.data])
  const form = draft ?? baseline
  const isDirty = query.data !== undefined && !sameForm(form, baseline)

  const patchForm = useCallback((patch: Partial<ConverterForm>) => {
    setDraft((current) => ({ ...(current ?? baseline), ...patch }))
  }, [baseline])

  const save = useCallback(async () => {
    const body = converterPutSchema.parse(form)
    await apiFetch('/settings/converter', {
      method: 'PUT',
      body: JSON.stringify(body),
    })
    setDraft(null)
    await queryClient.invalidateQueries({ queryKey: CONVERTER_SETTINGS_KEY })
  }, [form, queryClient])

  return {
    form,
    isDirty,
    ready: query.isSuccess,
    patchForm,
    save,
    saveClass: isDirty ? 'btn-save-dirty' : undefined,
    saveLabel: isDirty ? 'Save Changes •' : 'Save',
    errorEvent: (message: string) => {
      window.dispatchEvent(
        new CustomEvent('av-kit:settings:error', { detail: { namespace: 'converter', message } }),
      )
    },
    SettingsValidationError,
    ApiError,
  }
}
