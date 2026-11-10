import { useState } from 'react'

import { Button } from '../../components/ui/Button'
import { SelectInput } from '../../components/ui/SelectInput'
import {
  applyField,
  ASPECT_PRESETS,
  presetFeasible,
  type AspectPresetId,
  type CropBox,
  type CropField,
  type CropImage,
} from './capture-crop'
import { CROP_BUTTONS, type ToolbarButtonSpec } from './capture-toolbar'
import { ToolbarIconButton } from './ToolbarIconButton'

const FIELD_STEP_SHIFT = 10

const FIELDS: ReadonlyArray<{ field: CropField; key: string; label: string }> = [
  { field: 'x', key: 'x', label: 'X' },
  { field: 'y', key: 'y', label: 'Y' },
  { field: 'width', key: 'w', label: 'W' },
  { field: 'height', key: 'h', label: 'H' },
]

export type CaptureCropBarProps = {
  box: CropBox
  image: CropImage
  aspect: AspectPresetId
  swapped: boolean
  /** The POST is pending: Save as copy is busy and disabled. */
  busy: boolean
  /** The aspect's ratio, or null under Free; a field entry keeps it. */
  ratio: number | null
  /** Why the swap is disabled, if it is. */
  swapReason?: string
  onAspect: (aspect: AspectPresetId) => void
  onSwap: () => void
  onBox: (box: CropBox) => void
  onReset: () => void
  onCancel: () => void
  onSave: () => void
}

type CropFieldInputProps = {
  field: CropField
  testId: string
  label: string
  box: CropBox
  image: CropImage
  ratio: number | null
  onBox: (box: CropBox) => void
}

/** CROP_BAR field: Enter or blur applies, bad text and Esc revert, ArrowUp and ArrowDown step by 1 (Shift 10). */
function CropFieldInput({ field, testId, label, box, image, ratio, onBox }: CropFieldInputProps) {
  const [draft, setDraft] = useState<string | null>(null)
  function apply(text: string): void {
    setDraft(null)
    const next = applyField(box, field, text, image, ratio)
    if (next !== null) {
      onBox(next)
    }
  }
  return (
    <label className="flex shrink-0 items-center gap-1 text-sm">
      {label}
      <input
        data-testid={testId}
        className="w-14 font-mono"
        inputMode="numeric"
        value={draft ?? String(box[field])}
        onChange={(event) => {
          setDraft(event.target.value)
        }}
        onBlur={() => {
          if (draft !== null) {
            apply(draft)
          }
        }}
        onKeyDown={(event) => {
          if (event.key === 'Enter') {
            event.preventDefault()
            event.stopPropagation()
            if (draft !== null) {
              apply(draft)
            }
            return
          }
          if (event.key === 'Escape') {
            event.preventDefault()
            event.stopPropagation()
            setDraft(null)
            return
          }
          if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
            event.preventDefault()
            event.stopPropagation()
            const step = (event.shiftKey ? FIELD_STEP_SHIFT : 1) * (event.key === 'ArrowUp' ? 1 : -1)
            apply(String(box[field] + step))
          }
        }}
      />
    </label>
  )
}

/**
 * CROP_BAR (MEU-131, D-523): replaces the option groups while the crop is open. Aspect and its swap, the X, Y, W and
 * H fields, the size readout, Reset, Cancel and Save as copy.
 */
export function CaptureCropBar({
  box,
  image,
  aspect,
  swapped,
  busy,
  ratio,
  swapReason,
  onAspect,
  onSwap,
  onBox,
  onReset,
  onCancel,
  onSave,
}: CaptureCropBarProps) {
  const swapSpec = CROP_BUTTONS['capture-crop-swap'] as ToolbarButtonSpec
  return (
    <div data-testid="capture-crop-bar" role="group" aria-label="Crop" className="flex shrink-0 items-center gap-1">
      <span className="flex shrink-0 [&>div]:flex-row [&>div]:items-center [&>div]:gap-1">
        <SelectInput
          label="Aspect"
          data-testid="capture-crop-aspect"
          className="h-7! w-auto! px-2!"
          value={aspect}
          options={ASPECT_PRESETS.map(({ id, label }) => ({
            value: id,
            label,
            disabled: !presetFeasible(id, image, swapped),
          }))}
          onChange={(event) => {
            const next = ASPECT_PRESETS.find((preset) => preset.id === event.target.value)
            if (next !== undefined) {
              onAspect(next.id)
            }
          }}
        />
      </span>
      <ToolbarIconButton
        spec={swapSpec}
        id="capture-crop-swap"
        variant="ghost"
        shortcut="X"
        disabled={swapReason !== undefined}
        reason={swapReason}
        onClick={onSwap}
      />
      {FIELDS.map(({ field, key, label }) => (
        <CropFieldInput
          key={key}
          field={field}
          testId={`capture-crop-${key}`}
          label={label}
          box={box}
          image={image}
          ratio={ratio}
          onBox={onBox}
        />
      ))}
      <output data-testid="capture-crop-size" className="shrink-0 px-1 text-sm text-fg-muted">
        {`${box.width} × ${box.height} px`}
      </output>
      <Button size="sm" variant="ghost" data-testid="capture-crop-reset" onClick={onReset}>
        Reset
      </Button>
      <Button size="sm" variant="ghost" data-testid="capture-crop-cancel" onClick={onCancel}>
        Cancel
      </Button>
      <Button
        size="sm"
        variant="primary"
        data-testid="capture-crop-save"
        disabled={busy}
        aria-busy={busy ? 'true' : undefined}
        onClick={onSave}
      >
        Save as copy
      </Button>
    </div>
  )
}
