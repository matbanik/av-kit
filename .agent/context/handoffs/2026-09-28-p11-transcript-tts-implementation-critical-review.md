---
date: "2026-09-28"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-09-28-p11-transcript-tts/implementation-plan.md"
round: 2
verdict: "approved"
findings_count: 3
template_version: "2.2"
requested_verbosity: "detailed"
agent: "claude-fable-5-1-subagent"
loop_id: "p11tt-execution-review-2026-09-28"
---

# Critical Review: 2026-09-28-p11-transcript-tts (Round 1)

> **Review Mode**: `execution`
> **Verdict**: `changes_required`

---

## Review binding

- **Intent anchor**: The plan's goal is to *"Deliver Session 25 of `.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md` as grouped"* — MEU-55 `gui-transcript-layout` (Add row and status line; channel rows on the shared `QueueCard` anatomy through `QueueList`; the 13-button footer replaced by a three-action header toolbar, per-card ▲ ▼ and a per-card ⋮ menu; single-select preserved) and MEU-56 `gui-tts-layout` (Text/Voice two-column grid, Cleanup and Manage disclosures, one-line voice list, speed slider with a preset segment, one static run bar), both carrying the closed MEU-48 ACs, everything inside `COMPOSITION_LOCK`. The verdict below answers whether the delivered code achieves that.
- **Intent achieved**: `partial` — both pages are composed as specified, every payload, mutation, enablement rule and test ID is preserved, and the Windows gate is authoritative and clean; one bound Session-24 rule (RULE-1/RULE-3 focus restoration on AC-55.5) is implemented for the success path only and demonstrably leaves keyboard focus on `BODY` after a rejected reorder.
- **Reviewed state**: HEAD `d9ff880` (branch `claude/amazing-albattani-qcl51p`), clean tree; code-identical under `ui/`, `packages/`, `mcp-server/` to the Windows-gated commit `7dab4d1` (`git diff 7dab4d1 HEAD --stat -- ui packages mcp-server` is empty). Baseline `0f51036`; `git diff 0f51036 1ed5c7b --stat -- ui/` is empty, so the fixture-capture commit is code-identical to the baseline.
- **Reviewer**: independent Claude Code `Agent` subagent, Fable 5.1, high effort, per `human-review-decision.md` (`USER_EXPLICIT`, same-vendor exception recorded there). The reviewer did not author any of the work and wrote this file directly; no product, test, plan or work-handoff file was modified. Scratch probes ran only under the session scratchpad.
- **Verdict-rule conflict surfaced**: the workflow's Verdict Rule says `changes_required` needs a `High`/`Critical`; the dispatch prompt for this round says "Approve only if no High or Medium finding remains", and `REVIEW-TEMPLATE.md` allows a `Medium` finding to be `Blocking: yes`. Finding 1 is a demonstrated runtime defect inside AC-55.5's contract with a reproducer, so the stricter dispatch instruction is applied and the conflict is recorded here rather than silently resolved. If the orchestrator/user rules that a Medium cannot block this loop, the same file state would be `approved` with Finding 1 open as `Blocking: no`.

---

## Scope

**Target**: MEU-55 and MEU-56 work handoffs (`.agent/context/handoffs/2026-09-28-p11-transcript-tts-MEU-55-handoff.md`, `-MEU-56-handoff.md`); `implementation-plan.md`, `task.md`, `walkthrough.md`, `human-gate-decision.md`, `human-review-decision.md`, `validate-task.sh`/`.ps1`, `windows-gate-result.json`; the full `git diff 0f51036 HEAD -- ui/` (22 files, +2911/−719); SSOT (`meu-status.yaml`, `meu-registry.md`, `current-focus.md`, Phase 11 grouping, `docs/BUILD_PLAN.md`).
**Review Type**: execution review (multi-MEU project; both handoffs loaded — the seed was MEU-56, expanded per the Project-Integrated Handoff rule).
**Checklist Applied**: IR-1..IR-7 (with IR-5 per-test grading), DR-1..DR-8.

---

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| 1 | Medium | yes | behavior | **Rejected reorder leaves keyboard focus on `BODY` (violates AC-55.5; RULE-1/RULE-3 lineage).** The ▲ ▼ focus-restoration effect explicitly returns without restoring focus when the order did not change (`if (items.findIndex(...) === pending.from) return`). That branch is exactly the rejection path: while the PUT is in flight the clicked button is `disabled` (a real browser drops focus to `body`, which is the RULE-3 precondition the plan bound to this AC), and when the server rejects (`409`/network error) `busy` releases, the button re-enables, but nothing re-focuses it. Reproduced with a scratch probe against the unchanged page: hold `PUT /transcripts/reorder`, click Bravo's `up-btn`, blur to `body`, release a `409` → `error-banner` shows "reorder rejected", order stays `a,b,c,d,e`, `document.activeElement === BODY`. The Session 24 shared fallback this rule descends from (`QueueList.tsx:318-330`) restores focus after the gate releases regardless of whether the order changed ("covering success and rejection", peer review R1/R2-1); the transcript page re-implements it with the success-only guard, and `transcript-page.behavior.test.ts:408-436` proves only the success path. | `ui/src/renderer/src/features/transcript/TranscriptPage.tsx:213-231` (guard at `:219-221`); test gap `ui/tests/unit/transcript-page.behavior.test.ts:408-436` | Drop the order-unchanged early return: once `busy` releases, always re-find the card by `data-job-id` inside `scrollerRef` and focus the same-direction button when enabled, else the other (the existing `target` selection already does this). Add a rejection regression next to the success case: hold the PUT, blur to `body`, release a `409`, assert `document.activeElement` is Bravo's `up-btn` and the order is unchanged. Optionally add the equivalent real-Electron case to AC-55.7 (hold, blur, reject). Because this touches `ui/`, rerun `green-55`, `static`, `amendments`, `pregate`, and `WINDOWS_GATE` before Round 2 (task H1-7 rule). | fixed (Round 2: `9fb0153`, verified in Recheck 2026-09-28) |
| 2 | Low | no | clerical | W2-5's `test.setTimeout(120_000)` → `180_000` is labelled part of TA-5, but the plan's TA-5 declaration (`implementation-plan.md` `TEST_AMENDMENTS`) lists interaction-path edits only; a timeout budget is neither an assertion nor a weakening, and the handoff discloses it with its timing evidence (55 clicks at ~2.0 s), so this is a labelling gap, not a discipline breach. | `ui/tests/e2e/transcript-queue.test.ts:298-300`; `…-MEU-55-handoff.md:108-110,170` | Record the budget raise as an execution amendment in `walkthrough.md` §Execution amendments (one line), so the "only TA-1..TA-7" claim is literally true. No code change. | fixed (Round 2: `walkthrough.md:133`, verified in Recheck 2026-09-28) |
| 3 | Low | no | behavior | **(Round 2, new) ▲ ▼ focus restore is unconditional.** `target?.focus()` runs without checking where focus is; `channel-input`/`add-btn` stay enabled while `busy` (pre-existing, `COMPOSITION_LOCK`), so focus the user moved into the Channel URL field during the reorder round-trip is pulled back to the card button (PROBE-R2-1 success → `up-btn` on c, typed value intact; PROBE-R2-2 500 → `down-btn` on c). Not an AC requirement; matches the approved Session 24 `QueueList.tsx:318-330` fallback, which is also unconditional; pre-dated `9fb0153` on the success path. See Recheck (2026-09-28) §Remaining Findings. | `ui/src/renderer/src/features/transcript/TranscriptPage.tsx:231`; `:443-453` | Skip `focus()` when `document.activeElement` is neither `document.body` nor inside the card; if adopted, apply the same guard to `QueueList.tsx:318-330` (IR-4). Outside this loop. | open (non-blocking; follow-up outside this loop) |

> `Blocking` is not `Severity`. Finding 1 is `Blocking: yes` under the dispatch instruction (see Review binding). Finding 2 never blocks.

### Out-of-Contract Observations (non-blocking, ≤ 5)

1. Under the Transcript seam every Playwright click settles in ~2.0 s (handoff §W2-5 duration). It is not the queue poll (`transcriptPollInterval` is 1 s Processing / 5 s otherwise) and predates this change (W2-6), but it is unexplained; worth a root-cause follow-up outside this loop.
2. The Voice `<section aria-labelledby>` and the `voice-grid` listbox are both named "Voice"; a screen reader announces the name twice. Cosmetic.
3. At idle with a configured output *directory*, `OUTPUT_ACTIONABLE` mounts `open-output-btn` whose `openPath` target is that directory — the pre-existing predicate and target, preserved by `COMPOSITION_LOCK`; noted, not a finding.
4. While `busy`, the transcript kebab opens with every item `disabled`; in a real browser `first?.focus()` on a disabled `menuitem` is a no-op, so focus stays on the trigger and the document-level Escape listener closes the menu (probe PROBE-2). Consistent with the absent-vs-disabled rule.

---

## Verification record

### AC coverage (AC-55.1–55.7, AC-56.1–56.6)

| AC | Production entrypoint verified | Test that would fail on regression | Result |
|---|---|---|---|
| AC-55.1 | `QueueCard.tsx:173-201,402-407,412,545,562-591,614-630`; `QueueCardMenu.tsx:98-112,269-283,315-327,458`; `QueueList.tsx:58,117-122,174,209`; `ProgressBar.tsx:21-22,49-62,75,90`; `status-tokens.ts:146-159` | `queue-card-slots.test.tsx:41,50,73,106,131` — byte-for-byte fixture across three slot-less cards; sibling-not-nested; ordered `data-testid`s + `onMenuOpen`; per-row resolver; tone swaps only the fill class and keeps `scaleX` | pass |
| AC-55.2 | `QueueHeaderRow.tsx:31-40,50-104,107-137` | `queue-card-slots.test.tsx:153,161,201`; `queue-header-row.test.tsx` unmodified (`git diff 0f51036 HEAD --name-only -- ui/tests` does not list it) | pass |
| AC-55.3 | `TranscriptPage.tsx:158-171,478-507`; `TranscriptToolbar.tsx:47-69` | `transcript-page.behavior.test.ts:207,229,242` (exact toolbar ID census, no mutations, Pause→Resume swap with the right POST, attached-hidden processor chip at Idle, disabled click issues nothing); Electron `transcript-queue.test.ts:525` | pass |
| AC-55.4 | `transcript-card.ts:131-143`; `TranscriptPage.tsx:333-426,512-540` | `…behavior.test.ts:268,287` (`data-job-id` order, no checkbox/drag handle, single-select swap, `StatusBadge` text, source has no `width:`/`STATUS_COLORS`/`ChannelCard`; `CARD_LINE_RULE` per status); Electron `:558` | pass |
| AC-55.5 | `transcript-card.ts:87-119`; `TranscriptPage.tsx:265-331,341-424` | `…behavior.test.ts:310,330,356,372,387,408,438`; Electron `:558,583` | **partial** — success path proven; rejection path fails (Finding 1) |
| AC-55.6 | `TranscriptPage.tsx:429-541` | `…behavior.test.ts:459,481,493`; Electron `:583,605` (real ≥ 320 px height, scroller on the wrapper, wrap at 760 px) | pass |
| AC-55.7 | — | `transcript-queue.test.ts:525,558,583,605`; W2-1..W2-6 active; no `.skip/.only/.todo` under `ui/tests` | pass (recorded Windows run 103/0/0) |
| AC-56.1 | `tts-prepare.ts:20-40`; `TTSPage.tsx:370-384` | `tts-page.behavior.test.ts:179` (key set equals `PREPARE_STEPS`, checkbox `value`s are raw ids, label lookup) | pass |
| AC-56.2 | `TTSPage.tsx:260-399` | `…behavior.test.ts:195` (grid classes, 11-row `resize-y` textarea named "Text", closed disclosure, no request on toggle, count tracks unchecking, prepare keys exactly `{enabled_steps,text}`); Electron `tts-generate.test.ts:407,429` | pass |
| AC-56.3 | `TTSPage.tsx:238-249,401-522` | `…behavior.test.ts:230` (chip text/tone, closed Manage, full details string, get-btn index, refetch never closes Manage, device PUT); Electron `:429` | pass |
| AC-56.4 | `TTSPage.tsx:121-153,193-234,534-615` | `…behavior.test.ts:260,290,310`; Electron `:453` | pass |
| AC-56.5 | `tts-run-bar.ts:19-27`; `TTSPage.tsx:236-237,250,619-763` | `…behavior.test.ts:334,362,375,401` (pure resolver table, idle slot, actionable-only buttons, `aria-valuenow` 25, done → output + IPC, error replaces slot); Electron `:479` | pass |
| AC-56.6 | — | `tts-generate.test.ts:407,429,453,479`; W2-1..W2-6 active | pass (recorded Windows run) |

### COMPOSITION_LOCK (old vs. new via `git show 0f51036:<path>`)

- **Transcript**: `POST /transcripts` body `{ channel_url }` and the blank guard unchanged (`addFromForm`); reorder body `buildReorderBody(items.map(id), item.id, dir)` — same builder, moved id is the card's own; compile/view/zip/folder/requeue/retry/remove call the same `transcript-commands.ts` functions; confirm portal, Escape handler and `TRANSCRIPT_ERROR_EVENT` kept; toolbar enablement `controlEnabled(...) && !busy` unchanged; per-card availability delegates to the unchanged `controlEnabled`/`actionVisible` (`transcript-card.ts:87-109`); `TRANSCRIPT_TEST_IDS` literally present; `test-ids.ts` diff is purely additive after the MEU-51 marker.
- **TTS**: `putSettings` leaves (`input_text` debounced 300 ms, `voice`, `speed`, `output_format`, `output_path`, `device`) unchanged; `postPrepare(text, enabledSteps, chunkMaxChars)`, `postGenerate({...})` body, `cancelJob`, `postDownload/Load/Unload` unchanged; `openTarget` computed exactly as before; `generate-btn`/`cancel-btn`/`unload-btn`/get/load enablement unchanged; open-output buttons move from disabled-when-inactionable to mounted-iff-actionable, which is the approved TT4 decision. No `packages/api` change (`git status --porcelain -- packages/api` empty; `git diff 7dab4d1 HEAD -- packages` empty).

### Shared-component regression (Downloader/Convert)

`QueueCard` without slots: identical markup proven two ways — the committed fixture test and an independent reproduction that rendered the **baseline commit's own** `QueueCard`/`QueueHeaderRow` (from `git archive 0f51036 ui/src`) against the committed `queue-slot-baseline.json` (2/2 pass). `QueueList`'s only shell change is `...cardSlots?.(job)` (`:209`), which spreads nothing for Downloader/Convert. `QueueHeaderRow` is now a wrapper with the same props and DOM; `queue-header-row.test.tsx` is unmodified and passes. `ProgressBar` default tone keeps `bg-accent` and the transform-only motion (`queue-primitives.test.ts` AC-43.6 pin passes). The Windows gate's Downloader/Convert Electron files passed (103 expected / 0 unexpected, AC-49.26 included).

### Accessibility

- Card region vs. trailing controls: links and ▲ ▼ are siblings of the `role="button"` region (`QueueCard.tsx:614`; `queue-card-slots.test.tsx:50` asserts `region.contains(trailing) === false`); region name `Select channel {name}`; `metaContent`/`detailContent` hold only text, a `progressbar` and an `sr-only` span.
- `VOICE_LISTBOX`: `role="listbox"` + `aria-label`, `role="option"` + `aria-selected`, roving `tabIndex` (0 on selected, else first visible), ArrowUp/Down/Home/End move focus only, Enter/Space/click select and always PUT (`TTSPage.tsx:206-234,534-569`); verified by `tts-page.behavior.test.ts:260` and probes PROBE-4/5/7.
- Menu semantics: `role="menu"`/`menuitem`, `aria-haspopup`/`aria-expanded`, Escape from anywhere, Tab closes, disabled-while-busy (unchanged `QueueCardMenu`; `data-testid` and `onOpenChange` additive).
- Focus after reorder: success restored (RULE-1 lookup inside `scrollerRef`); rejection not restored — Finding 1.

### TEST_AMENDMENTS discipline

Pre-existing test files modified since baseline: `layout-primitives.test.ts` (TA-1, class D: forbidden list shrinks, positive adoption assertions added), `queue-primitives.test.ts` (TA-2, class C: one census entry removed), `transcript-queue.test.ts` (TA-3 A/B, TA-4 B, TA-5 A + the timeout of Finding 2), `tts-generate.test.ts` (TA-6 A/B, TA-7 A/B), `test-ids.ts` (additive only). `queue-header-row.test.tsx`, `transcript-page.test.ts`, `tts-page.test.ts` untouched. Every ledger/IPC `expect.poll` in W2-5 (both files) is unchanged; W2-5 (transcript) gained a strengthening assertion (`first()` has `data-job-id` `e2e-2`). The "setup-only repairs" are honest: `renderPage` waits for the stubbed load; the RULE-3 parking is disclosed as a jsdom workaround (jsdom keeps focus on a disabled button); `import.meta.glob` follows the `queue-header-row.test.tsx` precedent; the exact-label locator fixes a genuine substring collision ("Numbers" vs "Page numbers").

### IR-5 test-rigor grading

| Test | Rating |
|---|---|
| `queue-card-slots.test.tsx` — baseline ×3 cases, siblings, menu items/`onMenuOpen`, list resolver, tone | 🟢 🟢 🟢 🟢 🟢 |
| `queue-card-slots.test.tsx` — header baseline, frame, SOURCE_PINS | 🟢 🟢 🟡 (source-text pins; adequate for their purpose) |
| `transcript-page.behavior.test.ts` — AC-55.3 ×3, AC-55.4 ×2, AC-55.5 menus/links/target/remove/▲▼/busy, AC-55.6 add/empty | 🟢 throughout (exact IDs, ledgers, bodies, IPC targets, negative paths) |
| `transcript-page.behavior.test.ts:408` focus (RULE-1/3) | 🟡 — strong for success; the rejection branch is unexercised (Finding 1) |
| `transcript-page.behavior.test.ts:493` geometry chain | 🟡 — class-name assertions; real geometry is covered by Electron `:583` |
| `tts-page.behavior.test.ts` — AC-56.1, 56.2, 56.3, 56.4 ×3, 56.5 ×4 | 🟢 throughout (`:362` passed in Red by design and is disclosed; its negative half is at `:334`) |
| Electron AC-55.7 ×4, AC-56.6 ×4 | 🟢 — no conditional early returns; every boolean is asserted, not returned |
| TA edits | none weakened; W2-4 (transcript) and W2-4/W2-5 (TTS) gained assertions |

No 🔴 test in scope.

### Correctness edge cases probed (scratchpad probes against the unchanged code)

| Probe | Result |
|---|---|
| PROBE-1 rejected reorder, RULE-3 precondition forced | `activeElement = BODY`, order `a,b,c,d,e`, error shown → **Finding 1** |
| PROBE-2 kebab while busy | all 5 items `disabled`; Escape closes |
| PROBE-3 remove from Echo's menu with Alpha selected, poll reorders before confirm | `DELETE /transcripts/e` (own card) |
| PROBE-4 voice chosen while the initial settings GET is held | stays `af_bella`; exactly one voice PUT |
| PROBE-5 PUT-triggered settings refetch returns a stale voice after hydration | choice kept (`hydrated` guard) |
| PROBE-6 settings speed 1.5 | no preset radio checked, slider 1.5, label `Speed 1.5×` |
| PROBE-7 language filter hides the selected voice | single visible option has `tabIndex 0` |
| PROBE-8 error event while Generating | only `error-banner` mounted (precedence error > progress > output) |
| `pendingFocus` cleanup path | the effect has no cleanup; the ref is cleared on the first non-busy pass, so a poll-driven `items` change cannot re-trigger it; unmount mid-flight is inert |

---

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Command | Exit | Evidence |
|-------|--------|---------|------|----------|
| All AC have source labels | pass | `grep -cE '^\| AC-5[56]\.[0-9]+ \| (unit\|integration) \|.*\| (Spec\|Local Canon\|Research)' docs/execution/plans/2026-09-28-p11-transcript-tts/implementation-plan.md` | 0 | `13` (7 + 6) |
| Validation cells are exact commands | pass | `grep -cE 'validate-task.sh [a-z0-9-]+ > "\$RECEIPTS_DIR/' docs/execution/plans/2026-09-28-p11-transcript-tts/task.md` | 0 | `17` receipt-form cells; H1-4 uses the git status receipt form |
| BUILD_PLAN audit row present | pass | `grep -n "^## BUILD_PLAN.md Audit" docs/execution/plans/2026-09-28-p11-transcript-tts/implementation-plan.md` | 0 | `270:## BUILD_PLAN.md Audit` |
| Post-MEU rows present (handoff, reflection, metrics) | pass | `grep -cE '^\| H2-[123] \|' docs/execution/plans/2026-09-28-p11-transcript-tts/task.md` | 0 | `3` |
| IR-1 live runtime evidence | pass | `bash docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.sh windows-gate-check` (RECEIPTS_DIR=scratchpad) | 0 | `PASS windows gate @ 7dab4d15…: vitest {'passed': 630, 'failed': 0, 'total': 630} e2e {'expected': 103, 'unexpected': 0, 'skipped': 0, 'flaky': 0}`; `git diff 7dab4d1 HEAD --stat -- ui packages mcp-server` empty |
| IR-2 stub behavioral compliance | pass | scratch probes PROBE-3/5 (ledger stubs honour reorder/poll and PUT→invalidate→GET) | 0 | see probe table |
| IR-3 error mapping | n/a | — | — | UI-only change; no route added |
| IR-4 fix generalization | partial | reading `QueueList.tsx:315-330` vs `TranscriptPage.tsx:213-231` | — | the Session 24 fallback covers rejection; the transcript re-implementation does not (Finding 1) |
| IR-5 test rigor | pass | table above | — | no 🔴 |
| IR-6 boundary validation | pass | `git show 0f51036:…TranscriptPage.tsx` / `…TTSPage.tsx` vs HEAD; `git diff 7dab4d1 HEAD -- packages` | 0 | no new write surface; payloads unchanged |
| IR-7 deferral & AC coverage | pass | handoff AC tables vs plan; `Deferred Items: None` in both | — | every AC-55.x/56.x row present; Out-of-Scope rows carry a Basis; integration ACs have Electron cases |

### Design Review (DR)

| Check | Result | Command | Exit | Evidence |
|-------|--------|---------|------|----------|
| Naming convention followed | pass | `ls .agent/context/handoffs/ \| grep p11-transcript-tts` | 0 | `-MEU-55-handoff.md`, `-MEU-56-handoff.md`, `-plan-critical-review.md`; this file is the canonical `-implementation-critical-review.md` |
| Template version present | pass | `grep -c 'template_version: "2.2"' <both handoffs>` | 0 | `1` each |
| YAML frontmatter well-formed | pass | `head -14` of both handoffs | 0 | all required keys present |
| DR-1 claim-to-state | pass | test line refs re-derived with `grep -n "^test('AC-5[56]"` and the unit-file reads | 0 | every cited line in both handoffs resolves to the named test |
| DR-2 residual old terms | pass | `rg -n "STATUS_COLORS\|function ChannelCard" ui/src/renderer/src/features/transcript/TranscriptPage.tsx` | 1 | no hits (asserted by `…behavior.test.ts:283-284`) |
| DR-7 evidence freshness | pass | targeted Vitest: `npm --prefix ui run test -- --run <11 in-scope files>` | 1 | `143 passed`, 2 failed = only `ENV_BOUND_TESTS` (AC-51.6 CRLF hash `DCABD0F9…` vs `819760B9…`; AC-41.3 `P:/zorivest` missing) — not counted per the gate decision |
| DR-8 completion vs residual risk | partial | handoff AC-55.5 row says ✅ | — | the rejection focus path is a residual gap the row does not disclose (Finding 1) |

### Post-Implementation Review (PR)

| Check | Result | Command | Exit | Evidence |
|-------|--------|---------|------|----------|
| Evidence bundle complete | pass | `grep -c 'evidence.v1' <both handoffs>` | 0 | `3` each (green, e2e, windows-gate) |
| FAIL_TO_PASS table present | pass | `grep -c '### FAIL_TO_PASS' <both handoffs>` | 0 | `1` each; Red-by-design rows disclosed |
| Commands independently runnable | pass | `windows-gate-check` and the targeted Vitest above were rerun by the reviewer | 0/1 | outputs above |
| Anti-placeholder scan clean | pass | `rg -n -e TODO -e FIXME -e TBD -e XXX -e lorem <handoffs, product files, new tests>` | 1 | no hits; `rg -n '\.(skip\|only\|todo)\(' ui/tests` no hits; width audit on both pages no hits |

```json
{"schema_version":"evidence.v1","check_id":"s25-review-r1-probe-rejection","command":"vitest run --config <scratchpad>/probe/vitest.probe.config.ts transcript.probe.test.ts (PROBE-1: hold PUT /transcripts/reorder, click Bravo up-btn, blur to body, release 409)","cwd":"<scratchpad>/probe (imports /home/user/av-kit/ui/src unchanged)","scope":"AC-55.5 focus restoration, rejection path","phase":"targeted","exit_code":0,"result":"fail (defect reproduced)","tested_state":"HEAD d9ff880 (code-identical to 7dab4d1)","output":"PROBE-1 activeElement after rejection = BODY; PROBE-1 order after rejection = a,b,c,d,e","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s25-review-r1-fixture-provenance","command":"git archive 0f51036 ui/src … | tar -x; vitest run tests/unit/baseline-repro.test.tsx (renders the baseline QueueCard/QueueHeaderRow against the committed queue-slot-baseline.json)","cwd":"<scratchpad>/base/ui","scope":"AC-55.1/AC-55.2 byte-for-byte claim","phase":"targeted","exit_code":0,"result":"pass","tested_state":"baseline 0f51036 sources vs fixture committed at 536494e","output":"2 passed (2)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s25-review-r1-targeted-vitest","command":"npm --prefix ui run test -- --run tests/unit/queue-card-slots.test.tsx tests/unit/transcript-page.behavior.test.ts tests/unit/tts-page.behavior.test.ts tests/unit/queue-header-row.test.tsx tests/unit/queue-card.test.ts tests/unit/transcript-page.test.ts tests/unit/tts-page.test.ts tests/unit/layout-primitives.test.ts tests/unit/queue-primitives.test.ts tests/unit/queue-canon.test.ts","cwd":"/home/user/av-kit","scope":"in-scope unit suites","phase":"targeted","exit_code":1,"result":"pass (only ENV_BOUND_TESTS failed)","tested_state":"HEAD d9ff880","output":"Tests 2 failed | 143 passed (145): AC-51.6 CRLF hash, AC-41.3 P:/zorivest — the two tolerated environment-bound failures","fresh":true}
```

---

## Verdict

`changes_required` — Finding 1 is an evidence-backed runtime defect inside AC-55.5's contract (RULE-1/RULE-3 focus restoration is success-only; a rejected reorder strands keyboard focus on `body`, reproduced against the unchanged page), rated Medium and blocking under this round's dispatch instruction. Everything else reviewed holds: all 13 ACs have real production code and regression-sensitive tests, `COMPOSITION_LOCK` is intact (payloads, mutations, enablement, every existing test ID), the shared-component changes are byte-for-byte neutral for Downloader/Convert (independently reproduced from the baseline sources), the amendments stay inside TA-1..TA-7 in their declared classes (one labelling gap, Finding 2), and the authoritative Windows gate is clean and code-identical to HEAD.

**Follow-up (via `/execution-corrections`)**: fix Finding 1 in `TranscriptPage.tsx` with a rejection regression in `transcript-page.behavior.test.ts`; rerun `green-55`, `static`, `amendments`, `pregate` and `WINDOWS_GATE`; record Finding 2's one-line amendment note; re-dispatch Round 2 (cap 6).

**Residual risk**: the ~2 s per-click settle under the Transcript seam remains unexplained (out-of-contract observation 1); it inflates E2E time but does not affect product behavior.

🕐 Completed: 2026-09-28 13:24 (UTC)

---

## Recheck (2026-09-28)

**Workflow**: `/execution-critical-review` Round 2 recheck (cap 6)
**Agent**: claude-fable-5-1-subagent (independent Claude Code `Agent` subagent, Fable 5.1, high effort; did not author the implementation or Round 1; wrote only this file)

### Review binding

- **Intent anchor**: The plan's goal is to *"Deliver Session 25 of `.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md` as grouped"* — MEU-55 `gui-transcript-layout` and MEU-56 `gui-tts-layout` on the shared queue anatomy, inside `COMPOSITION_LOCK`, carrying the closed MEU-48 ACs. Round 2 asks whether the Round 1 correction closes the one demonstrated gap (AC-55.5 rejection-path focus) without regressing anything, and whether the delivered work now achieves that intent.
- **Intent achieved**: `yes`.
- **Reviewed state**: HEAD `02fbb20` (clean tree). Code-identical under `ui/`, `packages/`, `mcp-server/` to the Windows-gated commit `c315640` (`git diff c315640 HEAD --stat -- ui/ packages/ mcp-server/` is empty, exit 0). The only code change since Round 1 (`d9ff880`) is `9fb0153`: `TranscriptPage.tsx` (−3 lines guard, −`from` field, comment) and `transcript-page.behavior.test.ts` (+`reorderStatus` stub branch, +1 test). `c315640`, `692b483`, `02fbb20` touch only `docs/` and `.agent/`.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|-------------|----------------|
| 1 — Medium, blocking: rejected ▲ ▼ reorder left keyboard focus on `body` (AC-55.5, RULE-1/RULE-3) | open | ✅ Fixed |
| 2 — Low, clerical: W2-5 timeout 120 → 180 s labelled TA-5 but not a declared TA-5 edit | open | ✅ Fixed |

### Confirmed Fixes

- **Finding 1** — `ui/src/renderer/src/features/transcript/TranscriptPage.tsx:217-232`. The effect now clears `pendingFocus` (`:222`) and re-finds the card by `data-job-id` inside `scrollerRef` on the first non-busy pass regardless of whether `items` changed; the `items.findIndex(...) === pending.from` early return and the `from` field (`:148`, `:268`) are gone. Behavior verified path by path against HEAD with scratchpad probes that import the unchanged page (`<scratchpad>/probe/r2.probe.test.ts`, 6/6 ran):
  - **409 rejection** (the shipped regression, `transcript-page.behavior.test.ts:445-473`): after the error banner shows and the order stays `a,b,c,d,e`, `document.activeElement` is Bravo's `up-btn`.
  - **Non-409 rejection** (500, PROBE-R2-2) and **thrown fetch** (`TypeError: Failed to fetch`, PROBE-R2-3): `run()`'s `catch` sets the banner, `finally` releases `busy`, and focus returns to the same-direction button of the same card (`down-btn` on `c`; `up-btn` on `d`). Order unchanged in both.
  - **Card removed mid-command** (PROBE-R2-4: poll drops `b` while the PUT is held, then 409): no throw, `activeElement` stays `BODY` (nothing to restore to), selection falls back to `a` via the existing `selectedId` effect (`:184-188`). Inert, as intended.
  - **Edge rows**: ▼ on Delta to the last position (PROBE-R2-5) lands with `down-btn` disabled and focus falls back to `up-btn` on `d`; ▲ on Echo (last card) rejected (PROBE-R2-6) restores `up-btn` on `e`. The shipped success test (`:415-443`) covers ▲ to the first position → `down-btn`. Both directions and both disabled-end cases are therefore exercised.
  - **Sequencing**: on success `invalidateQueries` resolves after the refetch, so the `items` render arrives while `busy` is still `true` (effect returns without clearing the ref, `:219-221`), and the `finally` `setBusy(false)` render performs the restore. On rejection only the `busy` edge fires the effect. A poll-driven `items` change after the ref is cleared is a no-op. There is no cleanup to leak: the effect registers nothing, and an unmount mid-flight leaves a dead ref.
  - **Red for the right reason**: the HEAD test file was run against the pre-fix page (`git archive 9fb0153^ ui/src ui/tests …` into `<scratchpad>/old/ui`, HEAD's `transcript-page.behavior.test.ts` dropped in). Result: 15 passed, exactly 1 failed — `AC-55.5 focus returns to the card after a rejected reorder too` with `expected <body>… to be <button …>` at the final `vi.waitFor`. The success test (`:415`) still passes on the old page, so the new test is the discriminating one.
  - **IR-4 generalization**: the effect is the only reorder focus path on the Transcript page; the Session 24 shared fallback (`QueueList.tsx:318-330`) already restores on success and rejection alike and is untouched. No other page re-implements the pattern (`rg -n "pendingFocus|restoreFocusId" ui/src` → only these two files).
- **Finding 2** — `docs/execution/plans/2026-09-28-p11-transcript-tts/walkthrough.md:133` records the W2-5 `test.setTimeout` raise as an execution amendment (setup time budget, no assertion changed) with the timing evidence. The handoff's "only TA-1..TA-7" claim is now literally true. `ui/tests/e2e/transcript-queue.test.ts` is unchanged since Round 1.

### Regression check on the fix (scope b)

- Targeted Vitest at HEAD: `npm --prefix ui run test -- --run tests/unit/transcript-page.behavior.test.ts tests/unit/queue-card-slots.test.tsx tests/unit/tts-page.behavior.test.ts tests/unit/queue-header-row.test.tsx tests/unit/queue-primitives.test.ts tests/unit/layout-primitives.test.ts` → `64 passed | 1 failed (65)`; the failure is `AC-51.6` (CRLF hash `DCABD0F9…` vs `819760B9…`), one of the two tolerated `ENV_BOUND_TESTS`. Not counted.
- `validate-task.sh amendments` → `PASS amendment guard` against baseline `0f51036`; the changed-test list is exactly the plan's own files plus the TA-1..TA-7 files; no `.skip/.only/.todo`.
- `validate-task.sh windows-gate-check` → `PASS windows gate @ c315640d05cc7ddf8293c8f0b64733c209bb0028: vitest {'passed': 631, 'failed': 0, 'total': 631} e2e {'expected': 103, 'unexpected': 0, 'skipped': 0, 'flaky': 0}` (631 = Round 1's 630 + the new regression). All 9 stages exit 0, `clean_tree: true`, lockfile `A86D9A42…2980`, electron 42.9.3.
- `COMPOSITION_LOCK`: `9fb0153` changes no request body, mutation, enablement rule or test ID (`git show 9fb0153 -- ui/` is the effect, the ref type, the `reorder()` ref write, and the test). Shared-component contracts (`CARD_SLOTS`, `MENU_ITEM_EXTENSION`, `LIST_SLOT_RESOLVER`, `HEADER_FRAME`, `PROGRESS_TONE`) are untouched since Round 1 (`git diff d9ff880 HEAD --stat -- ui/src/renderer/src/components` is empty).
- **W9-3 failed Windows run 1 (challenged, assessment upheld)**: the assessment's "no code overlap" claim was tested independently. `git diff 0f51036 HEAD --name-only -- ui/` lists no capture, settings, main, preload or e2e-helper file; `features/capture` and `features/settings` import none of `ProgressBar`, `status-tokens`, `StatusBadge` or any `components/queue/*` module (direct or transitive: `StatusBadge` is the only other `status-tokens` importer and is not used by either feature); the `status-tokens.ts` change is additive constants. A 60 s test timeout plus a worker-teardown timeout on the 3rd spec, with the same spec passing 22.5 s in run 2 and 3/3 alone, is consistent with the stated environment hang. The lost `error-context.md` is an evidence caveat, disclosed in both handoffs and the walkthrough; run 2 is a complete fresh full gate on the same commit with `flaky: 0`, so it stands as the authoritative D6 evidence.

### Remaining Findings

- **Low** / blocking: **no** / kind: behavior — **Finding 3 (new, non-blocking): the ▲ ▼ focus restore is unconditional, so focus the user deliberately moved during the in-flight window is pulled back to the card.** `TranscriptPage.tsx:231` calls `target?.focus()` without checking where focus currently is. `channel-input` (`:443-453`) and `add-btn` stay enabled while `busy` (pre-existing at baseline — `git show 0f51036:…/TranscriptPage.tsx` binds the input to no `busy` flag — and preserved by `COMPOSITION_LOCK`), so a user who clicks ▲ and then clicks into the Channel URL field and types before the PUT settles has the caret yanked to the button. Reproduced on HEAD: PROBE-R2-1 (success) → `activeElement = BUTTON[up-btn] card=c`, input value `abc` intact; PROBE-R2-2 (500) → `BUTTON[down-btn] card=c`. This is *not* an AC violation: AC-55.5 requires focus to return to the moved card and RULE-3 governs how the test proves the precondition; neither states an "only if focus was lost" guard, and the approved Session 24 shared fallback (`QueueList.tsx:318-330`) restores unconditionally too. On the success path the behavior predates `9fb0153`; the fix extends it to the rejection path exactly as Finding 1 required. Recorded here as a real observation with a reproducer rather than demoted to prose. **Suggested fix (outside this loop, or as a no-contract-change follow-up)**: before `target?.focus()`, return early when `document.activeElement` is neither `document.body` nor inside `card` (i.e. the user has already put focus somewhere meaningful); the shipped RULE-3 tests blur to `body` and keep passing. If adopted, apply the same guard to `QueueList.tsx:318-330` (IR-4).

### Out-of-Contract Observations (non-blocking, ≤ 3 bookkeeping)

1. `…-MEU-55-handoff.md:54` cites the new regression by name ("rejected-reorder regression (Round 1 correction)") rather than by line; it is `ui/tests/unit/transcript-page.behavior.test.ts:445`. Clerical.
2. The failed Windows run 1 has no durable receipt in the repo (its receipts and Playwright JSON live on Mat's machine; `error-context.md` lost). Disclosed; the passing run 2 is fully recorded. Residual auditability gap, not a finding.
3. Carried from Round 1: the ~2 s per-click settle under the Transcript seam remains unexplained; it inflates E2E time only.

### Docs and SSOT (scope d)

| Check | Result | Evidence |
|---|---|---|
| DR-1 claim-to-state (Corrections Applied, walkthrough §Round 1 corrections, §H1-6 on the fix) | pass | Every claim (early return removed, `from` removed, new test name and Red message, `green-55` 171, `amendments` PASS, gate 631/103, W9-3 run 1 shape) matches `git show 9fb0153`, the reproduced Red, and `windows-gate-result.json` |
| task.md | pass | H1-6 `[x]` with both `c315640` runs recorded; H1-7 `[ ]`; H2-1..H2-3 `[ ]` (closeout follows this verdict by design) |
| SSOT | pass | `meu-status.yaml` MEU-55 (`:1561`) and MEU-56 (`:1588`) `ready_for_review`, `execution_plan` bound to this folder; grouping row 25 `in review` (`…session-grouping.md:70`); `current-focus.md:1` says MEU-55/56 `ready_for_review` |
| DR-7 evidence freshness | pass | `windows-gate-check` reproduced above; handoff evidence.v1 `s25-windows-gate-r1` blocks in both handoffs carry `tested_state c315640…`, 631/631, 103/0/0 — identical to the JSON |
| DR-8 completion vs residual | pass | Both handoffs' AC-55.5 rows may now honestly read ✅; the Round 1 gap is closed and the residual (Finding 3) is out of contract |

### IR-5 (this round's test)

| Test | Rating |
|---|---|
| `transcript-page.behavior.test.ts:445` rejected reorder: holds the PUT, proves the RULE-3 precondition (`activeElement === body`), releases a 409, asserts the banner text, the unchanged `data-job-id` order, and the exact restored element | 🟢 Strong — fails on the pre-fix page for the asserted reason (reproduced) |

```json
{"schema_version":"evidence.v1","check_id":"s25-review-r2-red-on-prefix","command":"git archive 9fb0153^ ui/src ui/tests ui/package.json ui/vitest.config.ts | tar -x -C <scratchpad>/old; cp ui/tsconfig.json; git show HEAD:ui/tests/unit/transcript-page.behavior.test.ts > old/ui/tests/unit/transcript-page.behavior.test.ts; npx vitest run --config vitest.probe.config.ts tests/unit/transcript-page.behavior.test.ts","cwd":"<scratchpad>/old/ui (node_modules symlinked to /home/user/av-kit/ui/node_modules)","scope":"Round 1 Finding 1 regression test against the pre-fix TranscriptPage","phase":"targeted","exit_code":1,"result":"pass (expected Red reproduced)","tested_state":"page from 9fb0153^ (= d9ff880), test from HEAD 02fbb20","output":"Tests 1 failed | 15 passed (16): × AC-55.5 focus returns to the card after a rejected reorder too — AssertionError: expected <body>…</body> to be <button type=\"button\" …>","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s25-review-r2-probes","command":"npx vitest run --config vitest.probe.config.ts r2.probe.test.ts (PROBE-R2-1..6: success with focus moved to channel-input; 500 with focus in input; thrown fetch after blur; card removed by poll then 409; ▼ to last; ▲ on last rejected)","cwd":"<scratchpad>/probe (imports /home/user/av-kit/ui/src unchanged)","scope":"AC-55.5 focus restoration, all settle paths on HEAD","phase":"targeted","exit_code":0,"result":"pass (6 ran; Finding 3 observed in R2-1/R2-2)","tested_state":"HEAD 02fbb20 (code-identical to c315640)","output":"R2-1 BUTTON[up-btn] card=c input=abc; R2-2 BUTTON[down-btn] card=c order a,b,c,d,e; R2-3 BUTTON[up-btn] card=d order a,b,c,d,e; R2-4 threw=null activeElement=BODY selected=a; R2-5 BUTTON[up-btn] card=d; R2-6 BUTTON[up-btn] card=e order a,b,c,d,e","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s25-review-r2-targeted-vitest","command":"npm --prefix ui run test -- --run tests/unit/transcript-page.behavior.test.ts tests/unit/queue-card-slots.test.tsx tests/unit/tts-page.behavior.test.ts tests/unit/queue-header-row.test.tsx tests/unit/queue-primitives.test.ts tests/unit/layout-primitives.test.ts","cwd":"/home/user/av-kit","scope":"in-scope unit suites at HEAD","phase":"targeted","exit_code":1,"result":"pass (only ENV_BOUND_TESTS failed)","tested_state":"HEAD 02fbb20","output":"Tests 1 failed | 64 passed (65): AC-51.6 CRLF hash DCABD0F9… vs 819760B9… (tolerated env-bound)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s25-review-r2-gate-and-guard","command":"bash docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.sh windows-gate-check; bash docs/execution/plans/2026-09-28-p11-transcript-tts/validate-task.sh amendments (RECEIPTS_DIR=<scratchpad>/r2)","cwd":"/home/user/av-kit","scope":"authoritative D6 gate identity and TEST_AMENDMENTS guard","phase":"full-gate verification","exit_code":0,"result":"pass","tested_state":"HEAD 02fbb20; git diff c315640 HEAD -- ui packages mcp-server empty","output":"PASS windows gate @ c315640d05cc7ddf8293c8f0b64733c209bb0028: vitest {'passed': 631, 'failed': 0, 'total': 631} e2e {'expected': 103, 'unexpected': 0, 'skipped': 0, 'flaky': 0} | PASS amendment guard","fresh":true}
```

### Verdict

`approved` — Round 1 Finding 1 is closed on every settle path (409, non-409, thrown fetch, both directions, both disabled ends, card removed mid-command) with a regression test that is Red on the pre-fix page for the asserted reason; Finding 2 is recorded as an execution amendment; the fix introduces no contract, payload, enablement or shared-component change; the authoritative Windows gate on the code-identical commit `c315640` is clean (631/631, 103/0/0) and its earlier W9-3 failure has no code path into this session's diff. The delivered work achieves the plan's intent. One new Low, non-blocking behavior observation (Finding 3, unconditional focus restore) is recorded with a reproducer and a suggested guard; it is outside the AC contract and matches the approved Session 24 precedent, so it does not gate approval.

**Follow-up**: proceed to H2 closeout. Optionally open a small follow-up for Finding 3 (activeElement guard on both restore effects); no rerun of any gate is required by this verdict.

**Residual risk**: Finding 3's focus pull exists only inside the reorder round-trip window; the ~2 s Transcript-seam click settle (Round 1 observation) is unchanged.

🕐 Completed: 2026-09-28 15:52 (UTC)
