# Human gate decisions (execution)

Execution-time decisions that `.agent/docs/human-decision-protocol.md` routes to Mat. A brief here authorizes nothing until Mat's ruling is recorded under it.

## D-175: gate attempt 2 fails on an uncensused builder pin from `7706fcd`   [externally-blocked] [execution]

**Recommendation:** census the pin. Add one `routing-census.md` match entry for `.cursor/agents/av-kit-builder.md` line 4, a copy of the verifier's entry for the same line, and put it in the commit draft as its own `chore(registry)` commit ahead of the Session 43 commit. This is how the project handled the last pin change: the 2026-10-02 flatten-backup A-14 updated the census line hashes as a follow-on of the pin change, with classification and reason unchanged. It also keeps the fix explained by the change that caused it, and leaves the capture commit capture-only.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ Census the builder pin (one entry, split commit) | — | — | `docs/execution/plans/2026-10-02-capture-flatten-backup/human-gate-decision.md:273`; `docs/execution/plans/2026-09-30-tts-repair/human-gate-decision.md` A-2; tessl golden-file conventions |
| ⚠️ Mat or the registry-sync owner fixes it in a new commit | The fix lands beside `7706fcd` with no help from this session, and S43's tree stays free of another plan's file | Mat does the work, and HEAD moves again, so the gate needs an EC-8 that accepts a second commit | flatten-backup A-14 ("in the same commit") |
| ❌ Excuse the two test ids in the gate | No file outside S43 changes | A deterministic regression passes the gate unfixed. The `ui-tests` rule already shows the plan's stance: no excused failures beyond the row 0 baseline set. Practice says a test that fails on every run after a change is a regression to fix, not one to quarantine | tessl flaky-test-quarantine; Kafka KIP-1090 |
| ❌ Hold S43 (status quo) | Nothing changes | Rows 8, 9 and H1–H2 stay blocked on a one-line census gap | — |

**What the entry is.** Built with the checker's own rule (`verify_adoption.py:250-300`), the scan finds exactly one uncensused line: `.cursor/agents/av-kit-builder.md:4 model: composer-2.5-fast`, sha256 `a559daa5bcd0de6ff8fce7244c5acb39be5fa092f57a4f6adc3c782451915bb7`. The census already holds that hash for `.cursor/agents/av-kit-verifier.md` line 4 (`routing-census.md:2160-2164`, classification `loader`, reason "Preserved runtime loader field; local class/provenance stamp outside frontmatter."). The new entry carries the same fields with the builder's path. The builder's old entry (`83203330…`, `cursor-grok-4.6-xhigh`, `:2125-2129`) now matches nothing. Its removal is not needed for the tests and is left out (the narrowest diff). The census file's manifest `postimage_sha256` (`aaeb5614…`) already differs from the file (`3783ff20…`), and the tests passed at baseline, so the adoption verifier does not bind that hash on the live tree.

**Precedent:**
- 2026-10-02 flatten-backup A-14 (`USER_EXPLICIT`): a pin change updated the census hashes in the same commit, with classification unchanged. This applies directly.
- 2026-09-30 TTS repair A-2 (`USER_EXPLICIT`, "Rebind records (Recommended)"): stale adoption records rebound field by field, "stop and report if any other oracle fails". This applies by analogy.
- `TOOLING-SHARED-REGISTRY-COUPLING` (open, P2): the same test file breaks after every shared-registry change. This is its fourth recurrence.

**Research:** native `WebSearch`.
- Practice: [tessl golden-file conventions](https://tessl.io/registry/testland/golden-file-conventions/files) updates the expected output in the change that explains it, never in a separate refresh. [Lock the golden files](https://dev.to/codego_3211/lock-the-golden-files-split-agent-diffs-that-touch-the-answers-39db) says an agent must not rewrite its own oracle unreviewed: split the diff and have the human own the lock.
- Practice: [gitbot-fleet #458](https://github.com/hyperpolymath/gitbot-fleet/pull/458) treats widening an allowlist as an owner sign-off, not a test fix.
- Quarantine: [tessl flaky-test-quarantine](https://tessl.io/registry/testland/flaky-test-quarantine) says a test that fails every time after a change is a regression, so bisect and fix it rather than quarantine it. [KIP-1090](https://cwiki.apache.org/confluence/display/KAFKA/KIP-1090+Flaky+Test+Management) warns that making exclusions easy lets real failures be ignored.

**Reversibility / risk:** two-way. A wrong entry would only let one loader line through the census, and that line's hash is already accepted for the sibling file. The split commit lets Mat review or drop it alone. If any other `tests/tooling` REFUSE appears after the edit, the session stops and reports it; nothing else gets edited.

**If you do not answer:** S43 stays paused at row 8.

**What the recommendation would authorize:**
1. One appended `matches` entry in `docs/execution/plans/2026-09-26-framework-update-adoption/routing-census.md`.
2. That path added to S43's `scope-paths` allow-list and the Files Modified table (EC-8).
3. Rerun the two tests, then the full gate (`s43-gate.txt`).
4. A two-commit draft at H2.

It does not authorize: any other census field, `verify_adoption.py`, `tests/`, `adoption-manifest.json`, the agent files, `P:/.agent`, or any commit.

**Decision (D-175).** Source: `USER_EXPLICIT`, 2026-11-03, Claude Code (VS Code) chat. Mat wrote:

> D-175 census

This takes the recommendation and authorizes exactly the four items listed above it. **D-175 execution note.** The entry is appended as the last `matches` element (+7 lines, CRLF kept). The census's prose table still shows the old `cursor-grok-4.6-xhigh` text for the builder's line 4: the checker does not read it, and the ruling covers only the entry. The two tests rerun alone gave `10 passed` (`s43-175-adoption.txt`).

## D-176: Node 26 breaks the UI unit suite's storage; where to fix it   [source-conflict] [execution]

*Revised 2026-11-03. Mat sent the first brief (a flag on the gate step only) back for a review of what Node 26 changes, with HDP. This brief replaces it.*

**Recommendation:** fix it in the suite, not the gate. Add one worker flag to `ui/vitest.config.ts`, `test.poolOptions.forks.execArgv: ['--no-experimental-webstorage']`, with a comment saying why and that Vitest 5 makes it unnecessary. Ship it as its own `chore(test)` commit ahead of the S43 commit, as D-175 did. The review below finds this is the only change Node 26 needs in av-kit. Fixing it in the suite repairs `npm --prefix ui run test` for every session on this machine, not only S43's gate, and it keeps the gate running the PROFILE D6 command as written. The flag is accepted by Node 24 and Node 26 alike.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ Worker flag in `ui/vitest.config.ts`, own commit | — | — | vitest#10867; who2be #1028; cowork-genealogy #4197; Session 26 A17 |
| ⚠️ Flag on the gate's `ui-tests` step only (the first brief) | S43's diff stays inside its plan folder | `npm run test` stays broken for every other session and the other worktree; the gate no longer runs the D6 command as written; the next plan finds the same failure | `.agent/docs/commands.md:201` |
| ⚠️ Mat reinstalls Node 24 and pins it (`winget pin`) | No repo change, and the dev Node then matches Electron 42's bundled Node 24 | A machine change outside the repo; the suite still breaks for anyone on Node 25+; Node 24 leaves LTS support in April 2028, so this only postpones the fix | Electron 42 release notes |
| ❌ Upgrade Vitest to 5 now (the upstream fix) | Fixes the cause, with no flag | Two major versions (3.2.7 → 5.1.0) with breaking config changes (`poolOptions` was removed in v4) across 107 test files: its own MEU, not a gate repair | vitest#10867 |

Excusing the 34 tests is not an option, for the reason in D-175.

**What Node 26 changes for av-kit (review, 2026-11-03)**

| Area | Runs on | Node 26 effect | Evidence |
|---|---|---|---|
| UI unit suite (Vitest 3.2.7 + jsdom 25, `environment: 'node'` plus a per-file jsdom directive) | system Node | **Breaks.** Node 26.0.0's semver-major "return undefined for localStorage without file" makes `globalThis.localStorage` a getter that returns `undefined`, and Vitest 3's jsdom environment does not replace Node's globals. 34 tests throw in `localStorage.clear()`/`getItem()`. Others pass by taking the product's `catch` or memory fallback (`usePersistedState.ts:37-40`, `HelpCard.tsx:24-41`, `theme.ts:40-71`), so they quietly stop testing persistence. `sessionStorage` still works, but it is Node's in-process store, not jsdom's. | `s43-D6-ui-tests.txt`; Node 26.0.0 notes |
| UI unit suite with the flag | system Node | Passes. Through `NODE_OPTIONS`: `1 failed \| 1105 passed`, the failure being AC-80.8 (D-177, since amended), then `1106 passed` after TA-3. Through the recommended config key (a scratchpad config that spreads the real one and adds the array): the five storage files `61 passed` twice, the full suite `1106 passed`. The first config run had five 5 s timeouts in files that don't touch storage, while the machine's CPU sat at 79% (transform 53 s against 5 s). The next pair of runs, both routes back to back, passed `1106` each. The CLI form `--poolOptions.forks.execArgv=<flag>` hangs Vitest 3.2.7 before any test runs (it passes a string, not an array), so the key goes in the config file. | `s43-ui-nowebstorage.txt`, `s43-176-env-full2.txt`, `s43-176-cfg-five-{1,2}.txt`, `s43-176-cfg-full.txt`, `s43-176-cfg-full2.txt`, `s43-176-execargv.txt` |
| mcp-server build and suite (`environment: "node"`, no storage) | system Node | None: `446 passed` without the flag. | `s43-mcp-node26.txt` |
| `ui-build`, `ui-harness-build`, `ui-picker-stub` (electron-vite 5, Vite 7) | system Node | None: all exit 0. | `s43-n26-ui-build.txt`, `s43-n26-ui-harness-build.txt`, `s43-n26-ui-picker-stub.txt` |
| Electron suite (Playwright runner) | system Node for the runner; the app runs on Electron's Node | None found. The full run on Node 26 gave `6 failed | 175 passed` (21.0 min). AC-81.11 (`capture-inbox.test.ts:1930`) fails because ShareX holds F2, which is in the §Baseline set and was seen in S40. The other five (`launch.test.ts:41`, `settings.test.ts:187`, `:246`, `:359`, `tts-generate.test.ts:804`) are load timeouts and pass when run alone (`5 passed`, `s43-n26-e2e-rerun.txt`). The unit-suite flag does not reach this step. | `s43-n26-ui-electron.txt` |
| The app, and the MCP server it launches | Electron 42's bundled Node (`v24.18.1`; `ELECTRON_RUN_AS_NODE=1` in `mcp-setup-prompt.ts:59`) | None: system Node is not used at runtime. Electron's Node 24 accepts the flag and has no `localStorage` global. | `electron -e process.version` probe |
| Removed or deprecated Node APIs in our code (`url.parse`, `new Buffer`, `util.is*`, `punycode`, `process.binding`, `createCipher`, `fs.exists`, `module.parent`, `dirent.path`) | — | None: no hits in `ui/src`, `ui/tests`, `ui/scripts`, `mcp-server/src`, `mcp-server/tests` or `mcp-server/scripts`. | `rg` sweep |
| Version pins (`engines`, `.nvmrc`, CI workflows) | — | None exist, so nothing to update. `@types/node` `^22` only types the APIs and still matches. | `ui/package.json`, `mcp-server/package.json` |

**Why it passed at baseline.** WinGet installed `OpenJS.NodeJS.LTS 26.13.0` on 2026-11-01 22:58 (Windows Installer log). The row 0 baseline ran on 2026-10-29, and earlier sessions record `node v24.19.0` (`2026-10-14-capture-filmstrip-actions/walkthrough.md:186`, `2026-09-28-p11-capture-settings/walkthrough.md:152`). Node 24 keeps web storage behind a flag, so jsdom's storage was the only one. `node.exe`'s file date (10-28) is the build date, not the install date.

**Precedent:**
- Session 26 A17 (`USER_EXPLICIT`, `2026-09-28-p11-capture-settings/walkthrough.md:224-229`): environment drift outside av-kit got the narrowest fix at its cause, and the coupling was filed. This applies by analogy.
- D-175 (`USER_EXPLICIT`, above): a fix outside S43's product scope ships as its own commit ahead of the S43 commit. This applies directly to the commit shape.
- `E2E-ELECTRON-LAUNCH-FLAG` (`known-issues.yaml:19`): a shell variable was worked around per command, and its blast radius kept growing (`npm run dev` was later found to be hit as well). Cautionary: per-command workarounds don't stay contained.
- Node 22.22 to 24.19 (September; `2026-09-28-p11-capture-settings/walkthrough.md:14,152`): a Node major moved with no repo change. It doesn't apply: Node 24 left web storage flagged.
- Receipt `s43-hdp-176-sweep.txt`.

**Research:** native `WebSearch` and `WebFetch`.
- [vitest#10867](https://github.com/vitest-dev/vitest/issues/10867), closed "not planned" 2026-08-05: the maintainer says it is "fixed in Vitest 5. It can't be backported because it requires a breaking change". The reporter's workaround is the worker flag. [vitest#8757](https://github.com/vitest-dev/vitest/issues/8757) was closed earlier as a Node 25 (non-LTS) problem.
- [Node.js 26.0.0 release notes](https://nodejs.org/en/blog/release/v26.0.0): SEMVER-MAJOR "lib: return undefined for localStorage without file".
- In the wild: [who2be #1028](https://github.com/luetzey/who2be/pull/1028) and [cowork-genealogy #4197](https://github.com/PioneerAIAcademy/cowork-genealogy/pull/4197) add the worker flag in the Vitest config. [SignalK #3186](https://github.com/SignalK/signalk-server/pull/3186) and [player1inventory #353](https://github.com/ETBlue/player1inventory/pull/353) restore jsdom's storage in a setup file instead.
- [Electron 42 release notes](https://electronjs.org/blog/electron-42-0): Electron bundles Node 24, so the app's runtime is not on Node 26.

**Obviousness test (§4):** it fails test 1. The sources agree on the cause, but where to fix it is a conflict between the plan's scope (S5: no path outside `PRODUCT_SCOPE`) and fixing the problem where it lives. Widening scope is Mat's call, as in D-175.

**Reversibility / risk:** two-way. The flag only removes a global the suite never had on Node 24. If it hid a real storage defect, that defect also passed at baseline. Removing the line undoes it. Risk: a future Vitest 4+ upgrade must move or drop the key; the config comment says so. Unrelated to the flag: the unit suite times out under heavy load (above), so if attempt 4 shows timeouts with no other failure, the next step is to rerun on a quieter machine, not to change anything.

**Also needed for attempt 4 (not part of this decision):** ShareX holds F2, so AC-81.11 (`capture-inbox.test.ts:1930`) fails every run. The S40 precedent is that Mat closes ShareX and the gate reruns unchanged.

**If you do not answer:** S43 stays paused at row 8.

**What the recommendation would authorize:**
1. One `poolOptions.forks.execArgv` entry in `ui/vitest.config.ts`, with its comment.
2. That path added to the `scope-paths` allow-list and the Files Modified table (EC-9).
3. The handoffs and the reflection record the Node 24 to 26 change and the Vitest 5 follow-up.
4. Rerun the UI suite, then the full gate (attempt 4).
5. A three-commit draft at H2: `chore(registry)` (D-175), `chore(test)` (D-176), then the S43 commit.

It does not authorize: `session-gate.ps1`'s step commands, `ui/tests/unit/setup.ts`, any dependency change, `known-issues.yaml`, any Node install change, or any commit.

**Decision (D-176).** Source: `USER_EXPLICIT`, 2026-11-03, Claude Code (VS Code) chat. Mat wrote:

> D-176: recommendation accepted
> ShareX is closed now

This takes the recommendation and authorizes exactly the five items listed above it. **D-176 execution note.** `ui/vitest.config.ts` gains the `poolOptions.forks.execArgv` entry and its comment after `setupFiles`; nothing else in the file changes. The allow-list, the §Hub and state files table and EC-9 change together. Mat closed ShareX in the same message (S40 precedent), so gate attempt 4 runs with F2 free.

## D-177: `icon-hints.test.ts` AC-80.8 expects the old `Undo`/`Redo` hint text (census miss, S2)   [governance-value] [execution]

**Recommendation:** amend it as TA-3, the same way TA-2 amended AC-65.2: declare `HINT_OVERRIDE = { 'capture-undo': 'Undo (Ctrl+Z)', 'capture-redo': 'Redo (Ctrl+Y)' }` in `icon-hints.test.ts` and compare the hint text against `HINT_OVERRIDE[id] ?? spec.name` in AC-80.8's two loops. MEU-99's `HISTORY_HINTS` (Mat's synthesis D-1, plan AC-99.6) made this change on purpose; AC-80.8 asserts the same thing TA-2 already amended in another file. The row 1 census listed `icon-hints` only for its `endsWith` hits and missed this assertion, so under S2 it needs your ruling before any test edit.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ TA-3: `HINT_OVERRIDE` in AC-80.8 (3 lines) | — | — | plan TA-2 (`implementation-plan.md:141`) |
| ⚠️ Change `expectHinted` to read the hint from `TOOLBAR_BUTTONS` plus a shortcut table | One source of truth for the hints | A wider test-helper change than the amendment needs; AC-80.9 shares the helper | — |
| ❌ Drop the shortcut from the hints | No test edit | Undoes AC-99.6, TA-1 and TA-2 and the D-1 ruling; the chords become undiscoverable | synthesis D-1 |
| ❌ Excuse AC-80.8 | No file changes | A deterministic failure passes unfixed (D-175) | D-175 |

**What fails.** `AssertionError: shot open: capture-undo-hint text: expected 'Undo (Ctrl+Z)' to be 'Undo'` (`icon-hints.test.ts:297`, via the AC-80.8 loop at `:310-327`). The no-shot loop compares to the same `spec.name` for Undo and Redo, which are not in `NO_SHOT_IDS`. The `aria-label` and `title` checks are not affected.

**Precedent:** the plan's own TA-1 and TA-2 (`USER_EXPLICIT` plan approval, 2026-10-29): the same hint change, amended in the lines it names. This applies directly; only the file is new.

**Research:** not needed; this is the plan's own rule (S2) applied to a census miss.

**Reversibility / risk:** two-way; a test-only change scoped to two ids. It also needs `ui/tests/unit/icon-hints.test.ts` in the `scope-paths` allow-list and Files Modified (EC-10), and a §Census row correcting the disposition.

**If you do not answer:** S43 stays paused at row 8.

**What the recommendation would authorize:**
1. TA-3 in `ui/tests/unit/icon-hints.test.ts`: the `HINT_OVERRIDE` constant and the two `expected` expressions in AC-80.8; nothing else in the file.
2. That path added to the `scope-paths` allow-list and the MEU-99 Files Modified table (EC-10), and a corrected §Census row.
3. Rerun the file, then the full gate (attempt 4), together with D-176.

It does not authorize: any other test, `expectHinted`, product code, or any commit.

**Decision (D-177).** Source: `USER_EXPLICIT`, 2026-11-03, Claude Code (VS Code) chat. Mat wrote:

> D-177: recommendation accepted

This takes the recommendation and authorizes exactly the three items listed above it. **D-177 execution note.** TA-3 adds `HINT_OVERRIDE` after `NO_SHOT_IDS` and changes the two `expected` expressions in AC-80.8; `expectHinted` and every other test are unchanged. The allow-list, the MEU-99 Files Modified table, the §Census row and EC-10 change together. The same message asked for a new D-176 brief after a Node 26 review, so D-176 has no ruling yet.
