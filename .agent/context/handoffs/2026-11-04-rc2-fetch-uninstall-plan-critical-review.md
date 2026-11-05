---
date: "2026-11-05"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-04-rc2-fetch-uninstall/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s49-plan-2026-11-04-rc2-fetch-uninstall"
round: 1
---

# Critical Review: rc2-fetch-uninstall

> **Review Mode:** `plan`
> **Verdict:** `approved`

## Scope

**Intent anchor:** Session 49 makes the fetch script return its documented exit codes and makes the uninstaller remove the installer copy, with every outward step waiting on Mat.

**Intent achieved:** `yes`, for plan readiness, conditional on executing the prescribed checks. This is no implementation or runtime certification.

**Target:** working-tree `implementation-plan.md` and `task.md` under `docs/execution/plans/2026-11-04-rc2-fetch-uninstall/`, on `main`, HEAD `83229ea69b563a03d5c47d4678619c8da4c937d8`.

**Review Type:** independent plan review, round 1; class `avkit_independent_reviewer`. Claude Code / Anthropic authored the plan; Codex / OpenAI did not. **Checklist Applied:** PR-1 through PR-9, limited by D-273 to the changed substance in Q1–Q5. The prior approval supplies the carried fetch fix, macro and unchanged RC1-shaped helpers. Mat's D-266, D-273, D-274, D-276 and D-278 are accepted as instructed.

Only scratch artifacts under `C:/Temp/av-kit` were written. No tests, builds, electron-builder, installers, uninstallers or repository mutations were run. No prohibited secret file was opened. Other sessions' dirty files were left alone.

Reviewed SHA-256: plan `6f330caba3640a0e29c2cd93d4bee6ccf3f2a15bd16d37feb377ce92ac139900`; task `7c376dbeaa174443439624a9389c221c742a8108b0cee6452b271509338983ba`.

Final output validation passed: `rtk proxy .venv/Scripts/python.exe -B -X utf8 C:/Temp/av-kit/s49-review-output-check.py`, exit 0: verdict validates against the repository v2 schema; report contains the exact intent and Q1–Q5; both target hashes remain unchanged. Final Git status lists the same dirty/untracked paths as the initial observation.

## Findings

No evidence-backed High or Critical finding. No blocking finding. The Findings table is empty. Q2 records a narrow factual qualification; it does not establish a material delivery failure.

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Procedure | Exit | Evidence |
|---|---|---|---|---|
| Target and unstarted state | pass | Read both targets; inspect Git state, scheduled inventory and product diff | null | Only the two plan documents exist in the new folder; implementation rows remain unchecked; the four product/test paths have no HEAD diff. |
| Sources and scope | pass | Compare residual build-plan sections, targeted issue/MEU records and grouping §8 | null | `07-distribution.md:334–370`; MEU-125 exists at `meu-status.yaml:3246`; no FFmpeg rebuild or publication was added. |

Manual observations in this report have observer `codex-independent-reviewer` and `exit_code: null`.

### Design Review (DR): Q1–Q5

**Q1 — D-272 and decision extraction. Accepted.** The contract at `implementation-plan.md:269–271` requires complete parsed-data equality, not merely matching IDs. That preserves questions, rulings, reasoning and every nested value; changing a ruling while keeping its ID would fail equality. I independently loaded the register with `model.load`, dumped just the two selected records using indented sequences and no wrapping, read them back, compared their complete logs against a fresh register load, and called the unmodified readers. The extract passed the bounded grammar and returned D-228 and D-214/D-215/D-266/D-275, with their triage stages. No placeholder matches remain; D-228 already uses the prose replacement for the NSIS flag (`known-issues.yaml:4396`).

`decision_sources` accepted actual plan + actual grouping + extract: 24 decisions for uninstall and 27 for FFmpeg; their union is the 28 decisions H2-2 names. Future handoff decisions remain additional execution obligations. The direct register reads reproduced both refusals. H2-2 regenerates the extract immediately before the two fail-fast validator invocations (`task.md:66`), so row 7's old extract is not reused. Accepted as a feasibility proof, not a claim the unwritten production helper or future reflection has passed.

**Q2 — Prepackaged NSIS proof. Accepted, with one qualification.** `platformPackager.js:93–108,147–150` uses the existing app directory and still calls distributable packaging. `NsisTarget.js:62–68,393–408,447–463,709–713` loads the current NSIS configuration/include and compiles a fresh uninstaller and installer; `:623` enables `-WX` unless explicitly disabled, which this config does not do. `builder.js:106–120` and `config.js:36–42` merge the dotted output override over the file. Installer/archive/uninstaller output uses the target output directory, protecting the RC1 setup file. The locked and installed electron-builder/app-builder-lib versions both equal 26.18.0.

The same `appId`, default one-click/per-user mode, package name and cache define feed the normal installer template (`electron-builder.yml:1–18`; `NsisTarget.js:242–275,598–613`; `include/installer.nsh:88–100`). `dist:prep`, app assembly, resource copying and pack/sign hooks are skipped; no configured custom hook supplies this macro. Those omissions do not prevent the specified uninstall proof. Full-build integration remains MEU-125's obligation.

**Qualification:** `implementation-plan.md:265` overstates preservation if “ui/dist untouched” means every file. `nsisUtil.js:119–121` queues a copy to the input app's `resources/elevate.exe`; `packager.js:431–437` executes it even with prepackaged input. The output override protects RC1's installer, but is not a filesystem write barrier around `win-unpacked`. This is an existing packaging-helper refresh, with no demonstrated material payload change or published RC1 change. Narrow that wording; do not infer whole-directory immutability. If an implementation correction changes the authorized machine actions, D-278 sends it back to Mat.

**Q3 — ROUND_TRIP and Mat's machine. Accepted.** `implementation-plan.md:125–135,190–195` replaces the updater-folder gained-only comparison with explicit observations: A requires the old defect; B requires copy presence after install and copy/folder absence after uninstall plus data preservation; C exercises old→new; D exercises new→new and requires the second install's copy. This is a meaningful negative/positive chain. It does not pretend to observe the update guard's transient skip, which is pinned separately. Dropping exits 41/44 is appropriate for this macro-specific repackaging proof; it does not certify a full release payload.

S5 retains RC1's registry, installation, shortcut and running-app protections and adds the known-copy-only precondition (`:305`; RC1 script `:101–116`). Row 0 retains the hash-checked installer before mutation. The known 340 MB leftover is intentionally removed and disclosed, not unprotected user data. The copied script isolates `AVKIT_APP_DATA`, and the reused smoke checks the actual Electron user-data and executable paths (`packaged-app-smoke.mjs:102–118`). Each launch needs its empty throwaway directory as the smoke requires; that fails closed if missed. Normal roaming data is preserved by config and an explicit B check; local data has the stated top-level snapshot guarantee, not a byte-content guarantee. S5 gates external pre-state; C/D deliberately replace only the script's own installation. S6 stops progression after a dirty uninstall.

**Q4 — S2 and outward stops. Accepted.** An actual repackage refusal fails row 4. Rows 5→6→7 and H1/H2 depend on that chain (`task.md:46–53`), so no existing row can honestly continue with a missing installer. S2 (`implementation-plan.md:302`) either brings the failure to Mat or explicitly carries AC-114.4–AC-114.9 open into the existing MEU-125. Such a fallback is not completion of those ACs and cannot justify marking their current rows proved; it requires a recorded amendment consistent with D-278. There is no prescribed silent success path. No row commits, pushes, tags, releases or uploads; H2-5 only drafts a message. The local package stays rc.1 and local. D-276's already-authorized exact-scope commit is recorded as completed context, not rerun by these rows.

**Q5 — New rulings and carry-forward. Accepted.** D-273 limits this review, D-276 records the committed triage baseline without a push, and D-278 authorizes execution after this review approves without blockers (`implementation-plan.md:376–408`). D-278 explicitly returns changed machine behavior to Mat. H2-2 carries all nine plan decisions, all fourteen grouping rows including withdrawn D-246, and all five selected triage decisions; measured reader output agrees. Older “wait for Mat” introductory wording is superseded by D-278's explicit conditional authorization. It does not require another permission request after a clean approval. The later tooling session and notices work remain where Mat placed them.

### Plan Review (PR)

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Same two fixes, repackaging, four runtime phases, extraction and closeout chain. |
| PR-2 Not started | pass | Unchecked work rows, scheduled scripts absent, unchanged implementation paths. |
| PR-3 Task contract | pass | Rows name owners, outputs, exact checks, dependencies and status. |
| PR-4 Validation realism | pass | Q1 measured; Q2/Q3 traced to real producers; runtime checks remain required. |
| PR-5 Source-backed planning | pass | Residual contracts, installed sources and accepted Mat rulings support the delta. |
| PR-6 Corrections readiness | pass | Both handoffs and rolling review paths named; no previous correction census is due. |
| PR-7 Scope discipline | pass | MEU-125 exists and owns the full-build/version/notes follow-up; tooling remains Session 49b. |
| PR-8 Reachability and negative oracles | pass | Same NSIS entrypoint; old-uninstall negative; positive runtime observations; no demonstrated material false pass. |
| PR-9 Shared predicates | pass | Named installer paths and ROUND_TRIP govern the delta; D-278 resolves the older gate wording. |

Post-implementation certification: `n/a`.

### Durable observations

```json
{"schema_version":"evidence.v1","check_id":"s49-fu-r1-decision-extract","command":"rtk proxy .venv/Scripts/python.exe -B -X utf8 C:/Temp/av-kit/s49-review-decisions-probe.py","cwd":"P:/av-kit","scope":"selected issue logs, plan and grouping; imported readers only; scratch output","phase":"static","exit_code":0,"result":"pass","tested_state":"HEAD 83229ea; plan sha256 6f330caba3640a0e29c2cd93d4bee6ccf3f2a15bd16d37feb377ce92ac139900; task sha256 7c376dbeaa174443439624a9389c221c742a8108b0cee6452b271509338983ba","output":"roundtrip_equal_to_fresh_register=True; bounded_grammar=pass; D-228 read at triage; D-214,D-215,D-266,D-275 read at triage; decision_sources counts 24 and 27; placeholder_matches=0; FETCH-FFMPEG-EXIT-CODES has no decisions; source SHA256 remained 225c3d7292e6ef6ecc904c52b395c0c7b94748556e4e20bced5491f7920fefef","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s49-fu-r1-packaging-and-order","procedure":"Read the installed CLI/config merge, platform packager, NSIS target/templates and helper finalization; compare the RC1 round-trip and reused app smoke with plan rows 4-7, S2/S5/S6 and D-278.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Q2-Q5 plan feasibility and machine protection","phase":"static","exit_code":null,"result":"pass","tested_state":"HEAD 83229ea; working-tree plan/task hashes recorded above; locked and installed electron-builder/app-builder-lib 26.18.0","output":"Prepackaged skips app assembly but reaches current NSIS include and -WX compiles; output override protects setup artifact, with input elevate.exe refresh qualification; phases A-D assert the old defect and new cleanup; failed row 4 holds dependents; D-278 supplies conditional execution authority. No build or install executed.","fresh":true}
```

## Verdict

`approved` — the changed plan can deliver the registered objective. No blocking finding warrants another plan-review round. Qualify the broad `ui/dist` preservation wording as described under Q2. Runtime build/install success and the actual helper implementation still require execution evidence. This reviewer stops at the review boundary; the coordinator saves the report and validates the verdict against the ledger.
