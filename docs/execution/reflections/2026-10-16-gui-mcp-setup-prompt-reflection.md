---
date: "2026-10-17"
project: "gui-mcp-setup-prompt"
meus: ["MEU-71", "MEU-92"]
plan_source: "docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/implementation-plan.md"
template_version: "2.0"
---

# 2026-10-17 Meta-Reflection

> **Date**: 2026-10-17 (planned 2026-10-16, executed 2026-10-17)
> **MEU(s) Completed**: MEU-71 `gui-mcp-setup-prompt`, MEU-92 `dist-mcp-server-bundle`
> **Plan Source**: `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/implementation-plan.md`

---

## Execution Trace

### Friction Log

1. **What took longer than expected?**

   Row 0. The first baseline failed on a test this plan does not touch. AC-41.3 (`queue-canon.test.ts`) read its expected status-pill colours from Zorivest's live working tree. Zorivest MEU-662 (`1f254832`) had darkened that palette the evening before, so `main` failed independently of Session 31b. Resolving it took three human decisions:
   - Mat asked to decouple everything Zorivest-related, which became D-91 A.
   - D-90 pinned the copy to `61243baf`.
   - D-92 A-1 made the decoupling a new row 0a of this session.

   After that, the baseline re-ran clean (ui 975, mcp 428, Electron 157).

   Smaller delays:
   - **Missing region-picker stub.** A fresh worktree lacks the gitignored stub, so four capture-picker specs failed in the S8 evidence run. D-93 added a `picker-stub` stage to the baseline and the gate.
   - **gate71 run 1 failed AC-71.15** on 1 of 20 repeats. The Windows clipboard listener held the lock, so Chromium dropped the Copy write silently. This was stop S8; under D-94 A, the click and the read now retry inside `toPass`, with the assertions unchanged.
   - **green92 run 1:** `rmSync` hit `EPERM` because the killed child still held the temp directory. The helper now waits for the exit.
   - **pkg-probe run 1:** `CreateProcess` rejected the relative forward-slash exe path (D-97).
   - **The execution-review dispatch** was refused twice before Codex started, because `Invoke-CodexDispatch.ps1` accepts only `P:/av-kit` as the repository root. Session 35's precedent fixed it: the prompt is staged under `C:/Temp/av-kit/dispatch`, and the prompt names the worktree.
   - **Round 2 was refused on tokens.** Round 1 used 11.5M of the 21M budget, and the reserve rule needs that much again, so round 2 waited on Mat's `continue` (D-99).

2. **What instructions were ambiguous?**

   - **Where the example config is written.** The plan assigned `EXAMPLE_CONFIG` to row 4, but row 3's `green71-main` test set already runs AC-71.11 against it. The example was written in row 3 (D-95).
   - **Which decisions the reflection carries.** H2-1 and the grouping's carry-forward line name six grouping IDs and plan D-71 to D-93. The closeout validator, however, reconciles every grouping §8 row (so D-3, D-4 and D-5 too) and every handoff decision record (D-94 to D-98). The table follows the validator.
   - **The MCP_PROMPT_LOOK L3 step** expected one client run. Mat ran it in Claude Desktop with Sonnet 5.5 (`RESULT: connected`); walkthrough §MCP_PROMPT_LOOK records the variance from the plan's wording.

3. **What instructions were unnecessary?**

   Repeating the H1-2 gate record in both handoffs' Quality Gate Results. `walkthrough.md` and `gate-result.json` already hold it.

4. **What was missing?**

   - **Session 39's RULE-2 was not applied.** Neither execution-review prompt states the verdict schema's approval rule (every checklist row `pass` or `n/a`).
   - **The dispatcher cannot target a worktree.** This is the second session to work around it.
   - **The execution-review budget was not sized.** The ledger began at 21M. One round of a two-MEU review with a packaged probe used 11.5M, which left no room for a recheck.
   - **`plan_checks.py static` read decision IDs from the plan only.** Handoff-defined IDs (D-94, D-97) therefore failed (execution review F2).
   - **No rule for tests that read another repository.** No rule stopped a test from reading another repository's working tree.

5. **What did you do that wasn't in the prompt?**

   - **Kept the H1-2 gate receipts** (`s31b-run-gate-h1-2.txt`, `s31b-gate-result-h1-2.json`) before re-running the gate after F1, so the superseded run stays inspectable.
   - **Ran a path-scoped process listing before each gate,** because Session 35 was running its own Electron app from another worktree at the same time.
   - **Asked Mat for a full sentence for the ledger.** Mat's first two replies to D-99 were below the ledger's 20-character `--said` floor, so I asked for Mat's own sentence rather than composing one.

### Quality Signal Log

6. **Which tests caught real bugs?**

   - **AC-71.9 and AC-71.8 (the junction launch through `resources/mcp-server`).** They were Red under the old suffix entry guard, which is the packaged-layout failure MEU-71 exists to fix, and Green under `ENTRY_GUARD`.
   - **AC-92.4 (`PKG_PROBE`) on a hermetic copy.** It proved that the bundle starts with no `node_modules` above it. `PKG_EVIDENCE` binds that proof to the hashes of the 10 files it covered, which closed plan review round 1 F1 (a bare `passed` flag would accept stale proof).
   - **Codex execution review F1.** The reviewer, not a test, found the Claude Desktop prompt's bug: step 1 chose the MSIX config but step 2 backed up the standard `%APPDATA%` file. The new AC-71.4 negative test failed on the round-1 code and passes on the fix.
   - **AC-41.3.** It did its job (it caught a provenance drift), but against the wrong source; A-1 now points it at a committed copy.

7. **Which tests were trivially obvious?**

   - The TA-1 count pins (20 → 21 channels in three files) lock the inventory and nothing more.
   - AC-71.1 and AC-71.13 pin the same `CLIENT_SET` twice, once for main and once for the renderer's copy (D-96). That is deliberate, but each test alone is trivial.

8. **Did pyright/ruff catch anything meaningful?**

   Not applicable: no Python product file changed, so the gate skipped py-types, py-lint and py-tests by scope. `tsc` and ESLint passed on every gate run with no finding.

### Workflow Signal Log

9. **Was the FIC useful as written?**

   Yes. The named contracts (`PROMPT_BUILDER`, `ENTRY_GUARD`, `SERVER_ENTRY`, `BUNDLE_SCRIPT`, `PKG_PROBE`, `PKG_EVIDENCE`) mapped one to one onto code and tests. The token boundary held structurally, because the builder has no token input. One gap: the Claude Desktop contract said only "with the MSIX-virtualized config path note". It did not require every later step to use the file step 1 chose, and that gap is where F1 came from.

10. **Was the handoff template right-sized?**

    About right. 15 ACs for MEU-71 and 4 for MEU-92, plus the cross-reference rows to AC-23, AC-41 and AC-71.

11. **How many tool calls did this session take?**

    Not tracked precisely. Several hundred across planning (three plan-review rounds) and execution, including at least one context compaction.

12. **Which rows were delegated, to which subagent (harness + model), and did any delegated result need rework?**

    No rows were delegated; Claude Code (Opus 5.5) ran every row.
    - **Plan review:** Codex CLI `gpt-6.1-sol` (high), approved at round 3. Round 1 had one High finding (F1, stale packaged evidence). Round 2 was a PR-6 procedural refusal on a truncated census.
    - **Execution review:** the same route. Round 1 `changes_required` (F1 High, blocking: the Claude Desktop MSIX backup; F2 Low: the static decision lookup), 11,498,809 tokens. Round 2 `approved`, 0 findings, `intent_achieved: yes`, 3,825,102 tokens, after Mat's budget `continue` (D-99). Round 2 also corrected two of my own records without raising a finding: the F1 note said 12 other goldens (there are 10 others of 11), and it named an H1-2 result copy that was never written. Both are corrected in `walkthrough.md`.

### Decisions Log

| ID | Stage | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|-------|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-1 | grouping | When are the gated build-plan edits (matrix rows, MEU-79's 11 section, 06/gui-actions-index) written? | autonomous | After Session 30's execution review approves; the grouping writes only ungated homes (03/04/07/09) and the SSOT | Local Canon | Grouping §8 D-1 (carried). Session 30's `windows-gate-check` refuses any `GATED_PATHS` change after its gate, so editing them early would reopen its Windows gate; waiting costs one dangling anchor and a few days of missing matrix rows. | — |
| D-2 | grouping | Does `MCP-SETUP-PROMPT` join Session 31? | human | Yes, as MEU-71; Session 31 becomes P3 | Human-approved | Grouping §8 D-2 (carried). It shares `SettingsPage.tsx` and the Settings Electron wave with MEU-70, so one plan/review cycle instead of two; superseded in placement by D-55 once Session 31 ran without it. | USER_EXPLICIT 2026-10-09 'All recommendations accpeted as proposed' |
| D-3 | grouping | Are the tech-debt rows MEUs? | autonomous | No; a separate debt batch | Local Canon | Grouping §8 D-3 (carried; the reflection check reconciles every §8 row). Same rule as the 2026-09-30 grouping D-5 and `issue-triage.md` (TECH-DEBT to a debt batch); outside this session's scope. | — |
| D-4 | grouping | Session order | autonomous | 31, then P2 sessions 32, 33, 34, then P3 35, 36, then P4 37, 38, 39 | Local Canon | Grouping §8 D-4 (carried). Priority bands from the triage matrix; Session 31 keeps its queued slot, and shared files set 35 after 33 and 39 after 36. | — |
| D-5 | grouping | Keep TTS page work (MEU-75, MEU-79) out of the engine session? | autonomous | Yes, Session 35 after Session 33 | Local Canon | Grouping §8 D-5 (carried); outside this session's scope. MEU-77 edits the same `TTSPage.tsx`, so the page work lands once after both. | — |
| D-6 | grouping | Where does the independent MEU scoping review run? | human | Codex scoping review on the grouping draft (batches with 3+ MEUs), not during triage | Human-approved | Grouping §8 D-6 (carried). The review ledger needs an acceptance-criteria source, which exists only once MEUs and their build-plan homes exist. | USER_EXPLICIT 2026-10-09 'All recommendations accpeted as proposed' |
| D-7 | grouping | Repair the shared `status_labels` in `meu-status.yaml`? | autonomous | Yes: every row's labels rebuilt from its own status during registration | Local Canon | Grouping §8 D-7 (carried). One shared YAML anchor made approved and pending rows all read `ready_for_review`; the status field was right, only the labels were wrong, and `render --check` passes. | — |
| D-55 | grouping | Where does MEU-71 run, now that Session 31 executed without it? | human | Its own Session 31b (MEU-71 alone), next | Human-approved | Grouping §8 D-55. Folding it into a later session would tie a small UI MEU to unrelated work, and Session 32, the other candidate home, had already closed. | USER_EXPLICIT 2026-10-16 'accept all' |
| D-56 | grouping | Who makes the packaged `mcp-server` dependencies present and proves `MCP_ENTRY_PROBE` starts? | human | A new MEU-92 `dist-mcp-server-bundle` in Session 31b after MEU-71: an `esbuild` bundle shipped as `resources/mcp-server`, with `MCP_ENTRY_PROBE` on a built `win-unpacked` tree as a pass condition (plan Decision Brief option 1) | Human-approved | Grouping §8 D-56. Triage D-50 assumed MEU-72 kept this, but MEU-72 closed with it out of scope, so it had no owner; a pass condition on a built tree follows p7 RULE-1. | USER_EXPLICIT 2026-10-16 'Accept' (item 2 of "1. increase budget to 20M 2. Accept 3. approved as proposed") |
| D-71 | planning | Where is the prompt text built, and from what inputs? | autonomous | A pure `buildSetupPrompt` in `ui/src/main/mcp-setup-prompt.ts` with no token input, no I/O and no clock (`PROMPT_BUILDER`) | Local Canon | Golden tests need a deterministic function; building it in main keeps executable and app-data paths out of the renderer, and omitting the token from the signature makes the token boundary structural rather than a filter (plan D-71). | — |
| D-72 | planning | How does main know the server path in dev and packaged modes? | autonomous | `mcpServerEntry` returns `resources/mcp-server/index.mjs` packaged and `../../../mcp-server/dist/index.js` from `ui/out/main` in dev (`SERVER_ENTRY`) | Local Canon | Mirrors the `packagedBackendPath` helper, is testable without Electron, and keeps one switch for the MEU-92 file name (plan D-72). | — |
| D-73 | planning | Which Claude Code command form, and how are paths quoted? | autonomous | `claude mcp remove avkit --scope S`, then `claude mcp add` with `-e` env pairs and `--` before the double-quoted exe and server; a path with a double quote, `$` or backtick raises `PATH_QUOTE_ERROR` (`CLAUDE_CODE_BLOCK`) | Research-backed | Remove-then-add replaces any stale entry including the failed F8 local-scope one; without `--` the variadic `-e` would swallow the command; double quotes keep spaces and backslashes literal in PowerShell and bash, and the refused characters are the ones either shell expands (plan D-73, native research on the Claude Code MCP docs and CLI help). | — |
| D-74 | planning | Entry name and per-client shapes | autonomous | Key `avkit` everywhere; Codex TOML `[mcp_servers.avkit]` with an env table; Cursor, Claude Desktop, Windsurf and generic use `mcpServers`; VS Code uses `servers` with type stdio (`CODEX_BLOCK`, `JSON_BLOCKS`, `SERVER_KEY`) | Research-backed | One key lets the merge step say "only avkit", and a hyphen-free key avoids clients that normalise or reject hyphens in TOML bare keys (plan D-74, native research on each client's MCP docs). | — |
| D-75 | planning | How is scope shown for clients without a project file? | autonomous | `GridSelect` gains an optional disabled prop; scope is forced to user and disabled for claude-desktop, windsurf and generic (`SCOPE_DISABLED`) | Local Canon | Hiding the select would shift the layout per client; disabling keeps it stable, and the builder still throws on an invalid pair so the UI and IPC rules cannot drift silently (plan D-75). | — |
| D-76 | planning | How should the server decide it is the entry point? | autonomous | `isMainModule` compares `realpathSync.native` of argv[1] and of `import.meta.url`, case-insensitive on win32, false on any error (`ENTRY_GUARD`) | Research-backed | A suffix list breaks on every new layout (packaged, bundled, junctioned); real-path comparison is layout-free, and false on error keeps test imports from starting the server (plan D-76, Node docs on main-module resolution). | — |
| D-77 | planning | When does the gui-actions-index Copy prompt row land? | autonomous | In row 2, with its Red test, not at plan time (`INDEX_ROW`) | Local Canon | A plan-time row would turn main red under AC-23.20 until the channel exists; landing it with the Red keeps main green and the row still precedes the code, and the 07 Docs row is amended to say so (plan D-77). | — |
| D-78 | planning | 07 asks the MCP README to name the placement; which README? | autonomous | No MCP README exists; 05 `:329`, `mcp.json.example` and `SETUP_INSTRUCTION` carry it, and the 07 Docs row is amended | Local Canon | A new README would add a fourth place to keep in sync; the server instructions reach agents directly, which is where a placement hint helps (plan D-78). | — |
| D-79 | planning | What happens to `docs/distribution/mcp.json.example`? | autonomous | Rewrite it to the generic block with placeholders, key `avkit`, `ELECTRON_RUN_AS_NODE` and no token (`EXAMPLE_CONFIG`) | Local Canon | The old example contradicts the token boundary and the launch rule; leaving it would teach the shape this MEU removes (plan D-79). | — |
| D-80 | planning | How does the agent report failure codes? | autonomous | The verify step maps an error text starting with `code:` to `RESULT: failed (verify, code)` (`RESULT_LINE`) | Local Canon | The code is already the first token of every tool error (`toToolError`), so the agent copies it rather than paraphrasing (plan D-80). | — |
| D-81 | planning | Backup file name | autonomous | `file.avkit-backup-yyyyMMddTHHmmssZ` in UTC, chosen by the agent at run time (`BACKUP_NAME`) | Local Canon | A basic ISO timestamp sorts by name and has no characters Windows file names reject (plan D-81). | — |
| D-82 | planning | How is the launch shape proved without a packaged build in MEU-71? | autonomous | A ui Vitest spawns the repo's Electron binary with `ELECTRON_RUN_AS_NODE=1` on the dev server entry, plus a static `FUSE_PIN` on `electron-builder.yml` | Research-backed | The same binary family ships in the installer and the fuse pin catches the one config change that would break it; MEU-92's packaged probe then covers `av-kit.exe` itself (plan D-82, Electron env-var and fuses docs). | — |
| D-83 | planning | Bundle or ship node_modules, and in what format? | autonomous | esbuild 0.28.2 (exact), ESM, platform node, target node22, a `createRequire` banner, output `mcp-server/bundle/index.mjs`, run by tsx so it is typechecked (`BUNDLE_SCRIPT`) | Research-backed | One file with no install step is the smallest packaged surface; the banner gives inlined CommonJS dependencies a `require`, and Electron 42's Node runs node22-level ESM (plan D-83, esbuild API docs). | — |
| D-84 | planning | Is `MCP_ENTRY_PROBE` a record or a pass condition? | autonomous | A pass condition on a fresh `electron-builder --win dir` build, in place and on a hermetic copy (`PKG_PROBE`), bound to the hashes of the files it proved (`PKG_EVIDENCE`) | Local Canon | Session 32 only recorded the failure and no one owned it; the hermetic copy proves the bundle borrows no repository modules, and plan review round 1 F1 showed a bare passed flag could accept proof of changed bytes, so every consumer re-hashes the bound files (plan D-84). | — |
| D-85 | planning | How are licences of inlined dependencies shipped? | autonomous | `collectLicenses` reads the esbuild metafile and writes `LICENSES.txt` next to the bundle; a missing licence fails the build (`BUNDLE_LICENSES`) | Research-backed | Inlining drops the packages' own LICENSE files from the shipped tree, and driving it from the metafile covers transitive packages without a hand list (plan D-85, esbuild legal-comments docs). | — |
| D-86 | planning | How does the renderer get the prompt without the token crossing IPC? | autonomous | A strict `get-mcp-setup-prompt` channel whose handler builds the text from a `mcpServerLaunch` dependency and appData, never calling `readMcpToken` (`PROMPT_CHANNEL`, `PROMPT_HANDLER`, `LAUNCH_DEP`) | Local Canon | The prompt needs paths only main knows; returning text over a new channel keeps the token out of the renderer, and the spy test makes that checkable (plan D-86). | — |
| D-87 | planning | How does Copy prompt write the clipboard? | autonomous | The existing `writeClipboardText` with the viewer's text (`COPY_PROMPT`) | Local Canon | The text is already in the renderer for display; a second main-side copy channel would duplicate an existing one (plan D-87). | — |
| D-88 | planning | How is the entry guard proved on a packaged-like layout before MEU-92? | autonomous | An mcp-server test junctions `tmp/resources/mcp-server` to `mcp-server/dist` and runs node on `index.js` through it, with a fake backend and no token | Research-backed | It reproduces the packaged file name without a packaged build, is Red under the old guard, and also proves the liveness/dependencies split the prompt relies on (plan D-88, Node docs: a Windows junction needs no elevation). | — |
| D-89 | execution | What shape does av-kit's copy of the Zorivest files take? | autonomous | Copies under `_inspiration/zorivest/`, each the blob at a named Zorivest commit (never the working tree), with a `PROVENANCE.md` row of source path, commit, date, git blob id and LF sha256; AC-41.3 reads the copy with its assertions unchanged | Local Canon | Precedent (the committed MCP audit skill copy) and research converge on a committed snapshot with recorded provenance; two-way, invisible to users and sets no threshold, so no ruling needed (plan and MEU-71 handoff D-89, Amendment A-1). | — |
| D-90 | execution | Which version of Zorivest's `globals.css` becomes av-kit's copy? | human | `61243baf`, the commit before Zorivest MEU-662: it holds exactly the hexes av-kit ships, so decoupling changes nothing visible | Human-approved | The pill hue colours only the icon and a 10% fill, and `#ea580c` (about 3.56:1) and `#16a34a` (about 3.30:1) on white clear WCAG 1.4.11, so the darker MEU-662 palette fixes no failing criterion; adopting it later is an ordinary av-kit change. | USER_EXPLICIT 2026-10-17 'D-90 61243baf, D-91 A, D-92 A-1' |
| D-91 | execution | How far does "decouple anything to do with zorivest" go? | human | A: remove every dependency and keep the history; AC-41.3 reads the copy, the four canon pointers make av-kit the owner with Zorivest as provenance only, AC-41.3 leaves `ENV_BOUND_TESTS`, `QUEUE-PILL-TOKEN-DRIFT` closes, and closed plans, handoffs, reflections and decision records stay untouched | Human-approved | Fixing only the test would leave the canon pointing at whatever the Zorivest checkout declares, so the next Zorivest change would recouple av-kit; a full scrub would copy dozens of source files and erase where patterns came from. | USER_EXPLICIT 2026-10-17 'D-90 61243baf, D-91 A, D-92 A-1' |
| D-92 | execution | How does the decoupling reach main? | human | Amendment A-1 in Session 31b: a new row 0a before the baseline, reviewed by H1-7, proposed at closeout as its own commit ahead of the MEU-71/92 commit; Session 35 picks it up when it merges main | Human-approved | A separate mini-session would block 31b for a full plan-and-review cycle on a small change, and carrying AC-41.3 as a baseline failure again would defer what Mat asked for and weaken the gate. | USER_EXPLICIT 2026-10-17 'D-90 61243baf, D-91 A, D-92 A-1' |
| D-93 | execution | The fresh worktree lacked the gitignored region-picker stub, so four capture-picker specs failed in the S8 evidence run; does the plan build it? | autonomous | baseline and gate run `npm --prefix ui run build:picker-stub` before the Electron suite (`Invoke-PickerStub`, `gate-picker-stub`) | Local Canon | The repo's own script writes only ignored output; without the stage the baseline and gate depend on whatever an earlier session left in the native publish folders (Session 36 RULE-1, Session 39 G-1 precedent). | — |
| D-94 | execution | gate71 run 1 failed 1 of 10 AC-71.15 repeats because a Windows clipboard listener held the lock and the copy was dropped silently (stop S8); how is the test fixed? | human | A: in both AC-71.15 tests the click and the clipboard read run inside `expect(...).toPass` with a 10 s timeout, so a dropped copy is clicked again; assertions unchanged, and test 2's retry also treats an empty read as a lost race | Human-approved | A repeated click is a real product write, so retrying replaces a write the OS dropped without weakening the oracle, and a broken Copy prompt still times out; dropping the sentinel, an in-app read-back retry, or re-running unchanged each lost (blind test 2, out-of-plan channel change, a 1-in-20 failure in every later gate). | USER_EXPLICIT 2026-10-17 'A' |
| D-95 | execution | Row 3's green71-main runs `example-config.test.ts` (AC-71.11), but the plan assigns `EXAMPLE_CONFIG` to row 4; where is the example written? | autonomous | Write `docs/distribution/mcp.json.example` to the `EXAMPLE_CONFIG` shape in row 3 and leave it unchanged in row 4 | Local Canon | Row 3 could not go green with the old example; the file is documentation with no runtime reader, so moving it a row earlier changes no behaviour, while editing the gate's test set would weaken row 3's check (MEU-71 handoff). | — |
| D-96 | execution | Does the renderer import the `CLIENT_SET` labels from `src/main/mcp-setup-prompt.ts`? | autonomous | The renderer keeps its own `MCP_CLIENT_OPTIONS` copy; AC-71.13 pins the renderer list and AC-71.1 the main list, both against `CLIENT_SET` | Local Canon | Importing main code would pull `node:path` into the sandboxed renderer bundle, and a new shared module is outside `PRODUCT_SCOPE`; two pinned copies cannot drift without a test failing (MEU-71 handoff). | — |
| D-97 | execution | pkg-probe run 1 could not launch `ui/dist/win-unpacked/av-kit.exe` (FileNotFoundError, WinError 2) although it exists; is the probe harness repaired in place? | autonomous | `plan_checks.py mcp_probe` launches the resolved absolute path of argv[0]; the existence check, initialize request, 10 s deadline and `probe_passed` are unchanged, and pkg-probe re-runs from the start | Local Canon | A direct check showed CreateProcess rejecting the relative forward-slash path while the absolute path runs `av-kit.exe` in node mode; the fix changes how the probe starts the process, not what it requires, so it cannot turn a failing entry green (MEU-92 handoff; D-93 and AGENTS.md:57 precedent). | — |
| D-98 | execution | AC-92.2 needs the real build's metafile, but the shipped `bundle/` holds only `index.mjs` and `LICENSES.txt`; where does the test get it? | autonomous | `bundle.ts` exports `BUNDLE_OPTIONS` and runs only as the main module; the test rebuilds with those options and `write: false`, derives package names from that metafile with its own regex, and checks `LICENSES.txt` for a heading per package | Local Canon | Writing the metafile into `bundle/` would ship it and a second output folder adds an artifact to keep in step; rebuilding from the exported options reads the same inputs, and independent name derivation keeps `collectLicenses` from being its own oracle (MEU-92 handoff). | — |
| D-99 | execution | Execution review round 2 was refused on tokens (round 1 used 11,498,809 of a 21M budget and the reserve rule needs as much again); how large is the review budget? | human | A total execution-review budget of 50M (29M added through the ledger's `continue`) | Human-approved | Round 2 is a recheck of two fixes, but the ledger reserves one round's actual cost; stopping the loop would leave the blocking F1 fix unreviewed, and a smaller raise could refuse round 3 the same way (MEU-71 handoff D-99; walkthrough §Execution review round 1). | USER_EXPLICIT 2026-10-17 'Approved: raise the execution review budget to 50M total.' |

The H2-1 row and the grouping's carry-forward line name grouping D-1, D-2, D-6, D-7, D-55 and D-56. D-3, D-4 and D-5 are carried as well, as in Sessions 36 and 39, because the reflection check reconciles every §8 row of the grouping. D-89 to D-93 appear in both the plan (amendment A-1) and the MEU-71 handoff, with stage `execution` in both. D-94 to D-99 are handoff records; D-99 (the round-2 token budget) is the MEU-71 handoff's last record, and `walkthrough.md` §Execution review round 1 quotes Mat's words. The triage decisions on `MCP-SETUP-PROMPT` and `MCP-PACKAGED-ENTRY-UNREACHABLE` belong to the triage record and are cited here in prose only.

---

## Pattern Extraction

### Patterns to KEEP
1. **Make the token boundary structural.** `buildSetupPrompt` takes no token, and the IPC handler never calls `readMcpToken`. The spy test checks absence, rather than filtering output.
2. **Prove the packaged entry on a hermetic copy, bound to file hashes.** `PKG_PROBE` runs `av-kit.exe` in place and on a copy with no `node_modules` above it. `PKG_EVIDENCE` refuses the proof once any of the 10 bound files changes.
3. **Stop at S8 with a Decision Brief instead of editing a test.** This happened three times: AC-41.3, the AC-71.15 clipboard race and the token budget. Each was resolved by Mat's own words.
4. **Have a human run the prompt in a real client.** Mat's Claude Desktop run (`RESULT: connected`) exercised the whole prompt the way a user would, which no unit test does.

### Patterns to DROP
1. **Tests that read another repository's working tree.** AC-41.3 failed on `main` because Zorivest moved. A committed snapshot with a `PROVENANCE.md` row (D-89) replaces it.

### Patterns to ADD
1. **Instruction steps that choose between files name "the file chosen in step N" afterwards, never a fixed path.** F1 came from a fixed backup path after a conditional choice.
2. **Size the execution-review budget at ledger `begin` from this kind of plan's actual round cost.** Here, 21M left no room for a recheck after an 11.5M round.
3. **Plan-local static checks read decision IDs from every decision source the closeout validator reads.** That means the plan and the handoffs (F2).

### Calibration Adjustment
- **Estimated time:** one planning session plus one execution session for one UI MEU and one packaging MEU.
- **Actual time:** planned and reviewed (three rounds) on 2026-10-16; executed on 2026-10-17, with a same-day amendment (A-1) inserted before the baseline.
- **Repeated runs:** gate71 2 runs, green92 2, pkg-probe 2, the session gate 2 (H1-2, then after F1). Execution review took two ledger rounds (15.3M tokens), after two dispatch attempts that the dispatcher refused before Codex started.
- **Adjusted estimate for similar MEUs:** add one amendment-sized slot whenever a test reads outside the repository, and one execution recheck round to the budget.

---

## Next Session Design Rules

```
RULE-1: No test reads another repository's working tree; an external provenance check reads a committed snapshot with its source commit and hash recorded.
SOURCE: Session 31b row 0: AC-41.3 read P:/zorivest/ui/src/renderer/src/globals.css live and failed on main when Zorivest MEU-662 landed (D-89 to D-91).
EXAMPLE: queue-canon.test.ts PILL_TOKEN_SOURCE = 'P:/zorivest/ui/...' → '_inspiration/zorivest/ui/src/renderer/src/globals.css' plus a PROVENANCE.md row (commit 61243baf, blob id, LF sha256).
```

```
RULE-2: A worktree session's execution-review dispatch works on the first attempt: the prompt is staged under C:/Temp/av-kit/dispatch, the dispatcher starts in P:/av-kit, and the prompt names the worktree as the only place the work exists. The ledger budget at begin covers at least two rounds at the plan's expected round cost.
SOURCE: Session 31b H1-7: two dispatch attempts were refused on the repository-root check, and round 2 was refused on tokens (D-99).
EXAMPLE: exec_dispatch.ps1 -Round N copies the prompt to C:/Temp/av-kit/dispatch/<id>-r<N>-prompt.txt, then runs Set-Location P:/av-kit; review_ledger.py begin --tokens 50000000 for a two-MEU session with a packaged build.
```

```
RULE-3: Carry Session 39 RULE-2 into every review prompt: on approved, every checklist_results[].result is pass or n/a.
SOURCE: Session 31b's two execution-review prompts omitted it (Workflow log Q4).
EXAMPLE: prompt Output B gains "On approved, every checklist_results[].result is pass or n/a; a partial row means changes_required with a blocking finding."
```

---

## Next Day Outline

1. **Commit and merge (Mat).** Two commits are proposed, with no AI attribution trailer:
   - the A-1 decoupling first (the `_inspiration/zorivest/` copy, AC-41.3 and the canon pointers);
   - then MEU-71 and MEU-92.

   Nothing is committed or pushed. Session 35 picks up A-1 when it merges `main`.
2. **Mat's Claude Desktop entry still points at this worktree's `mcp-server/dist/index.js`.** Re-run the setup prompt from the installed app once a packaged build ships, so the entry names `resources/mcp-server/index.mjs`.
3. **Follow-ups to file through `/issue-triage`:**
   - Teach `Invoke-CodexDispatch.ps1` to accept a registered worktree root.
   - The MCP_PROMPT_LOOK L5 step was not run.
   - Adopting Zorivest MEU-662's darker light palette is optional and needs its own MEU.
4. **Bake in RULE-1 to RULE-3.**
5. **Next session per the grouping order (D-4).**

---

## Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total tool calls | not tracked precisely (several hundred across planning and execution) |
| Time to first green test | 2026-10-17 (row 3, `green71-main`, first product run) |
| Tests added | ui Vitest 975 → 1007 (+32). mcp-server Vitest 428 → 446 (+18). Electron 157 → 159 (+2, AC-71.15). Plus the packaged `MCP_ENTRY_PROBE` (in place and hermetic). |
| Codex findings | Plan review (Codex `gpt-6.1-sol`): R1 `changes_required` (1 High, F1); R2 `changes_required` (PR-6 procedural, no new finding); R3 approved, 0 open. Execution review: R1 `changes_required` (F1 High, blocking; F2 Low). R2 approved, 0 open, `intent_achieved: yes`. |
| Handoff Score (X/7) | 7/7 (all plan ACs present; both execution findings fixed, none open) |
| Rule Adherence (%) | 85 |
| Prompt→commit time | 2026-10-16 → 2026-10-17 (review approval; commit pending the human) |

### Rules Sampled for Adherence Check

| Rule | Source | Followed? |
|------|--------|-----------|
| Tests before production code; Red before Green | AGENTS.md §Testing & TDD | Yes. Rows 2 and 6 were Red with `vitest-red` attribution before any product change, and the F1 fix had a failing test first (`s31b-f1-red.txt`) |
| No test expectation change without approval | AGENTS.md §Testing & TDD | Yes. The AC-71.15 retry was Mat's D-94 A, with the assertions unchanged. The `claude-desktop-user.txt` golden changed only as part of the blocking F1 fix the reviewer required |
| Independent review; no self-approval | AGENTS.md §Dual-Agent Workflow | Yes. Codex reviewed the plan (three rounds) and the execution; no verdict was set by the author |
| Product scope limited to the Files table | Plan `PRODUCT_SCOPE` | Yes. `-Check scope` reported 78 changed paths, none outside scope |
| Apply the previous session's design rules | Session 39 reflection RULE-1, RULE-2 | Partly. `validate-task.ps1` sets `RECEIPTS_DIR` itself (RULE-1). The review prompts omit the approval coupling (RULE-2) |

---

## Instruction Coverage

```yaml
schema: v1
session:
  id: "session-31b-gui-mcp-setup-prompt-2026-10-17"
  task_class: tdd
  outcome: success
sections:
  - {id: priority_0_system_constraints_non_negotiable, cited: true, influence: 3}
  - {id: planning_contract, cited: true, influence: 2}
  - {id: testing_tdd_protocol, cited: true, influence: 3}
  - {id: execution_contract, cited: true, influence: 3}
  - {id: session_discipline, cited: true, influence: 2}
  - {id: dual_agent_workflow, cited: true, influence: 3}
  - {id: rtk_token_optimized_commands, cited: true, influence: 1}
  - {id: instruction_coverage_reflection, cited: true, influence: 2}
loaded:
  workflows: [create_plan, plan_corrections, execution_session, tdd_implementation, execution_critical_review]
  roles: [orchestrator, coder, tester]
  skills: [timestamp]
  refs:
    - .agent/docs/harness-profiles.md
    - .agent/context/harness.local.md
    - .agent/docs/human-decision-protocol.md
    - .agent/schemas/reflection.v1.yaml
    - .agent/schemas/review-verdict.schema.v2.json
    - docs/build-plan/05-mcp-server.md
    - docs/build-plan/06-gui.md
    - docs/build-plan/07-distribution.md
    - .agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md
    - docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/implementation-plan.md
    - docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/task.md
decisive_rules:
  - P1:tests-before-production-code
  - P1:human-approval-for-test-changes
  - P1:independent-review-no-self-approval
  - P1:baseline-failures-are-not-regressions
  - P0:never-commit-or-push-without-human-approval
conflicts:
  - "H2-1 and the grouping carry-forward line name six grouping decisions and plan D-71 to D-93; the closeout validator reconciles every grouping §8 row and every handoff decision record. Resolved by following the validator (D-3, D-4, D-5 and D-94 to D-99 carried)."
  - "The harness asked for a Co-Authored-By trailer on commits; the user's rule forbids AI attribution trailers, so the commit drafts have none."
  - "A connected docs server asked for docs to be created there; the user's rule keeps deliverables as local repo files."
  - "The ledger's 20-character --said floor refused Mat's short budget replies; Claude may not compose consent text, so Mat was asked for a sentence (D-99)."
note: "S31b ships the per-client MCP setup prompt (no token in any block, real-path entry guard) and the esbuild mcp-server bundle proved by MCP_ENTRY_PROBE on win-unpacked; amendment A-1 decoupled AC-41.3 from Zorivest's working tree. Plan review approved r3; execution review approved r2 after r1 F1 (High) and F2 (Low) were fixed test-first."
slim_candidate: ["The H1-2 gate record repeated in both handoffs, already in walkthrough.md and gate-result.json"]
overthinking_observed: false
review_churn:
  rounds_to_approval: {plan: 3, execution: 2}
  findings_per_round:
    - {review: plan, round: 1, critical: 0, high: 1, medium: 0, low: 0}
    - {review: plan, round: 2, critical: 0, high: 0, medium: 0, low: 0}
    - {review: plan, round: 3, critical: 0, high: 0, medium: 0, low: 0}
    - {review: execution, round: 1, critical: 0, high: 1, medium: 0, low: 1}
    - {review: execution, round: 2, critical: 0, high: 0, medium: 0, low: 0}
  churned_findings: 3
  finding_categories: {weak_test: 1, contract_drift: 1, other: 1}
  verdicts: {changes_required: 3, approved: 2}
meu_work_classes: [correctness, mixed]
```
