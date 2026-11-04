import type { CaptureViewVariant } from './CaptureViewport'

/** The two paths VIEWED_FILE chooses between (a CaptureListItem satisfies this). */
export type ViewedFileShot = { original_path: string; annotated_path: string | null }

/**
 * VIEWED_FILE (MEU-84, D-16): the file the viewport shows. The Annotated view names the
 * annotated copy while one exists; otherwise the original. No shot gives null.
 */
export function viewedFilePath(variant: CaptureViewVariant, shot: ViewedFileShot | null | undefined): string | null {
  if (shot == null) {
    return null
  }
  if (variant === 'annotated' && typeof shot.annotated_path === 'string' && shot.annotated_path.length > 0) {
    return shot.annotated_path
  }
  return shot.original_path
}
