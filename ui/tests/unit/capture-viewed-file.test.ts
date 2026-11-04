import { describe, expect, it } from 'vitest'

import { viewedFilePath } from '../../src/renderer/src/features/capture/capture-viewed-file'

const SHOT = { original_path: 'C:/shots/a.png', annotated_path: 'C:/shots/a.annotated.png' as string | null }

describe('MEU-84 VIEWED_FILE (AC-84.3)', () => {
  it('AC-84.3 the Annotated view names the annotated copy and the Original view names the original', () => {
    expect(viewedFilePath('annotated', SHOT)).toBe('C:/shots/a.annotated.png')
    expect(viewedFilePath('original', SHOT)).toBe('C:/shots/a.png')
  })

  it('AC-84.3 negative: a null or empty annotated path falls back to the original, and no shot is null', () => {
    expect(viewedFilePath('annotated', { ...SHOT, annotated_path: null })).toBe('C:/shots/a.png')
    expect(viewedFilePath('annotated', { ...SHOT, annotated_path: '' })).toBe('C:/shots/a.png')
    expect(viewedFilePath('annotated', null)).toBeNull()
    expect(viewedFilePath('original', null)).toBeNull()
  })
})
