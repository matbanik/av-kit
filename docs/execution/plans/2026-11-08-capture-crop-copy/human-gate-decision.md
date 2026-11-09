# Human gate decisions (planning)

This is the one question this plan puts to Mat at the plan gate (`implementation-plan.md` §User Review Required), briefed under `.agent/docs/human-decision-protocol.md`. A brief here authorizes nothing until Mat's ruling is recorded under it, and its sources go into the decision log. The searches are saved in `C:/Temp/av-kit/s59-hdp-d499-web1.txt` (no relevant result) and `C:/Temp/av-kit/s59-hdp-d499-web2.txt`.

## D-499: how the MCP audit baseline meets the new `crop` action   [governance-value] [planning]

**Mat's ruling (2026-11-09):** option A, as recommended: `BASELINE_PENDING` in the test, plus a filed issue. Mat's words: "D-499 A".

**Recommendation:** option A. Name the gap in the test and in the register:
- `coverage.test.ts` gets `BASELINE_PENDING = ["avkit_capture.crop"]`.
- AC-68.5's committed-baseline clause then asserts that the baseline misses exactly the pending keys, that each of them is a served action and absent from the baseline, and that the baseline has no extra key.
- Row 6 files `MCP-AUDIT-BASELINE-PENDING-CROP`, linked to `YOUTUBE-CAPTIONS-IP-BLOCK`. The next authoritative baseline update closes it and empties the list in the same change.

With A, `main` stays green, and every other baseline check keeps its full force: a missing key that isn't pending, an extra key, and a non-pass entry with no issue still fail. The gap is written down where the next release audit will meet it.

**Why it reaches Mat.** The crop adds an `ACTION_INDEX` row. AC-68.5 (`mcp-server/tests/audit/coverage.test.ts:78-85`) asserts that the committed baseline (`.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json`: authoritative, recorded at `ddd1117` on 2026-10-16, 70 entries, all `pass`) covers exactly the served set, so the crop breaks it.

The usual fix, an authoritative refresh, is blocked:
- `BASELINE_UPDATE_RULE` (`.agent/skills/mcp-tool-audit/SKILL.md:49`) refuses `--update-baseline` on any REGRESSION.
- The open `YOUTUBE-CAPTIONS-IP-BLOCK` (`.agent/context/known-issues.yaml:2931`) makes seven transcript actions REGRESSION on this network. Its blast radius says: "Do not refresh the audit baseline to hide it."
- Hand-editing the baseline is forbidden: after an authoritative run, the only allowed edit is an `issue` id (`BASELINE_ANNOTATION_RULE`, `SKILL.md:51`).

Every way through changes what AC-68.5 accepts or what the release audit sees, which is a new threshold (HDP §4 test 4).

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ A: `BASELINE_PENDING` in the test, plus a filed issue | — | — | Qt QUIP 24, GitLab, Rad UI below |
| ⚠️ B: a gate-only tolerance in MEU-67's shape | AC-68.5 itself doesn't change. Only this session's gate tolerates the one failure, after re-proving the baseline is byte-identical and the gap is exactly `crop` | `main`'s MCP suite stays red for every session until the baseline is refreshed, which can't happen while the caption block is open. Each later gate needs the same tolerance or fails. MEU-67 closed its tolerance with a refresh in the same session; B can't | `docs/execution/plans/2026-10-02-capture-flatten-backup/implementation-plan.md:200` (`BASELINE_PENDING`, gate-only), `:176` (`LOCAL_SEQUENCE`) |
| ⚠️ C: an authoritative refresh in this session | No exception anywhere. The baseline gains a real recorded `crop` entry, as MEU-67's did for `flatten` and `revert` | Needs the live audit, which is a network run and needs Mat's words. It exits 2 while the caption block holds, so the baseline stays byte-identical. Waiting on it can hold the session open indefinitely | `SKILL.md:49`; `known-issues.yaml:2931`; MEU-67 `LOCAL_SEQUENCE` step 1 |
| ❌ D: do nothing | No new mechanism | AC-68.5 fails, the session gate's `mcp-tests` step fails, and the session can't close | `coverage.test.ts:78-85` |

**Precedent:**
- MEU-67 met the same gap for `flatten` and `revert` (2026-10-02). Its `BASELINE_PENDING` was a gate-only tolerance (D-20, `:200`), closed in the same session by an authoritative `--update-baseline` run (`:176`). That route worked because nothing had regressed then.
- The caption issue's resolution path forbids refreshing the baseline to hide its REGRESSIONs (`known-issues.yaml:2931`).
- Session 57's release rule (`docs/execution/plans/2026-11-08-release-rc2/audit-rule.py`, uncommitted, read only) accepts exactly the seven caption REGRESSIONs and refuses any other delta, NEW included (its selftest case "an action is new", `:405`). Session 57 runs first (D-498), so rc.2's audit doesn't see `crop`. Whichever release audit comes next does, under every option except C, so under A the filed issue names that audit as the place to accept `avkit_capture.crop` as NEW.

**Research:** `pomera_web_search` (exa). The tavily search returned nothing relevant.
- [Qt QUIP 24](https://contribute.qt-project.org/quips/24/): a test that is ignored is "a form of quarantine". It is allowed only with an open, assigned ticket named next to the entry, and the conditions should be "narrowly specified". The entry is removed when the ticket is fixed.
- [GitLab test quarantine](https://handbook.gitlab.com/handbook/engineering/testing/quarantine-process/): a quarantine needs an issue first, is temporary, and keeps unrelated failures from blocking engineers.
- [Rad UI quarantine policy](https://www.rad-ui.com/docs/contributing/flaky-test-quarantine): guard "the narrowest failing assertion rather than broad test files", with a tracking issue and a restore note.
- [SysRoot](https://sysroot.io/blog/flaky-tests-quarantine-strategy-ci-cd-reliability): keep the list "in version control so quarantine changes go through code review", and require a ticket for each entry.

These are about flaky tests, not a snapshot that can't be re-recorded, but the shape carries over: name the one gap in a reviewed file, tie it to a ticket, and remove it when the cause is fixed. A follows that shape, and B keeps the suite red.

**Obviousness test (§4):** fails test 4. It changes what an audit-coverage test accepts, and what the next release audit has to accept.

**Reversibility / risk:** two-way. A is one constant, one test clause and one register entry, all removed by the next authoritative update. The risk is that the pending list outlives its reason. The filed issue and AC-130.28's check (a pending key that is in the baseline fails) cover that: once a refresh records `crop`, the test fails until the list is emptied.

**If you do not answer:** row 0 stops (S12). Unlike most autonomous defaults, an unanswered D-499 doesn't carry the recommendation, because row 4b's tests depend on the ruling.

**What the recommendation would authorize:**
1. `BASELINE_PENDING = ["avkit_capture.crop"]` in `mcp-server/tests/audit/coverage.test.ts`, with a comment naming D-499 and the issue id.
2. Amending AC-68.5's committed-baseline clause: `missing` equals `BASELINE_PENDING`, `extra` is empty, each pending key is in `ACTION_SET` and not in the baseline, and the non-pass and finding checks stay as they are (AC-130.28).
3. Filing `MCP-AUDIT-BASELINE-PENDING-CROP` with `issue-file.py` at row 6: severity low, component `mcp-server` (the register's model has no tooling component), linked to `YOUTUBE-CAPTIONS-IP-BLOCK`, closed by the next authoritative update, and naming the next release audit as where `avkit_capture.crop` is accepted as NEW.

It does not authorize: running the live audit; `--update-baseline`; any edit to `baseline-snapshot.json`; changing Session 57's `audit-rule.py`; or pending any action other than `avkit_capture.crop`.
