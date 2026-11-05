# Parked, never run

Mat kept FFmpeg as it is on 2026-11-04, including libdvdcss, as an accepted risk (triage D-266 in `.agent/context/known-issues.yaml`). So this plan will not run. Nothing in it was executed.

Mat's words: "I thought I deceided to do nothing about FFmpeg. If we build it we will loose on the updates released by ohter builders." Asked whether to do nothing about FFmpeg, keeping libdvdcss in rc.2, they answered: "FFmpeg, keeping libdvdcss in rc.2: yes".

## What stays valid

- `implementation-plan.md` and `task.md` are the exact bytes Codex approved. Don't edit them, because the review is bound to these bytes and to this goal.
- The review is at `.agent/context/handoffs/2026-11-04-rc2-ffmpeg-uninstall-plan-critical-review.md`. Its approval covers this plan only.
- The §Recipe patch, the single-statement contracts and the research are the starting point if the risk ever changes.

## What has moved on

- Session 49 is now `docs/execution/plans/2026-11-04-rc2-fetch-uninstall/`: the fetch script's exit codes and the uninstall fix, with no FFmpeg build.
- MEU-113 is now `dist-fetch-exit-codes`, anchored at `docs/build-plan/07-distribution.md#fetch-exit-codes-residual`. The MEU-113 slug, the `#ffmpeg-no-libdvdcss-residual` anchor and any D-214 route this plan names predate that change.
- The open questions this plan raised for the build host, the rebuilt archive's home and RC1 went away with the build (D-246, D-251, D-215).
- This plan's H2-2 can't pass as written. It repeats `--decision-issue`, which keeps only the last value, and it points the validator at the register, whose YAML the validator refuses. The new plan's D-272 has the route. Its hub row also resolves issues "through `tools/issue_triage.py`", which has no such command, and H2-2 carries five grouping rows where the validator requires all of §8.

To revive this route, Mat rules on the risk again, a new MEU is registered for the build, and the plan is re-reviewed against the repository as it stands then.
