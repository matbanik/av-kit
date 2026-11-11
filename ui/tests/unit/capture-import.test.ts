// @vitest-environment jsdom
/** MEU-132 image import helpers: AC-132.1 to AC-132.5 (plan 2026-11-10-gui-capture-image-import, D-551 to D-558). */
import { describe, expect, it } from 'vitest'

import {
  IMPORT_EXTENSIONS,
  IMPORT_FAILED_REASON,
  importDisplayName,
  importFiles,
  isEditableTarget,
  isImportableName,
  NOT_AN_IMAGE_REASON,
  NOT_ON_DISK_REASON,
  type ImportEntry,
} from '../../src/renderer/src/features/capture/capture-import'
import { ApiError } from '../../src/renderer/src/lib/api'

type Call = { kind: 'import'; path: string } | { kind: 'refetch' }

/** A port that records each call and answers from `answer`, one call at a time. */
function recordingPort(answer: (path: string) => Promise<unknown> = async () => ({ item: {} })): {
  calls: Call[]
  inFlight: { max: number }
  port: { importOne: (path: string) => Promise<unknown>; refetch: () => Promise<void> }
} {
  const calls: Call[] = []
  const inFlight = { max: 0 }
  let running = 0
  return {
    calls,
    inFlight,
    port: {
      importOne: async (path) => {
        calls.push({ kind: 'import', path })
        running += 1
        inFlight.max = Math.max(inFlight.max, running)
        try {
          await new Promise((r) => setTimeout(r, 1))
          return await answer(path)
        } finally {
          running -= 1
        }
      },
      refetch: async () => {
        calls.push({ kind: 'refetch' })
      },
    },
  }
}

const entry = (path: string): ImportEntry => ({ path, name: path.split(/[\\/]/).pop() ?? path })

describe('MEU-132 IMPORT_TYPES (AC-132.1)', () => {
  it('AC-132.1 the four extensions in order', () => {
    expect([...IMPORT_EXTENSIONS]).toEqual(['png', 'jpg', 'jpeg', 'webp'])
  })

  it('AC-132.1 accepts the four image suffixes in any case and refuses the rest', () => {
    for (const name of ['a.png', 'A.PNG', 'b.Jpeg', 'c.webp', 'd.e.jpg']) {
      expect(isImportableName(name), name).toBe(true)
    }
    for (const name of ['notes.txt', 'a.png.txt', '.png', 'png', 'a.', 'a.gif']) {
      expect(isImportableName(name), name).toBe(false)
    }
  })
})

describe('MEU-132 IMPORT_NAME (AC-132.2)', () => {
  it('AC-132.2 keeps the basename after either separator', () => {
    expect(importDisplayName('C:\\x\\y\\shot.png')).toBe('shot.png')
    expect(importDisplayName('/x/shot.png')).toBe('shot.png')
    expect(importDisplayName('plain.png')).toBe('plain.png')
  })

  it('AC-132.2 replaces a control character and a lone surrogate with U+FFFD and nothing else', () => {
    expect(importDisplayName('be\u0007ll.png')).toBe('be\uFFFDll.png')
    expect(importDisplayName('half\uD800.png')).toBe('half\uFFFD.png')
    expect(importDisplayName('del\u007F.png')).toBe('del\uFFFD.png')
    expect(importDisplayName('pair\uD83D\uDE00.png')).toBe('pair\uD83D\uDE00.png')
  })

  it('AC-132.2 an empty name and a trailing separator read (unnamed file)', () => {
    expect(importDisplayName('')).toBe('(unnamed file)')
    expect(importDisplayName('C:\\x\\')).toBe('(unnamed file)')
  })
})

describe('MEU-132 IMPORT_RUN fan-out (AC-132.3)', () => {
  it('AC-132.3 imports the images one by one in order, skips the text file, then refetches once', async () => {
    const { calls, inFlight, port } = recordingPort()
    const result = await importFiles([entry('C:\\in\\a.png'), entry('C:\\in\\notes.txt'), entry('C:\\in\\b.jpg')], port)
    expect(calls).toEqual([
      { kind: 'import', path: 'C:\\in\\a.png' },
      { kind: 'import', path: 'C:\\in\\b.jpg' },
      { kind: 'refetch' },
    ])
    expect(inFlight.max).toBe(1)
    expect(result.message).toBe(
      'Imported 2 of 3. 1 failed: notes.txt - not an image av-kit can open (png, jpg, jpeg, webp)',
    )
    expect(result.attempted).toEqual(['a.png', 'notes.txt', 'b.jpg'])
    expect(result.succeeded).toEqual(['a.png', 'b.jpg'])
    expect(result.failed).toEqual([{ id: 'notes.txt', reason: NOT_AN_IMAGE_REASON }])
  })

  it('AC-132.3 two images give Imported 2 of 2.', async () => {
    const { calls, port } = recordingPort()
    const result = await importFiles([entry('/in/a.png'), entry('/in/b.webp')], port)
    expect(result.message).toBe('Imported 2 of 2.')
    expect(calls.filter((c) => c.kind === 'refetch')).toHaveLength(1)
  })
})

describe('MEU-132 IMPORT_RUN errors (AC-132.4)', () => {
  it('AC-132.4 the import route refusal shows its own text', async () => {
    const { port } = recordingPort(async () => {
      throw new ApiError(422, 'InboxPathError', 'no file at that path', null)
    })
    const result = await importFiles([entry('C:\\in\\gone.png')], port)
    expect(result.failed).toEqual([{ id: 'gone.png', reason: 'no file at that path' }])
    expect(result.message).toBe('Imported 0 of 1. 1 failed: gone.png - no file at that path')
  })

  it('AC-132.4 every other error reads the fixed reason and names no path', async () => {
    const errors: unknown[] = [
      new ApiError(503, 'FETCH_FAILED', 'EACCES C:\\secret\\a.png', null),
      new ApiError(503, 'BACKEND_NOT_READY', 'Backend not ready \u2014 C:\\secret\\a.png', null),
      new ApiError(422, 'HTTP_ERROR', 'C:\\secret\\a.png', null),
      new ApiError(422, 'validation_error', 'Request validation failed', null),
      new ApiError(500, 'internal_error', 'Internal server error (request id r1)', null),
      new Error('EACCES C:\\secret\\a.png'),
    ]
    for (const error of errors) {
      const { calls, port } = recordingPort(async () => {
        throw error
      })
      const result = await importFiles([entry('C:\\secret\\a.png')], port)
      const label = error instanceof ApiError ? error.code : 'Error'
      expect(calls[0], label).toEqual({ kind: 'import', path: 'C:\\secret\\a.png' })
      expect(result.failed, label).toEqual([{ id: 'a.png', reason: IMPORT_FAILED_REASON }])
      expect(result.message, label).not.toContain('C:\\')
      expect(result.message, label).toBe('Imported 0 of 1. 1 failed: a.png - the import could not be completed')
    }
  })

  it('AC-132.4 an empty path fails not a file on disk with no call', async () => {
    const { calls, port } = recordingPort()
    const result = await importFiles([{ path: '', name: 'clip.png' }, entry('C:\\in\\ok.png')], port)
    expect(calls).toEqual([{ kind: 'import', path: 'C:\\in\\ok.png' }, { kind: 'refetch' }])
    expect(result.failed).toEqual([{ id: 'clip.png', reason: NOT_ON_DISK_REASON }])
    expect(result.message).toBe('Imported 1 of 2. 1 failed: clip.png - not a file on disk')
  })

  it('AC-132.4 only non-images make no call and no refetch, and no message holds a path', async () => {
    const { calls, port } = recordingPort()
    const result = await importFiles([entry('C:\\secret\\a.txt'), entry('C:\\secret\\b.gif')], port)
    expect(result.attempted).toEqual(['a.txt', 'b.gif'])
    expect(calls).toEqual([])
    expect(result.message).toBe(
      'Imported 0 of 2. 2 failed: a.txt - not an image av-kit can open (png, jpg, jpeg, webp); b.gif - not an image av-kit can open (png, jpg, jpeg, webp)',
    )
    expect(result.message).not.toContain('C:\\')
  })
})

describe('MEU-132 PASTE_KEY editable targets (AC-132.5)', () => {
  it('AC-132.5 text fields and contenteditable keep their native paste', () => {
    const textarea = document.createElement('textarea')
    const div = document.createElement('div')
    div.contentEditable = 'true'
    document.body.append(div)
    const editable: EventTarget[] = [textarea, div]
    for (const type of ['text', 'search', 'number', 'url', 'tel', 'email', 'password']) {
      const input = document.createElement('input')
      input.type = type
      editable.push(input)
    }
    const bare = document.createElement('input')
    bare.removeAttribute('type')
    editable.push(bare)
    for (const target of editable) {
      const label = target instanceof HTMLInputElement ? `input ${target.type}` : (target as Element).tagName
      expect(isEditableTarget(target), label).toBe(true)
    }
    div.remove()
  })

  it('AC-132.5 a button, a checkbox, the body, null and window are not editable', () => {
    const checkbox = document.createElement('input')
    checkbox.type = 'checkbox'
    const others: (EventTarget | null)[] = [document.createElement('button'), checkbox, document.body, null, window]
    for (const target of others) {
      expect(isEditableTarget(target), String(target)).toBe(false)
    }
  })
})
