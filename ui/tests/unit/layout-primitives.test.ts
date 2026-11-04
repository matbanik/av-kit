/** @vitest-environment jsdom */

/** MEU-51 FIC: Red-first assertions from the approved Session 23 plan AC-51.1–51.7. */
import { createHash } from 'node:crypto'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { cleanup, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'

const ui = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const componentDir = resolve(ui, 'src/renderer/src/components/ui')
const registryPath = resolve(ui, 'tests/e2e/test-ids.ts')
const e2ePath = resolve(ui, 'tests/e2e/layout-primitives.test.ts')
const harnessHtml = resolve(ui, 'src/renderer/primitive-harness.html')
const harnessEntry = resolve(ui, 'src/renderer/src/primitive-harness.tsx')

function componentPath(name: string): string {
  return resolve(componentDir, `${name}.tsx`)
}

async function loadComponent(name: string) {
  const modulePath = `../../src/renderer/src/components/ui/${name}.tsx`
  return import(/* @vite-ignore */ modulePath)
}

afterEach(cleanup)

describe('MEU-51 shared layout primitives', () => {
  it('AC-51.1 Disclosure uses a controlled canonical button and hides closed content', async () => {
    expect(existsSync(componentPath('Disclosure'))).toBe(true)
    const { Disclosure } = await loadComponent('Disclosure')
    const onOpenChange = vi.fn()
    const child = createElement('button', { type: 'button' }, 'Inside')
    const view = render(createElement(Disclosure, { id: 'advanced', title: 'Advanced', open: false, onOpenChange }, child))
    const trigger = screen.getByRole('button', { name: 'Advanced' })
    expect(trigger.className).toContain('btn-')
    expect(trigger.getAttribute('aria-expanded')).toBe('false')
    expect(trigger.getAttribute('aria-controls')).toBe('advanced-panel')
    expect(screen.queryByRole('button', { name: 'Inside' })).toBeNull()
    const user = userEvent.setup()
    await user.click(trigger)
    expect(onOpenChange).toHaveBeenCalledWith(true)
    view.rerender(createElement(Disclosure, { id: 'advanced', title: 'Advanced', open: true, onOpenChange }, child))
    expect(trigger.getAttribute('aria-expanded')).toBe('true')
    expect(screen.getByRole('button', { name: 'Inside' })).toBeTruthy()
    trigger.focus()
    await user.keyboard('{Enter}')
    await user.keyboard(' ')
    expect(onOpenChange).toHaveBeenLastCalledWith(false)
  })

  it('AC-51.2 SegmentedControl uses caller IDs, native radios, and finite values', async () => {
    expect(existsSync(componentPath('SegmentedControl'))).toBe(true)
    const { SegmentedControl } = await loadComponent('SegmentedControl')
    const onValueChange = vi.fn()
    const options = [
      { id: 'cookie-none', value: 'none', label: 'None' },
      { id: 'cookie-browser', value: 'browser', label: 'Browser' },
      { id: 'cookie-file', value: 'file', label: 'File' },
    ]
    const view = render(createElement(SegmentedControl, { name: 'cookie-mode', value: 'none', options, onValueChange }))
    const radios = screen.getAllByRole('radio') as HTMLInputElement[]
    expect(radios.map((radio) => radio.id)).toEqual(options.map((option) => option.id))
    expect(radios.map((radio) => radio.name)).toEqual(['cookie-mode', 'cookie-mode', 'cookie-mode'])
    expect(radios.filter((radio) => radio.checked)).toHaveLength(1)
    const user = userEvent.setup()
    await user.click(screen.getByRole('radio', { name: 'Browser' }))
    expect(onValueChange).toHaveBeenCalledWith('browser')
    view.rerender(createElement(SegmentedControl, { name: 'cookie-mode', value: 'browser', options, onValueChange }))
    expect((screen.getByRole('radio', { name: 'Browser' }) as HTMLInputElement).checked).toBe(true)
    screen.getByRole('radio', { name: 'Browser' }).focus()
    await user.keyboard('{ArrowRight}')
    expect(onValueChange).toHaveBeenCalledWith('file')
    expect(onValueChange.mock.calls.every(([value]) => options.some((option) => option.value === value))).toBe(true)
  })

  it('AC-51.2/R1 keeps caller test IDs on radios in multiple instances', async () => {
    const { SegmentedControl } = await loadComponent('SegmentedControl')
    render(createElement('div', null,
      createElement(SegmentedControl, {
        name: 'cookie-mode', value: 'none', onValueChange: vi.fn(),
        options: [
          { id: 'cookie-none', testId: 'cookie-mode-none', value: 'none', label: 'None' },
          { id: 'cookie-browser', testId: 'cookie-mode-browser', value: 'browser', label: 'Browser' },
        ],
      }),
      createElement(SegmentedControl, {
        name: 'speed-mode', value: 'normal', onValueChange: vi.fn(),
        options: [{ id: 'speed-normal', testId: 'speed-mode-normal', value: 'normal', label: 'Normal' }],
      }),
    ))
    for (const [testId, id] of [
      ['cookie-mode-none', 'cookie-none'],
      ['cookie-mode-browser', 'cookie-browser'],
      ['speed-mode-normal', 'speed-normal'],
    ]) {
      const radio = screen.getByTestId(testId)
      expect(radio.tagName).toBe('INPUT')
      expect(radio.getAttribute('type')).toBe('radio')
      expect(radio.id).toBe(id)
    }
  })

  it('AC-51.3 StatusChip renders readable text for each finite token tone', async () => {
    expect(existsSync(componentPath('StatusChip'))).toBe(true)
    const { StatusChip } = await loadComponent('StatusChip')
    for (const tone of ['neutral', 'info', 'success', 'warning', 'danger'] as const) {
      const view = render(createElement(StatusChip, { label: 'Queued', count: 3, tone, testId: `chip-${tone}` }))
      const chip = screen.getByTestId(`chip-${tone}`)
      expect(chip.textContent).toContain('Queued')
      expect(chip.textContent).toContain('3')
      expect(chip.getAttribute('data-tone')).toBe(tone)
      expect(chip.className).toMatch(/bg-|text-/)
      view.unmount()
    }
    expect(readFileSync(componentPath('StatusChip'), 'utf8')).not.toMatch(/#[0-9a-f]{3,8}\b/i)
  })

  it('AC-51.4 FormRow and PathRow keep associations, exact value, and one Browse action', async () => {
    expect(existsSync(componentPath('FormRow'))).toBe(true)
    expect(existsSync(componentPath('PathRow'))).toBe(true)
    const { FormRow } = await loadComponent('FormRow')
    const { PathRow } = await loadComponent('PathRow')
    const form = render(createElement(FormRow, { id: 'model-dir', label: 'Model directory', hint: 'Use an absolute path', error: 'Required' }, createElement('input')))
    const field = screen.getByRole('textbox', { name: 'Model directory' })
    expect(field.id).toBe('model-dir')
    expect(field.getAttribute('aria-describedby')).toContain('model-dir-hint')
    expect(field.getAttribute('aria-describedby')).toContain('model-dir-error')
    expect(screen.getByText('Required').getAttribute('id')).toBe('model-dir-error')
    form.unmount()
    const onChange = vi.fn()
    const onBrowse = vi.fn()
    render(createElement(PathRow, { id: 'output-dir', label: 'Output folder', value: 'C:/one folder', onChange, onBrowse }))
    const pathInput = screen.getByRole('textbox', { name: 'Output folder' }) as HTMLInputElement
    expect(pathInput.value).toBe('C:/one folder')
    await userEvent.setup().type(pathInput, '/next')
    expect(onChange).toHaveBeenCalled()
    await userEvent.setup().click(screen.getByRole('button', { name: 'Browse' }))
    expect(onBrowse).toHaveBeenCalledTimes(1)
  })

  it('AC-51.4/R1/R2 forwards independent path control IDs and omits absent Browse', async () => {
    const { PathRow } = await loadComponent('PathRow')
    const onBrowse = vi.fn()
    render(createElement('div', null,
      createElement(PathRow, {
        id: 'download-path', label: 'Download path', value: 'C:/one folder', onChange: vi.fn(),
        onBrowse, testId: 'download-path-row', inputTestId: 'settings-leaf-path',
        browseTestId: 'browse-download-path-btn',
      }),
      createElement(PathRow, {
        id: 'capture-path', label: 'Capture path', value: 'D:/shots', onChange: vi.fn(),
        testId: 'capture-path-row', inputTestId: 'capture-inbox-path',
      }),
    ))
    const input = screen.getByTestId('settings-leaf-path') as HTMLInputElement
    expect(input.tagName).toBe('INPUT')
    expect(input.value).toBe('C:/one folder')
    expect(screen.getByTestId('browse-download-path-btn').tagName).toBe('BUTTON')
    await userEvent.setup().click(screen.getByTestId('browse-download-path-btn'))
    expect(onBrowse).toHaveBeenCalledTimes(1)
    const second = screen.getByTestId('capture-path-row')
    expect(within(second).getByTestId('capture-inbox-path').tagName).toBe('INPUT')
    expect(within(second).queryByRole('button', { name: 'Browse' })).toBeNull()
  })

  it('AC-58.5 PathRow readOnly is additive: the field is read-only and Browse still fires once', async () => {
    const { PathRow } = await loadComponent('PathRow')
    const onBrowse = vi.fn()
    const onChange = vi.fn()
    render(createElement(PathRow, {
      id: 'ro-path', label: 'FFmpeg path', value: 'C:/bin/ffmpeg.exe', onChange, onBrowse,
      readOnly: true, inputTestId: 'ro-input', browseTestId: 'ro-browse',
    }))
    const input = screen.getByTestId('ro-input') as HTMLInputElement
    expect(input.readOnly).toBe(true)
    await userEvent.setup().type(input, 'x')
    expect(onChange).not.toHaveBeenCalled()
    expect(input.value).toBe('C:/bin/ffmpeg.exe')
    await userEvent.setup().click(screen.getByTestId('ro-browse'))
    expect(onBrowse).toHaveBeenCalledTimes(1)
  })

  it('AC-51.5 components stay isolated, token based, and retain the canonical Button contract', () => {
    for (const name of ['Disclosure', 'SegmentedControl', 'StatusChip', 'FormRow', 'PathRow']) {
      const path = componentPath(name)
      expect(existsSync(path), name).toBe(true)
      const source = readFileSync(path, 'utf8')
      expect(source, name).not.toMatch(/(?:features\/|pages\/|apiFetch|transition-all|TODO|FIXME|NotImplementedError|#[0-9a-f]{3,8}\b)/i)
    }
    const button = readFileSync(componentPath('Button'), 'utf8')
    expect(button).toContain("type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive'")
    expect(button).toContain("type ButtonSize = 'sm' | 'md' | 'lg'")
  })

  it('AC-51.6 adds unique primitive IDs while preserving the exact prior registry prefix [TA-26]', () => {
    const registry = readFileSync(registryPath, 'utf8')
    const marker = '// MEU-51 primitive harness IDs.'
    expect(registry).toContain(marker)
    const prefix = registry.split(marker)[0]
    const hash = createHash('sha256').update(prefix).digest('hex').toUpperCase()
    expect(hash).toBe('6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454')
    const priorValues = [...prefix.matchAll(/^export const \w+ = '([^']+)'/gm)].map((match) => match[1])
    const newValues = [...registry.split(marker)[1].matchAll(/^export const \w+ = '([^']+)'/gm)].map((match) => match[1])
    expect(new Set(newValues).size).toBe(newValues.length)
    expect(newValues.every((value) => !priorValues.includes(value))).toBe(true)
    for (const id of ['primitive-disclosure', 'primitive-segment', 'primitive-chip', 'primitive-form', 'primitive-path']) {
      expect(newValues).toContain(id)
    }
  })

  it('AC-51.7 wires a fresh, allowlisted real Electron harness without product page mounts', () => {
    expect(existsSync(e2ePath)).toBe(true)
    expect(existsSync(harnessHtml)).toBe(true)
    expect(existsSync(harnessEntry)).toBe(true)
    const entry = readFileSync(harnessEntry, 'utf8')
    for (const name of ['Disclosure', 'SegmentedControl', 'StatusChip', 'FormRow', 'PathRow']) {
      expect(entry).toContain(`components/ui/${name}`)
    }
    const config = readFileSync(resolve(ui, 'electron.vite.config.ts'), 'utf8')
    const setup = readFileSync(resolve(ui, 'tests/e2e/global-setup.ts'), 'utf8')
    const e2e = readFileSync(e2ePath, 'utf8')
    expect(config).toContain('AVKIT_PRIMITIVE_HARNESS_BUILD')
    expect(config).toContain('primitive-harness.html')
    expect(setup).toContain('AVKIT_E2E_OUT_DIR')
    expect(setup).toContain('out-e2e')
    expect(setup).toContain('primitive-harness.html')
    expect(e2e).toContain('_electron.launch')
    expect(e2e).toContain('primitive-harness.html')
    expect(e2e).toContain('toBeVisible')
    // TA-1 (Session 25, class D): Transcript (MEU-55) and TTS (MEU-56) adopt the
    // primitives; the pages still awaiting their page MEU keep the restriction.
    // TM-1 (Session 26): Capture (MEU-57) and Settings (MEU-58) adopt their primitives;
    // no page remains under the pre-adoption restriction.
    const settings = readFileSync(resolve(ui, 'src/renderer/src/features/settings/SettingsPage.tsx'), 'utf8')
    for (const primitive of ['SegmentedControl', 'StatusChip', 'FormRow', 'PathRow']) {
      expect(settings, `SettingsPage adopts ${primitive}`).toContain(`components/ui/${primitive}`)
    }
    const capture = readFileSync(resolve(ui, 'src/renderer/src/features/capture/CapturePage.tsx'), 'utf8')
    for (const primitive of ['Disclosure', 'StatusChip', 'PathRow']) {
      expect(capture, `CapturePage adopts ${primitive}`).toContain(`components/ui/${primitive}`)
    }
    // Human-approved Session 24 supersedes the pre-adoption restriction for
    // these two pages; the remaining scheduled pages retain it.
    for (const [folder, page] of [['downloader', 'DownloaderPage'], ['converter', 'ConvertPage']]) {
      const source = readFileSync(resolve(ui, 'src/renderer/src/features', folder, `${page}.tsx`), 'utf8')
      for (const primitive of ['Disclosure', 'SegmentedControl', 'StatusChip']) {
        expect(source, `${page} adopts ${primitive}`).toContain(`components/ui/${primitive}`)
      }
    }
    const transcript = readFileSync(resolve(ui, 'src/renderer/src/features/transcript/TranscriptPage.tsx'), 'utf8')
    expect(transcript, 'TranscriptPage adopts StatusChip').toContain('components/ui/StatusChip')
    const tts = readFileSync(resolve(ui, 'src/renderer/src/features/tts/TTSPage.tsx'), 'utf8')
    for (const primitive of ['Disclosure', 'SegmentedControl', 'StatusChip']) {
      expect(tts, `TTSPage adopts ${primitive}`).toContain(`components/ui/${primitive}`)
    }
  })
})

describe('MEU-65 Disclosure optional props (Session 29 plan AC-65.6)', () => {
  it('AC-65.6 a Disclosure without the new props renders as before: ghost, no svg, title-only text', async () => {
    const { Disclosure } = await loadComponent('Disclosure')
    render(createElement(Disclosure, { id: 'plain', title: 'Advanced', open: false, onOpenChange: vi.fn() }, 'Body'))
    const trigger = screen.getByRole('button', { name: 'Advanced' })
    expect(trigger.className).toContain('btn-ghost')
    expect(trigger.querySelector('svg')).toBeNull()
    expect(trigger.textContent).toBe('Advanced')
    expect(trigger.childNodes).toHaveLength(1)
    expect(document.querySelector('[data-testid="plain-chevron"]')).toBeNull()
  })

  it('AC-65.6 variant, icon and chevron render when passed; the chevron state follows open', async () => {
    const { Disclosure } = await loadComponent('Disclosure')
    const icon = createElement('svg', { 'aria-hidden': 'true', 'data-testid': 'lead-icon' })
    const view = render(
      createElement(
        Disclosure,
        { id: 'opts', title: 'Options', open: false, onOpenChange: vi.fn(), variant: 'secondary', icon, chevron: true },
        'Body',
      ),
    )
    const trigger = screen.getByRole('button', { name: 'Options' })
    expect(trigger.className).toContain('btn-secondary')
    expect(trigger.className).not.toContain('btn-ghost')
    expect(trigger.firstElementChild?.getAttribute('data-testid')).toBe('lead-icon')
    const chevron = within(trigger).getByTestId('opts-chevron')
    expect(chevron.getAttribute('data-state')).toBe('closed')
    expect(chevron.querySelector('svg')?.getAttribute('aria-hidden')).toBe('true')
    view.rerender(
      createElement(
        Disclosure,
        { id: 'opts', title: 'Options', open: true, onOpenChange: vi.fn(), variant: 'secondary', icon, chevron: true },
        'Body',
      ),
    )
    expect(within(trigger).getByTestId('opts-chevron').getAttribute('data-state')).toBe('open')
    expect(trigger.getAttribute('aria-expanded')).toBe('true')
  })
})

describe('MEU-79 SegmentedControl size (Session 35 plan AC-79.5)', () => {
  it('AC-79.5 default and sm keep the baseline inner class; md appends only h-9', async () => {
    const { SegmentedControl } = await loadComponent('SegmentedControl')
    const baseline = 'inline-flex rounded-[var(--radius-control)] border border-border bg-surface-0 p-0.5'
    const options = [
      { id: 'size-1-0', testId: 'size-1-0', value: '1', label: '1.0' },
      { id: 'size-1-5', testId: 'size-1-5', value: '1.5', label: '1.5' },
    ]
    const inner = (size?: 'sm' | 'md'): { className: string; html: string } => {
      const props: Record<string, unknown> = { name: 'Speed preset', value: '1', options, onValueChange: vi.fn() }
      if (size !== undefined) {
        props.size = size
      }
      const view = render(createElement(SegmentedControl, props))
      const div = view.container.querySelector('fieldset > div')
      expect(div).not.toBeNull()
      const out = { className: (div as HTMLElement).className, html: (div as HTMLElement).innerHTML }
      view.unmount()
      return out
    }
    const plain = inner()
    const sm = inner('sm')
    const md = inner('md')
    expect(plain.className).toBe(baseline)
    expect(plain.className).not.toContain('h-9')
    expect(sm.className).toBe(baseline)
    expect(md.className).toBe(`${baseline} h-9`)
    expect(sm.html).toBe(plain.html)
    expect(md.html).toBe(sm.html)
  })
})

describe('MEU-93 PathRow placeholder and browseDisabled (Session 40 plan AC-93.1)', () => {
  it('AC-93.1 placeholder reaches the input; browseDisabled disables Browse and a click never calls onBrowse', async () => {
    const { PathRow } = await loadComponent('PathRow')
    const onBrowse = vi.fn()
    render(createElement(PathRow, {
      id: 'ph-path', label: 'Backup folder', value: '', onChange: vi.fn(), onBrowse,
      placeholder: 'D:/x', browseDisabled: true, inputTestId: 'ph-input', browseTestId: 'ph-browse',
    }))
    expect(screen.getByTestId('ph-input').getAttribute('placeholder')).toBe('D:/x')
    const browse = screen.getByTestId('ph-browse') as HTMLButtonElement
    expect(browse.disabled).toBe(true)
    await userEvent.setup().click(browse)
    expect(onBrowse).not.toHaveBeenCalled()
  })

  it('AC-93.1 without the props there is no placeholder and no disabled attribute; browseDisabled={false} keeps Browse live', async () => {
    const { PathRow } = await loadComponent('PathRow')
    const onBrowse = vi.fn()
    const plain = render(createElement(PathRow, {
      id: 'plain-path', label: 'Output folder', value: 'C:/out', onChange: vi.fn(), onBrowse,
      inputTestId: 'plain-input', browseTestId: 'plain-browse',
    }))
    expect(screen.getByTestId('plain-input').hasAttribute('placeholder')).toBe(false)
    expect(screen.getByTestId('plain-browse').hasAttribute('disabled')).toBe(false)
    plain.unmount()
    render(createElement(PathRow, {
      id: 'live-path', label: 'Output folder', value: 'C:/out', onChange: vi.fn(), onBrowse,
      browseDisabled: false, inputTestId: 'live-input', browseTestId: 'live-browse',
    }))
    const browse = screen.getByTestId('live-browse') as HTMLButtonElement
    expect(browse.disabled).toBe(false)
    await userEvent.setup().click(browse)
    expect(onBrowse).toHaveBeenCalledTimes(1)
  })
})
