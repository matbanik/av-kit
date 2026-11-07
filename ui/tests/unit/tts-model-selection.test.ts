/**
 * MEU-117 AC-117.13: `defaultModelSelection` never picks a variant this build can't run.
 * Each rule (the chosen row, the first downloaded, the first row) skips a row with
 * `available: false`; the loaded row is kept, as a load of an unavailable variant is refused.
 */
import { describe, expect, it } from 'vitest'

import { defaultModelSelection } from '../../src/renderer/src/features/tts/tts-controls'

const PYTORCH = { id: 'kokoro-pt-fp32', is_downloaded: true, available: false }
const ONNX_FP16 = { id: 'kokoro-onnx-fp16', is_downloaded: false, available: true }
const ONNX_INT8 = { id: 'kokoro-onnx-int8', is_downloaded: true, available: true }

describe('MEU-117 AC-117.13 defaultModelSelection skips unavailable rows', () => {
  it('AC-117.13 skips an unavailable chosen row for the next rule', () => {
    const catalog = [PYTORCH, ONNX_FP16, ONNX_INT8]
    expect(defaultModelSelection({ chosen: PYTORCH.id, loadedVariantId: null, catalog })).toBe(ONNX_INT8.id)
    expect(defaultModelSelection({ chosen: ONNX_FP16.id, loadedVariantId: null, catalog })).toBe(ONNX_FP16.id)
  })

  it('AC-117.13 the first-downloaded rule skips an unavailable row', () => {
    const catalog = [PYTORCH, ONNX_FP16, ONNX_INT8]
    expect(defaultModelSelection({ chosen: null, loadedVariantId: null, catalog })).toBe(ONNX_INT8.id)
  })

  it('AC-117.13 the first-row rule skips an unavailable row', () => {
    const catalog = [{ ...PYTORCH, is_downloaded: false }, ONNX_FP16]
    expect(defaultModelSelection({ chosen: null, loadedVariantId: null, catalog })).toBe(ONNX_FP16.id)
  })

  it('AC-117.13 keeps the loaded row', () => {
    const catalog = [PYTORCH, ONNX_FP16, ONNX_INT8]
    expect(defaultModelSelection({ chosen: null, loadedVariantId: ONNX_FP16.id, catalog })).toBe(ONNX_FP16.id)
  })

  it('AC-117.13 returns null when no row is available', () => {
    const onnxAbsent = { id: 'kokoro-onnx-fp32', is_downloaded: false, available: false }
    expect(defaultModelSelection({ chosen: null, loadedVariantId: null, catalog: [PYTORCH, onnxAbsent] })).toBeNull()
    expect(
      defaultModelSelection({ chosen: PYTORCH.id, loadedVariantId: null, catalog: [PYTORCH, onnxAbsent] }),
    ).toBeNull()
  })

  it('AC-117.13 a row without available counts as available', () => {
    const legacy = { id: 'kokoro-onnx-fp32', is_downloaded: false }
    expect(defaultModelSelection({ chosen: legacy.id, loadedVariantId: null, catalog: [legacy] })).toBe(legacy.id)
    expect(defaultModelSelection({ chosen: null, loadedVariantId: null, catalog: [PYTORCH, legacy] })).toBe(legacy.id)
  })
})
