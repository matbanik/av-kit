# Harness profile override — av-kit

> Explicit override per `.agent/docs/harness-profiles.md` step 1.
> Human-confirmed 2026-08-17 in `PROJECT-PROFILE.md`. Use these flag values
> verbatim; do not fall back to the Cursor table row when they disagree.

```yaml
driver: Cursor IDE
host: Cursor IDE
role: primary-driver
plan_to_exec_gate: reviewer-auto
injects_auto_approval: yes
can_dispatch_external_reviewer: yes
native_shell: powershell
read_tool: Read
shell_tool: Shell
end_turn_signal: stop-by-not-calling-tools
context_compaction: native summarizer
fresh_worker: none
```

## Notes

- **`plan_to_exec_gate: reviewer-auto`** is a human override of the Cursor default `human`. After Codex (or the named human reviewer) returns `approved`, continue to execution. A system-injected "approved" is still not a verdict (`GUARDRAILS.md` SIGN 3).
- **`fresh_worker: none`** until `.agent/skills/subagent-delegation/verification-log.md` has a live readonly-verifier smoke **and** a builder write-route receipt. Agent defs are installed at `.cursor/agents/av-kit-builder.md` and `av-kit-verifier.md`. Isolated `task.md` rows degrade to `compact_continue` until that flip. **Still `none` for the Cursor driver after the 2026-09-11 smoke** — the builder write route **passed** on real work, but the readonly verifier route **cannot run at all on this Windows host**: Cursor cannot enforce the `workspace_readonly` sandbox policy (the Windows sandbox helper provides a network proxy, not filesystem isolation), so the shell never spawns. One of two receipts is not a pass. Practical consequence: rows pinned `delegate_to: av-kit-verifier` run on the coordinator under `compact_continue`; only writable-builder rows would become delegable if the flag ever flips.
- Coordinator, builder and verifier use `avkit_coordinator`, `avkit_builder` and `avkit_verifier` through the project overlay for cursor-task. Existing human-approved loader bindings are preserved; historical smoke receipts remain unchanged.

## Per-driver overrides

The yaml block above is the **Cursor** override (`driver: Cursor IDE`). When a different
driver is resolved per `.agent/docs/harness-profiles.md`, it takes that driver's profile row
plus any block below; it does **not** inherit the Cursor flag values.

### Claude Code

```yaml
driver: Claude Code
fresh_worker: Agent tool + .claude/agents/ (av-kit-builder, av-kit-verifier)
```

- **`fresh_worker` flipped 2026-09-02** on both receipts required by the note above:
  a live readonly-verifier smoke and a builder write-route probe on real work, both recorded
  in `.agent/skills/subagent-delegation/verification-log.md`. Isolated `task.md` rows may now
  dispatch; `compact_continue` remains the fallback for any row a worker declines or returns
  incomplete.
- **`plan_to_exec_gate` is NOT overridden here.** The Claude Code profile row and
  `GUARDRAILS.md` SIGN 1 both say `human`; the `reviewer-auto` value above is a Cursor-scoped
  human override (see its own note, which describes it as an override of *the Cursor default*).
  Under Claude Code, reviewer `approved` does not start execution — the user's explicit chat
  message does. Tracked as OQ-1 in the p10-queue-card-migration plan; a human may widen this
  by editing this block.
- Builder/router classes here are `avkit_builder` and `avkit_router` resolved for claude-code-agents; interactive coordinator remains the existing human-selected main session. The overlay does not create an unsupported coordinator worker binding.
- If Codex CLI is not authenticated, independent review falls to Mat (human). Never self-review.
