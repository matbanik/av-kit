import { useEffect, useId, useMemo, useRef, useState, type KeyboardEvent } from 'react'

import { SelectInput } from '../../components/ui/SelectInput'
import { StatusChip } from '../../components/ui/StatusChip'
import { groupVoices, matchVoices, voiceUnavailableText, type VoiceOut } from './tts-voices'

// `VOICE_UNAVAILABLE_REASON` in `test-ids.ts`. Hardcoded here because the page that owns the
// other ids (`TTSPage.tsx`) is outside MEU-74's file set and cannot pass a new one down.
const REASON_TEST_ID = 'voice-unavailable-reason'

/** The page owns its registered test ids (`test-ids.ts`); the combobox only applies them. */
export type VoiceComboboxTestIds = {
  input: string
  chip: string
  list: string
  option: string
  language: string
}

export type VoiceComboboxProps = {
  voices: VoiceOut[]
  value: string
  onSelect: (voiceId: string) => void
  testIds: VoiceComboboxTestIds
}

/**
 * Searchable voice picker (WAI-ARIA APG combobox with a listbox popup, MEU-64).
 *
 * The input filters by voice id, description and language. The popup groups the
 * matches by language and carries the language select in its header. It opens on
 * focus/typing/ArrowDown, stays open while a voice is chosen, and closes on Escape or
 * a pointer press outside the picker. Escape never changes the voice.
 *
 * MEU-74: an unavailable voice stays listed and reachable by the arrow keys, but is an
 * `aria-disabled` option that click, Enter and Space never select. It shows its reason,
 * and so does the chip when the current selection is unavailable.
 */
export function VoiceCombobox({ voices, value, onSelect, testIds }: VoiceComboboxProps): React.JSX.Element {
  const listId = useId()
  const rootRef = useRef<HTMLDivElement | null>(null)
  const inputRef = useRef<HTMLInputElement | null>(null)
  const listRef = useRef<HTMLDivElement | null>(null)
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [language, setLanguage] = useState('')
  const [active, setActive] = useState(-1)

  const languages = useMemo(() => groupVoices(voices).map((group) => group.language), [voices])
  const matches = useMemo(() => matchVoices(voices, query, language || null), [voices, query, language])
  const groups = useMemo(() => groupVoices(matches), [matches])
  // Options in display order (grouped), so arrow keys follow what is on screen.
  const ordered = useMemo(() => groups.flatMap((group) => group.voices), [groups])
  const selected = voices.find((item) => item.voice_id === value)
  const selectedReason = selected ? voiceUnavailableText(selected) : null
  const selectedVisible = ordered.some((item) => item.voice_id === value)
  const optionId = (voiceId: string): string => `${listId}-option-${voiceId}`
  const activeVoice = active >= 0 ? ordered[active] : undefined

  useEffect(() => {
    if (!open) {
      return
    }
    const onPointerDown = (event: MouseEvent): void => {
      if (rootRef.current && !rootRef.current.contains(event.target as Node)) {
        setOpen(false)
        setActive(-1)
        setQuery('')
      }
    }
    document.addEventListener('mousedown', onPointerDown)
    return () => {
      document.removeEventListener('mousedown', onPointerDown)
    }
  }, [open])

  useEffect(() => {
    if (activeVoice) {
      document.getElementById(`${listId}-option-${activeVoice.voice_id}`)?.scrollIntoView?.({ block: 'nearest' })
    }
  }, [activeVoice, listId])

  function close(): void {
    setOpen(false)
    setActive(-1)
    setQuery('')
  }

  function moveActive(next: number): void {
    if (ordered.length === 0) {
      setActive(-1)
      return
    }
    setActive(Math.max(0, Math.min(ordered.length - 1, next)))
  }

  function onInputKeyDown(event: KeyboardEvent<HTMLInputElement>): void {
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault()
        if (!open) {
          setOpen(true)
        }
        moveActive(active + 1)
        return
      case 'ArrowUp':
        event.preventDefault()
        if (!open) {
          setOpen(true)
          moveActive(ordered.length - 1)
          return
        }
        moveActive(active - 1)
        return
      case 'Home':
        if (open) {
          event.preventDefault()
          moveActive(0)
        }
        return
      case 'End':
        if (open) {
          event.preventDefault()
          moveActive(ordered.length - 1)
        }
        return
      case 'Enter':
        if (open && activeVoice) {
          event.preventDefault()
          if (voiceUnavailableText(activeVoice) === null) {
            onSelect(activeVoice.voice_id)
          }
        }
        return
      case 'Escape':
        if (open) {
          event.preventDefault()
          close()
        }
        return
      default:
        return
    }
  }

  /** Roving focus inside the popup: arrows/Home/End move focus only; Enter/Space select. */
  function onOptionKeyDown(event: KeyboardEvent<HTMLDivElement>, voiceId: string, disabled: boolean): void {
    const options = Array.from(listRef.current?.querySelectorAll<HTMLElement>('[role="option"]') ?? [])
    const index = options.indexOf(event.currentTarget)
    const focusAt = (next: number): void => {
      event.preventDefault()
      options[Math.max(0, Math.min(options.length - 1, next))]?.focus()
    }
    switch (event.key) {
      case 'ArrowDown':
        focusAt(index + 1)
        return
      case 'ArrowUp':
        focusAt(index - 1)
        return
      case 'Home':
        focusAt(0)
        return
      case 'End':
        focusAt(options.length - 1)
        return
      case 'Enter':
      case ' ':
        event.preventDefault()
        if (!disabled) {
          onSelect(voiceId)
        }
        return
      case 'Escape':
        event.preventDefault()
        close()
        inputRef.current?.focus()
        return
      default:
        return
    }
  }

  return (
    <div ref={rootRef} className="relative flex flex-col gap-1.5">
      <div className="flex flex-wrap items-center gap-2">
        <label htmlFor={`${listId}-input`} className="text-sm font-medium text-fg-muted">
          Voice
        </label>
        {selected && selectedReason !== null ? (
          // StatusChip takes a text label only, so the unavailable chip carries its reason itself.
          <span
            data-testid={testIds.chip}
            data-tone="warning"
            className="inline-flex items-center gap-1 rounded-[var(--radius-full)] bg-status-pending/10 px-2 py-0.5 text-xs font-medium text-fg"
          >
            <span>{`${selected.voice_id} · ${selected.style_description}`}</span>
            <span data-testid={REASON_TEST_ID} className="text-fg-muted">
              {selectedReason}
            </span>
          </span>
        ) : (
          <StatusChip
            testId={testIds.chip}
            tone="neutral"
            label={
              selected
                ? `${selected.voice_id} · ${selected.style_description}`
                : voices.length === 0
                  ? 'Loading voices…'
                  : value
            }
          />
        )}
      </div>
      <input
        ref={inputRef}
        id={`${listId}-input`}
        data-testid={testIds.input}
        type="text"
        role="combobox"
        aria-expanded={open}
        aria-controls={listId}
        aria-autocomplete="list"
        aria-activedescendant={open && activeVoice ? optionId(activeVoice.voice_id) : undefined}
        autoComplete="off"
        placeholder="Search voices by name or language"
        className={[
          'h-9 w-full rounded-[var(--radius-control)] border border-border bg-surface-0 px-3 text-sm text-fg',
          'focus:border-accent focus:shadow-[0_0_0_3px_var(--color-accent-ring)] focus:outline-none',
        ].join(' ')}
        value={query}
        onClick={() => {
          setOpen(true)
        }}
        onChange={(event) => {
          setQuery(event.target.value)
          setActive(-1)
          setOpen(true)
        }}
        onKeyDown={onInputKeyDown}
      />
      {open ? (
        <div className="absolute top-full right-0 left-0 z-20 mt-1 flex flex-col gap-2 rounded-[var(--radius-md)] border border-border bg-bg-elevated p-2 shadow-lg">
          <div className="flex items-end gap-2">
            <SelectInput
              data-testid={testIds.language}
              label="Language"
              className="w-[180px]"
              options={[{ value: '', label: 'All' }, ...languages.map((lang) => ({ value: lang, label: lang }))]}
              value={language}
              onChange={(event) => {
                setLanguage(event.target.value)
                setActive(-1)
              }}
            />
            <span className="ml-auto text-xs tabular-nums text-fg-muted">{`${ordered.length} voices`}</span>
          </div>
          <div
            ref={listRef}
            id={listId}
            data-testid={testIds.list}
            role="listbox"
            aria-label="Voice"
            className="flex max-h-[280px] flex-col overflow-auto rounded-[var(--radius-md)] border border-border"
          >
            {ordered.length === 0 ? <p className="p-2 text-sm text-fg-muted">No voices match</p> : null}
            {groups.map((group) => (
              <div key={group.language} role="group" aria-label={group.language} className="flex flex-col">
                <div aria-hidden="true" className="px-2 pt-1.5 pb-0.5 text-xs font-semibold text-fg-muted">
                  {group.language}
                </div>
                {group.voices.map((item) => {
                  const isSelected = item.voice_id === value
                  const tabbable = selectedVisible ? isSelected : item === ordered[0]
                  const isActive = activeVoice?.voice_id === item.voice_id
                  const reason = voiceUnavailableText(item)
                  const disabled = reason !== null
                  return (
                    <div
                      key={item.voice_id}
                      id={optionId(item.voice_id)}
                      role="option"
                      data-testid={testIds.option}
                      aria-selected={isSelected}
                      aria-disabled={disabled ? true : undefined}
                      tabIndex={tabbable ? 0 : -1}
                      className={[
                        'flex h-[30px] shrink-0 items-center gap-2 border px-2 text-sm',
                        disabled ? 'cursor-not-allowed text-fg-muted' : 'cursor-pointer',
                        'focus-visible:outline-none focus-visible:shadow-[0_0_0_3px_var(--color-accent-ring)]',
                        isSelected ? 'border-accent/50 bg-accent/10' : 'border-transparent hover:bg-neutral/30',
                        isActive ? 'shadow-[0_0_0_3px_var(--color-accent-ring)]' : '',
                      ].join(' ')}
                      onClick={() => {
                        if (!disabled) {
                          onSelect(item.voice_id)
                        }
                      }}
                      onKeyDown={(event) => {
                        onOptionKeyDown(event, item.voice_id, disabled)
                      }}
                    >
                      <span className="font-medium">{item.voice_id}</span>
                      <span className="min-w-0 truncate text-fg-muted">{item.style_description}</span>
                      {disabled ? (
                        <span data-testid={REASON_TEST_ID} className="ml-auto shrink-0 text-xs text-fg-muted">
                          {reason}
                        </span>
                      ) : null}
                    </div>
                  )
                })}
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  )
}
