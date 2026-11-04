/**
 * Settings section frame classes (MEU-70 SECTION_EMPHASIS, Session 31 plan D-14 / D-20). Stated
 * once here and spread by every section producer: SettingsSectionFrame and StartAtSignInControl.
 *
 * Every frame always carries the same padding and a 2 px left border, so making a section current
 * changes only colours and never moves content. `-mx-3` is cancelled by the border plus `pl-2.5`
 * on the left and by `pr-3` on the right. There is deliberately no negative vertical margin: the
 * column's 24 px gap must stay larger than the 16 px scroll margin, or the previous section would
 * stay inside the rail's top band (BOX_SEPARATION).
 */
export const SECTION_FRAME_BASE = [
  'flex scroll-mt-4 flex-col gap-3 outline-none',
  '-mx-3 pl-2.5 pr-3 py-2 rounded-[var(--radius-control)] border-l-2',
  'transition-[background-color,border-color] duration-[var(--duration-fast)] ease-[var(--ease-out)]',
].join(' ')

const CURRENT_CLASSES = 'bg-bg-elevated/40 border-accent'
const IDLE_CLASSES = 'border-transparent'

export type SectionFrameProps = {
  className: string
  'data-current'?: 'true'
}

/** Class list and current marker for a settings section frame. Never sets aria-current (AC-58.12). */
export function sectionFrameProps(current: boolean): SectionFrameProps {
  return current
    ? { className: `${SECTION_FRAME_BASE} ${CURRENT_CLASSES}`, 'data-current': 'true' }
    : { className: `${SECTION_FRAME_BASE} ${IDLE_CLASSES}` }
}
