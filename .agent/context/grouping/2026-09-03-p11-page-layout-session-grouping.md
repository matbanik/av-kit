# Phase 11 — Page Layout · Session Grouping

> **Source:** the six 2026-09-03 page-layout mockups in `docs/proposals/`
> (`downloader`, `convert`, `transcript`, `tts`, `capture`, `settings`).
> **Date:** 2026-09-03
> **Origin:** mockup review + MEU registration. Registers Phase 11 and MEU-50–MEU-58.
> **Band:** P2. **Spec home:** `docs/build-plan/11-page-layout.md` (authored by MEU-50).

Phase 10 replaced the queue **rows**. Phase 11 replaces the page **composition around**
them: every one of the six mockups is explicitly scoped "composition only — same IPC, same
mutations, same enablement rules, every test id kept as keep / move / change". No API
change, no new backend capability, no new runtime dependency (dnd-kit lands in MEU-49,
before this phase opens).

**Capture is in scope here even though Phase 10 excluded it.** Phase 10's exclusion was
correct and narrow: `CaptureInbox` is a thumbnail filmstrip, not a work queue, so it gets no
`QueueCard`. The Capture mockup does not make it a queue — it separates three concerns
(global / per-shot / settings) into three rows. That is layout, which is what Phase 11 is.

---

## Mockup → MEU map

| Mockup | Lands in | Notes |
|---|---|---|
| `downloader-page-layout` Zone 2 (queue header row) | **MEU-52** | Page-agnostic; also serves Convert and Transcript |
| `downloader-page-layout` Zone 1 (add panel) | **MEU-53** | Downloader-specific |
| `convert-page-layout` Zone 1 (add panel) | **MEU-54** | Zone 2 is MEU-52, inherited unchanged |
| `transcript-page-layout` | **MEU-55** | Absorbs closed MEU-48's transcript half |
| `tts-page-layout` | **MEU-56** | Absorbs closed MEU-48's TTS half |
| `capture-page-layout` | **MEU-57** | New — Phase 10 had no Capture row |
| `settings-page-layout` | **MEU-58** | New — Phase 10 had no Settings row |
| All six: shared vocabulary (column cap, zones, form grid, disclosure, segment, chips, save-model captions) | **MEU-50** (spec) + **MEU-51** (components) | The anti-duplication spine |
| All six §06 "Decisions to lock" (~40 open product questions) | **MEU-50** | Resolved once, in one place, before any page MEU plans |

---

## MEU-48 is closed, not cancelled

MEU-48 (`gui-queue-convergence`) was scoped on 2026-08-28 as *"Transcript `ChannelCard` onto
the shared primitives (fixes the G33 `width: %` violation); TTS gets the shared
`ProgressBar`"*. Both deliverables are **strict subsets** of MEU-55 and MEU-56.

Executing MEU-48 as written in session 22 would open `TranscriptPage.tsx` and `TTSPage.tsx`,
restructure `ChannelCard`, write a FIC, write tests, run a review round — and then MEU-55/56
would reopen the same two files and rewrite the same components against a different card
anatomy, invalidating those tests. That is a full duplicate plan → implement → review cycle
on the same surface.

So MEU-48 is `closed` with `closed_reason` recording the supersession, and its two ACs are
**inherited as mandatory ACs** by MEU-55 and MEU-56:

| Inherited AC | Now owned by | Must not be dropped because |
|---|---|---|
| Transcript `ChannelCard` renders through the shared queue primitives; no `width: %` inline style (G33) | MEU-55 | It is a standards violation fix, not a cosmetic preference |
| TTS uses the shared `ProgressBar` rather than a local bar | MEU-56 | It is the last un-deduplicated progress bar in `ui/` |

MEU-50's spec doc must carry both forward in the Phase 11 §Supersession section so a future
reader of `10-queue-card-ui.md` can trace where the convergence went.

---

## Sessions (proposed)

| # | Slug | Status | Plan folder | MEUs |
|---|---|---|---|---|
| 22 | `p10-queue-card-dnd` | approved | `docs/execution/plans/2026-09-03-p10-queue-card-dnd/` | MEU-49. Phase 10 **exit** session — drag reorder into `QueueList` + ARIA announcements. Phase 10 gate and independent review approved. |
| 23 | `p11-layout-canon` | approved | `docs/execution/plans/2026-09-26-p11-layout-canon/` | MEU-50, MEU-51. Spec + decision locks + unwired shared primitives. Test-only Electron primitive E2E; full existing wave green after five human-approved test-seam/setup repairs. GPT-6 Astra/high execution review approved in Round 2. |
| 24 | `p11-queue-pages` | approved | `docs/execution/plans/2026-09-26-p11-queue-pages/` | MEU-52, MEU-53, MEU-54. Shared queue header and both add panels; final 597 Vitest and 95 Electron tests pass. User-authorized GPT-6 Astra/high execution review approved in Round 3. |
| 25 | `p11-transcript-tts` | approved | `docs/execution/plans/2026-09-28-p11-transcript-tts/` | MEU-55, MEU-56. The two pages that inherit the closed MEU-48 ACs. Plan approved in Round 3 and execution in Round 2 by the user-authorized Fable 5.1 reviewer; the authoritative Windows gate passes 631 Vitest and 103 Electron tests. |
| 26 | `p11-capture-settings` | approved | `docs/execution/plans/2026-09-28-p11-capture-settings/` | MEU-57, MEU-58. The two non-queue pages. Phase 11 **exit**. The plan was approved in Round 2 and the execution in Round 2 by the user-authorized Fable 5.1 reviewer. The authoritative Windows gate (attempt 7, `cb864f3`) passes 675 Vitest and 110 Electron tests after six environment or legacy-test-race failures, each fixed under explicit approval (A11–A17). |

---

## MEUs

| MEU | Slug | Slice | Layer | Depends on |
|---|---|---|---|---|
| MEU-50 | `canon-page-layout` | Phase 11 spec doc; every mockup §06 decision locked; column-cap token; zone / form-grid / disclosure / segment / chip / save-caption vocabulary; supersession pointers into 06, 08, 09, 10 | docs + ui/styles | MEU-49 |
| MEU-51 | `gui-layout-primitives` | `Disclosure`, `SegmentedControl`, `StatusChip`, `FormRow`, `PathRow` + testid registration | ui | MEU-50 |
| MEU-52 | `gui-queue-header-row` | `QueueHeaderRow` = select-all + non-zero status chips + live processor chip + `QueueToolbar` in one row; mounted on Downloader **and** Convert | ui | MEU-51 |
| MEU-53 | `gui-downloader-layout` | Zone 1 add panel: URL+Add row, content-width options row, `Advanced` disclosure holding Cookies segment and the three SABR controls, SABR chip beside Quality, one panel status line | ui | MEU-52 |
| MEU-54 | `gui-convert-layout` | Zone 1 add panel: task segment + encoder chip + Refresh, drop strip + `Add n`, removable staged chips, one task-options row, Advanced override disclosure, output footer | ui | MEU-53 |
| MEU-55 | `gui-transcript-layout` | Add row; channel cards on the `QueueCard` anatomy; 13-button footer → three-action header toolbar + per-card ▲ ▼ + ⋮ menu; single-select preserved | ui | MEU-52, MEU-49 |
| MEU-56 | `gui-tts-layout` | Two-column text/voice grid; Cleanup and Manage-models disclosures; one-line voice list; speed slider + preset segment; one run bar | ui | MEU-51 |
| MEU-57 | `gui-capture-layout` | Header row with hotkey key cap + Settings disclosure; 200 px thumbnail filmstrip; per-shot viewport toolbar with tool segment; inline confirm strips | ui | MEU-51 |
| MEU-58 | `gui-settings-layout` | Sticky section rail (Pages / App / Setup); 168 px label-control grid; path+Browse rows; per-section save-model captions; diagnostics as chip lists | ui | MEU-51 |

---

## Dependency graph

```
MEU-47 gui-queue-bulk (approved, session 21)
   |
   v
MEU-49 gui-queue-dnd ............................. session 22  [Phase 10 exit]
   |
   v
MEU-50 canon-page-layout ......................... session 23
   |
   v
MEU-51 gui-layout-primitives
   |
   +-----------------+-----------------+-----------------+
   v                 v                 v                 v
MEU-52            MEU-56            MEU-57            MEU-58
gui-queue-        gui-tts-          gui-capture-      gui-settings-
header-row        layout            layout            layout
   |                 |                 |                 |
   |              session 25        session 26       session 26
   v
MEU-53 gui-downloader-layout ..................... session 24
   |
   v
MEU-54 gui-convert-layout
   |
   v
MEU-55 gui-transcript-layout ..................... session 25
       (also depends on MEU-49 for card reorder)
```

**Critical path:** MEU-49 → MEU-50 → MEU-51 → MEU-52 → MEU-53 → MEU-54 → MEU-55.
MEU-56/57/58 hang off MEU-51 and are only sequenced late because they share a session with
work that needs the header row; they are not on the critical path.

---

## Why grouped this way

### Session 22 — `p10-queue-card-dnd` (MEU-49) · Phase 10 exit

MEU-49 runs **before** Phase 11 rather than after, and that ordering is the single largest
token saving in this plan. Drag reorder lands inside `QueueList`, which is a shared
component. MEU-55 then adopts `QueueList` for Transcript channel cards and **inherits
reorder for free** — including the ▲ ▼ keyboard path the Transcript mockup draws. Running
MEU-49 after Phase 11 would mean opening `QueueList` and all three consuming pages a second
time to retrofit drag handles.

It stays a session of its own because it introduces the phase's only new runtime dependency
(dnd-kit) and because a clean Phase 10 phase-gate run before Phase 11 opens is what makes
the Phase 11 baseline trustworthy.

### Session 23 — `p11-layout-canon` (MEU-50, MEU-51)

MEU-50 is docs and tokens; MEU-51 is presentational components with no product page mounts yet.
The slice validates with unit tests and a test-only Electron primitive harness E2E wave,
while the existing Playwright waves stay green. The harness is isolated from the ordinary
product build and package; page composition E2E belongs to MEU-52–58.

MEU-50 must come first and must come alone-ish, because the six mockups collectively leave
about forty open product decisions in their §06 sections (Advanced default state, chips vs.
the eight-count summary, staged-file removal, format `<select>` vs. segment, cookie segment
vs. native radios, save-model unification, per-checkbox explanatory copy, and so on).
Resolving those **once, in one document** is the difference between one decision pass and
six. Every downstream MEU then cites `Spec` against `11-page-layout.md` instead of
re-litigating from a mockup.

MEU-51 rides with it because `Disclosure`, `SegmentedControl`, `StatusChip` and the form-row
pair appear in **five of the six mockups**. Building them per-page would recreate exactly the
duplication Phase 10 existed to delete — the `formatFileSize` lesson, one abstraction layer
up. Shipping them with no consumer is acceptable for one session only because MEU-52 lands
the first consumer immediately after.

### Session 24 — `p11-queue-pages` (MEU-52, MEU-53, MEU-54)

The Downloader mockup states the constraint directly: the queue header row "is page-agnostic
and should land on both pages in the same MEU so the two queues do not diverge again."
MEU-52 therefore mounts on Downloader and Convert together — that is a correctness boundary,
not a convenience.

MEU-53 and MEU-54 then reopen those same two files for their Zone 1 add panels. Splitting
them into a later session would pay the file-comprehension cost twice; keeping all three MEUs
in one session means `DownloaderPage.tsx` and `ConvertPage.tsx` are read once and the panel
idiom is learned once. MEU-54 depends on MEU-53 rather than on MEU-52 directly so the second
add panel is built by reusing the first one's proven structure, not by inventing a parallel
one.

One Playwright wave covers both pages.

### Session 25 — `p11-transcript-tts` (MEU-55, MEU-56)

These are the two pages carrying inherited ACs from closed MEU-48, so they belong together —
a reviewer checks the supersession once. Both are single-page recompositions on primitives
that already exist by this point, with no shared surface between them, so neither can break
the other.

MEU-55 is the largest single MEU in the phase: thirteen footer buttons redistributed across a
three-action header toolbar, a per-card kebab menu and two reorder icon buttons, plus a card anatomy
change. It goes after MEU-52 because its header row *is* MEU-52's component with a
Transcript-shaped chip set.

### Session 26 — `p11-capture-settings` (MEU-57, MEU-58) · Phase 11 exit

The two pages with no queue at all. Both are pure `Disclosure` + form-grid consumers, which
makes them the natural validation of whether MEU-51's primitives were specified well enough
to serve a page that was never in the queue family. If they need primitive changes, that is
discovered here, at the end, where it costs one session rather than blocking the queue pages.

Settings is last on purpose: its rail links to every other page's settings section, so the
section names and save-model captions are only stable once the five page MEUs have landed.

---

## What this grouping deliberately does *not* do

- **No per-page "do the whole page" MEUs.** Tempting, and wrong: the queue header row and the
  layout primitives would each get invented two-to-five times.
- **No merging of MEU-50 into the first page MEU.** A spec written while implementing a page
  encodes that page's accidents as canon.
- **No Phase 10 reopening.** `QueueCard`, `QueueList`, `BulkActionBar`, the selection model,
  and the queue scroll-container height chain (`h-full min-h-0` on the page root,
  `flex-1 min-h-[20rem]` on the queue region, `overflow-auto` on a per-page wrapper around
  `QueueList` — never on `listClasses`, and the controls above the queue in a single
  `min-h-0 … overflow-auto` pane with a `shrink-0` summary/toolbar footer, so the controls
  and not the queue absorb the column's height deficit) are inputs to Phase 11, not subjects
  of it. That last clause is the one a page redesign is most likely to drop by accident: the
  column is oversubscribed at the default window, and a queue left free to shrink lands near
  90px, which silently removes keyboard reorder (AC-49.27) with no visible layout breakage.
  If a mockup appears to require a card-anatomy change (Convert's task-meta second line,
  Transcript's channel second line), it is expressed as a `QueueCard` *slot*, not a rewrite.
- **No stealing hub Next.** MEU-61 (`gui-login-item`, 2026-09-20 residual) lands a Settings Startup card and NSIS uninstall cleanup. It does **not** replace MEU-50. Do not fold the login-item control into MEU-58’s first layout pass as an unstated extra — MEU-58 must **keep** `start-at-sign-in-panel` (mockup §05 keep row) once MEU-61 has shipped.
- **No backend work.** Phase 11 has none. If a plan discovers it needs an API change, that is
  a signal the mockup was misread — escalate rather than widen.

---

## Order of `/create-plan`

1. `p10-queue-card-dnd` — MEU-49 (Phase 10 exit + phase gate)
2. `2026-XX-XX-p11-layout-canon` — MEU-50, MEU-51
3. `p11-queue-pages` — MEU-52, MEU-53, MEU-54
4. `p11-transcript-tts` — MEU-55, MEU-56
5. `p11-capture-settings` — MEU-57, MEU-58 (Phase 11 exit + phase gate)
