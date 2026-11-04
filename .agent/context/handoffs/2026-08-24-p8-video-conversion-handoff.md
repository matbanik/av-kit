---
date: "2026-08-24"
project: "p8-video-conversion"
meu: "MEU-28–33"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/build-plan/08-video-conversion.md"
build_plan_section: "bp08"
agent: "cursor-grok-4.6"
reviewer: "none (planning spec; no implementation-plan.md)"
predecessor: "none"
---

# Handoff: 2026-08-24-p8-video-conversion-handoff

> **Status**: `complete` (spec + MEU registration only)
> **Action Required**: `VALIDATE_AND_APPROVE` (human: confirm layout/locks; then `/create-plan p8-conversion-engine` after p7)

---

## Scope

**MEU**: MEU-28–33 — Phase 8 Convert (domain through GUI spec). No production code.
**Build Plan Section**: [08-video-conversion.md](../../docs/build-plan/08-video-conversion.md)
**Predecessor**: none (un-defers ConversionJob GUI)

---

## Acceptance Criteria

Planning session — ACs are **specified**, not implemented. Implementation ACs land in `/create-plan` FICs.

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-S1 | spec | Convert rail item below TTS, `/convert`, Ctrl+4 | Human-approved + Local Canon 06-gui | — | ✅ specified |
| AC-S2 | spec | Downloader-shaped queue; one page; Compress/Cut/Extract segments | Research-backed Krug + Local Canon Downloader | — | ✅ specified |
| AC-S3 | spec | Five named presets, default Balanced; FFmpeg flags not on default surface | Spec inspiration + Krug | — | ✅ specified |
| AC-S4 | spec | One `ConversionJob` table (`kind`); TTS/download `MediaPort.convert` unchanged | Local Canon Phase 1 + 2026-08-24 reversal | — | ✅ specified |
| AC-S5 | spec | REST `/conversions` envelope + MCP `avkit_convert` + settings `converter` | Local Canon 04/05 | — | ✅ specified |
| AC-S6 | spec | MEU-28–33 registered; grouping fan-out 13–15 | Local Canon session-grouping | `meu_status.py render --check` | ✅ specified |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| n/a | Planning-only; no TDD this session | — | — |

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| `rtk proxy uv run python tools/meu_status.py render` | 0 | Loaded 33 MEUs across 9 phases; regions rendered |
| `rtk proxy uv run python tools/meu_status.py render --check` | 0 | Drift check passed — 33 MEUs, 9 phases |

### Quality Gate Results

```
pyright: not run (no production code)
ruff: not run
pytest: not run
anti-placeholder: n/a
meu_status render --check: pass
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `docs/build-plan/08-video-conversion.md` | new | full | Phase 8 SSOT |
| `docs/BUILD_PLAN.md` | modified | thesis, phases, locks, inspiration | Index Phase 8; un-defer Convert GUI |
| `docs/build-plan/00-overview.md`–`07-distribution.md` | modified | addenda | Pointers; no silent contradiction |
| `docs/build-plan/build-priority-matrix.md` | modified | 8.1–8.6 | MEU order |
| `docs/build-plan/gui-actions-index.md` | modified | nav + convert:* | Action canon |
| `.agent/context/meu-status.yaml` | modified | phase 8 + MEU-28–33 | SSOT |
| `.agent/context/grouping/2026-08-24-p8-video-conversion-session-grouping.md` | new | full | Fan-out 13–15 |
| `.agent/context/current-focus.md` | modified | full | Spec registered; p7 still in flight |

```diff
- Deferred | … ConversionJob GUI
+ Convert GUI | Rail Convert below TTS; Downloader-shaped queue; preset-first
```

---

## Codex Validation Report

_Left blank. session-grouping is not a SIGN 1 plan review. Phase 8 spec has not been independently Codex-reviewed._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Run all Commands Executed and compare output
4. Run Quality Gate commands independently
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| — | — | No independent review this session | — | Optional: Codex read of `08-video-conversion.md` before Session 13 | open |

### Verdict

`n/a` — planning spec; no `/validation-review` dispatched (self-review prohibition; grouping workflow forbids review dispatch).

---

## Corrections Applied (2026-08-24)

_None._

**Findings resolved**: 0/0

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| — | — | — | — |

---

## Deferred Items

| Item | Reason | Deferred-to MEU (scheduled) | Follow-up |
|------|--------|-----------------------------|-----------|
| Timeline player, 2-pass, size-target, split, subtitle extract, Downloader→Convert handoff | Named Phase 8 deferrals (Krug + do not reopen MEU-20) | not an MEU (grouping named deferrals) | `08-video-conversion.md` §Integration |
| Implementation MEU-28–33 | PLANNING only | MEU-28 then 29–33 | `/create-plan p8-conversion-engine` after p7 |
| Independent Codex review of Phase 8 spec | Not SIGN 1 (no implementation-plan.md) | — | Human may request spec review |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-24 | cursor-grok-4.6 | Phase 8 spec + MEU registration |
