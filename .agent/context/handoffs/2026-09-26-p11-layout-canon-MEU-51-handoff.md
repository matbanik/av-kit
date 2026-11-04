---
date: "2026-09-26"
project: "2026-09-26-p11-layout-canon"
meu: "MEU-51"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-09-26-p11-layout-canon/implementation-plan.md"
build_plan_section: "bp11s11.2"
agent: "Codex"
reviewer: "gpt-6-astra-high"
predecessor: "2026-09-26-p11-layout-canon-MEU-50-handoff.md"
---

# Handoff: 2026-09-26-p11-layout-canon-MEU-51-handoff

> **Status**: `complete` · **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-51 — five unwired, controlled layout primitives: `Disclosure`, `SegmentedControl`, `StatusChip`, `FormRow`, and `PathRow`. A separate test-only renderer entry mounts the real components in an Electron `BrowserWindow`; no product page imports them. The ordinary build and package exclude the harness.

**Build Plan Section**: [Phase 11 shared layout primitives](../../../docs/build-plan/11-page-layout.md#shared-layout-primitives); [Session 23 plan](../../../docs/execution/plans/2026-09-26-p11-layout-canon/implementation-plan.md).

**Predecessor**: [MEU-50 canon handoff](2026-09-26-p11-layout-canon-MEU-50-handoff.md). The canon and its six tests were Green before MEU-51 Red.

**Boundary inventory**: `SegmentedControl` emits only a caller-supplied option value; `Disclosure` emits a boolean; `PathRow` forwards exact caller text and one Browse callback. Build flag `AVKIT_PRIMITIVE_HARNESS_BUILD` accepts unset or `1`; E2E output selector `AVKIT_E2E_OUT_DIR` accepts unset/`out` or `out-e2e`. Both reject other values. No REST, MCP, or new persisted input boundary is introduced.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|---|---|---|---|---|---|
| AC-51.1 | unit | Controlled disclosure uses canonical Button, native click/Enter/Space, synchronized ARIA, and focus-safe closed panel. | Research-backed: W3C APG Disclosure | `layout-primitives.test.ts` AC-51.1; Electron AC-51.7 | ✅ |
| AC-51.2 | unit | Native radio segment retains caller IDs/name, one checked value, arrow-key choice, and finite emissions. | Research-backed: W3C APG Radio Group | `layout-primitives.test.ts` AC-51.2; Electron AC-51.7 | ✅ |
| AC-51.3 | unit | Each finite tone renders readable chip label/count with theme token classes. | Local Canon: Phase 10 status tokens | `layout-primitives.test.ts` AC-51.3; Electron AC-51.7 | ✅ |
| AC-51.4 | unit | Form label, hint, and error associate with control; path value and Browse callback remain exact. | Local Canon: Phase 6 Settings; W3C APG Button | `layout-primitives.test.ts` AC-51.4; Electron AC-51.7 | ✅ |
| AC-51.5 | unit | Components import no page/API code, add no package or Button variant/size, and contain no placeholder/raw-color/broad-motion rule. | Local Canon: grouping and GUI rules | `layout-primitives.test.ts` AC-51.5; `p11-primitive-scope-check.txt` | ✅ |
| AC-51.6 | unit | Five new IDs are unique and disjoint from prior IDs; preexisting registry bytes and caller IDs remain unchanged. | Local Canon: `PRESERVED_TESTIDS` | `layout-primitives.test.ts` AC-51.6; SHA-256 prefix check | ✅ |
| AC-51.7 | integration + E2E | Real Electron harness proves all five controls and callback effects; isolated output is fresh, ordinary output excludes harness, invalid selectors fail, product pages remain untouched. | Human-approved: user Option 1, Session 23 | `tests/e2e/layout-primitives.test.ts`; `p11-harness-check.txt`; `p11-invalid-env-check.txt` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output | Green Output | File:Line |
|---|---|---|---|
| AC-51.1–51.7 | `p11-primitives-red.json`: 7 collected, 7 `AssertionError` failures, 0 pending, no file error; `p11-primitives-red-check.txt` says `PASS RED_ORACLE AC-51`. | `p11-primitives-green.txt`: 7 passed; `p11-primitives-e2e.txt`: 1 passed in real Electron. | `ui/tests/unit/layout-primitives.test.ts:30`; `ui/tests/e2e/layout-primitives.test.ts:12` |

### Commands Executed

Every command captured all process streams under `C:/Temp/av-kit/`, saved `$LASTEXITCODE`, and reported only the receipt tail. The complete per-edit progression is in [walkthrough.md](../../../docs/execution/plans/2026-09-26-p11-layout-canon/walkthrough.md).

| Command | Exit Code | Key Output |
|---|---:|---|
| `rtk proxy npm --prefix ui run test -- tests/unit/layout-canon.test.ts tests/unit/layout-primitives.test.ts` | 0 | `p11-meu51-targeted.txt`: 13 passed |
| `rtk proxy npm --prefix ui run typecheck` | 0 | `p11-meu51-type.txt`: zero errors |
| `rtk proxy npm --prefix ui run lint` | 0 | `p11-meu51-lint.txt`: zero warnings/errors |
| Task row 10 isolated build → real Electron E2E → product build command | 0 | `p11-harness-check.txt`: `PASS isolated and product build/E2E`; E2E 1 passed |
| Negative environment guard command | 0 | `p11-invalid-env-check.txt`: both invalid values rejected |
| Static page import/placeholder command | 0 | `p11-primitive-scope-check.txt`: no page mounts, placeholders, raw hex, or broad transition |

### Quality Gate Results

```text
Targeted Vitest: 13 passed, 0 failed (MEU-50 + MEU-51).
TypeScript: zero errors.
ESLint: zero warnings/errors.
Real Electron primitive E2E: 1 passed.
Isolated and ordinary builds: both passed; harness HTML absent from ordinary out/renderer.
Package selection: electron-builder.yml retains only out/**/*.
```

The E2E initially failed to launch because its own launch environment set `ELECTRON_RUN_AS_NODE` to an empty string. Removing that entry and waiting for the already-created product window before selecting the new harness window fixed test setup; interaction assertions were unchanged. The final run exercised a separate real `BrowserWindow` with the built harness HTML.

**Disclosed test-contract correction:** The first AC-51.6 assertion incorrectly demanded global uniqueness from the existing registry. Its preexisting `CANCEL_BTN` and `TTS_CANCEL_BTN` intentionally share `cancel-btn`. The approved contract requires previous values to remain exact and **new** IDs to be unique. The assertion was corrected after Red to check uniqueness/disjointness of only the five appended IDs while retaining the SHA-256 of the entire previous registry prefix. This is an explicit test-immutability deviation, submitted for independent reviewer judgment; no prior ID value or primitive interaction expectation changed.

**Post-MEU H1 gate (2026-09-26):** The user explicitly authorized narrow repair of five existing E2E failures found by the initial full run. Final receipts passed: typecheck (`C:/Temp/av-kit/p11-repair-typecheck.txt`), lint (`p11-repair-lint.txt`), 577 Vitest tests (`p11-repair-vitest.txt`), ordinary build (`p11-repair-build.txt`), and 85 real Electron tests (`p11-repair-full-e2e.txt`, including AC-51.7). All five repaired cases passed together (`p11-five-targeted-final.txt`). The E2E fixture/setup changes and Red progression are in the walkthrough §H1-2. Behavioral assertions were preserved, and no product page was edited for those repairs.

**Independent Round 1 correction evidence:** GPT-6 Astra/high filed one High R1 and one Medium R2 in the rolling implementation review: caller option/path control test IDs did not land on interactive nodes, and Browse could not be omitted. Two added rendered-control tests failed first (`C:/Temp/av-kit/p11-review-r1-red.txt`: 2 behavior failures, 7 existing cases skipped by the targeted filter). `SegmentedControl` now forwards per-option `testId` to each native radio; `PathRow` now forwards independent input/Browse IDs and omits Browse when no callback exists. Intermediate targeted receipt: 1 passed / 1 failed (`p11-review-r1-after-segment.txt`); final primitive receipt: **9 passed** (`p11-review-r1-primitives-green.txt`). Full post-correction gates: typecheck/lint clean (`p11-review-r1-typecheck.txt`, `p11-review-r1-lint.txt`), **579 Vitest passed** (`p11-review-r1-vitest.txt`), isolated primitive E2E and ordinary build isolation passed (`p11-review-r1-harness-check.txt`), and **85 full Electron E2E passed** (`p11-review-r1-full-e2e.txt`). The seven original AC assertions, registered IDs, and five-case repair assertions remain intact.

---

## Changed Files

| File | Action | Lines | Summary |
|---|---|---:|---|
| `ui/src/renderer/src/components/ui/{Disclosure,SegmentedControl,StatusChip,FormRow,PathRow}.tsx` | new | component files | Controlled, caller-owned presentational primitives |
| `ui/tests/unit/layout-primitives.test.ts` | new | 1–227 | Seven source-backed AC tests plus two Red-first reviewer correction tests; disclosed AC-51.6 correction |
| `ui/tests/e2e/layout-primitives.test.ts` | new | 1–84 | Real Electron keyboard, accessibility, callback, and visual assertions |
| `ui/src/renderer/primitive-harness.html`, `ui/src/renderer/src/primitive-harness.tsx` | new | entry files | Test-only renderer with local state and the five real components |
| `ui/tests/e2e/test-ids.ts` | modified | 300–305 | Five additive IDs; prior prefix hash unchanged |
| `ui/electron.vite.config.ts` | modified | 7–10, renderer input | Exact-value conditional harness input |
| `ui/tests/e2e/global-setup.ts` | modified | setup function | Allowlisted output choice and source/config freshness |
| `.gitignore` | modified | UI output entries | Ignore generated `ui/out-e2e/` |
| `ui/tests/e2e/capture-inbox.test.ts` | modified | helper and W9/AC-59/AC-60 setup | Human-approved H1 gate repair: real dirty mark and current-surface image clicks; behavioral assertions unchanged |
| `ui/tests/e2e/{download-queue,convert-queue,transcript-queue}.test.ts` | modified | DELETE seams | Human-approved H1 gate repair: bodyless 204 mock responses across the same fixture pattern |
| `ui/src/renderer/src/components/ui/{SegmentedControl,PathRow}.tsx` | revised after review | caller ID/action props | R1/R2 correction: per-option/native radio IDs; independent path input/Browse IDs and optional Browse |

```diff
 ui/electron.vite.config.ts
+const primitiveHarnessBuild = process.env.AVKIT_PRIMITIVE_HARNESS_BUILD
+if (primitiveHarnessBuild !== undefined && primitiveHarnessBuild !== '1') {
+  throw new Error('AVKIT_PRIMITIVE_HARNESS_BUILD must be unset or exactly 1')
+}
 ui/tests/e2e/global-setup.ts
+const selected = process.env.AVKIT_E2E_OUT_DIR ?? 'out'
+if (selected !== 'out' && selected !== 'out-e2e') {
+  throw new Error('AVKIT_E2E_OUT_DIR must be out or out-e2e')
+}
 .gitignore
+ui/out-e2e/
 ui/tests/e2e/download-queue.test.ts
-        return new Response('', { status: 204 })
+        return new Response(null, { status: 204 })
 ui/tests/e2e/capture-inbox.test.ts
-  await page.mouse.click(originX + 3 * scale, originY + 6 * scale)
+  await clickSampleImagePoint(page, 3, 6)
 ui/src/renderer/src/components/ui/SegmentedControl.tsx
+              data-testid={option.testId}
 ui/src/renderer/src/components/ui/PathRow.tsx
-  onBrowse: () => void
+  onBrowse?: () => void
+  inputTestId?: string
+  browseTestId?: string
```

---

## Codex Validation Report

Round 1 independent GPT-6 Astra/high review returned `changes_required` with R1 High/R2 Medium. The reviewer accepted the AC-51.6 Red correction and the five E2E repairs. Both findings have source and Red-first test corrections above. The independent Round 2 recheck verified both fixes and returned `approved` with zero remaining findings; the reviewer-authored verdict is in the rolling implementation review file, and `C:/Temp/av-kit/p11-exec-review-check.txt` passed the target-bound approval check. MEU-51 is `approved` in the status SSOT.

---

## Corrections Applied (2026-09-26)

In-session corrections: FormRow/PathRow association failure was fixed in production code by giving FormRow an action suffix and keeping the labelled input as its cloned control; the registered-ID line endings were restored byte for byte before new IDs were appended; E2E launch/window selection was corrected. Independent Round 1 R1/R2 corrections then added actual radio/input/Browse locator support and an optional Browse action, with two Red tests and passing gates as recorded above. The independent Round 2 reviewer approved those corrections; the implementer did not author the approval verdict.

---

## Deferred Items

None from MEU-51. Product page mounts and their first page-specific E2E assertions remain assigned to the already scheduled MEU-52–58 per the approved Phase 11 grouping. They are not Session 23 omissions.

---

## History

| Event | Date | Agent | Detail |
|---|---|---|---|
| Red | 2026-09-26 | Codex | Seven AC assertion failures before component/harness work. |
| Green | 2026-09-26 | Codex | Seven unit and one real Electron E2E passed; isolated and ordinary builds passed. |
| Handoff | 2026-09-26 | Codex | Prepared for independent execution review after H1 gate. |
| Review R1 | 2026-09-26 | GPT-6 Astra/high | `changes_required`: R1 caller control IDs, R2 optional Browse. |
| Corrections | 2026-09-26 | Codex | Two Red-first tests, primitive fixes, 579 Vitest and 85 Electron passed; submitted for Round 2. |
| Review R2 | 2026-09-26 | GPT-6 Astra/high | `approved`: R1/R2 fixed, zero remaining findings. |
