# Phase 8 — Video conversion — Session MEU Grouping Proposal

> **Source:** [BUILD_PLAN.md](../../../docs/BUILD_PLAN.md) · [08-video-conversion.md](../../../docs/build-plan/08-video-conversion.md) · [00–07 pointers](../../../docs/build-plan/) · [build-priority-matrix.md](../../../docs/build-plan/build-priority-matrix.md) · [_video_conversion_pseudo_logic.md](../../../_inspiration/_video_conversion_pseudo_logic.md)
> **Generated:** 2026-08-24
> **Method:** Stage A decompose/register from deferred ConversionJob GUI + inspiration; Stage B dependency-first grouping. Calibrated against av-kit `p3-services`, `p5-mcp-server`, `p6-gui-downloader`.
> **Origin:** USER_EXPLICIT 2026-08-24 — read conversion inspiration, review GUI, Krug layout, update BUILD_PLAN, create `docs/build-plan` spec. Un-defers ConversionJob GUI.
> **Status: Active** — reversible PLANNING draft, **not a gate**. Feeds `/create-plan`; introduces no HARD stop and no turn-ender.

This workstream is **separate** from Session 12 `p7-distribution`. That session’s “do not invent MEU IDs / do not rewrite FastAPI/MCP” applied to distribution only. Phase 8 registers MEU-28–33 here via `/session-grouping` Stage A.

---

## Progress (execution, not grouping redesign)

| Session | Slug | Status | Plan folder | Notes |
|---------|------|--------|-------------|-------|
| 12 | `p7-distribution` | ✅ complete | `docs/execution/plans/2026-08-24-p7-distribution/` | MEU-24–25 `approved`. Exec r2. USER_EXPLICIT 2026-08-24 started Phase 8 Session 13. |
| 13 | `p8-conversion-engine` | ✅ complete | `docs/execution/plans/2026-08-24-p8-conversion-engine/` | Exec r2 `approved`. MEU-28–30. Do not pack MEU-31–33. Session 8c complete. |
| 14 | `p8-conversion-api-mcp` | ✅ complete | `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/` | Exec r2 `approved`. MEU-31–32. Do not pack MEU-33. Session 8c complete. |
| 15 | `p8-conversion-gui` | ✅ complete | `docs/execution/plans/2026-08-26-p8-conversion-gui/` | Exec r2 `approved`. MEU-33. Session 8c complete. |

---

## 1 · MEU / Scope Summary

| MEU | Slug | Covers (spec / findings) | Layer | Depends on |
|-----|------|--------------------------|-------|------------|
| MEU-28 | `domain-conversion` | 08 §Domain — enums, ConversionJob, GPUCapabilities, additive MediaPort; TTS/download `convert()` unchanged | Domain | MEU-4 |
| MEU-29 | `infra-conversion` | 08 §Infrastructure — `conversion_jobs`, FFmpeg encode/cut/extract/gpu/progress | Infra | MEU-28, MEU-5, MEU-8 |
| MEU-30 | `svc-conversion` | 08 §Service — sequential queue, skip/suffix, pause/cancel | Service | MEU-29 |
| MEU-31 | `api-conversion` | 08 §REST — `/conversions`, `converter` settings, OpenAPI | API | MEU-30, MEU-14 |
| MEU-32 | `mcp-convert` | 08 §MCP — `avkit_convert` compound + confirm | MCP | MEU-31, MEU-17 |
| MEU-33 | `gui-convert` | 08 §Convert page — rail below TTS, Krug/Downloader layout, Wave 8 | GUI | MEU-31, MEU-19, MEU-26 |

**Traceability (inspiration / Krug / GUI review → MEU):**

| Finding | MEU |
|---------|-----|
| Bulk compress + GPU + CQ presets | 28–30, 33 |
| Cut in/out + extract audio | 28–30, 33 |
| Sequential GPU (one FFmpeg) | 30 |
| No ConversionJob for TTS MP3 | 28, 30 |
| Don’t Make Me Think: one rail item, presets, progressive disclosure, Downloader conventions | 33 |
| M2 REST↔MCP parity | 31, 32 |
| Eighth table, no STI `jobs` | 29 |
| Named deferrals (timeline, 2-pass, size-target, Downloader handoff) | not MEUs |

---

## 2 · Dependency Graph + Critical Path

```
MEU-4 (ports exist)
  └─► MEU-28 domain-conversion
        └─► MEU-29 infra-conversion  ◄── MEU-5, MEU-8
              └─► MEU-30 svc-conversion
                    └─► MEU-31 api-conversion  ◄── MEU-14
                          ├─► MEU-32 mcp-convert  ◄── MEU-17
                          └─► MEU-33 gui-convert  ◄── MEU-19, MEU-26
```

**Critical path:** MEU-28 → 29 → 30 → 31 → 33.

**Parallel after MEU-31:** MEU-32 (MCP) and MEU-33 (GUI) do not depend on each other. Prefer MCP before GUI if one session must own both (smaller than a GUI page). This grouping puts them in **separate** sessions.

---

## 3 · Recommended grouping — 3 sessions (fan-out exception)

Single-plan-per-phase would pack domain through GUI like a mini Phase 1–6 and exceed a comfortable session (calibrate vs `p3-services` + `p6-gui-downloader` combined). Fan-out is the documented exception.

### Session 13 — `p8-conversion-engine`  ✅ complete

- **MEUs:** MEU-28, MEU-29, MEU-30
- **Layer/files:** `packages/core` domain/ports/services; `packages/infrastructure` media adapter + `conversion_jobs` + UoW
- **Why grouped:** One FFmpeg worker cannot be tested at the API without the entity/table/service. Shared files (`media.py`, adapter). Same as bundling download domain+adapter+service would have been — here the YouTube stack already exists so this slice is conversion-only.
- **Token est:** calibrate vs **`p3-services`** (MEU-10–13, four services) — this session is three MEUs on one worker; slightly smaller.
- **Split flag:** split if encode+GPU detection balloons; keep domain+table together.

### Session 14 — `p8-conversion-api-mcp`  ✅ complete

- **MEUs:** MEU-31, MEU-32
- **Layer/files:** `packages/api` conversions router/schemas; `mcp-server` `avkit_convert`; OpenAPI
- **Why grouped:** M2 parity in one pass (same as `p5-mcp-server` after REST).
- **Token est:** calibrate vs **`p5-mcp-server`** (MEU-17–18) — one resource, not six tools.
- **Split flag:** no.

### Session 15 — `p8-conversion-gui`  ✅ complete

- **MEUs:** MEU-33
- **Layer/files:** `ui/` NavRail, router, `features/converter/`, Help, settings card, E2E Wave 8, action index audit
- **Why grouped:** One page = one GUI session (Local Canon `p6-gui-downloader` / transcript / TTS).
- **Token est:** calibrate vs **`p6-gui-downloader`** (MEU-20).
- **Split flag:** no.

---

## 4 · Plan-creation pathway

Ordered `/create-plan` invocations (do not skip):

1. `/create-plan p8-conversion-engine` — after Session 12 `p7-distribution` is `[x]`/`approved` **or** the human explicitly overlaps them.
2. `/create-plan p8-conversion-api-mcp`
3. `/create-plan p8-conversion-gui`

Default single-plan-per-phase is **not** used.

---

## 5 · Prerequisite gate

| Blocked on | Can begin now |
|------------|----------------|
| Session 13 blocked on p7 **only if** both would edit `packages/infrastructure` FFmpeg bundle/adapter in the same sitting. Spec writing is done. Implementation of MEU-28 can proceed after p7 or with a human overlap waiver. | Spec + MEU registration (this document). |

---

## 6 · Session summary roll-up

| Order | Slug | MEUs | `/create-plan` |
|------:|------|------|----------------|
| 13 | `p8-conversion-engine` | 28–30 | `/create-plan p8-conversion-engine` |
| 14 | `p8-conversion-api-mcp` | 31–32 | `/create-plan p8-conversion-api-mcp` |
| 15 | `p8-conversion-gui` | 33 | `/create-plan p8-conversion-gui` |

---

## 7 · Token calibration sources

- Engine: `docs/execution/plans/2026-08-19-p3-services/`
- API+MCP: `docs/execution/plans/2026-08-19-p5-mcp-server/`
- GUI: `docs/execution/plans/2026-08-20-p6-gui-downloader/`

---

## 8 · Open decisions for the human (feeds `/create-plan` Step 2B)

Locked in the Phase 8 spec (sources cited there). Confirm or override before Session 13:

1. **Rail label `Convert`** (not Converter) — Krug short intent label.
2. **One `ConversionJob` table** with `kind`, not three entities.
3. **Numeric in/out**, no timeline player in MVP.
4. **Software fallback** if bundled FFmpeg lacks NVENC — not a p7 ship-gate.
5. **Start Phase 8 implementation after p7**, unless you say to overlap.
