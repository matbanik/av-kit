# 2026-11-15 HDP v2 and framework sync · Session grouping

> **Source:** Mat's request "Look at P:/zorivest and P:/agentic-framework. I'd like to create new session grouping for enhacments to HDP so I do not have to make expert decsions and other features that have been introduced."
> **Generated:** 2026-11-15
> **Method:**
> - Diffed av-kit's `.agent/docs/human-decision-protocol.md` (287 lines; it matches the framework as adopted on 2026-09-26) against the agentic-framework's `core/.agent/docs/human-decision-protocol.md` at `a73d6df` (2026-11-14, 295 lines). That commit ports Zorivest's HD1 (MEU-940 to MEU-942) and HD3 (MEU-964), and is the latest upstream commit.
> - Listed every upstream commit since 2026-09-26 and checked each against av-kit's tree. Only review-limits (`6dd76b7`) has been ported, in the non-MEU session `review-limits-no-token-budget` (`42f02bc`).
> - Read Zorivest's `2026-11-07-human-decision-protocol-session-grouping.md` (HD1 done on 2026-11-13, HD3 done on 2026-11-14) and the AO, PE, AG and PK groupings, to see what is done there, what is pending and what is Zorivest-only.
> - No MEU is registered. Framework ports in av-kit run as named sessions without an MEU (Session 49b, D-280; `review-limits-no-token-budget`).
> **Origin:** the protocol av-kit runs today sends Mat every decision that fails the obviousness test, in a long brief with a pros-and-cons table. Upstream now narrows what reaches the human, and makes each question cheaper to answer, in five ways:
> 1. A one-line "decide before you ask" rule in `AGENTS.md`. It covers popups, chat questions and subagent returns.
> 2. A closed list of fourteen kinds of decision that always go to the human (§4a, M-1 to M-14). Everything else that passes research and the obviousness test is the agent's.
> 3. Brief v2: the question in plain words, "I recommend A", one line per alternative, and ids only in a Refs line. "yes" accepts the recommendation.
> 4. The expert pass (§5a): one fresh-context review of each set of briefs before Mat sees them. It cuts a recommendation that adds work, or changes one that cannot be done or undone as written.
> 5. The hand-over rule (§6): Mat can hand one set of briefs back to the agent in his own words. The agent then rules them and records that it did, except where an M item forbids it.
>
> Zorivest's decision jury (AO7, MEU-935 and MEU-936), where models rule in place of the human, is still pending there and needs Zorivest's orchestrator. It is watched, not grouped (§3, Not grouped).
> **Status:** Active. This is a reversible draft, not a gate. Nothing here approves a plan or authorizes execution. Every session changes policy files (`AGENTS.md`, the protocol, the closeout validator), so each plan's approval is Mat's M-3 ruling on that change. The grouping rules nothing on his behalf.
> **Parallel work:** none seen. Only the `main` worktree exists, and HEAD is `6813232`. The post-rc.3 grouping (Sessions 75 to 83, D-801 to D-817) was written earlier today and is uncommitted. Session 74 is prompted. No Session 84 or later, and no D-818 or later, is claimed anywhere.

---

## 1. MEU / scope summary

No MEU (D-821). Each row is one upstream change, the session that ports it, and the av-kit files it touches.

| Upstream change | Slug | Covers | Layer | Depends on |
|-----------------|------|--------|-------|------------|
| `a73d6df` validator part: record each decision once | `closeout-record-once` (Session 84) | The reflection is no longer compared with its sources. The validator refuses only the leftover template example line and a `chosen` that still starts with `pending`. Two logs must give one decision the same stage. | `tools/validate_closeout_artifacts.py`, `tests/tooling/` | — |
| `ec3857a` plan-root search ends at the repository boundary | `closeout-record-once` (Session 84) | Known issue `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` (moved from Session 76, D-822) | `tools/validate_closeout_artifacts.py` (`project_root`) | — |
| `a73d6df` protocol part (HD1) | `hdp-v2-protocol` (Session 85) | Decide-before-you-ask rule in `AGENTS.md`; sweep adds `current-focus.md`; §3 Research (a local measurement counts); §4a M-list with `hdp` as the only mode (D-820); Brief v2; §6 record once; §7 Anti-patterns removed, §8 becomes §7 Basis; templates and workflow references | `.agent/docs/human-decision-protocol.md`, `AGENTS.md`, `.agent/templates/`, `.agent/workflows/`, `.agent/skills/` | Session 84 |
| `a73d6df` expert pass and hand-over (HD3) | `hdp-expert-pass` (Session 86) | §5a; `.agent/skills/expert-pass/SKILL.md`; an av-kit peer-reviewer agent on the shared `peer_reviewer` class (D-823); routing and delegation rows; the hand-over rule in §6 | `.agent/docs/`, `.agent/skills/`, `.claude/agents/`, `.agent/model-registry.local.yaml` | Session 85 |
| `0a8d5bc` deep-research templates, and the noreply author check from `fb00d40` | `framework-small-syncs` (Session 87) | `deep-research-prompting` gains its templates and `strip_embedded_images.py` (av-kit has only `SKILL.md`); a commit-identity check before commit | `.agent/skills/deep-research-prompting/`, `.agent/skills/git-workflow/`, `tools/` | — |

### Traceability: upstream commits since adoption

| Commit | Date | What | Here |
|--------|------|------|------|
| `a73d6df` | 2026-11-14 | HDP port (HD1, HD3), expert pass | Sessions 84, 85, 86 |
| `fb00d40` | 2026-11-12 | Standing commit grant; noreply identity check; secret scan; lane land routes | Identity check: Session 87. Grant: not grouped (D-825) |
| `ec3857a` | 2026-11-10 | Closeout plan-root search ends at the repository | Session 84 |
| `fb2d26d` | 2026-11-09 | Credits PE21 start authority | Not grouped |
| `4bb774f` | 2026-11-09 | context-1m skill | Not grouped |
| `ee7566b` and earlier fleet commits | to 2026-11-06 | Fleet | Not grouped |
| `b1b5d63` | — | Metrics, lane route, `--meu` repeat | Not grouped |
| `80cd38f`, `237331c`, `0dcdea0` | — | Lanes, governed land, OS lease, main-ref guard | Not grouped |
| `0a8d5bc` | — | Deep-research templates | Session 87 |
| `b172b08` | — | Commit-gate hook, stage-0 rules | Not grouped (D-825) |
| `6dd76b7` | — | Review limits | Ported (`42f02bc`) |
| `d698342` | 2026-10-20 | Per-plan run parameters | Not grouped (D-733, D-820) |
| `3b3a5df` | 2026-10-17 | Credits scheduled runs, stop gate, completion preflight | Not grouped |
| `7621e45` | — | Stop-email notifier | Not grouped |
| `80461f6` | — | Dispatch resume and fork; `Invoke-ClaudeDispatch.ps1` | Not grouped |
| `47a205c` | — | Build-plan authoring workflow | Not grouped |
| 2026-10-07 refresh | 2026-10-07 | `scout` and `peer_reviewer` agent templates | `peer_reviewer`: Session 86. `scout`: not grouped |

---

## 2. Dependency graph + critical path

```text
Session 84 closeout-record-once ──► Session 85 hdp-v2-protocol ──► Session 86 hdp-expert-pass

Session 87 framework-small-syncs   (independent)
```

**Critical path:** 84 → 85 → 86. Session 84 goes first because it only loosens the validator, so old reflections still pass. Session 85's new reflection template would fail today's validator.

**Parallel tiers:** Session 87 shares two files with Session 85 (`.agent/workflows/inspiration-research.md` and `.agent/skills/git-workflow/SKILL.md`; found by Session 87's planner), so it runs after Session 85 and binds to the content Session 85 leaves. Session 84 and the post-rc.3 Session 76 no longer share a file once the known issue moves (D-822).

---

## 3. Recommended grouping — 4 sessions (84–87)

### Session 84 — `closeout-record-once` (no MEU) · P2

- **Layer / files:** `tools/validate_closeout_artifacts.py` (the reflection checks and `project_root`), `tests/tooling/test_closeout_register_grammar.py` or a new stages test after upstream's `test_validate_closeout_stages.py`, and `known-issues.yaml` (close `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR`).
- **Covers:** the validator half of `a73d6df`; `ec3857a`; the known issue.
- **Why grouped:** both changes edit the same file, and the plan-root fix is upstream's own answer to the known issue. One review covers one file.
- **Gate:** av-kit's validator has 5,671 lines and upstream's has 5,183, because av-kit added its own checks. The port is made by contract, not by copying the file. The plan lists each av-kit-only check and says it stays. Removing the check that compares the reflection with its sources is an M-3 and M-11 change, so Mat rules it when he approves the plan.
- **Cloud/local:** local (the tests read the repository's own files).
- **Token estimate:** calibrate against `review-limits-no-token-budget` (an upstream tooling port with selftest arms) and Session 49b `closeout-register-grammar`.
- **Split flag:** no.

### Session 85 — `hdp-v2-protocol` (no MEU) · P2

- **Layer / files:**
  - `.agent/docs/human-decision-protocol.md`: rewritten to upstream's structure. av-kit's local sweep sources, `rg` receipt commands and Pomera research steps stay; upstream dropped them as project-specific.
  - `AGENTS.md`: the decide-before-you-ask entry rule. Mat's global instructions already hold it (Zorivest MEU-941, D-1 A), but Codex reads only `AGENTS.md`.
  - `.agent/templates/`: PLAN, REFLECTION, HANDOFF and TASK, following upstream's changes to the same templates.
  - Workflows and skills that cite the protocol's sections: `create-plan.md`, `session-grouping.md`, `execution-session.md`, `issue-triage.md`, `next-project.md`, `meu-handoff.md`, `plan-corrections.md`, `inspiration-research.md`, and the `git-workflow` and `session-meta-review` skills.
- **Covers:** HD1. The §4a M-list is adapted to av-kit: each item's source column names av-kit's own file, and items that name machinery av-kit lacks (`stop_gate.py`, `commit_gate.py`, headless runs) say so. `hdp` is the only `decisions:` mode (D-820).
- **Why grouped:** the protocol, its templates and every reference to its section numbers must change together, or the references point at the wrong sections.
- **Gate:** Session 84 is closed. The plan's reference check covers every `human-decision-protocol.md §` citation in the tree.
- **Cloud/local:** local.
- **Token estimate:** calibrate against `review-limits-no-token-budget`; the document review is the larger part.
- **Split flag:** no.

### Session 86 — `hdp-expert-pass` (no MEU) · P2

- **Layer / files:**
  - `.agent/docs/human-decision-protocol.md`: §5a and the §6 hand-over rule.
  - `.agent/skills/expert-pass/SKILL.md` (new), and `.agent/skills/README.md`.
  - `.claude/agents/av-kit-peer-reviewer.md` (new, from upstream's peer-reviewer template), with an av-kit class in `.agent/model-registry.local.yaml` bound like the shared `peer_reviewer` class (Claude Opus 5.5, high).
  - `.agent/docs/model-routing.md` and `.agent/docs/model-delegation.md`: the peer-reviewer role and the expert-pass row.
  - The commands index, if av-kit has one.
- **Covers:** HD3. The pass is advice only: no hook, no schema and no gate. The one way to skip it is Mat saying so. Hand-over records `resolution: autonomous`, with reasoning that starts "Handed to the agent: USER_EXPLICIT <date> '<quote>'". It applies only to items with no M hit, or an M-3, M-5, M-6 or M-8 hit.
- **Why grouped:** these are the two features that take expert calls off Mat. The pass tests a recommendation before Mat sees it, and the hand-over lets him hand a set back. Both sit in the protocol Session 85 rewrites.
- **Gate:** Session 85 is closed. Adding a class to the local registry overlay is an M-3 change, so Mat rules it when he approves the plan. The overlay stays add-only, and the independent reviewer's binding is not touched.
- **Cloud/local:** local (the agent file is resolved by `resolve_model.py sync` against `P:/.agent`).
- **Token estimate:** calibrate against Session 85.
- **Split flag:** no.

### Session 87 — `framework-small-syncs` (no MEU) · P3

- **Layer / files:**
  - `.agent/skills/deep-research-prompting/`: upstream's `templates/` (d1, d2, d3, skeleton, snapshot, domain overlay) and `scripts/strip_embedded_images.py`.
  - A commit-identity check: before a commit, it refuses an author or committer address that is not the noreply address. It follows `commit_batch.py`'s `author_not_noreply` check from `fb00d40`, without `commit_batch.py` itself or its lane routes. The `git-workflow` skill names the check.
- **Covers:** the two remaining upstream features av-kit can use without new machinery.
- **Why grouped:** both are small copies with a test each, and neither touches the protocol.
- **Gate:** none. Whether the identity check runs in the gate or only in the commit skill is decided at plan time.
- **Cloud/local:** local.
- **Token estimate:** calibrate against Session 49b `closeout-register-grammar`.
- **Split flag:** no.

### Not grouped

| Feature | Upstream | Why not | Revisit when |
|---------|----------|---------|--------------|
| `human-all` decisions mode; per-plan run parameters | `a73d6df` §4a, `d698342` | D-733 left `run_parameters.py` out. The mode adds questions, and Mat asked for fewer (D-820). | Mat asks to be asked about everything in some session |
| Standing commit grant; commit-gate hook | `fb00d40`, `b172b08` | Adopting it changes `AGENTS.md` "Never auto-commit/push", an M-3 item that only Mat can rule. It also needs run parameters. Today commits happen on Mat's word (D-825). | Mat says he wants agents to commit their own work |
| Lanes, governed land, OS lease, main-ref guard | `80cd38f`, `237331c`, `0dcdea0`, `b1b5d63` | Mat's rule is main only, with no branches or worktrees. Only Zorivest has an exception. | Never, unless Mat's rule changes |
| Credits scheduled runs, stop gate, completion preflight, PE21 start authority | `3b3a5df`, `fb2d26d` | av-kit runs no headless or scheduled sessions | av-kit starts scheduled runs |
| Fleet | `ee7566b` and earlier | Mat's own work | — |
| Decision jury: models rule in place of the human | Zorivest AO7 (MEU-935, MEU-936) | Pending in Zorivest; needs the AO orchestrator and credits; Mat holds an M-3 there | AO7 lands in Zorivest and upstream |
| context-1m skill | `4bb774f` | Already installed as Mat's user skill | — |
| Dispatch resume and fork; `Invoke-ClaudeDispatch.ps1` | `80461f6` | av-kit sends Codex reviews only, and upstream refuses resume for review classes. Claude work runs in-session subagents. | av-kit dispatches non-review work to Codex |
| Stop-email notifier | `7621e45` | Opt-in, and no need seen | Mat asks for notifications |
| Build-plan authoring workflow | `47a205c` | av-kit's build plan exists and has its own checks | A new product build plan |
| `scout` agent | 2026-10-07 refresh | Claude Code's built-in Explore agent does the same job | — |
| Session wait skill; parking | Zorivest AG8, PK | Zorivest-only | — |

---

## 4. Plan-creation pathway

On Mat's word, run `/create-plan` once per session, in §5 order. Nothing is planned now: Mat asked for a grouping. Each plan reads the upstream diff of the files it ports and states, row by row, what av-kit keeps of its own.

1. `/create-plan closeout-record-once` → no MEU
2. `/create-plan hdp-v2-protocol` → no MEU
3. `/create-plan hdp-expert-pass` → no MEU
4. `/create-plan framework-small-syncs` → no MEU

---

## 5. Prerequisite gate

- **Queue (D-824):** Session 74 first. Then Sessions 84, 85 and 86, ahead of the post-rc.3 Sessions 75 to 83. Session 87 comes after Session 83. Planning and plan review are not blocked. Executing any session waits for Mat's explicit message (`plan_to_exec_gate: human`).
- **Session 84:** the plan names each av-kit-only validator check it keeps.
- **Session 85:** Session 84 is closed.
- **Session 86:** Session 85 is closed.
- No branch or worktree; main only. No edit to `P:/agentic-framework`, `P:/zorivest` or `P:/.agent`.

---

## 6. Session summary

| Session | Slug | MEUs | Band | Status | Plan folder |
|---------|------|------|------|--------|-------------|
| 84 | `closeout-record-once` | — | P2 | proposed | — |
| 85 | `hdp-v2-protocol` | — | P2 | proposed | — |
| 86 | `hdp-expert-pass` | — | P2 | proposed | — |
| 87 | `framework-small-syncs` | — | P3 | proposed | — |

---

## 7. Token calibration sources

`metrics.md` has no token column, so these are named sessions, not numbers.

- **Sessions 84, 85, 86:** `review-limits-no-token-budget` (2026-11-14), the last upstream port, with selftest arms and a closeout under the validator.
- **Sessions 84, 87:** Session 49b `closeout-register-grammar`, tooling with no MEU.

---

## 8. Open Decisions

| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-818 | Group the HDP enhancements and the other upstream features for av-kit? | human | Yes. Four sessions, 84 to 87; no plan created. | Human-approved | Mat asked for exactly this. | USER_EXPLICIT 2026-11-15 "Look at P:/zorivest and P:/agentic-framework. I'd like to create new session grouping for enhacments to HDP so I do not have to make expert decsions and other features that have been introduced." |
| D-819 | Which upstream features are grouped? | autonomous | The HDP port, the closeout fix, the deep-research templates and the identity check. The rest are in §3 Not grouped, each with its reason. | Local Canon | Lanes conflict with Mat's main-only rule. Credits, the stop gate and dispatch resume serve headless runs av-kit does not have. Fleet is Mat's. Porting everything lost: most of it adds machinery av-kit has no use for. Two-way: one message adds a row. | — |
| D-820 | Which `decisions:` modes does av-kit get? | autonomous | `hdp` only. `human-all` and `run_parameters.py` are not ported, so D-733 stands. | Local Canon | Mat's request is for fewer questions; `human-all` asks more. Porting run parameters for a mode nobody asked for would reverse D-733. Two-way: the mode can be added later with run parameters. | — |
| D-821 | How is the work sliced? | autonomous | Four sessions with no MEU: validator first, then the protocol, then the expert pass and hand-over, then the small syncs. | Local Canon | Framework ports run without an MEU (Session 49b, D-280; `review-limits-no-token-budget`). The validator goes first because its change only loosens checks, so old reflections still pass. One session for all of `a73d6df` lost: it would put a 5,671-line tool and a protocol rewrite in one review. Two-way. | — |
| D-822 | Where does `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` go? | autonomous | Session 84, by porting `ec3857a`. It leaves the post-rc.3 Session 76, which then no longer touches the validator. | Local Canon | Upstream's fix ends the plan-root search at the repository boundary, which is the issue's root cause, and Session 84 already edits that file. Keeping it in Session 76 lost: two sessions would edit one function. Two-way. | — |
| D-823 | Who runs the expert pass? | autonomous | A fresh-context Claude subagent on an av-kit peer-reviewer class bound like the shared `peer_reviewer` (Claude Opus 5.5, high). Not Codex. | Local Canon | Upstream §5a names `peer_reviewer`, and the shared registry already binds it. Codex is av-kit's paid independent reviewer, and its verdict role must not mix with advice. Two-way: the routing row can name another class. | — |
| D-824 | Where do Sessions 84 to 87 sit in the queue? | autonomous | After Session 74: 84, 85 and 86 ahead of the post-rc.3 Sessions 75 to 83; 87 after 83. | Local Canon | Every later plan gate asks Mat fewer and plainer questions once the new protocol is in place. The post-rc.3 sessions are P2 to P4 debt with no deadline. Two-way: one message moves it. | — |
| D-825 | Port the standing commit grant and the commit-gate hook? | autonomous | No, not now. Today's rule stays: commits happen on Mat's word. | Local Canon | Adopting the grant edits `AGENTS.md` "Never auto-commit/push", an M-3 item only Mat can rule, and it needs run parameters (D-733). Leaving it out changes nothing, so it needs no ruling. Two-way: Mat can open it with one message. | — |

## 9. Decision Briefs

None open. Every §8 row is either Mat's request (D-818) or a reversible choice that keeps today's rules (D-819 to D-825). Each plan's approval is still Mat's ruling on the policy change it makes (header, Status).

Expert pass: not run: no briefs (av-kit's protocol has no §5a until Session 86).

Carry-forward: each row appears in its consuming session's reflection `### Decisions Log` with stage `grouping`, under today's §6. Once Session 84 lands, the validator no longer compares the reflection with the grouping, and once Session 85 lands, a reflection lists only its own reversible choices. The lines below say which rows bear on each session.

- Session 84 carries D-818, D-821, D-822 and D-824.
- Session 85 carries D-818, D-819, D-820, D-821 and D-824.
- Session 86 carries D-818, D-821, D-823 and D-824.
- Session 87 carries D-818, D-819, D-821, D-824 and D-825.
