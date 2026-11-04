import { describe, expect, it } from 'vitest'

import { filmstripLabel } from '../../src/renderer/src/features/capture/capture-filmstrip-label'

function localTime(iso: string): string {
  const date = new Date(iso)
  const pad = (value: number): string => String(value).padStart(2, '0')
  return `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

describe('MEU-57 FILMSTRIP_LABEL_RULE', () => {
  it('AC-57.4 strips a leading ISO date and a space separator from the visible name', () => {
    const label = filmstripLabel('2026-09-03 14-22-08 settings-dialog.png', '2026-09-03T14:22:08Z')
    expect(label.name).toBe('14-22-08 settings-dialog.png')
    expect(label.full).toBe('2026-09-03 14-22-08 settings-dialog.png')
  })

  it('AC-57.4 strips an underscore-separated picker timestamp prefix (TIMESTAMP_FORMAT)', () => {
    expect(filmstripLabel('2026-09-03_14-22-08.png', '2026-09-03T14:22:08Z').name).toBe('14-22-08.png')
  })

  it('AC-57.4 keeps names without a date prefix unchanged', () => {
    expect(filmstripLabel('queue-card-menu.png', '2026-09-03T14:19:51Z').name).toBe('queue-card-menu.png')
    expect(filmstripLabel('2026-9-3 x.png', '2026-09-03T14:19:51Z').name).toBe('2026-9-3 x.png')
  })

  it('AC-57.4 falls back to the full name when stripping would leave nothing', () => {
    expect(filmstripLabel('2026-09-03 ', '2026-09-03T14:19:51Z').name).toBe('2026-09-03 ')
    expect(filmstripLabel('2026-09-03_', '2026-09-03T14:19:51Z').name).toBe('2026-09-03_')
  })

  it('AC-57.4 time line is created_at as local HH:MM:SS; an invalid timestamp yields no time', () => {
    expect(filmstripLabel('a.png', '2026-08-27T12:00:05Z').time).toBe(localTime('2026-08-27T12:00:05Z'))
    expect(filmstripLabel('a.png', 'not-a-date').time).toBe('')
  })
})
