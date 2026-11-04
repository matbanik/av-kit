import { describe, expect, it } from 'vitest'

import { resolveRunBarSlot } from '../../src/renderer/src/features/tts/tts-run-bar'

describe('MEU-63 RUN_BAR_ERROR', () => {
  it('AC-63.4 a Failed job with an error_message selects the error slot', () => {
    expect(resolveRunBarSlot({ error: null, status: 'Failed', jobError: 'tts asset missing: tts_onnx_vocab' })).toBe(
      'error',
    )
  })

  it('AC-63.4 an empty or absent job error on a Failed job keeps the output slot', () => {
    expect(resolveRunBarSlot({ error: null, status: 'Failed', jobError: '' })).toBe('output')
    expect(resolveRunBarSlot({ error: null, status: 'Failed', jobError: null })).toBe('output')
    expect(resolveRunBarSlot({ error: null, status: 'Failed' })).toBe('output')
  })

  it('AC-63.4 a stale error_message on a non-Failed job is ignored', () => {
    expect(resolveRunBarSlot({ error: null, status: 'Done', jobError: 'stale' })).toBe('output')
    expect(resolveRunBarSlot({ error: null, status: 'Generating', jobError: 'stale' })).toBe('progress')
  })

  it('AC-63.4 a client error wins over the job error', () => {
    expect(resolveRunBarSlot({ error: 'client', status: 'Failed', jobError: 'job' })).toBe('error')
  })
})
