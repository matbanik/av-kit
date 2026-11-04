# Phase 1–7 — Approved BUILD_PLAN — Session MEU Grouping Proposal

> **Source:** [BUILD_PLAN.md](../../../docs/BUILD_PLAN.md) · [00–07 phase specs](../../../docs/build-plan/) · [build-priority-matrix.md](../../../docs/build-plan/build-priority-matrix.md) · Codex r4 `approved` ([plan-critical-review.md](../handoffs/2026-08-18-build-plan-plan-critical-review.md))
> **Generated:** 2026-08-18
> **Method:** Stage A decompose/register from empty `meus: []`, then Stage B dependency-first grouping. Calibrated against zorivest `p15c-risk-lens-correctness`, `p13-tui-mvp`, `p15b-help-search`, `2026-07-28-mcp-issues`, `p27-desktop-distribution` (no av-kit prior sessions exist).
> **Origin:** User “start the session grouping” after independent r4 `approved` on Phase 0–7.
> **Status: Active** — reversible PLANNING draft, **not a gate**. Feeds `/create-plan`; introduces no HARD stop and no turn-ender.

## Progress (execution, not grouping redesign)

| Session | Slug | Status | Plan folder | Notes |
|---------|------|--------|-------------|-------|
| 1 | `p1-domain-foundation` | ✅ complete | `docs/execution/plans/2026-08-18-p1-domain-foundation/` | Codex plan r3 + exec r2 `approved`; MEU-1–4 `approved`; 44 unit tests |
| 2 | `p2-persistence-io` | ✅ complete | `docs/execution/plans/2026-08-19-p2-persistence-io/` | Plan Codex r4 + exec r2 `approved`; MEU-5 + MEU-8 `approved`; 74 tests |
| 3 | `p2-external-adapters` | ✅ complete | `docs/execution/plans/2026-08-19-p2-external-adapters/` | Plan Codex r4 + exec r2 `approved`; MEU-6/7/9 `approved`; 113 tests |
| 4 | `p3-services` | ✅ complete | `docs/execution/plans/2026-08-19-p3-services/` | Plan r2 + exec r2 `approved`; MEU-13/10/11/12 `approved`; 181 tests |
| 5 | `p4-rest-api` | ✅ complete | `docs/execution/plans/2026-08-19-p4-rest-api/` | Plan Codex r5 + exec r2 `approved`; MEU-14–16 `approved`; 109 API/G29 tests. Dual Bearer + `ERROR_ENVELOPE` + empty-ID 422 + reorder oracles + committed OpenAPI. |
| 6 | `p5-mcp-server` | ✅ complete | `docs/execution/plans/2026-08-19-p5-mcp-server/` | Plan Codex r3 + exec r2 `approved`. MEU-17/18 `approved`. 141 vitest; 290 Python regression. |
| 7 | `p6-gui-shell` | ✅ complete | `docs/execution/plans/2026-08-19-p6-gui-shell/` | Plan Codex r3 + exec r2 `approved`. MEU-19 `approved`. 29 vitest; Playwright 10; pytest 298. Do not start Sessions 8–12 until `/create-plan p6-gui-downloader`. |
| 8 | `p6-gui-downloader` | ✅ complete | `docs/execution/plans/2026-08-20-p6-gui-downloader/` | Plan Codex r5 + exec r2 `approved`. MEU-20 `approved`. 60 vitest; Playwright 16; pytest 298. Do not start Sessions 9–12 until `/create-plan p6-gui-transcript`. |
| 8b | `p6-gui-zorivest-chrome` | ✅ complete | `docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/` | Plan Codex r3 + exec r2 `approved`. MEU-26 `approved`. 85 vitest; Playwright 22; pytest 298. Chrome stays; do not rewind. |
| 8c | `p6-gui-console-polish` | ✅ complete | `docs/execution/plans/2026-08-20-p6-gui-console-polish/` | Plan Codex r3 + exec r3 `approved`. MEU-27 `approved`. USER_EXPLICIT 2026-08-27 after Sessions 9–18. 234 vitest; Playwright 24; pytest 375. |
| 9 | `p6-gui-transcript` | ✅ complete | `docs/execution/plans/2026-08-20-p6-gui-transcript/` | Plan Codex r3 + exec r1 `approved`. MEU-21 delivered `/transcript` cards/tree/palette/Wave 2. 117 vitest; Playwright 30; pytest 298. Chrome stayed. |
| 10 | `p6-gui-tts-models` | ✅ complete | `docs/execution/plans/2026-08-20-p6-gui-tts-models/` | Plan Codex r4 + exec r2 `approved`. MEU-22 TTS/models page + Wave 2. 141 vitest; Playwright 6 TTS; pytest 298. |
| 11 | `p6-gui-settings-help` | ✅ complete | `docs/execution/plans/2026-08-21-p6-gui-settings-help/` | Plan Codex r3 + exec r3 `approved`. MEU-23 Settings/Help/IPC + Wave 4/6. 165 vitest; Playwright Wave4/6 6; pytest 298. Do not start MEU-24–25. |
| 12 | `p7-distribution` | ✅ complete | `docs/execution/plans/2026-08-24-p7-distribution/` | Plan Codex r3 + exec r2 `approved`. MEU-24/25 `approved`. Real onedir + NSIS (288,524,010 bytes). Session 8c ✅ complete. |
| 12b | `p6-gui-login-item` | ✅ complete | `docs/execution/plans/2026-09-20-p6-gui-login-item/` | Plan Codex r2 + exec r3 `approved`. MEU-61 per-user login item (not WinSW). Does not replace hub Next MEU-50. |

---

## 1 · MEU / Scope Summary

Phase 0 is spec-only (diagram + golden rules). No Phase 0 MEU.

| MEU | Slug | Covers (spec / review locks) | Layer | Depends on |
|-----|------|------------------------------|-------|------------|
| MEU-1 | `domain-scaffold` | 01 §Package layout; uv/core test harness | Domain scaffold | — |
| MEU-2 | `domain-enums-vos` | 01 §Enums + session VOs (QueueRuntime, SABR, ModelDownloadRuntime) | Domain | MEU-1 |
| MEU-3 | `domain-entities` | 01 persistable jobs/items/archive/settings; no `video_ids` column | Domain | MEU-2 |
| MEU-4 | `domain-ports-errors` | 01 ports + errors (A2: AgeRestrictedError, SABRDetectedError) | Domain | MEU-2, MEU-3 |
| MEU-5 | `infra-sqlite-uow` | 02 DB/ORM/UoW; WAL = API request + worker (A12) | Infra | MEU-4 |
| MEU-6 | `infra-youtube` | 02 yt-dlp, cookies, SABR, AgeRestricted | Infra | MEU-4 |
| MEU-7 | `infra-transcript` | 02 youtube-transcript-api; None = skip | Infra | MEU-4 |
| MEU-8 | `infra-filesystem-media` | 02 FS compile-only `read_text` (R2-6); FFmpeg setting→bundle→PATH | Infra | MEU-4 |
| MEU-9 | `infra-tts-models` | 02 Kokoro + HF catalog; no ModelFetchJob | Infra | MEU-4 |
| MEU-10 | `svc-download` | 03 DownloadService + session pause/SABR/apply-defaults | Service | MEU-5, 6, 8 |
| MEU-11 | `svc-transcript` | 03 start/resume/retry/Stop (R2-3); compile/zip | Service | MEU-5, 6, 7, 8 |
| MEU-12 | `svc-tts-models` | 03 prepare + TTS `text` body + ModelDownloadRuntime | Service | MEU-5, 8, 9 |
| MEU-13 | `svc-settings-health` | 03 leaf settings; HealthService sole `seq` (R2-4) | Service | MEU-5, 8 |
| MEU-14 | `api-app-auth` | 04 factory, dual Bearer, envelopes, extra=forbid | API | MEU-10–13 |
| MEU-15 | `api-downloads-health-settings` | 04 download/SABR/cookies/apply-defaults/health/settings | API | MEU-14 |
| MEU-16 | `api-transcripts-tts-models` | 04 transcript/TTS/models + OpenAPI | API | MEU-14 |
| MEU-17 | `mcp-runtime` | 05 discovery; token; no SQLite (A12) | MCP | MEU-14 |
| MEU-18 | `mcp-tools` | 05 compound `avkit_*`; REST parity | MCP | MEU-17, 15, 16 |
| MEU-19 | `gui-shell` | 06 single-instance + live-identity (R2-1); IPC (R2-5); apiFetch | GUI | MEU-14 |
| MEU-20 | `gui-downloader` | 06 downloader page + Query v5 `{items, processor}` | GUI | MEU-19, 15 |
| MEU-26 | `gui-chrome-zorivest` | 06 rail/header/right console chrome (Zorivest look) | GUI | MEU-19, 20 |
| MEU-21 | `gui-transcript` | 06 cards + tree at `output_dir` (R3-1) | GUI | MEU-19, 16 |
| MEU-22 | `gui-tts-models` | 06 TTS/models; `~/Documents` (R3-2); dialog file-load | GUI | MEU-19, 16 |
| MEU-23 | `gui-settings-help` | 06 settings Browse (A8); copy MCP (R2-2); HelpCards; action audit | GUI | MEU-19–22 |
| MEU-61 | `gui-login-item` | 06 §Startup login item; OS Run key; NSIS DeleteRegValue | GUI | MEU-23, MEU-25 |
| MEU-24 | `dist-backend` | 07 onedir + descriptor; no attach; no secrets in file | Dist | MEU-14, 19 |
| MEU-25 | `dist-installer` | 07 NSIS + FFmpeg + MCP ship | Dist | MEU-24, 17 |

**Traceability (review → MEU):** A1/R2-1 → MEU-19, MEU-24. A2 → MEU-4, MEU-6. A8/R2-7 → MEU-23 (+ route MEUs 15–16). A12 → MEU-5, MEU-17. R2-2 → MEU-17, MEU-23, MEU-25. R2-3 → MEU-11. R2-4 → MEU-13, MEU-19. R2-5 → MEU-19. R2-6 → MEU-4, MEU-8, MEU-12. R2-8 → MEU-19, MEU-24. R3-1 → MEU-11, MEU-21. R3-2 → MEU-22, MEU-23.

Named deferrals are **not** MEUs: SSE, OCR Part 1, multi-file TTS, MCP Guard. **ConversionJob GUI was un-deferred 2026-08-24** — see [2026-08-24-p8-video-conversion-session-grouping.md](2026-08-24-p8-video-conversion-session-grouping.md) (MEU-28–33).

---

## 2 · Dependency Graph + Critical Path

```
MEU-1 scaffold
  └─► MEU-2 enums/VOs
        ├─► MEU-3 entities
        └─► MEU-4 ports/errors  ◄── MEU-3
              │
              ├─► MEU-5 sqlite/UoW ─┐
              ├─► MEU-6 youtube     │
              ├─► MEU-7 transcript  │  (parallel after MEU-4)
              ├─► MEU-8 fs/media    │
              └─► MEU-9 tts/models ─┘
                    │
     MEU-10 download  ◄── 5,6,8
     MEU-11 transcript ◄── 5,6,7,8
     MEU-12 tts/models ◄── 5,8,9
     MEU-13 settings/health ◄── 5,8
                    │
                    ▼
              MEU-14 api-app-auth
                 ├─► MEU-15 download/health/settings routes
                 ├─► MEU-16 transcript/tts/models routes
                 ├─► MEU-17 mcp-runtime ──► MEU-18 mcp-tools (needs 15+16)
                 └─► MEU-19 gui-shell
                        ├─► MEU-20 downloader (needs 15)
                        ├─► MEU-21 transcript (needs 16)     ║ parallel pages
                        └─► MEU-22 tts/models (needs 16)     ║
                               └─► MEU-23 settings/help/audit
                                      │
              MEU-24 dist-backend ◄── 14,19
              MEU-25 dist-installer ◄── 24,17
```

**Critical path:** MEU-1 → 2 → 3 → 4 → 5 → (10 ∥ 11 ∥ 12 ∥ 13) → 14 → 19 → 20 → 23 → 24 → 25.

**Parallel tiers:**
- After MEU-4: MEU-5 / 6 / 7 / 8 / 9 (session grouping still does 5+8 before 6+7+9 for local-IO first).
- After MEU-5+8: MEU-10 / 11 / 12 / 13.
- After MEU-14: MEU-15 ∥ MEU-16; MEU-17 ∥ MEU-19.
- After MEU-19+16: MEU-21 ∥ MEU-22.

---

## 3 · Recommended Grouping — 12 Sessions

Default is **one `/create-plan` per phase**. Documented exceptions: **Phase 2** (two sessions — SQLite/FFmpeg vs network/ML adapters) and **Phase 6** (five sessions — empty `ui/`, one page per pass).

### Session 1 · `p1-domain-foundation`  ✅ complete (2026-08-19)
**MEU-1–4** · Phase 1 · `packages/core` + `tests/unit`

| Attribute | Detail |
|-----------|--------|
| Why grouped | One TDD vocabulary: scaffold → types → entities → ports. Shared files (`avkit_core/`). |
| Token est. | Calibrate vs zorivest **p15c Session 1** (domain/engine types, no GUI). |
| Split flag | If context > ~50% after MEU-3, park MEU-4 for a short follow-on — unlikely. |

### Session 2 · `p2-persistence-io`  *(Phase 2 exception)*  ✅ complete (2026-08-19)
**MEU-5, MEU-8** · SQLite UoW + filesystem + FFmpeg

| Attribute | Detail |
|-----------|--------|
| Why grouped | Local IO only; same `{app_data}` / probe-order concerns; unblocks every service. |
| Token est. | Calibrate vs zorivest **p13 Session 1** (empty-package persistence/scaffold analog). |
| Split flag | No. |

### Session 3 · `p2-external-adapters`  *(Phase 2 exception)*  ✅ complete (2026-08-19)
**MEU-6, MEU-7, MEU-9** · yt-dlp, transcripts, Kokoro/HF

Plan Codex r4 + exec r2 `approved`. Adapters live under `avkit_infra/{youtube,transcript,tts,model_manager}`. Carry-forward: RULE-1 non-finite progress fields, RULE-2 cookie `CookieTestError` from `OSError`, RULE-3 PyTorch `.to(device).eval()`. Do not rewrite adapters in Session 4.

| Attribute | Detail |
|-----------|--------|
| Why grouped | External binaries/APIs; no mutual imports; same error-mapping discipline. |
| Token est. | Calibrate vs zorivest **p13 mid-track** (external client + adapter), not vs a UI host session. |
| Split flag | If Kokoro load work dominates, split MEU-9 into its own session. |

### Session 4 · `p3-services`  ✅ complete (2026-08-19)
**MEU-10–13** · Phase 3 (single-plan-per-phase)

Plan folder: `docs/execution/plans/2026-08-19-p3-services/`. Execution order delivered: MEU-13 → MEU-10 → MEU-11 → MEU-12. Services live in `avkit_core/services/` (not `packages/application`). Plan Codex r2 + exec r2 `approved`. MEU-13/10/11/12 `approved`. 181 tests. Carry-forward from Session 3 (RULE-1/2/3) plus Session 4 atomic `set_namespace`, Paused-stop, single-flight TTS/model download. Do not invent MEU IDs. Next is Session 5 `/create-plan p4-rest-api`.

| Attribute | Detail |
|-----------|--------|
| Why grouped | All services share UoW factory + ports; status machines are one contract. |
| Token est. | Calibrate vs zorivest **p13 multi-screen** session (several cooperating units). |
| Split flag | **Yes — 50% candidate.** Natural cut: finish MEU-13+10+11, continue MEU-12 next turn. |

### Session 5 · `p4-rest-api`  ✅ complete (2026-08-19)
**MEU-14–16** · Phase 4 (single-plan-per-phase)

Plan folder: `docs/execution/plans/2026-08-19-p4-rest-api/`. Execution order delivered: MEU-14 → MEU-15 → MEU-16. Plan Codex r5 + exec r2 `approved`. MEU-14/15/16 `approved`. 109 API/G29 tests. Carry-forward into Session 6: dual Bearer (`AUTH_TOKENS`; MCP uses the stable key, never the GUI nonce), `ERROR_ENVELOPE`, `Field(min_length=1)` on model IDs, reorder permutation oracles, `VOICES_FACADE`, `SETTINGS_UI_API_KEYS={theme}`, atomic `set_namespace`, Paused-stop, single-flight TTS/model download, RULE-1/2/3. Do not rewrite FastAPI routers. Do not invent MEU IDs. Next is Session 6 `/create-plan p5-mcp-server` (Session 7 may run in parallel).

| Attribute | Detail |
|-----------|--------|
| Why grouped | Factory + both router bundles + OpenAPI in one wire-shape freeze. |
| Token est. | Calibrate vs a zorivest Phase-4 route batch (mechanical once services exist). |
| Split flag | No. |

### Session 6 · `p5-mcp-server`  ✅ complete (2026-08-19)
**MEU-17–18** · Phase 5 · **parallel with Session 7** after Session 5

Plan folder: `docs/execution/plans/2026-08-19-p5-mcp-server/`. Execution order delivered: MEU-17 → MEU-18. USER_EXPLICIT 2026-08-19 started this session. Thin REST wrappers only — no SQLite, yt-dlp, or GUI files. Carry-forward from Session 5: MCP token ≠ GUI nonce; Zod `.strict()` mirrors `extra="forbid"`; empty `variant_id` rejected at the schema; list envelopes `{ items, processor }`; no transcript/media bytes in tool results. MEU-17: discovery/token/stdio client. MEU-18: 46-action `ACTION_INDEX`, `ZOD_STRICT_CENSUS`, confirm gate, `SETTINGS_SCHEMA_URI`. Plan Codex r3 + exec r2 `approved`. Exec r1 Highs (token redaction, registered M7, URL/schema_version) + Medium body oracle. 141 vitest; 290 Python regression. Do not invent MEU IDs. Next is Session 7 `/create-plan p6-gui-shell` in a **separate** plan.

| Attribute | Detail |
|-----------|--------|
| Why grouped | Runtime then tools; REST-only; no GUI files. |
| Token est. | Calibrate vs zorivest **2026-07-28-mcp-issues**. |
| Split flag | No. |

### Session 7 · `p6-gui-shell`  *(Phase 6 exception)*  ✅ complete (2026-08-20)
**MEU-19** · Electron main/preload/AppShell/console

Plan folder: `docs/execution/plans/2026-08-19-p6-gui-shell/`. USER_EXPLICIT 2026-08-19 started this session via `/create-plan p6-gui-shell`. Plan Codex r3 + exec r2 `approved`. MEU-19 `approved`. 29 vitest; Playwright 10; pytest 298. Carry-forward: GUI nonce ≠ MCP token; live-identity orphan reap (R2-1); allowlisted IPC (R2-5); `SHELL_HOME` is a skeleton, not DownloaderPage. Non-blocking residual: Vitest stays green if `boot()` drops `resolveBootIdentity` (exec r2 F7). Do not invent MEU IDs. Do not rewrite FastAPI or MCP tools. Do not start MEU-20–25 until `/create-plan p6-gui-downloader`.

| Attribute | Detail |
|-----------|--------|
| Why grouped | Live-identity + IPC security must land before any page. |
| Token est. | Calibrate vs zorivest **p15b Session 1** (UI foundation + first host), heavier on main-process. |
| Split flag | No — do not mix a page into this session. |

### Session 8 · `p6-gui-downloader`  *(Phase 6 exception)*  ✅ complete (2026-08-20)
**MEU-20** · Default route

Plan folder: `docs/execution/plans/2026-08-20-p6-gui-downloader/`. USER_EXPLICIT 2026-08-20 started this session via `/create-plan p6-gui-downloader`. Prerequisite MEU-19 `approved`. Carry-forward: GUI nonce ≠ MCP token; `{ items, processor }`; cookie radios persist via `PUT /settings/downloader`; `/` becomes DownloaderPage. Do not invent MEU IDs. Do not rewrite FastAPI or MCP tools. Do not start MEU-21–25 in this plan.

| Attribute | Detail |
|-----------|--------|
| Why grouped | First consumer of list envelopes + SABR/cookies; proves `apiFetch`. |
| Token est. | Calibrate vs zorivest **p15b Session 2** (single-host integration). |
| Split flag | No. |

### Session 8b · `p6-gui-zorivest-chrome`  *(Phase 6 chrome insert)*  ✅ complete
**MEU-26** · Shell chrome

Plan folder: `docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/`. USER_EXPLICIT 2026-08-20. Do not start MEU-21–25. `HUB_NEXT_AFTER` stays `/create-plan p6-gui-transcript`.

| Attribute | Detail |
|-----------|--------|
| Why grouped | Chrome look/feel is independent of Transcript/TTS page work. |
| Token est. | Calibrate vs zorivest layout chrome (NavRail + Header + Trade drawer). |
| Split flag | No. |

### Session 9 · `p6-gui-transcript`  *(Phase 6 exception)*  ✅ complete (2026-08-20)
**MEU-21** · Channel cards + output tree

Plan folder: `docs/execution/plans/2026-08-20-p6-gui-transcript/`. Plan Codex r3 + exec r1 `approved`. MEU-21 delivered cards/tree/palette/Wave 2. Do not invent MEU IDs. Do not rewrite FastAPI or MCP tools. Do not start MEU-22–25 from this session. Next: `/create-plan p6-gui-tts-models`.

| Attribute | Detail |
|-----------|--------|
| Why grouped | Distinct card/tree contract; do not mix with TTS in the first GUI wave. |
| Token est. | Calibrate vs **p15b Session 2**. |
| Split flag | No. |

### Session 10 · `p6-gui-tts-models`  *(Phase 6 exception)*  ✅ complete
**MEU-22** · TTS editor + Model Manager

Plan folder: `docs/execution/plans/2026-08-20-p6-gui-tts-models/`. Plan Codex r4 + exec r2 `approved`. MEU-22 `approved`. Carry-forward RULE-1/2/3 (catalog id map; E2E dialog stubs; Pending in ENABLED_WHEN). Next: `/create-plan p6-gui-settings-help`.

| Attribute | Detail |
|-----------|--------|
| Why grouped | Prepare pipeline + model manager + dialog file-load. |
| Token est. | Calibrate vs **p15b Session 2**. |
| Split flag | No. |

### Session 11 · `p6-gui-settings-help`  *(Phase 6 exception)*  ✅ complete
**MEU-23**

Plan folder: `docs/execution/plans/2026-08-21-p6-gui-settings-help/`. Plan Codex r3 + exec r3 `approved`. MEU-23 `approved`. Settings page leaves + Browse/MCP/readiness IPC + HelpCards + audit + Wave 4/6 (incl. W6-3 off-route help:toggle). 165 vitest; Playwright Wave4/6 6; pytest 298. Do not invent MEU IDs. Do not rewrite FastAPI or MCP tools. Do not rewind MEU-26 chrome. Do not start MEU-24–25. Next: `/create-plan p7-distribution`.

| Attribute | Detail |
|-----------|--------|
| Why grouped | Settings + HelpCards + bidirectional action audit need all pages present. |
| Token est. | Calibrate vs **p15b Session 2** + registration-audit tail of that phase. |
| Split flag | E2E-only tail may `[B]` on `E2E-SANDBOX-NODISPLAY` (write + wire; CI follow-up). |

### Session 12 · `p7-distribution`  ✅ complete
**MEU-24–25** · Phase 7

Plan folder: `docs/execution/plans/2026-08-24-p7-distribution/`. Plan Codex r3 + exec r2 `approved`. MEU-24 onedir COLLECT + READY smoke; MEU-25 NSIS extraResources + pinned FFmpeg + `bundled_ffmpeg()`. Do not invent MEU IDs. Do not rewrite FastAPI/MCP. Do not rewind chrome. Session 8c ✅ complete. `CLEAN_VM` remains a later `[B]`.

| Attribute | Detail |
|-----------|--------|
| Why grouped | Onedir descriptor then NSIS/FFmpeg/MCP payload — one ship gate. |
| Token est. | Calibrate vs zorivest **p27-desktop-distribution**. |
| Split flag | No. |

---

## 4 · Plan-Creation Pathway

Multi-session fan-out (exception to single-plan-per-phase) as listed. Run **in order**. After Session 5, Session 6 and Session 7 may proceed in **either order** or in parallel tracks (different packages).

| # | Invocation | MEUs | Build-plan sections |
|---|------------|------|---------------------|
| 1 | `/create-plan p1-domain-foundation` | MEU-1–4 | `01-domain-layer.md` |
| 2 | `/create-plan p2-persistence-io` | MEU-5, MEU-8 | `02-infrastructure.md` §Database, §Filesystem, §Media |
| 3 | `/create-plan p2-external-adapters` | MEU-6, MEU-7, MEU-9 | `02-infrastructure.md` §YouTube, §Transcript, §TTS, §Model manager |
| 4 | `/create-plan p3-services` | MEU-10–13 | `03-service-layer.md` |
| 5 | `/create-plan p4-rest-api` | MEU-14–16 | `04-rest-api.md` |
| 6 | `/create-plan p5-mcp-server` | MEU-17–18 | `05-mcp-server.md` |
| 7 | `/create-plan p6-gui-shell` | MEU-19 | `06-gui.md` §Startup, IPC, layout, console |
| 8 | `/create-plan p6-gui-downloader` | MEU-20 | `06-gui.md` §Downloader |
| 8b | `/create-plan p6-gui-zorivest-chrome` | MEU-26 | `06-gui.md` §Layout + console chrome |
| 9 | `/create-plan p6-gui-transcript` | MEU-21 | `06-gui.md` §Transcript |
| 10 | `/create-plan p6-gui-tts-models` | MEU-22 | `06-gui.md` §TTS |
| 11 | `/create-plan p6-gui-settings-help` | MEU-23 | `06-gui.md` §Settings + Help + `gui-actions-index.md` |
| 12 | `/create-plan p7-distribution` | MEU-24–25 | `07-distribution.md` |

Do **not** invent further MEU IDs in `/create-plan`. Scope comes from this table.

---

## 5 · Prerequisite Gate

| Prerequisite | Status | Blocks |
|--------------|:------:|--------|
| Phase 0–7 specs Codex r4 `approved` | ✅ | — |
| MEU-1–25 in `meu-status.yaml` | ✅ | — |
| Session 1 `p1-domain-foundation` | ✅ complete (2026-08-19) | Session 2 |
| Session 2 `p2-persistence-io` | ✅ complete (2026-08-19) | Session 3 |
| Session 3 `p2-external-adapters` | ✅ complete (2026-08-19) | Session 4 |
| Session 4 `p3-services` | ✅ complete (2026-08-19) | Session 5 |
| Session 5 `p4-rest-api` | ✅ complete (2026-08-19) | Session 6 or 7 |
| Session 6 `p5-mcp-server` | ✅ complete (2026-08-19) | Session 7 |
| Product packages (`packages/core`) | ✅ domain + `avkit_core/services/` (MEU-10–13 `approved`) | never import `avkit_infra` from core |
| `packages/infrastructure` | ✅ MEU-5–9 (`approved`) | later sessions may use adapters; do not rewrite them |
| `packages/application` | n/a — services live in `avkit_core/services/` | — |
| `packages/api` | ✅ MEU-14–16 (`approved`) | Session 6 MCP reuses `/api/v1`; do not rewrite routers |
| `mcp-server/` | ✅ MEU-17/18 `approved` | Session 7 may copy MCP token; do not rewrite tools |
| `ui/` | ✅ MEU-19 `approved` (Electron shell) | Sessions 8–12 pages |
| `triage-output.yaml` | n/a (empty known-issues) | — |

**Blocked on human:** none for Session 12 start. Do not invent MEU IDs. Do not commit without a user request.

---

## 6 · Session Summary

| Session | Slug | MEUs | Exception? |
|---------|------|------|:----------:|
| 1 | `p1-domain-foundation` | 1–4 | no |
| 2 | `p2-persistence-io` | 5, 8 | Phase 2 fan-out |
| 3 | `p2-external-adapters` | 6, 7, 9 | Phase 2 fan-out |
| 4 | `p3-services` | 10–13 | no (50% split candidate) |
| 5 | `p4-rest-api` | 14–16 | no |
| 6 | `p5-mcp-server` | 17–18 | no; ∥ Session 7 after 5 |
| 7 | `p6-gui-shell` | 19 | Phase 6 fan-out |
| 8 | `p6-gui-downloader` | 20 | Phase 6 fan-out |
| 8b | `p6-gui-zorivest-chrome` | 26 | Phase 6 chrome insert |
| 9 | `p6-gui-transcript` | 21 | Phase 6 fan-out |
| 10 | `p6-gui-tts-models` | 22 | Phase 6 fan-out |
| 11 | `p6-gui-settings-help` | 23 | Phase 6 fan-out |
| 12 | `p7-distribution` | 24–25 | no |

---

## 7 · Token Calibration Sources

| This session | Named peer |
|--------------|------------|
| S1 domain | zorivest `p15c-risk-lens-correctness` Session 1 |
| S2 persistence/IO | zorivest `p13-tui-mvp` Session 1 (empty-dir foundation) |
| S3 adapters | zorivest `p13-tui-mvp` mid-track client/adapter sessions |
| S4 services | zorivest `p13-tui-mvp` multi-unit session |
| S5 REST | zorivest Phase-4 route batches (create-plan Step 3 fallback) |
| S6 MCP | zorivest `2026-07-28-mcp-issues-session-grouping` |
| S7–S11 GUI | zorivest `p15b-help-search` Sessions 1–2 |
| S12 dist | zorivest `p27-desktop-distribution-session-grouping` |

Do not treat those peers’ printed token counts as av-kit budgets (Opus 4.8 tokenizer inflation). Use them as **shape** only.

---

## 8 · Open Decisions (for `/create-plan` Step 2B)

None that block Session 6. Recorded choices:

1. Session 4 completed in one plan (no 50% split). Carry-forward: atomic `set_namespace`, Paused-stop, single-flight TTS/model download.
2. After Session 5, Session 6 vs 7 order: **USER_EXPLICIT 2026-08-19** chose Session 6 (`p5-mcp-server`) first. Session 6 is complete. Session 7 started the same day via `/create-plan p6-gui-shell`.
3. GUI E2E un-run in the agent sandbox is `[B]` + CI (`E2E-SANDBOX-NODISPLAY`) per known-issue policy — not a grouping change.
4. **USER_EXPLICIT 2026-08-20** started Session 8 (`p6-gui-downloader`) after asking whether the blank window was expected. Completely empty chrome is **not** the Session 7 contract (nav/console/skeleton should show); an empty *downloader table* is expected until MEU-20 lands.
5. **USER_EXPLICIT 2026-08-20** started Session 9 (`p6-gui-transcript`) after Session 8b chrome `approved`. MEU-21 only; `HUB_NEXT_AFTER` becomes `/create-plan p6-gui-tts-models`.
6. **USER_EXPLICIT 2026-08-20** started Session 10 (`p6-gui-tts-models`, typed `p6-gui-tts-model`). MEU-22 only; `HUB_NEXT_AFTER` becomes `/create-plan p6-gui-settings-help`.
7. **USER_EXPLICIT 2026-08-21** started Session 11 (`p6-gui-settings-help`). MEU-23 only; `HUB_NEXT_AFTER` becomes `/create-plan p7-distribution`.
8. **USER_EXPLICIT 2026-08-24** started Session 12 (`p7-distribution`). MEU-24–25 only; `HUB_NEXT_AFTER` becomes `phase-7 complete`.
