# Cloud ↔ Local Agent Collaboration (Windows-bound work)

> **Purpose.** av-kit ships on Windows, but planning and most execution now happen
> in a **cloud driver** (Claude Code on claude.ai/code: a root Linux container with
> `bash`, no display, no `rtk`, no `pwsh`, no Codex CLI, outbound traffic through a
> proxy). Anything that needs the real target — real Electron on Windows, the
> Python suite as it is currently written, NSIS, the login item, the native capture
> picker, `C:/Temp` receipts, or a human looking at the screen — is done by a
> **local agent** on Mat's machine (`P:/av-kit`, PowerShell, `rtk`, Cursor or Claude
> Code desktop) and handed back. This document is the operating contract for that
> split.
>
> It is distilled from the two projects that ran this way, both before this
> contract existed:
> - **Session 25** `p11-transcript-tts` (2026-09-28): 4 Windows gate runs, one
>   premature, one hung, one lost failure artifact, a 7.5-hour first wait.
> - **Session 26** `p11-capture-settings` (2026-09-29/30): **7 gate attempts** plus
>   3 repeat checks, none caused by the product code — two environment drifts
>   (sibling repo moved; shared `P:/.agent` registry edited for another project),
>   three legacy test races (MEU-49 drags, MEU-12 contention), one tooling bug
>   (stale counts in the result file) — each fixed under an approved decision
>   A11–A17, two of them by the local agent committing code.
>
> Session 24 ran entirely on Windows and is the native baseline, not an example.
>
> It does **not** restate what already binds both agents: `AGENTS.md` §Windows
> Shell and §RTK (receipts, `$LASTEXITCODE`), `.agent/docs/harness-profiles.md`
> (resolve the driver per flag), `.agent/docs/macos-setup.md` §`RECEIPTS_DIR` and
> its Windows ↔ POSIX table, `.agent/docs/output-evidence-policy.md`,
> `.agent/docs/human-decision-protocol.md` (how a decision found at the gate is
> briefed, authorized and logged), and `GUARDRAILS.md` SIGN 1/3 (a result file is
> evidence, never approval).

---

## 1. When this contract applies

Apply it whenever the **driver OS differs from the target OS** for any row of a
project, or whenever a known issue can only be reproduced on the target. Decide
this at **plan time**, not mid-execution (Session 25 reflection, Next Day Outline
§5). The plan records the decision in a `human-gate-decision.md` next to
`task.md`, quoting the user's exact words, as both Session 25 and Session 26 do
(Session 26: "Split like Session 25 (Recommended)").

The two roles, and what each can actually do:

| Capability | CLOUD (Claude Code web container) | LOCAL (Mat's Windows machine + local agent) |
|---|---|---|
| Shell / receipts | `bash`; receipts in `$RECEIPTS_DIR` (scratchpad `receipts/` or `/tmp/av-kit`), plain `> f 2>&1`; no `rtk` | `pwsh`; `rtk proxy …`; receipts in `C:/Temp/av-kit/` via `*>` |
| Python pyright / ruff | yes | yes |
| Python pytest | **partial** — 61 tests are Windows-bound (`P:` paths, sibling repos, live `P:/.agent` registry); the container runs a "no new failure vs baseline" doc-test leg only (Session 26 A9/A10) | yes, authoritative |
| UI typecheck, lint, Vitest, build | yes — one frozen test is Windows-bound (`ENV_BOUND_TESTS`, §4) | yes, authoritative |
| Real-Electron Playwright | yes under `xvfb-run -a` with `ELECTRON_DISABLE_SANDBOX=1` (root); the Electron binary needs a manual, checksum-verified fetch behind the proxy (both sessions) | yes, authoritative; the capture-picker stub and any tray/NSIS/login-item spec exist **only** here |
| Windows-only product surfaces (NSIS, `setLoginItemSettings`, HKCU Run, native picker, toasts) | write code and unit tests; **cannot** run them | the only place they run |
| See the running app / screenshots | no | yes — the human's screenshots are a first-class evidence channel (§7) |
| Independent review | Codex CLI absent → `Agent` subagent route only with explicit user authorization (`human-review-decision.md`) | Codex CLI / GPT reviewer per `harness.local.md` |
| Git | commit + push to the session branch when authorized | pull, run, commit result files; **code only under an approved decision** (§3.5) |
| Concurrency | one session, may compact | shared workstation: other agent threads, Remote Control sessions, Electron processes, and **other projects editing shared machine state** (`P:/.agent`, sibling repos) |

Resolve the cloud driver per `harness-profiles.md`: driver = Claude Code,
`native_shell: bash`, `can_dispatch_external_reviewer: no` in practice (no CLI),
`plan_to_exec_gate: human`, `fresh_worker: Agent tool`.

---

## 2. Who does what

The rule is **do everything that can be done in the cloud in the cloud, and batch
everything that cannot into as few local runs as possible**. A local run costs a
human's attention; the first one of a project has cost 7.5–8.5 hours of
wall-clock in both sessions, later ones 20–35 minutes when Mat was at the machine.

| Activity | Owner | Notes |
|---|---|---|
| Planning, FIC, `task.md`, both gate scripts | CLOUD | Write `validate-task.sh` (container) **and** `validate-task.ps1` (Windows) from one stage list. The `.ps1` is written blind; plan review reads it against the `.sh` (Session 25 F8/F9). |
| TDD Red/Green, unit tests, static checks | CLOUD | Authoritative for anything outside the env-bound census. |
| Container pre-gate (`H1-2`) | CLOUD | Same stages as the target gate where they can run, **non-authoritative**, tolerates only `ENV_BOUND_*` failures with proven signatures. Must pass before any local request. |
| **Repeat checks** for timing-sensitive specs | CLOUD first (`--repeat-each`, separate output dir), LOCAL before each gate for Windows-only specs | Session 26 A12/A13/A16: 20× per touched drag spec, then the full suite ×2, before every attempt. |
| **External-input drift preflight** | LOCAL, in the `.ps1` | Record sibling repo HEADs (`P:/agentic-framework`), `P:/.agent/model-registry.json` hash, display/window state, before running (Session 26 RULE-2). |
| Authoritative full gate (`WINDOWS_GATE`) | LOCAL, human-triggered | Zero tolerance. Result bound to a commit (§3). |
| Windows-only feature verification | LOCAL | Same exchange; the request names the exact manual/E2E steps. |
| Reproducing a UI or Windows-only known issue | LOCAL | §7. |
| Fixes discovered **at** the gate (legacy test race, drifted fixture, overlay revalidation) | Either — under a Decision Brief and an A/D-numbered approval (§3.5) | Cloud by default; local when only the local machine can validate it (`7613beb`, `cb864f3`). |
| Independent review dispatch | CLOUD | Only after `windows-gate-check` passes on a code-identical HEAD. |
| SSOT updates (`meu-status.yaml`, `known-issues.yaml`, grouping, focus, handoffs, reflection, `decision_log`) | CLOUD | Local writes the minimum: result JSON, an authorized code commit, a `verification` block on an issue it reproduced. |

---

## 3. The gate exchange (`WINDOWS_GATE`)

### 3.1 Cloud: prepare the request

1. **Pre-gate green first.** `validate-task.sh pregate` passes with only
   `ENV_BOUND_*` failures, each matched to its signature. Session 25's premature
   run on `548bc2a` happened because the local side started before this.
2. **Repeat checks done.** Any spec touched by the change, or any legacy spec that
   has ever raced (`MEU-49` drags AC-49.25/26/27, `test_ac_12_7`), has run
   `--repeat-each=20` green in the container, into a directory other than
   `ui/test-results/`. Session 26 dropped "running the gate right after a change
   without a targeted repeat run".
3. **Stage list final.** Every build artifact the E2E suite needs is a stage (the
   isolated `out-e2e` harness build was missing on Session 25's first pass).
4. **Commit and push** the exact tree to test. Note the SHA.
5. **Mark the row.** The `task.md` row is owned `orchestrator → Mat (human) → tester`,
   is `[B]` with `### B-<row>` evidence "awaiting WINDOWS_GATE on `<sha>`" until the
   check passes, and is the **planned turn boundary**.
6. **End the turn with the request block** (§5.1) — the full block, not a bare
   `git pull; pwsh …; git push` snippet (Session 26 used the snippet; it had no
   expected counts, no preservation step and no quiet-machine step).

### 3.2 Local: run it

Pre-flight, every time:

- **Quiet machine.** No other agent thread, Remote Control session or
  `electron.exe` / Playwright / `node` gate process on `P:/av-kit`. One local agent
  per checkout. **Record the check** in the walkthrough or the chat line even when
  it is clean — Session 26 recorded none.
- **External inputs pinned.** The `.ps1` writes `P:/agentic-framework` HEAD, the
  `P:/.agent` registry hash and the overlay's `validated_against` into the result
  before stage 1. A mismatch with the last passing attempt is a preflight failure,
  not a stage failure (Session 26 attempts 1 and 6 lost ~3 h to drift discovered
  deep inside py-tests).
- **Right commit, clean tree.** `git rev-parse HEAD` equals the requested SHA;
  `git status --porcelain` empty except a leftover result file (the `.ps1`
  exempts `windows-gate-result.json`).
- **Environment.** `ELECTRON_RUN_AS_NODE` and `AVKIT_E2E_OUT_DIR` cleared
  (`E2E-ELECTRON-LAUNCH-FLAG`); `npm ci` is the first stage.
- **Receipts cleared.** The script deletes its own `C:/Temp/av-kit/<prefix>-*`
  receipts first and reports counts only for stages that ran (Session 26 A15:
  attempt 4's JSON carried attempt 3's Vitest/E2E counts).

Run exactly the requested command through `rtk proxy` from `P:/av-kit`. The script
stops at the first failing stage (later stages `not_run`) and writes the result
JSON next to itself.

On **failure**, before anything else:

- **Preserve.** Copy `ui/test-results/` and the receipts out of the repo to a dated
  folder (`C:/Temp/av-kit/keep/<sha>-attempt<N>/`). Playwright empties
  `ui/test-results/` at the start of **every** run, including diagnostic
  `--repeat-each` runs — both sessions lost an `error-context.md` this way.
- **Diagnose on the machine that fails.** A Windows-only failure is diagnosed with
  a targeted repeat on Windows (`--repeat-each=20`/`100`, separate output dir),
  and the mechanism is reproduced with a container probe where possible before a
  fix is proposed (Session 26 KEEP-2).
- **Classify** against the diff: product / legacy test race / env drift / tooling.
  "Flake" is not a class. Product → back to the owning MEU row. Anything else →
  a Decision Brief (§3.5).
- **Rerun only after a fix or a documented non-overlapping basis** (environment
  hang, teardown timeout). Attempts are numbered; the walkthrough gets an
  "Attempt N" section for each, pass or fail, with the preserved-artifact path.

On **success**, commit the result JSON (plus a short walkthrough note if useful) as
`docs(execution): record Session NN Windows gate (attempt N)` and push.

### 3.3 Cloud: validate and continue

1. `git pull`, then run the plan's `windows-gate-check`. Minimum assertions (the
   Session 26 version, `validate-task.sh` `windows-gate-check`): schema id,
   `clean_tree`, exact stage order, every `exit == 0`, `vitest.failed == 0`,
   `e2e.unexpected == 0`, `e2e.flaky in (0, null)`, **count floors** at the previous
   authoritative gate (no silent shrinkage), and **code identity** —
   `git diff --quiet <tested_commit> HEAD -- <gated paths>` empty and no
   uncommitted/untracked files under them. The check "correctly refused every
   stale or partial result" in Session 26 (KEEP-1); keep it strict.
2. **Gated paths must include everything the gate executes**: `ui packages
   mcp-server tests .agent/model-registry.local.json` and any file the `.ps1`
   reads. Session 26's check diffed only `ui packages mcp-server`, so the A11/A14
   test fixes and the A17 overlay change neither reopened the gate nor were
   caught by it.
3. Record the counts **once** (walkthrough), reference them from the MEU handoffs
   as `evidence.v1`.
4. Flip the row `[B]` → `[x]`; dispatch review.

### 3.4 Reopen rule

Any commit after the tested SHA that touches a **gated path** reopens the gate —
review-round fixes (`9fb0153`→`c315640` in Session 25, `1356c59` in Session 26)
and gate-time test/fixture fixes alike. Doc-only commits do not. Budget **several**
round trips per project, not one (Session 26 calibration).

### 3.5 Decisions found at the gate

A gate failure that is not a product defect needs a decision: amend a legacy test,
rebaseline a leg, revalidate an overlay, relax nothing. Follow
`human-decision-protocol.md`: precedent sweep + research first, then a **Decision
Brief with a recommendation** in `human-gate-decision.md` (verbatim option text,
verbatim answer), an `A-<n>` row in the plan's amendments table, and a
`decision_log` entry (`stage: execution`) in the handoff of the MEU whose gate it
was — at the time, not retrofitted at closeout (Session 26 had to retrofit twelve
of seventeen in `c0e97e2`, and D-6…D-12 exist only in the reflection).

- **Who implements:** the cloud by default. The local agent may commit code
  **only** under such a decision and only when the cloud cannot validate the
  change (`7613beb` A11-W test fix; `cb864f3` A17 overlay). The cloud then
  re-reads the diff independently before continuing, and the commit is a gated
  change (reopens the gate — which is why it is followed by the next attempt).
- **Relayed approvals.** If Mat answers in the local agent's chat, the cloud quotes
  the relayed text with its provenance ("relayed in the Session 26 report
  message", A11-W) — a relayed answer is still `USER_EXPLICIT`, but the quote must
  say it was relayed.
- **Shared machine state is a decision, not a fix.** Changing `P:/.agent`, a
  sibling repo, or `model-registry.local.json` to make a gate pass affects other
  projects; it is `one-way-door` class and gets a known issue if the coupling is
  structural (`TOOLING-SHARED-REGISTRY-COUPLING`).

---

## 4. Environment-bound census (`ENV_BOUND_TESTS` / `ENV_BOUND_E2E` / `ENV_BOUND_PY`)

The container tolerates a failure **only** if it is on a pre-declared list with a
signature the pre-gate script re-proves on every run. Never edit, skip or `todo` a
test to make it pass on Linux (AGENTS §Testing & TDD). Declare the census in every
plan; add members only with a proof.

| Tier | Member | Why Windows-bound | Signature / handling |
|---|---|---|---|
| Vitest | AC-51.6 `ui/tests/unit/layout-primitives.test.ts` | frozen SHA-256 of `test-ids.ts` taken from a CRLF checkout; `.gitattributes` `* text=auto` → LF on Linux | recompute the prefix hash with `\n`→`\r\n`; must equal `819760B9…` |
| Electron | capture-picker specs (4) | stub is a Windows-only `dotnet publish` | named list; skipped count must equal it |
| pytest | 61 tests across `tests/tooling` and adopters (`test_framework_adoption.py` and friends) | `P:` paths, live `P:/agentic-framework` checkout, live `P:/.agent` resolver/registry | container runs the doc-test leg as "no new failure vs the last authoritative commit" (Session 26 A9/A10-R); Windows runs all |
| **External inputs** (not tests) | `P:/agentic-framework` HEAD; `P:/.agent/model-registry.json` hash vs `.agent/model-registry.local.json` `validated_against` | edited by other projects between attempts | preflight in the `.ps1` (§3.2); drift → stop before stage 1 |

Every row above is also **tech debt**: hashes pinned to line endings, tests
reading another repo's drive, and tests coupled to machine-level state make the
suite OS- and machine-bound by accident. `TOOLING-SHARED-REGISTRY-COUPLING` is
filed; the CRLF hash should be filed the same way when a session has budget. Until
then the census is the control. (AC-41.3 left the census in Session 31b amendment A-1:
it reads av-kit's copy in `_inspiration/zorivest/`, not another repo's drive.)

---

## 5. Message contracts

### 5.1 Cloud → human/local: gate request (end-of-turn block)

```text
WINDOWS_GATE request — <plan-slug>, attempt <N>
branch:   <session branch>
commit:   <full sha>   (tree clean at exactly this sha; a leftover windows-gate-result.json is fine)
run:      pwsh -NoProfile -File docs/execution/plans/<plan>/validate-task.ps1 -Check windows-gate
from:     P:/av-kit, quiet machine (no other agent thread / Remote Control / Electron / Playwright — say so in the reply),
          ELECTRON_RUN_AS_NODE and AVKIT_E2E_OUT_DIR cleared
preflight: script records P:/agentic-framework HEAD + P:/.agent registry hash; if either differs from
          attempt <N-1>, stop and report before stage 1
expect:   stages <id list in order>; vitest ≥ <floor> passed / 0 failed; e2e ≥ <floor> expected / 0 unexpected / 0 flaky
return:   commit + push docs/execution/plans/<plan>/windows-gate-result.json
          ("docs(execution): record Session NN Windows gate (attempt N)")
on fail:  preserve ui/test-results + C:/Temp/av-kit/<prefix>-* to C:/Temp/av-kit/keep/<sha>-attempt<N>/ FIRST;
          targeted --repeat-each into a separate dir; classify vs diff; report — do not fix without an A-decision
```

If the request also covers a Windows-only manual check (NSIS uninstall, login
item, toast), list each step with its pass criterion and the file to write.

### 5.2 Local → cloud: result

- The pushed result JSON, schema `sNN-windows-gate.v1` (Session 26 shape):
  `tested_commit`, `clean_tree`, `lockfile_sha256`, `mcp_lockfile_sha256`,
  `electron`, `node`, `started`/`finished`, `stages[] {id, argv, exit, receipt,
  note?}` (a `note` explains non-zero-means-pass cases such as `rg` exit 1),
  `vitest {passed, failed, total}`, `e2e {expected, unexpected, skipped, flaky}`
  — `null` counts mean the stage did not run; **never** carried over from a
  previous attempt. Add the preflight fields (§3.2) in the next schema bump.
- One chat line: `WINDOWS_GATE attempt N <pass|fail> on <sha> → <result commit>;
  quiet-machine: <ok|what was stopped>; drift: <none|what>`. On failure: failing
  stage/test, decisive diagnostic lines, preserved-artifact path, repeat-run
  outcome.
- Anything done beyond the request (an extra diagnostic run, a stopped thread, a
  code commit under an A-decision) is named in that line or the walkthrough.

---

## 6. Timing and turn discipline

- The cloud **ends its turn** at the request; it may work on an unrelated session,
  but it does not poll and does not pre-run review on the untested tree.
- First round trip of a project: plan for hours (7.5 h and ~8.3 h). Subsequent
  ones while Mat is at the machine: 20–35 min; a round trip that includes 100×
  repeats and two full Electron runs: ~3 h. So batch every Windows-only check into
  one request, and front-load repeat and preflight checks so the gate is the
  confirmation, not the discovery.
- If the cloud session compacts while waiting, the `task.md` row, the last
  "Attempt N" walkthrough section and the request block are the resume point.

---

## 7. Applying this to issue triage

`/issue-triage` is a planning workflow, but its **verification** step has the same
split. `issue_triage.py verify --deep` (file existence, test references) runs in
the cloud. *Reproducing* an issue does not always:

| Issue class | Where it is verified | How the result comes back |
|---|---|---|
| Backend/API/MCP/core logic | CLOUD (pytest, contract tests, `curl` against a local uvicorn) | `verification` block written by the cloud |
| Renderer behaviour reachable in Vitest | CLOUD | same |
| Real-Electron behaviour, layout at the default window, anything visual | LOCAL — the human's screenshots and a targeted Playwright run | screenshots in chat; the cloud writes the row with file:line root cause; `verification` filled from the local result |
| Windows-only (`ELECTRON_RUN_AS_NODE`, NSIS, HKCU Run, picker, toasts, ffmpeg/spaCy on the machine) | LOCAL only | `verification.evidence_file` points at a committed excerpt (plan folder or `docs/execution/evidence/`), never at `C:/Temp` |

The 2026-09-30 batch is the cautionary example: the cloud filed
`TTS-GENERATE-FAILED-SILENT` from a log excerpt and the code with an ffmpeg
hypothesis; the local session, with the machine in front of it, found the actual
first failure was a missing spaCy `en_core_web_sm` model and an unwired ONNX vocab
path. A cloud-authored `root_cause` for a runtime failure is a **hypothesis until
the target confirms it** — label it so, and let the local result overwrite it.

For each issue that needs the target:

1. CLOUD writes the row (`add`) with `root_cause` citing code and, for runtime
   failures, an explicit "hypothesis:" prefix; `resolution_path` as usual.
2. CLOUD ends the turn with one **repro request** for the whole batch in the §5.1
   shape: issue id, exact steps or command, what "reproduced" looks like (log
   line, status text, screenshot subject), what to record.
3. LOCAL reproduces, then either pastes the evidence for the cloud to record, or
   sets `verification.last_checked/method/result/evidence_file` itself and runs
   `issue_triage.py render`. Never hand-edit `known-issues.md`. A decision made
   during triage (defer, reclassify, widen) goes in the issue's
   `enrichment.decision_log` (`human-decision-protocol.md` §Where it lives).
4. CLOUD classifies, runs `bucket`, feeds `/session-grouping`. Not reproduced on
   the target → `candidate`/`DEFER`, not `MEU-NEW`.

---

## 8. Anti-patterns seen → rule

| What happened | Session | Rule |
|---|---|---|
| Local gate started before the pre-gate passed and the stage list was final | 25 | Pre-gate green + stage list frozen before the request; the request names the SHA |
| Gate run straight after a change, with no targeted repeat; three attempts lost to legacy drag/contention races | 26 | Repeat checks (`--repeat-each`) before every attempt, in a separate output dir |
| Two drifts of machine-level inputs (sibling repo HEAD, shared registry) found deep inside py-tests | 26 | Preflight external inputs in the `.ps1`; drift stops before stage 1 |
| Result JSON carried the previous attempt's counts | 26 | Script clears receipts first; counts only for stages that ran; check rejects stale/partial |
| A second agent thread opened a duplicate gate run; a third was stress-testing a spec | 25 | One local agent per checkout; record the quiet-machine check every time |
| `error-context.md` lost to later runs wiping `ui/test-results/` | 25, 26 | Preserve to `keep/<sha>-attempt<N>/` before any rerun or repeat |
| Code-identity check covered `ui packages mcp-server` only; test and overlay fixes slipped past it | 26 | Gated paths = everything the gate executes |
| Local agent committed code with the approval relayed second-hand | 26 | Allowed only under an A/D decision; quote the relayed text with provenance; cloud re-reads the diff |
| Twelve of seventeen decisions logged only at closeout | 26 | `decision_log` entry when the decision is made |
| Full-gate counts pasted into two handoffs and re-edited per rerun | 25 | One canonical evidence record, referenced |
| `validate-task.ps1` written where it could not be run | 25 | Plan review reads the `.ps1` against the `.sh` stage list |
| Reviewer route and gate location decided mid-execution | 25 | Plan-time decisions in `human-review-decision.md` / `human-gate-decision.md` |
| Cloud filed a runtime failure's root cause from code alone; the machine disagreed | 30 Sep triage | Runtime root causes are hypotheses until the target confirms |

---

## 9. Checklists

**Cloud, before sending a request**
- [ ] `pregate` green; only census failures, each signature-matched
- [ ] repeat checks green for touched and known-racy specs (separate output dir)
- [ ] every E2E build artifact is a stage; `.ps1` and `.sh` stage lists identical; `.ps1` clears receipts and records preflight inputs
- [ ] tree committed and pushed; SHA in the request; row `[B]` with B-evidence
- [ ] request block (§5.1), with floors and the on-fail line, is the last thing in the turn

**Local, before running**
- [ ] quiet machine confirmed **and written down**
- [ ] preflight inputs match the last passing attempt (or stop and report)
- [ ] `git rev-parse HEAD` == requested SHA; tree clean (result file exempt)
- [ ] `ELECTRON_RUN_AS_NODE` / `AVKIT_E2E_OUT_DIR` cleared; running through `rtk proxy` from `P:/av-kit`

**Local, after running**
- [ ] on failure: preserved → repeat-diagnosed → classified → reported; no fix without an A-decision
- [ ] on success: result JSON committed and pushed with the attempt number
- [ ] one chat line: attempt, pass/fail, SHA, result commit, quiet-machine, drift

**Cloud, after the result**
- [ ] `windows-gate-check` passes (schema, clean tree, stages, exits, counts + floors, flaky, code identity over all gated paths)
- [ ] evidence recorded once; decisions logged in the handoff; row `[x]`; review dispatched
- [ ] any later gated-path commit → back to §3.1 as attempt N+1

---

## 10. Templates to reuse

Start from the plan-local artifacts rather than re-inventing them — Session 26's
where the two differ:

- `docs/execution/plans/2026-09-28-p11-capture-settings/human-gate-decision.md` — decision record with A-sections (question, verbatim options, verbatim answer)
- `…/2026-09-28-p11-capture-settings/validate-task.ps1` — 17-stage Windows runner: receipt clearing, `clean_tree` exemption, `mcp_lockfile_sha256`, stage `note`
- `…/2026-09-28-p11-capture-settings/validate-task.sh` `pregate`, `doc-tests`, `windows-gate-check` — container side with count floors and `flaky`
- `…/2026-09-28-p11-capture-settings/walkthrough.md` §Windows gate — attempt-by-attempt write-up including failures and a lost artifact
- `…/2026-09-28-p11-transcript-tts/validate-task.sh` `vitest_env_ok` — the signature-proof pattern for `ENV_BOUND_TESTS`
- `…/2026-09-28-p11-transcript-tts/windows-gate-result.json` / `…-capture-settings/windows-gate-result.json` — result schemas v25 / v26
