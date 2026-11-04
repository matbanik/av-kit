# Walkthrough — 2026-10-01-mcp-live-audit (Session 28, MEU-68)

Execution record. Raw receipts live in `$RECEIPTS_DIR` (container: the session scratchpad `receipts/`); the decisive lines are copied here as durable evidence.

## Prerequisites (row 1)

- **Execution authorization:** H-4 recorded in [human-gate-decision.md](human-gate-decision.md) §H-4 (`USER_EXPLICIT` 2026-10-01 "proceed"). The plan commit is `569619a`, pushed to `claude/sweet-goodall-mu69td`.
- **Context-tool re-check (create-plan §5f):** `graphify-out/` and `graphify-out-research/` are absent, and there is no `headroom` module, so `not_applicable` holds for execution. This matches the planning record, and the scope is unchanged.
- **Driver:** Claude Code web container (Linux). `RECEIPTS_DIR=/tmp/claude-0/-home-user-av-kit/f0323655-7142-5601-bc9c-c20abbfe7324/scratchpad/receipts`. No `rtk`; container rows run raw (D-11).
- **Input identity at row 1:**
  - HEAD `569619a8a2e08921c415f0caf440d47b5d3a59b0`
  - `mcp-server/package-lock.json` sha256 `62147de51afe8559…`; `uv.lock` sha256 `da452c3481bc2c7b…`
  - node v22.22.0, npm 10.9.4, uv 0.8.17, Python 3.11.15
  - ffmpeg 6.1.1 at `/usr/bin/ffmpeg`
- **Installs:**
  - `npm --prefix mcp-server ci`: exit 0.
  - `uv sync --frozen`: exit 0, but only 19 packages, and `import avkit_api` fails. That led to amendment **A1**: `uv sync --frozen --all-packages`, exit 0 with 113 packages, after which `avkit_api` imports and yt-dlp is 2026.07.04.
  - `npm --prefix mcp-server run build`: exit 0.
- **`MCP_TEST_FLOOR`:** the pre-edit `npm --prefix mcp-server run test` gave **215 total / 215 passed / 0 failed**. It is recorded in `mcp-test-floor.json`.
- **SSOT:**
  - `meu_status.py update MEU-68 in_progress --plan docs/execution/plans/2026-10-01-mcp-live-audit`, then `render`: "All regions rendered successfully".
  - `issue_triage.py add --id MCP-PACKAGED-ENTRY-UNREACHABLE --add-status candidate`, with the root cause prefixed "hypothesis:" (D-6; cloud-local §7: not reproduced on the target, so it is a `candidate`), then `render`.
- **Shell incident (disclosed):** one of my commands used an unquoted heredoc. Backticks in the amendment text ran as command substitutions: `uv sync --frozen` (it uninstalled the workspace packages and the next substitution reinstalled them), ImageMagick `import` (failed, no file written), `python -m avkit_api` (failed: system Python), and several "command not found". No repository file was created or changed apart from the intended plan section, which was rewritten correctly afterwards. Rule kept for the rest of the session: quoted heredocs only.

## Probe findings before Red (row 2)

A real stdio probe used the SDK `Client` + `StdioClientTransport` against `mcp-server/dist/index.js`:

- **`tools/list`:** all 8 tools list `inputSchema` `{"type":"object","properties":{}}`, and `_meta.action_descriptions` carries 18/12/5/7/2/2/13/8 = 67 actions. Filed as **`MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA`** (open, high). The handling is amendment A2 with decision D-12.
- **`avkit_download.remove` without `confirm`:** returns `isError: true`, text `MCP error -32602: Input validation error: Invalid arguments for tool avkit_download: Invalid literal value, expected true at confirm`. That is the SDK layer, as D-4 anticipated.
- **A tool call with no backend:** gives `app_not_running: …`. `tools/list` needs no token or backend, which led to amendment A3(a).

## Red (row 2)

- `validate-task.sh red` passes: `PASS red: 81 failing assertions, 15 passing, VITEST_ACS all named`. The failure kinds are `{'AssertionError': 81}` and zero suite-load errors.
- The first attempt had 5 `TypeError: Cannot read properties of undefined` and 1 `ENOENT`, because the stubs returned empty values. Those tests were hardened (`?.`, an existence assertion first) without changing any expected value. The `red` check now also rejects `^TypeError` and `ENOENT`.
- The 15 passing tests fall into two groups:
  - **Neutral stubs that already match the positive case:** for example, `stepVerdict` returning `pass`, "a non-member stays a failure" when tolerance is a no-op, and the empty-plan coverage checks.
  - **Tests whose subject is not stubbed:** `ACTION_INDEX` has 67 rows; the `forbidden-imports.txt` scan.
  - Each one is paired with a failing negative case in the same `describe`.
- Test files:
  - `mcp-server/tests/audit/{classify,coverage,baseline,isolation,ledger,report,redact}.test.ts` (`UNIT_TESTS`)
  - `run-cli.test.ts`, `runner-fake-backend.test.ts` and the `fake-backend.ts` helper (`RUNNER_TESTS`)
  - `docs.test.ts` (`DOC_TESTS`)
  - `forbidden-imports.txt` (AC-68.2 patterns, A3(c))

## Row-3 pins (live backend probes)

Method: a real `uv run python -m avkit_api --token … --mcp-token … --port 0 --app-data <scratch>`, driven with `curl` against `127.0.0.1:<port>/api/v1`. The process was stopped by PID afterwards. Container-home writes from an early probe that ran before the paths were set (`~/.avkit/models`, `~/Documents/Transcripts/jawed-videos`) were deleted.

| Behaviour | Observed / code | Pinned observable |
|---|---|---|
| `GET /health` | `{"status":"ok"}`, no version | Backend version comes from `GET /openapi.json` → `info.version` = `0.1.0` (A4d) |
| `download.apply_defaults` | `services/download.py:398-420` rewrites `quality/audio_format/audio_only` of Pending/QualityBlocked jobs | REST rows' `quality` equals `downloader.quality` (set to `lowest` for the domain, restored after), and `updated` equals the Pending count |
| `download.add` in the container | 500 `internal_error`; the log ends at `add_to_queue_extract_start`; yt-dlp run directly: "Sign in to confirm you’re not a bot" (+429) | `ENV_BOUND_AUDIT` member; filed `API-UNHANDLED-ERROR-OPAQUE` |
| `download.pause/resume/cancel/stop` | flags read by the worker (`download.py:255-282`); `resume` needs runtime Paused (409 otherwise) | Pause during the current job leads to processor Paused after it; `cancel` gives the active job Cancelled; `stop` gives processor Idle |
| `transcript.add` (`@jawed`) | 201, `video_count` 1 (the container listing works) | Replaced by the 4-video `watch_videos` playlist (A4a). Its add returns 500 in the container (bot check on extract), so it is env-bound here |
| `transcript` states | `start`/`pause` keep the job Processing until the worker checks the flag; `requeue` Processing→Pending 200; `retry` on Pending → 409 `ConflictError "illegal transcript transition Pending -> Pending"` | Two pause→stop cycles give Cancelled, then `requeue`/`retry` give Pending; the conflict contract is `retry` on Pending → 409 with the status unchanged |
| `models.download` int8 | 202; files land under `tts.models_directory`; `download-runtime` returns to Idle at once, `downloaded` lists the variant | Observable is REST `downloaded` plus the file present (not `download-runtime`) |
| `models.load` int8 cpu | 200, `is_loaded: true` | REST `status.is_loaded` |
| `tts.generate` | 201 job, then `status: "Failed"`, `error_message: "ONNX vocab file is missing"` | `MEU62_PENDING_TOLERANCE` matches (`vocab`); the authoritative run must `pass` |
| `convert` | `pause` is deferred until the current job ends (`resume` gives 409 "requires Paused" meanwhile); `cancel` gives the active job Cancelled and processor Idle; `reset` takes Cancelled to Pending; a cancelled job leaves a partial output file | Three jobs: short → long (pause lands, then Paused) → resume → long 2 → cancel → reset |
| `capture.capture` fullscreen in the container | 503 `internal_error` (the domain text is masked) | `ENV_BOUND_AUDIT` member with signature `internal_error` and proof `platform != win32` |
| `capture` register seed | `POST /captures {"mode":"register","path":…,"source":"scan"}` returns 201 with `item` | Container seed (A4c) |
| `capture.annotate` | writes `{stem}.annotated.png` + `{stem}.ann.json`; detail gains `annotated_path`/`sidecar_path` | REST detail paths present and the files exist |
| `capture.remove` | 204; original, annotated and sidecar files deleted; GET returns 404 | REST 404 + all three files absent (09 §remove "Delete files … then row"). Filed `MCP-INSTRUCTIONS-CAPTURE-REMOVE-FILES`: the server instructions say files are not deleted |
| `capture_interactive` | 201 Pending request (`expires_at` +120 s); REST `POST /captures/requests/{id}/cancel` gives Cancelled | Observable is the request Pending in REST; cleanup cancels it through REST |

## Green (rows 3–5)

- **Row 3 `green`:** `PASS green: 73 passed` (`UNIT_TESTS`).
  - Modules: `scripts/audit/{schema,classify,ledger,redact,report,fixtures,census,observer,plan}.ts` and `{summary,baseline}.schema.json`.
  - `AUDIT_PLAN` covers all 67 `AUDIT_ACTION_SET` pairs (coverage.test.ts).
- **Row 4 `fake`:** `PASS green: 89 passed` (`UNIT_TESTS` + `RUNNER_TESTS`).
  - The fake-backend suite launches the real `dist/index.js` over SDK stdio.
  - It covers discovery (8/67), `token_missing` → isolation refused exit 3, hollow → exit 1, REFUSAL_ORACLE pass and refusal_mutated, the isolation refusal with zero lifecycle mutations, and a clean run with the root removed.
  - **Fixes made during row 4 (no expected value changed):**
    - The fake got a `noTokenFile` option, because the server falls back to `{app_data}/mcp-token.txt` (`config.ts:156-178`).
    - The census network proof (a live yt-dlp extract) now runs only when a network member's failure already matches its signature. A first run had probed YouTube from a unit test (3.6 s), which 05 §Testing forbids.
- **Row 5 `typecheck-red-green`:** `PASS AC-68.17 typecheck Red -> Green; D6 row registered`.
  - **Red:** `tsc --noEmit -p tsconfig.json` passes with the probe in `classify.ts` (empty receipt).
  - **Probe:** `npm run typecheck` fails with `scripts/audit/classify.ts(311,14): error TS2322`.
  - **Green:** passes after the revert.
  - A first run of the check failed only because it grepped for the identifier, which tsc does not print. The check now matches `file(line,col): error TS2322`.
  - Added `mcp-server/tsconfig.scripts.json`; `package.json` scripts `typecheck` (`tsc --noEmit && tsc -p tsconfig.scripts.json`) and `audit` (`tsx scripts/audit/run.ts`); the D6 `mcp-audit` row in `.agent/docs/commands.md`.
- **Defects found in rows 2–3 and filed (product code untouched; `PART_A_PATHS`):**
  - `MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA` (high)
  - `API-UNHANDLED-ERROR-OPAQUE` (medium)
  - `MCP-INSTRUCTIONS-CAPTURE-REMOVE-FILES` (medium)
  - `MCP-PACKAGED-ENTRY-UNREACHABLE` (candidate, hypothesis)

## Container run (row 6)

`validate-task.sh audit-container` ran the real runner against a real spawned backend, at `04bc17f`:

```
mcp-audit container: 56/95 pass, 8 discovery finding(s), cleanup ok, exit 1
PASS audit-container: 56 pass, 39 tolerated; MEU62_PENDING_TOLERANCE [('avkit_tts', 'generate', 'ONNX vocab file is missing')]; filed findings ['schema_not_advertised:avkit_download', … 8 tools]; cleanup ok
```

- **Summary:** durable copy in [`container-audit-summary.json`](container-audit-summary.json), schema `mcp-audit-summary.v1`, `mode: container`.
- **Discovery:** 8 tools / 67 actions, with all 67 distinct `tool.action` pairs recorded as steps (95 steps).
- **Launch:** `initialized: true`, launch env keys `AVKIT_API_TOKEN, AVKIT_APP_DATA, HOME, PATH`.
- **Isolation:** `ok`, with all six `ISOLATION_KEYS` under the root.
- **Cleanup:** `{ok: true, residuals: [], backend_exited: true, root_removed: true}`.
- **No secrets:** `grep -c "guitok|Bearer"` over every output file returns 0.
- **Scorecard (pass / non-pass):**
  - settings 7/0, health 2/0, models 9/0, convert 19/0 (fully green);
  - capture 9/1 (`capture.capture` skip_env; the other 9 ran on the REST-register seed, D-8);
  - tts 2/4 (generate fails under MEU-62; get, job2 and cancel blocked);
  - download 7/17; transcript 1/17.

**`ENV_BOUND_AUDIT` census, as proven in this run.** Every member matched both its signature and its environment proof:

| Member | Decisive error (MCP text) | Environment proof |
|---|---|---|
| `avkit_capture.capture` | `internal_error: Internal server error` (HTTP 503, the domain text is masked) | `process.platform` = `linux` (not win32); the row-3 probe showed fullscreen → 503 |
| `avkit_download.add` (url_a, url_c) | `internal_error: Internal server error` (HTTP 500) | The runner's direct yt-dlp extract of `download_url_a` failed (`youtube_extract: false`). The row-3 probe text was "Sign in to confirm you’re not a bot" (+HTTP 429) |
| `avkit_transcript.add` | `internal_error: Internal server error` (HTTP 500) | the same network proof |

`download.add.b` (`dQw4w9WgXcQ`) **passed** in the container: its extract succeeded. The bot check is per-video and per-IP, which is why membership is decided per run by the proof, not by a static skip list. All 34 `blocked` steps sit beneath one of the members above or beneath `tts.generate` (`MEU62_PENDING_TOLERANCE`, matched on `ONNX vocab file is missing`).

Not yet exercised end to end, and left to the authoritative Windows run: the download and transcript lifecycles past `add`, `tts.generate/get/cancel`, and `capture.capture` (fullscreen).

## Docs (row 7)

- `validate-task.sh docs` passes: `PASS green: 7 passed` (`DOC_TESTS`), then `PASS docs`. That covers frontmatter, the two README index rows, and the 05 section free of every `STALE_SPEC_PATTERNS` literal, now stating the baseline path and the isolation rule. The negative case was proven at planning: the same fixed-string grep over the pre-row-7 section found 3 hit lines.
- New: `.agent/skills/mcp-tool-audit/SKILL.md` and `.agent/workflows/mcp-audit.md`.
- Updated: `.agent/workflows/README.md` (`/mcp-audit` row), `.agent/skills/README.md` (`mcp-tool-audit` row), and `docs/build-plan/05-mcp-server.md` §MCP live audit (reconciled to `ACTION_INDEX`; adds the Backend row for H-2; the Where-it-runs row now describes the container subset, D-8).

## Part A checkpoint (row 8): pre-handoff self-review

| AC | Evidence (Part A) | State |
|---|---|---|
| AC-68.1 | `run-cli.test.ts` (`buildLaunch` env shape) + `runner-fake-backend.test.ts` (real `dist/index.js` over stdio: initialize, `token_missing` → exit 3) + container run (`launch.initialized`, env keys) | met (A3a/A5 wording) |
| AC-68.2 | `run-cli.test.ts` (`forbidden-imports.txt` scan, seeded negative) + `scope a` (`rg -f`) | met |
| AC-68.3 / 68.4 | `classify.test.ts` (NEW/REMOVED/GHOST/schema findings, 9th tool) + fake-backend and container discovery 8/67 | met; real server today has 8 `schema_not_advertised` findings (filed) |
| AC-68.5 | `coverage.test.ts`: all 67 pairs covered, removing a step is detected, deps acyclic, 7 destructive steps | met; the baseline half waits for Part B |
| AC-68.6 | `classify.test.ts` + fake hollow (exit 1) + container run (every `pass` has an observable) | met |
| AC-68.7 | `classify.test.ts` + fake pass/refusal_mutated + container (convert/capture remove and clear passed the refusal oracle against the real server) | met in the container for convert/capture; download/transcript/tts on Windows |
| AC-68.8 | `isolation.test.ts` + fake refusal (exit 3, 0 lifecycle mutations) + container `isolation.ok` with 6 keys | met |
| AC-68.9 | `ledger.test.ts` + fake clean run + container cleanup `ok` | met |
| AC-68.10 / 68.11 | `baseline.test.ts` (6 deltas, 4 malformed baselines, rule refusals keep bytes) | met |
| AC-68.12 | `classify.test.ts` tolerance + `run-cli.test.ts` CLI + container census proofs | met |
| AC-68.13 | `report.test.ts` + container report (subset banner, all sections) | met |
| AC-68.14 | `redact.test.ts` + container outputs grep 0 | met |
| AC-68.15 | — | **Part B** (Windows authoritative run) |
| AC-68.16 | `docs.test.ts` | met |
| AC-68.17 | `typecheck-red-green` | met |
| AC-68.18 | `validate-task.sh docs` | met (the BUILD_PLAN Phase 5 note follows at H2) |

**Self-review notes and risks carried into Part B (not defects):**
- **Live-only timing.** On a fast Windows link, the download sequence depends on `download_url_c` (10 min) still `Downloading` when `cancel` lands. The pause observable, by contrast, is guaranteed eventually, because it is deferred to the next job boundary. The transcript pause/stop sequence was pinned from code (`transcript.py:412-423,546-589`); the container could not run it (bot check). The first authoritative run is its first live execution. A timing loss shows up as an explicit failure with the step's observable detail; it is never a skip.
- **`tts.cancel`** uses a precondition read with one re-establish.
- **Quoting the report.** The Markdown report embeds MCP error texts verbatim (redacted). It is evidence, not instructions.

No production code under `packages/`, `ui/` or `mcp-server/src/` changed (`scope a`).

`validate-task.sh gate-a` passes:
- `mcp-types` exit 0 and `mcp-build` exit 0;
- `PASS green: 311 passed`, and `PASS mcp-tests 311 > floor 215`;
- `PASS scope a: 51 changed paths, all allowed` and `PASS AC-68.2`;
- task-contract lint exit 0.

Part A was committed and pushed in the commit that follows this entry.

## Part B start: SEQUENCING_GATE and merge (row 9)

- **`origin/main` at `0e18fbd`** ("docs(tts-repair): H2-2 post-review state and H2-3 closeout") already carried Session 27. On main, MEU-62 is `approved`. Row 9 was therefore not a wait: it ran immediately after Part A.
- **Merge `76465a0`** (merge commit, no rebase; H-4 authorization).
  - Conflicts were in the five tool-managed SSOT files only.
  - `SSOT_MERGE_RULE`: took `origin/main`'s versions, then re-added the four issues filed in this session through `issue_triage.py add`, with fields taken from the pre-merge YAML. Then `meu_status.py update MEU-68 in_progress …` and render for both.
  - No generated region was hand-merged.
- **Amendment A7:** MEU-62 brought `avkit_models.download_asset`, so the set is now 68 actions. `AUDIT_PLAN` gained the two asset steps, and the registry-tied test counts moved from 67 to 68 (source-backed; flagged for the reviewer). With it, the audit tests pass at 96/96 and `tsc -p tsconfig.scripts.json` is clean.
- **`validate-task.sh seqgate`** passes: `MEU-62 status approved`, `meu_status render --check` passes, `issue_triage render --check` passes, `PASS scope b: 51 changed paths, all allowed`, `PASS AC-68.2`, `PASS SEQUENCING_GATE`.

## Container pregate on the merged tree (row 10)

Each attempt ran `validate-task.sh pregate`: `npm ci`, `uv sync --frozen --all-packages`, `mcp-types`, `mcp-build`, `mcp-tests` (318 passed), then `audit-container`.

| Attempt | Result | What it found → what changed |
|---|---|---|
| 1 | FAIL `('avkit_tts','generate','fail')` | **Real defect.** `tts.generate.job2` (≈3,600 chars) → `fetch_failed` at 30,005 ms: `POST /tts/generate` is synchronous and MCP times out at 30 s. Filed **`MCP-TTS-GENERATE-SYNCHRONOUS`** (high); A8/D-14. Meanwhile job 1 (66 chars) was Done in 12,531 ms with a valid MP3, after `download_asset` (vocab 409 contract, spaCy missing → ready). |
| 2 | FAIL `download.add`, `transcript.add` | `url_a` extracted fine in this run while `url_c` and the playlist hit the bot wall. The coarse proof (probe `url_a` only) correctly refused, so the proof was made per failing URL (A9). The `watch_videos` fixture was found incompatible with the backend adapter (`AttributeError`) and replaced by a Blender Studio playlist (A9). |
| 3 | FAIL `download.cancel` | All three adds passed, and c was `Downloading`; c then hit the bot wall during the media fetch (reproduced directly: `Failed`, "Sign in to confirm you’re not a bot") before `cancel` could act. `avkit_download.cancel` joined the census with the bot-wall signature and the container-host proof. The observable now reports the job's own status and error (R2-1). |
| 4 | **PASS** | `mcp-audit container: 77/96 pass … cleanup ok, exit 1` → `PASS audit-container: 77 pass, 19 tolerated; filed step failures [tts.cancel confirmed_no_effect]; filed findings [8 × schema_not_advertised]`, then `PASS pregate (non-authoritative)` |

- **Attempt 4 detail.**
  - The **transcript lifecycle passed end to end, live**: add (9 videos) → list/get/reorder → start → pause (Paused) → resume → pause → stop (Cancelled) → requeue (Pending) → retry on Pending = 409 contract → start → pause → stop → retry (Pending) → compile (`live-rigging-snow_vol1.md`) → remove.
  - TTS, models (with both assets), settings, health, convert and capture: all pass except the filed `tts.cancel`.
  - Download: the entity-free steps pass; adds a and c hit the bot wall (skip_env with proof); the 15 dependents are blocked.
  - **Not yet exercised end to end:** the download lifecycle past `add` and `capture.capture` (fullscreen). Both are left to the authoritative Windows run.
- **Windows portability fixes after attempt 4** (no behavior change in the container; the pregate is re-run on the request SHA):
  - `docs.test.ts` frontmatter regex accepts CRLF, because `.gitattributes` `text=auto` checks `.md` out as CRLF on Windows;
  - `uv` is spawned without a shell (the shell broke the `-c` quoting on Windows);
  - the `run.ts` entry check is case-insensitive on win32.

**Final pregate on the request tree `9b38503`** (clean tree): `PASS green: 318 passed`, then `mcp-audit container: 77/96 pass, 8 discovery finding(s), cleanup ok, exit 1`, then `PASS audit-container: 77 pass, 19 tolerated` and `PASS pregate (non-authoritative)`. The durable summary is [`pregate-audit-summary.json`](pregate-audit-summary.json).

## WINDOWS_GATE (row 11)

### Attempt 1: requested

The requested commit is the one that adds this section (it is a doc-only commit on top of `9b38503`; `GATED_PATHS` are identical). The request block is in the session chat and repeated in `task.md` §B-11.

### Attempt 1: PASS (relayed by the user, 2026-10-01)

Source: `USER_EXPLICIT` chat message from the user, relaying the local run:

> WINDOWS_GATE attempt 1 passed on 8345599, and the five return files are committed and pushed as 39de635 on claude/sweet-goodall-mu69td.

Details from that message:

- **Run.** From `P:/av-kit`, with the tree clean at exactly `8345599`. Versions: rtk 0.42.2, node v24.19.0, uv 0.12.5. It ran 15:29:02 to 15:30:28 -04:00 (about 90 s).
- **Stages and counts.** Every stage exited 0 except `mcp-audit`, which exited 1 (findings recorded). `mcp-tests` 318 passed / 0 failed.
- **Preflight records.** `P:/agentic-framework` HEAD `4033418`; registry hash `B06D7CDA…2C78`. These are recorded, not compared.
- **Quiet machine.** No Electron, Playwright or node gate process was running, and the script's own check agreed. Four idle Claude Code sessions and two Codex app-servers were open in Cursor, with no tool child processes and under 1 s CPU each over 40 s. No Remote Control process was found; only the process list was visible.
- **Packaged probe: not run.** No installed av-kit build was found, so `MCP-PACKAGED-ENTRY-UNREACHABLE` stays an unconfirmed `candidate`, and its record is unchanged.
- **Commit.** Exactly the five return files, SSH-signed, staged directly (no `agent-commit.ps1`, no session digest).

**Cloud check.** `validate-task.sh windows-gate-check` passes:

```
PASS windows gate @ 8345599d0c22b63c85bc070b7ad9d930048d5c7c: mcp_tests {'passed': 318, 'failed': 0, 'total': 318}; audit 68 actions, non-pass ['avkit_tts.cancel']
```

That covers the schema, clean tree, exact stage order, exits, `mcp_tests` > floor 215, an authoritative summary bound to the tested commit, `cleanup.ok`, the three must-pass actions, and the baseline header. Code identity also holds: `GATED_PATHS` are unchanged since `8345599`.

**Authoritative summary** ([`mcp-audit-summary.json`](mcp-audit-summary.json)):

- **Counts.** 96 steps: 95 pass, 1 fail, **0 skip_env, 0 blocked**.
- **Cleanup.** `{ok: true, residuals: [], backend_exited: true, root_removed: true}`.
- **Launch.** Env keys `AVKIT_API_TOKEN, AVKIT_APP_DATA, HOME, PATH, SystemRoot, TEMP, TMP, USERPROFILE`.
- **First live passes of the Windows-only surfaces:**
  - `download.cancel` (c Cancelled, processor Idle);
  - `download.pause`;
  - `download.get.done` (`Me at the zoo.mp4`, 629,172 B);
  - `capture.capture` (fullscreen PNG, 2,807,405 B);
  - `tts.generate` (MP3 60,044 B, 2.6 s);
  - both `download_asset` steps (already ready → 409 contract).
- **The one failure** is the filed `tts.cancel` (`confirmed_no_effect`, `MCP-TTS-GENERATE-SYNCHRONOUS`).
- **Discovery.** 8 `schema_not_advertised` findings (`MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA`).
- **Observation, not a finding.** `transcript.compile` produced a 37 B volume. The playlist's live-stream VODs evidently carry no fetchable captions, so the volume holds only its heading. The step's contract (a compile output file exists, non-empty, inside the root) holds. A future run could pin a captioned playlist if the volume content should be asserted.

## Findings (row 12)

- **Baseline.** `.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json` is annotated under `BASELINE_ANNOTATION_RULE`, with `issue` only: `avkit_tts.cancel` → `MCP-TTS-GENERATE-SYNCHRONOUS`, and the 8 findings → `MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA`. The diff is 9 `issue` keys (and their preceding commas).
- **No new issue was needed.** Every authoritative non-pass was already filed during Part A and the pregate. No failure is in MEU-62's surface: `tts.generate` passes, and `tts.cancel` is the synchronous-route defect, not the asset work.
- **Check.** `validate-task.sh findings-check` passes: `PASS findings: 1 non-pass, all filed`, and `issue_triage render --check` passes.

## H1 verification (H1-1 … H1-4)

Run in the container on the tree carrying `39de635` plus the row-11/12 and H1-3 working-tree edits. `GATED_PATHS` are unchanged since `8345599`, so the Windows result still binds.

| Row | Check | Decisive output |
|-----|-------|-----------------|
| H1-1 | `validate-task.sh task-state` | `PASS task-state: 12 rows done` |
| H1-2 | `validate-task.sh h1-verify` | `windows-gate-check` and `findings-check` PASS; `PASS scope b: 58 changed paths, all allowed`; `PASS AC-68.2: no toolset import in mcp-server/scripts`; `typecheck` exit 0; `PASS h1-verify` |
| H1-3 | `validate-task.sh ssot-review` | `Drift check passed — SSOT loaded (70 MEUs, 12 phases)`; `MEU-68 status ready_for_review`; `PASS ssot-review` |
| H1-4 | `validate-task.sh api-scope` | `PASS api-scope: no packages/ change vs 0e18fbd…; OpenAPI skip-with-basis (G8 not triggered)` |

H1-3 also set grouping §6 Session 28 to "in review" (plan folder linked) and refreshed `current-focus.md`.

## Handoff (H1-5)

[`2026-10-01-mcp-live-audit-MEU-68-handoff.md`](../../../../.agent/context/handoffs/2026-10-01-mcp-live-audit-MEU-68-handoff.md): `OK: required sections present; 18 AC row(s); 22 decision(s) logged; durable evidence present; plan_source binds to 2026-10-01-mcp-live-audit`, and the `--ac-coverage-only` run is OK.

- The validator's AC pattern reads `AC-68.x` as the single ID `AC-68`. So a separate check confirmed that all 18 rows `AC-68.1` … `AC-68.18` are present.
- **Decision Log:** the plan's H-1..H-3 and D-1..D-14, plus H-4 and the execution decisions D-15 (A7 counts), D-16 (A9 fixture and per-URL proof), D-17 (Windows portability, CRLF regex) and D-18 (the 37 B compile volume is an observation).
- **Amendment A10 (clerical).** The first run refused D-6, because its precedent's `${RESOURCES}` reads as a template placeholder. The decision-log copy now uses `$RESOURCES`; the prose quotation keeps the file's literal text.

## Execution review round 1 (H1-6) and corrections

The Fable 5.1 reviewer returned `approved` in round 1, with 3 Medium and 2 Low findings, none blocking ([review](../../../../.agent/context/handoffs/2026-10-01-mcp-live-audit-implementation-critical-review.md)). `review-check` passed. F1 and F2 were verified against the code, and both are real. They touch `GATED_PATHS`, so the corrections reopen `WINDOWS_GATE` (row H1-6). The plan records them as amendment A11.

| # | Verified | Correction | Red → Green |
|---|---|---|---|
| F1 | Yes. `transcript.py:415-420` checks `_pause` before item 0, so Paused never proved a fetch. Windows compiled a 37 B volume with headings only (`transcripts_done` 0), so D-18's "no captions" cause was wrong. | `transcript.resume` polls until a transcript is fetched or an item is `Failed`; `Skipped` keeps polling. `transcript.compile` needs `transcripts_done ≥ 1` and a matching `## Contents` count. New `transcript.requeue.conflict` step (OOC-3). Census member `avkit_transcript.compile`, proven by an adapter caption fetch raising the block error. | `transcript-oracle.test.ts`: 7 assertion failures plus 1 missing step → 11 pass |
| F2 | Yes, reproduced: `--baseline <missing> --update-baseline` launched the backend. | One existence check before the spawn → exit 4. | `run-cli.test.ts`: spy called once → never called, exit 4, no file |
| F3 | Yes. `windows-gate-check` counts summary steps, not baseline entries. | `coverage.test.ts` parses the committed baseline: entries = `AUDIT_ACTION_SET`; every non-pass entry and every finding has an `issue`. | New test passes. Removing the `tts.voices` entry from a temporary copy fails it; the file was restored from git. |
| F4 | Yes. On a scratch harness, a forced `download.add.a` fail still printed `non-pass ['avkit_tts.cancel']`. | Worst-of aggregation, in the runner's `WORST` order; `.ps1` records `audit.steps`. | Same harness: `non-pass ['avkit_download.add', 'avkit_tts.cancel']` |
| F5 | Governance only | Asks Mat to ratify D-14's classification (`tts.cancel` belongs to the synchronous route, not to MEU-62's asset work) | — |
| sibling | The first re-run hung: the backend missed `AVKIT_READY` within 60 s, and the un-killed child kept node alive until the 590 s timeout. | `startBackendProcess` kills a never-ready child, and the error names its pid. | `backend-spawn.test.ts`: missing symbol → pass, pid gone |

**Fresh checks on the corrected tree.**
- `npm --prefix mcp-server run typecheck` exit 0; `build` exit 0; `npm --prefix mcp-server test` **332 passed** (22 files).
- `validate-task.sh audit-container`: `mcp-audit container: 77/97 pass, 8 discovery finding(s), cleanup ok, exit 1`, then `PASS audit-container: 77 pass, 20 tolerated; filed step failures [tts.cancel confirmed_no_effect]`.
- Transcript domain in the container:
  - `transcript.resume`: `transcripts_done 0, last_item_status Failed` (youtube-transcript-api is IP-blocked here);
  - `transcript.compile`: `skip_env`, `no transcript fetched …`, `env_bound {member, signature_matched, env_proof}` all true;
  - both 409 contracts (`requeue`, `retry`) pass.
- Windows must fetch at least one transcript for `compile` to pass; nothing is tolerated there.

## WINDOWS_GATE attempt 2 (row 11, reopened by A11)

**Container pregate on `3c949fc`** (clean tree; the corrections commit), `validate-task.sh pregate`:
- `PASS green: 332 passed`;
- `mcp-audit container: 84/97 pass, 8 discovery finding(s), cleanup ok, exit 1`;
- `PASS audit-container: 84 pass, 13 tolerated; filed step failures [tts.cancel confirmed_no_effect]`;
- `PASS pregate (non-authoritative)`.

Tolerated in the container, each with signature and proof:
- `download.cancel`: bot wall, c Failed;
- `transcript.compile`: `no transcript fetched`, adapter IP-blocked;
- `capture.capture`: not win32;
- 9 download steps blocked beneath `download.cancel`.

Every other step passes, including both transcript 409 contracts and the full download lifecycle up to `cancel`.

**Requested commit:** the commit that adds this section (doc-only on top of `3c949fc`; `GATED_PATHS` identical). The request block is in the session chat. What attempt 2 must show beyond attempt 1:
- `transcript.resume` ends on a fetched transcript (`transcripts_done ≥ 1`);
- `transcript.compile` has a volume whose `## Contents` count equals `transcripts_done`;
- 97 steps;
- `audit.steps` in the result.

If the fixture playlist yields no fetchable transcript on Windows, `compile` fails explicitly. The fix is then a captioned fixture, not a tolerance.

### Attempt 2: PASS (relayed by the user, 2026-10-01)

> WINDOWS_GATE attempt 2 passed on a044446; the five return files are committed and pushed as 0434895 on claude/sweet-goodall-mu69td.

- **Run.** From `P:/av-kit`, tree clean at exactly `a044446`, 16:37:45–16:39:15 -04:00. Preflight hashes `4033418…` / `B06D7CDA…2C78`, identical to attempt 1. `ELECTRON_RUN_AS_NODE` and `AVKIT_E2E_OUT_DIR` were cleared.
- **Quiet machine.** No Electron, Playwright, Vitest or av-kit process; the script's busy check found none. Other Claude Code and Codex sessions in Cursor were idle. No Remote Control process was seen (process list only).
- **Deviation (request error, mine).** The attempt-2 request block omitted `-QuietMachineConfirmed`, which the script at `a044446` requires for the preflight stage. Mat passed it as his own attestation. The attempt-1 command carried it. No code identity is affected.
- **Stages.** All 7 ran; every one exited 0 except `mcp-audit`, which exited 1 (findings). `mcp-tests` 332 passed / 0 failed.
- **Authoritative summary** ([`mcp-audit-summary.json`](mcp-audit-summary.json)): 97 steps, 96 pass, 1 fail (`tts.cancel`, `confirmed_no_effect`), 0 skip_env, 0 blocked; cleanup `{ok, residuals [], backend_exited, root_removed}`; 8 `schema_not_advertised` findings. The result records `audit.steps: 97`.
- **The F1 contract, now proven live:**
  - `transcript.resume`: `transcripts_done 1, last_item_status Done`;
  - `transcript.compile`: `live-rigging-snow_vol1.md 112681 B; 1 section(s), transcripts_done 1`;
  - both 409 contracts (`requeue`, `retry`) pass.
  - Attempt 1's 37 B volume is superseded.
- **Cloud check.** `validate-task.sh windows-gate-check`: `PASS windows gate @ a044446f134fdb2849463b0c2f08be63d64d64f8: mcp_tests {'passed': 332, 'failed': 0, 'total': 332}; audit 68 actions, non-pass ['avkit_tts.cancel']` (worst-of census, F4).

### Rows 12 and H1-1 … H1-4 re-run (after attempt 2)

- **Row 12.** The attempt-1 annotation diff (9 `issue` keys) was replayed onto the new baseline: `avkit_tts.cancel` → `MCP-TTS-GENERATE-SYNCHRONOUS`, and the 8 findings → `MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA`. `findings-check`: `PASS findings: 1 non-pass, all filed`.
- **H1-1** `task-state`: `PASS task-state: 12 rows done`.
- **H1-2** `h1-verify`: findings PASS, `PASS scope b: 63 changed paths, all allowed`, `PASS AC-68.2`, typecheck exit 0, `PASS h1-verify`.
- **H1-3** `ssot-review`: PASS (MEU-68 stays `ready_for_review`).
- **H1-4** `api-scope`: PASS (no `packages/` change).
- **Fresh suite.** `npm --prefix mcp-server test` 332 passed, including the F3 test over the re-annotated committed baseline.

## Execution review round 2 (H1-6)

The Fable 5.1 reviewer verified F1–F4 and S1 as resolved against the attempt-2 evidence: summary sha matches the result, schemas validate, the baseline diff is `issue` keys only, and redaction is clean. It judged the `-QuietMachineConfirmed` deviation immaterial and returned **`approved`** (round 2). `review-check`: `PASS execution review approved round 2 by claude-fable-5-1-subagent`.

Open, non-blocking, routed to Mat:
- **F5**: ratify D-14's classification (`tts.cancel` is the synchronous route, not MEU-62's surface).
- **R2-1** (Medium): `coverage.test.ts:83` returns early when the committed baseline is absent. It should assert existence. The test is under `GATED_PATHS`, so fixing it means `WINDOWS_GATE` attempt 3, or deferring it as a known issue.

The handoff's clerical counts and the AC-68.9 / AC-68.11 citations are corrected (round-2 OOC).

## F5 ratified; R2-1 fixed; WINDOWS_GATE attempt 3 (A12, A13)

- **F5.** Mat answered "Ratify D-14 (Recommended)" (`human-gate-decision.md` §F5). MEU-62 stays `approved`.
- **R2-1.** Mat chose "Fix now + attempt 3". `coverage.test.ts` now asserts that the committed baseline exists. Red: with the file absent, the old test passed 8/8 and the new one fails. The file was restored byte-identical (`9e186da`).
- **Pregate on `9e186da` failed, and that was correct.** `download.cancel` showed the container's YouTube wall as `HTTP Error 403: Forbidden`, which did not match the census signature. A direct yt-dlp fetch reproduced the 403 for both fixtures. A13 adds the 403 to the signature and strengthens the proof: host **and** a direct test fetch of the cancel target failing the same way (round-1 OOC-2). Tests first: 1 assertion failure → 334 pass.
- **Pregate on `efeee3e`** (clean): `PASS green: 334 passed`; `mcp-audit container: 84/97 pass … exit 1`; `PASS audit-container: 84 pass, 13 tolerated`; `PASS pregate (non-authoritative)`. Each `skip_env` (`download.cancel`, `transcript.compile`, `capture.capture`) has member, signature and proof all true.
- **Requested commit:** the commit that adds this section (doc-only on top of `efeee3e`; `GATED_PATHS` identical). This time the run command includes `-QuietMachineConfirmed`.

### Attempt 3: PASS (relayed by the user, 2026-10-01)

> WINDOWS_GATE attempt 3 passed on 65bfa42; the five return files are committed and pushed as d9e2497.

- **Run.** From `P:/av-kit`, tree clean at `65bfa42`, 17:39:08–17:40:36 -04:00, with `-QuietMachineConfirmed`. Preflight hashes identical to attempt 2. Quiet machine: no Electron, Playwright, Vitest or av-kit process; the other agent sessions were idle (one unrelated `codex-code-mode-host.exe`). No Remote Control process was seen.
- **Results.** 7 stages; all exited 0 except `mcp-audit`, which exited 1. `mcp-tests` 334/0. Audit: 97 steps, 96 pass, 1 fail (`tts.cancel` `confirmed_no_effect`), 0 skip_env, 0 blocked; 8 `schema_not_advertised`; cleanup ok.
  - `transcript.resume`: `transcripts_done 1, Done`.
  - `transcript.compile`: 112,681 B, 1 section.
  - `download.cancel`: `c Cancelled, processor Idle`.
- **Cloud.** `windows-gate-check`: `PASS windows gate @ 65bfa42605a253a46eca92881777c6901da88c98: mcp_tests {'passed': 334, 'failed': 0, 'total': 334}; audit 68 actions, non-pass ['avkit_tts.cancel']`.
- **Re-run afterwards.**
  - Row 12: the annotation patch was replayed; `PASS findings: 1 non-pass, all filed`.
  - H1-1 `PASS task-state: 12 rows done`.
  - H1-2 `PASS h1-verify` (scope b 63 paths).
  - H1-3 `PASS ssot-review`; H1-4 `PASS api-scope`.
  - Fresh suite: 334 passed (audit 112).

## Execution review round 3 and H2 closeout

- **Round 3: `approved`** (`PASS execution review approved round 3 by claude-fable-5-1-subagent`). R2-1 is resolved; F5 was closed by Mat; A13 cannot mask a failure (its proof fails closed on 200, 404, a crash or a timeout). New R3-1 (Low): the container network proofs are single-shot. It is filed as `MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT` (TECH-DEBT, P3).
- **A14.** The H2-1 decision sources dropped the grouping (ID collision). Its D-2/D-4/D-5 are carried as `G-D-*`. The handoff's D-20 is renumbered D-22. The issue's D-21 record is rewritten in the validator's YAML subset (values identical).
- **H2-1.** Reflection `OK: all 15 template section(s) present; all 7 required schema field(s) emitted; 3 design rule(s), all sourced; 28 recorded decision(s) reconciled against 31 Decisions Log row(s)`.
- **H2-2.** MEU-68 `approved`; `MCP-LIVE-AUDIT-WORKFLOW` resolved, with its evidence at `windows-gate-result.json`; the Phase 5 note says "MEU-68 approved"; grouping Session 28 `approved`; focus and metrics updated; `PASS post-review-state`.
- **H2-3.** `PASS closeout: 21 rows done`; `lint_task_contract` OK; `scope b` 66 paths allowed. Commit-message draft: [`commit-message.txt`](commit-message.txt).
