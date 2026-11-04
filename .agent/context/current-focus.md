Current priority: Session 43 `capture-editor-repair` (MEU-99 history chords, MEU-100 resize handles, MEU-101 text re-edit and scaling), the only session of the 2026-10-29 grouping (`.agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md`). Executing on `main` (2026-11-03): the plan review approved in round 2 (D-161), rows 0-9 `[x]`, and the H1-2 fresh gate passed on its third run (every step exit 0, py-tests by the baseline rule; runs 1 and 2 hit load timeouts in `ui-electron` only). Mat ruled D-175 (census the builder pin), D-176 (Vitest worker flag for Node 26 `localStorage`) and D-177 (TA-3 in `icon-hints.test.ts`) on 2026-11-03. Next: the handoffs and the Codex execution review. Nothing is committed.
- Plan: `docs/execution/plans/2026-10-29-capture-editor-repair/`. Handoffs: `.agent/context/handoffs/2026-10-29-capture-editor-repair-MEU-{99,100,101}-handoff.md`.
- Execution corrections EC-1 to EC-10 (`walkthrough.md` §Execution Correction Notes).

Current priority: Session 42 `tts-sideload-load` (MEU-98, rider `TTS-SPACY-SYSPATH-STALE-DIR`, eSpeak evidence stage), the third session of the 2026-10-17 grouping. Executed on `main` (2026-10-27): rows 0–9 `[x]`, and row 10 `[B]` (b) because eSpeak NG is absent (`TTS-ESPEAK-LIVE-PATH-UNVERIFIED` stays open with a fresh `verification`). The H1-2 fresh gate passed (every step exit 0; py-tests `1 failed, 956 passed`, the one failure the baseline-excused AC-25.7 id). The Codex execution review approved in round 1 with no findings. Closed out (2026-10-27): MEU-98 is `approved`, `MODEL-SIDELOAD-LOAD-500` and `TTS-SPACY-SYSPATH-STALE-DIR` are resolved, and the grouping is delivered (Sessions 40 to 42 approved). Nothing is committed yet; the draft is `C:/Temp/av-kit/commit-draft.txt`.
- Plan: `docs/execution/plans/2026-10-26-tts-sideload-load/`. Handoff: `.agent/context/handoffs/2026-10-26-tts-sideload-load-MEU-98-handoff.md`. Reflection: `docs/execution/reflections/2026-10-26-tts-sideload-load-reflection.md`.
- Execution correction notes ECN-1 to ECN-3 (`implementation-plan.md`): the baseline re-recorded at `c34866b`, B-10 kept in `task.md`, and the receipts root.

Current priority: Session 41 `gui-keyboard-palette` (MEU-95 → MEU-96 → MEU-97, rider `GUI-AUDIT-CLIPBOARD-RESOLVER`), the second session of the 2026-10-17 grouping (`.agent/context/grouping/2026-10-17-gui-shell-and-tts-sideload-session-grouping.md`). Executed on `main` (2026-10-26) and closed out (2026-10-27): the plan review approved in round 3, the H1-2 fresh gate passed (every step exit 0, py-tests by the baseline rule), and the Codex execution review approved in round 1 (F1 Medium, non-blocking, now `CAPTURE-HINT-TEST-PRESENCE-ONLY`). The three MEUs are `approved`; the four issues are resolved. Committed as `d30f62b`.
- Plan: `docs/execution/plans/2026-10-26-gui-keyboard-palette/`. Handoffs: `.agent/context/handoffs/2026-10-26-gui-keyboard-palette-MEU-{95,96,97}-handoff.md`.
- Execution corrections EC-1 to EC-5 (`walkthrough.md`); Mat ruled EC-1 (D-153), EC-3 (D-155: registry chords bubble out of Capture's draw surface) and EC-5 (D-157).

Session 40 `gui-theme-path-fields` (MEU-94 theme-reactive selects, MEU-93 path fields) is `approved` (2026-10-26) on Mat's ruling D-120 (option 2): gate runs 1–4 stand as the gate, and the Codex execution review approved in round 2 after round 1 F1 (High) was fixed as EC-6. Committed on `main` in `P:/av-kit` on Mat's direction (2026-10-26).
- Plan: `docs/execution/plans/2026-10-24-gui-theme-path-fields/`. The plan review approved round 2. Handoffs: `.agent/context/handoffs/2026-10-24-gui-theme-path-fields-MEU-{94,93}-handoff.md`. Reflection: `docs/execution/reflections/2026-10-24-gui-theme-path-fields-reflection.md`.
- Gate: Mat accepted runs 1–4 as the gate (`walkthrough.md` §Gate ruling).
  - Every AC-93/94 test passed in all four runs. Each run had one non-baseline failure (AC-81.11, then AC-19.17, AC-67.24 and AC-67.35), each an environment or host-load miss, and no run passed whole.
  - The H1-2 fresh gate and H1-6b were waived, not run. The H1-7 Codex execution review approved in round 2 (`.agent/context/handoffs/2026-10-24-gui-theme-path-fields-implementation-critical-review.md`).
- Resolved: `GUI-LIGHT-THEME-SELECT-STALE-DARK`, `GUI-CONVERT-OUTPUT-NO-BROWSE`. Opened: `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` (the gate's Electron hangs) and `PACKAGING-MCP-SNIPPET-TOKEN-STALE` (AC-25.7).
- Landed on `main` on 2026-11-03: Zorivest `1f254832`'s darker light pill hexes, on Mat's ruling of 2026-10-26.

Repository state (2026-10-24):
- Git history was squashed to one root commit, `7b29fcd` ("Initial commit: av-kit as of 2026-10-24"), and force-pushed. The 286 earlier commits are in `P:/av-kit-backup/full-history-20261024-3da69a1.bundle`; commit hashes cited in handoffs, plans, receipts and `baseline.sha` files resolve only there, so old `validate-task.ps1` scripts that read a pinned baseline do not re-run on `main`.
- No branches or worktrees besides `main`. Every session through 39, plus 31b, is approved and merged.
- Session 31b `gui-mcp-setup-prompt` (MEU-71, MEU-92) was committed and merged on 2026-10-24 (before the squash). The merge kept both sides of `known-issues.yaml`, `meu-status.yaml` (MEU-92 before MEU-93) and `metrics.md`, set `QUEUE-PILL-TOKEN-DRIFT` `meu_links: []` (grouping D-96), and re-rendered the generated Markdown. Merge checks: `render --check` for both SSOTs, ui typecheck and lint pass, ui Vitest 1013/1013, MCP typecheck pass, MCP Vitest 446/446 (after rebuilding `mcp-server/dist`). Electron E2E and the packaged `PKG_PROBE` were not re-run after the merge.
- Resolved by the merge: `MCP-SETUP-PROMPT`, `MCP-PACKAGED-ENTRY-UNREACHABLE`, `QUEUE-PILL-TOKEN-DRIFT`.

Next steps:
1. Commit Session 42 on Mat's direction (draft: `C:/Temp/av-kit/commit-draft.txt`). For `TTS-ESPEAK-LIVE-PATH-UNVERIFIED`, Mat installs eSpeak NG 1.52 and runs AC-74.11 in the dev app; row 10 then turns `[x]`.
2. Run the Electron E2E suite and the packaged `PKG_PROBE` on merged `main` (not run since the 31b merge).
3. Mat's ruling on D-101 (FFmpeg LGPL versus GPL); it blocks `FFMPEG-PIN-URL-404` and the FFmpeg debt batch, not Sessions 40–42.

Open follow-ups from earlier sessions:
- Session 30 `/plan-corrections`: review F6 (stale plan wordings) and the missing Files-table row for `tests/tooling/test_framework_adoption.py`.
- `2026-09-29-human-decision-protocol-adoption`: approved; its H2 closeout (reflection and metrics row) is still missing.
- Triage candidate: should av-kit's light `--color-accent` (`#0891b2`) follow Zorivest as `--color-accent-cyan` did (Session 31 A-5)?
- `TOOLING-SHARED-REGISTRY-COUPLING`: give `test_framework_adoption.py` a fixture registry home.
