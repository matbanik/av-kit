# Phase 9 — Screenshot capture — Session MEU Grouping Proposal

> **Source:** [BUILD_PLAN.md](../../../docs/BUILD_PLAN.md) · [09-screenshot-capture.md](../../../docs/build-plan/09-screenshot-capture.md) · [00–08 pointers](../../../docs/build-plan/) · [build-priority-matrix.md](../../../docs/build-plan/build-priority-matrix.md)
> **Date:** 2026-08-26
> **Origin:** USER_EXPLICIT 2026-08-26 — create Phase 9 build-plan in the Convert pattern (F2 region → inbox → filmstrip + annotate; GUI + MCP; tray).

This workstream is **separate** from Session 8c (`p6-gui-console-polish` / MEU-27), now ✅ complete.

## Sessions (proposed)

| # | Slug | Status | Plan folder | Notes |
|---|------|--------|-------------|-------|
| 16 | `p9-capture-engine` | ✅ complete | `docs/execution/plans/2026-08-26-p9-capture-engine/` | MEU-34–36. Do not pack MEU-37–39. Session 8c complete. |
| 17 | `p9-capture-api-mcp` | ✅ complete | `docs/execution/plans/2026-08-27-p9-capture-api-mcp/` | MEU-37–38. Do not pack MEU-39. Session 8c complete. |
| 18 | `p9-capture-gui` | ✅ complete | `docs/execution/plans/2026-08-27-p9-capture-gui/` | MEU-39 (tray + overlay + page). Session 8c complete. |

## MEUs

| MEU | Slug | Slice | Layer | Depends on |
|-----|------|-------|-------|------------|
| MEU-34 | `domain-capture` | 09 §Domain — enums, CaptureShot, CaptureRequest, ports | Domain | MEU-4 |
| MEU-35 | `infra-capture` | 09 §Infrastructure — tables + Pillow/mss adapter | Infra | MEU-34, MEU-5 |
| MEU-36 | `svc-capture` | 09 §Service — scan, interactive 409, bake, delete files | Service | MEU-35 |
| MEU-37 | `api-capture` | 09 §REST — `/captures`, `capture` settings, OpenAPI | API | MEU-36, MEU-14 |
| MEU-38 | `mcp-capture` | 09 §MCP — `avkit_capture` | MCP | MEU-37, MEU-17 |
| MEU-39 | `gui-capture` | 09 §GUI — tray, F2, overlay, rail, page, Wave 9 | GUI | MEU-37, MEU-19, MEU-26 |

```
MEU-4
  └─► MEU-34 domain-capture
        └─► MEU-35 infra-capture  ◄── MEU-5
              └─► MEU-36 svc-capture
                    └─► MEU-37 api-capture  ◄── MEU-14
                          ├─► MEU-38 mcp-capture  ◄── MEU-17
                          └─► MEU-39 gui-capture  ◄── MEU-19, MEU-26
```

**Critical path:** MEU-34 → 35 → 36 → 37 → 39.

### Session 16 — `p9-capture-engine`

- **MEUs:** MEU-34, MEU-35, MEU-36
- **Why grouped:** One bake/grab adapter cannot be tested at the API without the entity/table/service. Same split as `p8-conversion-engine`.

### Session 17 — `p9-capture-api-mcp`

- **MEUs:** MEU-37, MEU-38
- **Why grouped:** REST + compound MCP parity (same as `p8-conversion-api-mcp`).

### Session 18 — `p9-capture-gui`

- **MEUs:** MEU-39
- **Why grouped:** Tray/hotkey/overlay is Electron main; the page is the consumer. One GUI session like MEU-33, larger because of the OS surface.

## Order of `/create-plan`

1. `/create-plan p9-capture-engine` — after Phase 9 spec review (or human overlap).
2. `/create-plan p9-capture-api-mcp`
3. `/create-plan p9-capture-gui`

Do not pack Downloader→Convert. Session 8c / MEU-27 is complete.
