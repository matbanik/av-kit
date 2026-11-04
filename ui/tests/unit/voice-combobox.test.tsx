/** @vitest-environment jsdom */

/**
 * MEU-64 VoiceCombobox (AC-64.4, AC-64.5) in isolation: the WAI-ARIA APG combobox with a
 * listbox popup. The page-level flows (PUT ledger) live in tts-page.behavior.test.ts.
 */
import { cleanup, render, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement, useState } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { VoiceCombobox } from '../../src/renderer/src/features/tts/VoiceCombobox'
import { groupVoices, matchVoices } from '../../src/renderer/src/features/tts/tts-voices'

const TEST_IDS = {
  input: 'voice-combobox',
  chip: 'voice-selected-chip',
  list: 'voice-grid',
  option: 'voice-card',
  language: 'language-select',
}

const VOICES = [
  { voice_id: 'af_heart', language: 'American English', gender: 'Female', style_description: 'heart' },
  { voice_id: 'am_adam', language: 'American English', gender: 'Male', style_description: 'adam' },
  { voice_id: 'bf_emma', language: 'British English', gender: 'Female', style_description: 'emma' },
  { voice_id: 'ff_siwis', language: 'French', gender: 'Female', style_description: 'siwis' },
]

function Harness(props: { onSelect: (voiceId: string) => void }) {
  const [value, setValue] = useState('af_heart')
  return createElement(
    'div',
    null,
    createElement('button', { type: 'button', 'data-testid': 'outside' }, 'outside'),
    createElement(VoiceCombobox, {
      voices: VOICES,
      value,
      testIds: TEST_IDS,
      onSelect: (voiceId: string) => {
        props.onSelect(voiceId)
        setValue(voiceId)
      },
    }),
  )
}

function setup() {
  const onSelect = vi.fn()
  const user = userEvent.setup()
  const view = render(createElement(Harness, { onSelect }))
  const byTestId = (id: string): HTMLElement => within(view.container).getByTestId(id)
  const query = (id: string): HTMLElement | null => within(view.container).queryByTestId(id)
  return { onSelect, user, byTestId, query }
}

afterEach(() => {
  cleanup()
})

describe('MEU-64 VoiceCombobox', () => {
  it('AC-64.4 closed by default: combobox input, selection chip, no popup', () => {
    const { byTestId, query } = setup()
    const input = byTestId('voice-combobox')
    expect(input.tagName).toBe('INPUT')
    expect(input.getAttribute('role')).toBe('combobox')
    expect(input.getAttribute('aria-expanded')).toBe('false')
    expect(input.getAttribute('aria-autocomplete')).toBe('list')
    expect(input.hasAttribute('aria-activedescendant')).toBe(false)
    expect(query('voice-grid')).toBeNull()
    expect(query('language-select')).toBeNull()
    expect(byTestId('voice-selected-chip').textContent).toBe('af_heart · heart')
  })

  it('AC-64.4 ArrowDown opens the popup; Home/End jump; Enter selects and keeps it open', async () => {
    const { byTestId, onSelect, user } = setup()
    const input = byTestId('voice-combobox')
    input.focus()
    await user.keyboard('{ArrowDown}')
    expect(input.getAttribute('aria-expanded')).toBe('true')
    const list = byTestId('voice-grid')
    expect(input.getAttribute('aria-controls')).toBe(list.id)
    const options = within(list).getAllByRole('option')
    expect(options.map((node) => node.textContent)).toEqual([
      expect.stringContaining('af_heart'),
      expect.stringContaining('am_adam'),
      expect.stringContaining('bf_emma'),
      expect.stringContaining('ff_siwis'),
    ])
    expect(input.getAttribute('aria-activedescendant')).toBe(options[0].id)
    await user.keyboard('{End}')
    expect(input.getAttribute('aria-activedescendant')).toBe(options[3].id)
    await user.keyboard('{Home}')
    expect(input.getAttribute('aria-activedescendant')).toBe(options[0].id)
    await user.keyboard('{ArrowDown}{ArrowDown}{Enter}')
    expect(onSelect).toHaveBeenCalledTimes(1)
    expect(onSelect).toHaveBeenCalledWith('bf_emma')
    expect(byTestId('voice-grid')).toBe(list)
    expect(within(list).getAllByRole('option')[2].getAttribute('aria-selected')).toBe('true')
    expect(byTestId('voice-selected-chip').textContent).toBe('bf_emma · emma')
  })

  it('AC-64.4 groups follow catalog order, each labelled by its language', async () => {
    const { byTestId, user } = setup()
    await user.click(byTestId('voice-combobox'))
    const groups = within(byTestId('voice-grid')).getAllByRole('group')
    expect(groups.map((group) => group.getAttribute('aria-label'))).toEqual([
      'American English',
      'British English',
      'French',
    ])
    expect(within(groups[0]).getAllByRole('option')).toHaveLength(2)
  })

  it('AC-64.4 Escape and an outside press close without selecting; the query resets', async () => {
    const { byTestId, onSelect, query, user } = setup()
    const input = byTestId('voice-combobox') as HTMLInputElement
    await user.type(input, 'emma')
    await user.keyboard('{ArrowDown}{Escape}')
    expect(input.getAttribute('aria-expanded')).toBe('false')
    expect(query('voice-grid')).toBeNull()
    expect(input.value).toBe('')
    await user.click(input)
    expect(input.getAttribute('aria-expanded')).toBe('true')
    await user.click(byTestId('outside'))
    expect(input.getAttribute('aria-expanded')).toBe('false')
    expect(onSelect).not.toHaveBeenCalled()
    expect(byTestId('voice-selected-chip').textContent).toBe('af_heart · heart')
  })

  it('AC-64.4 no match: empty state, no active option, Enter selects nothing', async () => {
    const { byTestId, onSelect, user } = setup()
    const input = byTestId('voice-combobox')
    await user.type(input, 'zzz')
    const list = byTestId('voice-grid')
    expect(within(list).queryAllByRole('option')).toHaveLength(0)
    expect(list.textContent).toContain('No voices match')
    await user.keyboard('{ArrowDown}{Enter}')
    expect(input.hasAttribute('aria-activedescendant')).toBe(false)
    expect(onSelect).not.toHaveBeenCalled()
  })

  it('AC-64.5 the language select sits in the popup header and ANDs with the query', async () => {
    const { byTestId, user } = setup()
    await user.click(byTestId('voice-combobox'))
    const language = byTestId('language-select') as HTMLSelectElement
    expect(byTestId('voice-grid').parentElement?.contains(language)).toBe(true)
    expect(Array.from(language.options).map((option) => option.textContent)).toEqual([
      'All',
      'American English',
      'British English',
      'French',
    ])
    await user.selectOptions(language, 'French')
    expect(byTestId('voice-combobox').getAttribute('aria-expanded')).toBe('true')
    expect(within(byTestId('voice-grid')).getAllByRole('option').map((node) => node.textContent)).toEqual([
      expect.stringContaining('ff_siwis'),
    ])
    await user.type(byTestId('voice-combobox'), 'am_')
    expect(within(byTestId('voice-grid')).queryAllByRole('option')).toHaveLength(0)
    expect(byTestId('voice-grid').textContent).toContain('No voices match')
    await user.selectOptions(byTestId('language-select'), '')
    expect(within(byTestId('voice-grid')).getAllByRole('option').map((node) => node.textContent)).toEqual([
      expect.stringContaining('am_adam'),
    ])
  })

  it('AC-64.4 matchVoices trims, ignores case and matches id, description or language; groupVoices keeps order', () => {
    expect(matchVoices(VOICES, '  EMMA ', null).map((v) => v.voice_id)).toEqual(['bf_emma'])
    expect(matchVoices(VOICES, 'french', null).map((v) => v.voice_id)).toEqual(['ff_siwis'])
    expect(matchVoices(VOICES, 'af_', 'French')).toEqual([])
    expect(matchVoices(VOICES, '', 'American English').map((v) => v.voice_id)).toEqual(['af_heart', 'am_adam'])
    expect(groupVoices([VOICES[2], VOICES[0], VOICES[3], VOICES[1]]).map((g) => [g.language, g.voices.length])).toEqual([
      ['British English', 1],
      ['American English', 2],
      ['French', 1],
    ])
  })
})

// MEU-74 (AC-74.8): `available: false` voices are listed but cannot be selected. A row without
// the fields is available (the older-backend shape above).
const VOICES_74 = [
  { voice_id: 'af_heart', language: 'American English', gender: 'Female', style_description: 'heart', available: true, reason: null },
  { voice_id: 'am_adam', language: 'American English', gender: 'Male', style_description: 'adam' },
  { voice_id: 'ef_dora', language: 'Spanish', gender: 'Female', style_description: 'dora', available: false, reason: 'espeak_missing' },
  { voice_id: 'jf_alpha', language: 'Japanese', gender: 'Female', style_description: 'alpha', available: false, reason: 'language_unsupported' },
] as const

function Harness74(props: { initial: string; onSelect: (voiceId: string) => void }) {
  const [value, setValue] = useState(props.initial)
  return createElement(VoiceCombobox, {
    voices: VOICES_74.map((voice) => ({ ...voice })),
    value,
    testIds: TEST_IDS,
    onSelect: (voiceId: string) => {
      props.onSelect(voiceId)
      setValue(voiceId)
    },
  })
}

function setup74(initial = 'af_heart') {
  const onSelect = vi.fn()
  const user = userEvent.setup()
  const view = render(createElement(Harness74, { initial, onSelect }))
  const byTestId = (id: string): HTMLElement => within(view.container).getByTestId(id)
  const option = (voiceId: string): HTMLElement =>
    within(byTestId('voice-grid'))
      .getAllByRole('option')
      .find((node) => node.textContent?.includes(voiceId)) as HTMLElement
  return { onSelect, user, byTestId, option }
}

describe('MEU-74 VoiceCombobox availability', () => {
  it('AC-74.8 unavailable voices are aria-disabled options that show their reason', async () => {
    const { byTestId, option, user } = setup74()
    await user.click(byTestId('voice-combobox'))
    expect(within(byTestId('voice-grid')).getAllByRole('option')).toHaveLength(4)
    expect(option('ef_dora').getAttribute('aria-disabled')).toBe('true')
    expect(within(option('ef_dora')).getByTestId('voice-unavailable-reason').textContent).toBe('Needs eSpeak NG')
    expect(option('jf_alpha').getAttribute('aria-disabled')).toBe('true')
    expect(within(option('jf_alpha')).getByTestId('voice-unavailable-reason').textContent).toBe(
      'Language not supported yet',
    )
    for (const voiceId of ['af_heart', 'am_adam']) {
      expect(option(voiceId).getAttribute('aria-disabled')).not.toBe('true')
      expect(within(option(voiceId)).queryByTestId('voice-unavailable-reason')).toBeNull()
    }
  })

  it('AC-74.8 a click on an unavailable option selects nothing', async () => {
    const { byTestId, onSelect, option, user } = setup74()
    await user.click(byTestId('voice-combobox'))
    await user.click(option('ef_dora'))
    await user.click(option('jf_alpha'))
    expect(onSelect).not.toHaveBeenCalled()
    expect(byTestId('voice-selected-chip').textContent).toBe('af_heart · heart')
  })

  it('AC-74.8 Enter on an active unavailable option selects nothing', async () => {
    const { byTestId, onSelect, option, user } = setup74()
    const input = byTestId('voice-combobox')
    input.focus()
    await user.keyboard('{ArrowDown}{End}')
    expect(input.getAttribute('aria-activedescendant')).toBe(option('jf_alpha').id)
    await user.keyboard('{Enter}')
    option('ef_dora').dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }))
    expect(onSelect).not.toHaveBeenCalled()
    expect(byTestId('voice-selected-chip').textContent).toBe('af_heart · heart')
  })

  it('AC-74.8 available voices, with or without the fields, still select', async () => {
    const { byTestId, onSelect, option, user } = setup74()
    await user.click(byTestId('voice-combobox'))
    await user.click(option('am_adam'))
    expect(onSelect).toHaveBeenCalledWith('am_adam')
    await user.keyboard('{Home}{Enter}')
    expect(onSelect).toHaveBeenLastCalledWith('af_heart')
    expect(onSelect).toHaveBeenCalledTimes(2)
  })

  it('AC-74.8 an unavailable current selection shows its reason on the chip', () => {
    const { byTestId } = setup74('ef_dora')
    const chip = byTestId('voice-selected-chip')
    expect(chip.textContent).toContain('ef_dora · dora')
    expect(within(chip).getByTestId('voice-unavailable-reason').textContent).toBe('Needs eSpeak NG')
  })

  it('AC-74.8 an available selection keeps the plain chip', () => {
    const { byTestId } = setup74('am_adam')
    expect(byTestId('voice-selected-chip').textContent).toBe('am_adam · adam')
  })
})
