/**
 * MEU-117 AC-117.13: `defaultModelSelection` never picks a variant this build can't run.
 * Each rule (the chosen row, the first downloaded, the first row) skips a row with
 * `available: false`; the loaded row is kept, as a load of an unavailable variant is refused.
 */
import { readFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

import * as controls from '../../src/renderer/src/features/tts/tts-controls'
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

// MEU-121 `svc-tts-fp16-nonfinite` (Session 52, D-239, D-329, D-330): a fresh install
// preselects ONNX INT8, then FP32; FP16 stays offered.
const REPO_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../../..')

/** The seeded variants a new install gets, read from `engine.py` (D-329). */
function seededVariants(): Array<{ id: string; format: string }> {
  const engine = readFileSync(
    join(REPO_ROOT, 'packages/infrastructure/src/avkit_infra/database/engine.py'),
    'utf8',
  )
  const block = /SEED_VARIANTS[^=]*= \(([\s\S]*?)\n\)/.exec(engine)?.[1] ?? ''
  return [...block.matchAll(/\("([^"]+)", "[^"]+", "([^"]+)", "[^"]+", /g)].map((m) => ({
    id: m[1] as string,
    format: m[2] as string,
  }))
}

/**
 * The catalog on a CPU build, sorted by id as `list_catalog` returns it: PyTorch is
 * unavailable, `downloaded` rows are downloaded, and `unavailable` rows are served unavailable.
 */
function cpuCatalog(
  downloaded: string[] = [],
  unavailable: string[] = [],
): Array<{ id: string; is_downloaded: boolean; available: boolean }> {
  return seededVariants()
    .map((row) => ({
      id: row.id,
      is_downloaded: downloaded.includes(row.id),
      available: row.format !== 'PyTorch' && !unavailable.includes(row.id),
    }))
    .sort((a, b) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0))
}

function fresh(catalog: ReturnType<typeof cpuCatalog>): string | null {
  return defaultModelSelection({ chosen: null, loadedVariantId: null, catalog })
}

describe('MEU-121 a fresh install preselects ONNX INT8', () => {
  it('AC-121.1 the fresh seeded catalog preselects kokoro-onnx-int8', () => {
    const catalog = cpuCatalog()
    expect(catalog.length).toBeGreaterThan(0)
    expect(fresh(catalog)).toBe('kokoro-onnx-int8')
  })

  it('AC-121.2 PRESELECT_ORDER is INT8 then FP32, both seeded', () => {
    expect(controls).toHaveProperty('PRESELECT_ORDER')
    const seeded = seededVariants().map((row) => row.id)
    expect(controls.PRESELECT_ORDER).toEqual(['kokoro-onnx-int8', 'kokoro-onnx-fp32'])
    expect(controls.PRESELECT_ORDER.filter((id) => !seeded.includes(id))).toEqual([])
  })

  it('AC-121.3 with several rows downloaded the order decides', () => {
    const onnx = ['kokoro-onnx-fp16', 'kokoro-onnx-fp32', 'kokoro-onnx-int8']
    expect([
      fresh(cpuCatalog(['kokoro-onnx-fp16', 'kokoro-onnx-fp32'])),
      fresh(cpuCatalog(onnx)),
      fresh(cpuCatalog(['kokoro-onnx-fp16'])),
    ]).toEqual(['kokoro-onnx-fp32', 'kokoro-onnx-int8', 'kokoro-onnx-fp16'])
  })

  it('AC-121.4 INT8 served unavailable with nothing downloaded preselects FP32', () => {
    expect(fresh(cpuCatalog([], ['kokoro-onnx-int8']))).toBe('kokoro-onnx-fp32')
  })
})
