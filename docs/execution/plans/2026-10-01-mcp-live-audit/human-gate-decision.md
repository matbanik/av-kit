# Human gate decisions: audit target, sequencing, execution and gate location

All answers below come from the trusted user channel (`USER_EXPLICIT`, Claude Code web session) during planning on 2026-10-01. Each quotes the question, the option text shown and the verbatim answer.

## H-2 — Audit target backend

Question:

> Which backend should the authoritative audit run hit? It calls destructive actions (download.clear, convert.clear, capture.remove) and settings.set.

Option text presented (recommended):

> **Isolated spawned backend (Recommended)**: The runner starts its own `python -m avkit_api` with a throwaway app-data folder and temp output folders. It uses the real Kokoro, ffmpeg, Windows capture and network, but your real queues, settings and inbox are never touched. The MCP server is still launched over stdio with the copyMcpConfig env, pointed at that backend.

The alternative offered was "Attach to my running app".

User answer, verbatim:

> Isolated spawned backend (Recommended)

Bound in the plan as `ISOLATED_ROOT`, `ISOLATION_GUARD`, `MCP_LAUNCH` and AC-68.8.

## H-3 — Sequencing against MEU-62

Question:

> MEU-68 depends on MEU-62 (Session 27 TTS repair), which isn't planned yet. How should Session 28 be sequenced?

Option text presented (not the recommended one):

> **Build now, baseline later**: Write the runner, workflow, skill and container subset now, in parallel with Session 27. Only the authoritative Windows run and the committed baseline wait for MEU-62. It's faster, but it's two active projects at once, against the one-project-per-session rule.

The recommended alternative was "Wait for MEU-62".

User answer, verbatim:

> Build now, baseline later

What it authorizes, once execution is authorized (H-4):

- Part A (task rows 1–8) may run before MEU-62 is approved. It is bounded by `PART_A_PATHS`.
- Part B (rows 9–12) waits for `SEQUENCING_GATE`.

It is recorded as a user-directed departure from AGENTS §Session Discipline ("One related project per session"). It is not a change to that rule.

## H-4 — Execution authorization and gate location

Source: `USER_EXPLICIT`, Claude Code web session, 2026-10-01. The message came after the plan review was approved in Round 2. My previous turn had said: "If you say 'commit', I'll commit just these files … If you'd rather send the execution message ('proceed'), that also covers commits and pushes on this branch." The turn before that had stated: "A plain 'proceed' is read as accepting H-4's recommendation and every autonomous decision below. It also authorizes commits and pushes to `claude/sweet-goodall-mu69td` and merging `origin/main` into it at row 9. It authorizes no PR, merge to `main`, release or deploy." (`implementation-plan.md` §User Review Required.)

User message, verbatim:

> proceed

What it authorizes:

- **H-4 Option A (recommended): split like Sessions 25 and 26.**
  - Part A (rows 1–8) and row 10 run in this container.
  - Part B's authoritative run (row 11) is one Windows `WINDOWS_GATE` that Mat triggers with `validate-task.ps1 -Check windows-gate`.
  - Row 11 is the planned turn boundary.
- Every autonomous decision in `implementation-plan.md` §Decision Log (D-1..D-11) and the Round 1/Round 2 corrections, accepted as `Human-approved`.
- Git: commits and pushes to `claude/sweet-goodall-mu69td`, and the row-9 merge of `origin/main` into it (merge commit, no rebase).

This authorizes no PR, no merge to `main`, no release and no deploy. It does not relax `SEQUENCING_GATE`: Part B still waits for MEU-62 `approved` (H-3).

## F5 — Ratification of D-14 (execution review rounds 1–2)

Source: `USER_EXPLICIT`, Claude Code web session, 2026-10-01, through an AskUserQuestion answer.

Question asked:

> F5: the plan's Stop Condition says a fail in MEU-62's surface (tts.*) reopens MEU-62. The only authoritative fail is avkit_tts.cancel, which I classified (D-14) as the pre-existing synchronous POST /tts/generate route (filed MCP-TTS-GENERATE-SYNCHRONOUS), not MEU-62's asset work. Do you ratify that classification?

User answer, verbatim:

> Ratify D-14 (Recommended)

Effect: the §Stop Condition is not triggered. MEU-62 stays `approved`, and `avkit_tts.cancel` remains a filed failure under `MCP-TTS-GENERATE-SYNCHRONOUS`.

## R2-1 — Handling of the review round 2 finding

Same source and channel. Question: "coverage.test.ts silently returns when the committed baseline file is missing (should assert it exists). It's test-only but under GATED_PATHS, so fixing it now needs WINDOWS_GATE attempt 3 (~90 s run). How should I handle it?"

User answer, verbatim:

> Fix now + attempt 3
