---
review_mode: implementation
target_plan: "docs/execution/plans/2026-08-19-p5-mcp-server/implementation-plan.md"
agent: gpt-5.6-sol
verdict: approved
findings_count: 0
round: 2
---

# Execution Critical Review: p5-mcp-server — Round 2

## Intent Anchor

Session 6 was intended to deliver MEU-17 and MEU-18 as a thin stdio MCP facade over the existing `/api/v1` surface: safe backend/token discovery, six compound tools with 46 strict actions, destructive confirmation, registered per-action guidance, and no direct infrastructure or GUI work. The current delivery achieves that intent, including the four round-1 correction surfaces, with the full registered MCP and Python regression gates green.

## Findings

| Finding | Severity |
|---|---|
| None. No evidence-backed Critical, High, Medium, or Low finding survived verification. | — |

No Critical or High findings exist in round 2.

## Scope

The correlated target is `docs/execution/plans/2026-08-19-p5-mcp-server/`, whose approved plan names exactly the MEU-17 and MEU-18 handoffs. This round reviewed both handoffs, the plan/task, `docs/build-plan/05-mcp-server.md`, the named-set locks, all files under `mcp-server/src/` and `mcp-server/tests/`, the registered Python regression surface, and the MEU/phase/Hub SSOT fields.

The workspace has no Git repository, so the review verifies current file state and fresh isolated receipts rather than historical diffs. The Session 6 scope lock remains intact: MEU-17 and MEU-18 only; no Session 7, GUI, FastAPI rewrite, infrastructure implementation, or invented MEU is part of this verdict.

## Round-1 Findings Recheck

| Finding | Result | Independent round-2 evidence |
|---|---|---|
| F1 — reflected env/file tokens in handler `TOOL_ERROR` text | Fixed | `mcp-server/src/config.ts:86-101` collects both secret sources; `mcp-server/src/client.ts:36-75,135-148` redacts public error/result text. The handler-shaped env and file reflection cases assert exact substring absence at `mcp-server/tests/client.test.ts:170,194`; `C:/Temp/av-kit/p5-mcp-exec-r2-f1-token-oracle.txt` reports 2 passed. |
| F2 — detached M7 descriptions | Fixed | Every action option is described (for example `mcp-server/src/toolsets/download.ts:60-61`), and registration publishes the 46-row `_meta.action_descriptions` map at `mcp-server/src/toolsets/registry.ts:246-257`. The registered-surface oracle at `mcp-server/tests/m7-resource.test.ts:57-76` verifies all 46 descriptions and at least three distinct M7 markers; `C:/Temp/av-kit/p5-mcp-exec-r2-f2-m7-oracle.txt` reports 1 passed. |
| F3 — malformed pin and unsupported descriptor schema consumed | Fixed | `mcp-server/src/config.ts:54-66` requires a parseable HTTP(S) API base, and `mcp-server/src/config.ts:69-80` rejects descriptor schema versions other than 1. `C:/Temp/av-kit/p5-mcp-exec-r2-f3-config-oracle.txt` reports both exact negative cases passed: malformed pin → `invalid_api_base`; schema 999 with no pin → `app_not_running`. |
| F4 — incomplete all-row body oracle | Fixed | `mcp-server/tests/fixtures.ts:169-228` defines an expected body for every action, including `undefined` for GET/DELETE, and `mcp-server/tests/action-index.test.ts:43-72` compares every actual body. `C:/Temp/av-kit/p5-mcp-exec-r2-f4-body-oracle.txt` reports all 46 rows passed. |

## IR-1–IR-7 Checklist

| Check | Result | Evidence |
|---|---|---|
| IR-1 — Live runtime evidence | Pass (contract-adapted) | The approved MCP contract requires mocked `fetch`, and the real SDK server is constructed/registered before handler calls traverse Zod → client → mocked HTTP. The retained Python composition-root smoke uses real temporary SQLite with no dependency overrides (`tests/integration/test_api_wiring.py:12-30`). Fresh gates: 141 Vitest and 290 Python tests passed. No prohibited live YouTube/HF/Kokoro call was made. |
| IR-2 — Stub behavioral compliance | N/A | The MCP package is a stateless HTTP facade and owns no repository/UoW/save-get stubs. Exact source scans find no direct SQLite or infrastructure implementation. |
| IR-3 — Error mapping completeness | Pass (contract-adapted) | MCP 422/409 envelopes and fetch failures become handler-shaped `TOOL_ERROR`; strict/confirm failures stop before fetch. The retained E2E suite covers route 404/409/422 behavior and passed in the 290-test regression receipt. |
| IR-4 — Fix generalization | Pass | F1 covers both token sources and both error/success sanitization paths; F2 covers all six schemas and 46 registered actions; F3 covers the sole descriptor reader and both pin/descriptor inputs; F4 covers all 46 rows. Repo-wide MCP scans found no sibling direct-library, placeholder, skip, deprecated registration, or stdio-noise instance. |
| IR-5 — Test rigor audit | Pass | Every in-scope test file was audited. No weak test remains; ratings are recorded below. The full suite passed 141/141. |
| IR-6 — Boundary validation coverage | Pass | All 46 action variants use strict schemas; the 46-row extra-key census and all destructive missing/false-confirm cases assert fetch count 0. Discovery URL/schema boundaries and settings/API error propagation have explicit negative tests. |
| IR-7 — Deferral and AC integrity | Pass | Corrected extraction reports MEU-17 plan/handoff 9/9 and MEU-18 14/14 with zero missing. Named Session 7+ deferrals remain scheduled in SSOT; sourced out-of-scope rows are not disguised skips. |

### IR-5 Per-File Test Ratings

| Test file | Rating | Rationale |
|---|---|---|
| `config.test.ts` | 🟢 Strong | Exact discovery precedence, stale pin, both token sources, malformed URL, unsupported descriptor version, and error codes. |
| `client.test.ts` | 🟢 Strong | Concrete Bearer, timeout, fetch count, public error shape, envelope mapping, and reflected env/file token absence assertions. |
| `runtime.test.ts` | 🟡 Adequate | Constructs the real MCP server and asserts required instructions; its local core-file scan is narrower than the independent raw all-source scan. |
| `action-index.test.ts` | 🟢 Strong | Exact 46-row tool/method/path/body census plus old-name and omitted-route rejection. |
| `strict-confirm.test.ts` | 🟢 Strong | All 46 extra-key cases, all four destructive missing/false-confirm cases, non-destructive stops, and empty variants assert behavior and fetch counts. |
| `tools-parity.test.ts` | 🟢 Strong | Concrete list envelopes, 422/409 text, forbidden-field stripping, voices path, reorder permutation, and settings-body assertions. |
| `m7-resource.test.ts` | 🟢 Strong | Verifies exported and registered 46-row descriptions, marker distinctness, `_meta` linkage, instructions, and the settings resource. |
| `fixtures.ts` | Support | Independent 46-row expected index, inputs, and exact expected-body oracle; not an executable suite by itself. |

## Adversarial Verification Checklist

| Check | Result | Evidence |
|---|---|---|
| AV-1 — Failing-then-passing proof | Pass | Both MEU handoffs retain Red evidence; the correction record identifies five failing correction tests before the fresh 141-test Green suite. Round 2 independently reran each corrected surface. |
| AV-2 — No bypass hacks | Pass | Full test audit found no early-return, assertion mocking, or catch-and-pass bypass. |
| AV-3 — Changed paths asserted | Pass | F1–F4 each have direct behavioral assertions on handler output, registered metadata, boundary return codes, or actual fetch bodies. |
| AV-4 — No skipped/xfail masking | Pass | `C:/Temp/av-kit/p5-mcp-exec-r2-scan-g36.txt` is a raw zero-match receipt. |
| AV-5 — No unresolved placeholders | Pass | `C:/Temp/av-kit/p5-mcp-exec-r2-scan-placeholders.txt` is a raw zero-match receipt. |
| AV-6 — Source-backed criteria | Pass | All delivered behavior traces to the approved plan/spec/local-canon locks; this round adds no product requirement. |

## Contract Surfaces Confirmed

- Discovery/token: invalid pins, schema-version rejection, stale-pin no-fetch, token precedence, missing-token no-fetch, liveness exemption, and reflected-token redaction all satisfy AC-17.1–17.7.
- `ACTION_INDEX`: registered compound tools and action options total exactly 6 and 46; every row asserts method, interpolated path, and exact request body. Old names and omitted routes are absent.
- Zod/confirm: the all-46 strict census and all four destructive actions reject before fetch; the three non-destructive stops work without `confirm`.
- Response parity: list envelope, 422/409 error envelope, reorder permutation, voices facade, settings behavior, and `FORBIDDEN_RESULT_FIELDS` pass.
- M7/resource: all 46 descriptions are attached to registered Zod options and `_meta.action_descriptions`, contain at least three distinct markers, and settings descriptions reference `avkit://settings/schema`.
- Registration/build: `registerTool()` and `registerResource()` are used; deprecated `.tool()` is absent; typecheck, build, and stdio-noise scans pass.
- Hexagonal/scope: the required raw `rg -n yt_dlp mcp-server/src` receipt is empty. Direct-library and placeholder scans are also empty. The runtime settings key remains `yt_dlp_debug` through the approved assembled leaf construction.
- SSOT: MEU-17/18 are `ready_for_review` with the no-slash plan path; phase `"5"` contains the slash path; Hub Next is exactly `` `/create-plan p6-gui-shell` ``; rendered regions are drift-free.

## Commands Executed

All verification commands used PowerShell all-stream redirects and fresh `C:/Temp/av-kit/p5-mcp-exec-r2-*` receipts.

| Command / probe | Exit | Receipt / result |
|---|---:|---|
| F1 reflected env/file token oracle | 0 | `p5-mcp-exec-r2-f1-token-oracle.txt`; 2 passed |
| F2 registered per-action M7 oracle | 0 | `p5-mcp-exec-r2-f2-m7-oracle.txt`; 1 passed |
| F3 malformed pin + schema-version oracle | 0 | `p5-mcp-exec-r2-f3-config-oracle.txt`; 2 passed |
| F4 all-row body oracle | 0 | `p5-mcp-exec-r2-f4-body-oracle.txt`; 46 passed |
| `npx tsc --noEmit` | 0 | `p5-mcp-exec-r2-tsc.txt`; no TypeScript errors |
| `npx vitest run` | 0 | `p5-mcp-exec-r2-vitest.txt`; 7 files, 141 tests passed |
| `npm run build` | 0 | `p5-mcp-exec-r2-build.txt`; `tsc -p tsconfig.json` |
| Registered Python regression command | 0 | `p5-mcp-exec-r2-python-regression.txt`; 290 passed, 1 deprecation warning |
| Raw `rg -n yt_dlp mcp-server/src` | 1 (clean) | `p5-mcp-exec-r2-scan-yt-dlp.txt`; zero matches |
| Direct-library scan | 1 (clean) | `p5-mcp-exec-r2-scan-direct-libs.txt`; zero matches |
| Placeholder scan | 1 (clean) | `p5-mcp-exec-r2-scan-placeholders.txt`; zero matches |
| G36 skip/todo scan | 1 (clean) | `p5-mcp-exec-r2-scan-g36.txt`; zero matches |
| Stdio-noise scan | 1 (clean) | `p5-mcp-exec-r2-stdio-noise-scan.txt`; zero matches |
| Registration API scan | 0 | `p5-mcp-exec-r2-registration-scan.txt`; `registerTool` + `registerResource`, no deprecated `.tool()` |
| Corrected per-MEU AC coverage oracle | 0 | `p5-mcp-exec-r2-ac-coverage-corrected.txt`; 9/9 and 14/14, none missing |
| SSOT / phase / Hub oracle | 0 | `p5-mcp-exec-r2-ssot-oracle.txt`; exact status and path values |
| `tools/meu_status.py render --check` | 0 | `p5-mcp-exec-r2-meu-render-check.txt`; 25 MEUs / 8 phases, no drift |
| Canonical-path pre-edit guard | 0 | `p5-mcp-exec-r2-pre-edit-guard.txt`; exact rolling path matched |
| `tools/check_exec_review.py --self-test` | 0 | `p5-mcp-exec-r2-review-self-test.txt`; checker self-test passed |
| Approved review contract check | 0 | `p5-mcp-exec-r2-review-check.txt`; mode/target/verdict/round accepted |
| Review frontmatter/marker/rolling-file oracle | 0 | `p5-mcp-exec-r2-review-structure.txt`; exact first contract block and one rolling file |

## Open Questions and Assumptions

- No human decision is required for the verdict. All four prior findings are fixed against their explicit approved-plan contracts.
- Mocked `fetch` is intentional and source-backed; live YouTube/HF/Kokoro behavior is excluded from this review.
- Current-file verification cannot establish historical authorship because the workspace is not a Git repository; it does establish the present delivered behavior.

## Verdict

`approved` — zero findings survived the generate→verify pass. All four round-1 findings are independently closed, all in-contract adversarial surfaces pass, and both complete registered gates are green.

No `/execution-corrections` follow-up is required. This reviewer does not mark task/SSOT rows, perform H2 closeout, or start Session 7.

## Residual Risk

Verification is bounded to the approved local mocked-HTTP contract and current filesystem state. No live external media/model service was exercised by design. No material in-contract residual risk remains.

---

## Prior Round 1 Record — 2026-08-19

# Execution Critical Review: p5-mcp-server

## Intent Anchor

Session 6 was intended to deliver MEU-17 and MEU-18 as a thin stdio MCP facade over the existing `/api/v1` surface: safe backend/token discovery, six compound tools with 46 strict actions, destructive confirmation, usable per-action guidance, and no direct infrastructure or GUI work. The delivered package is broadly functional and its registered gates are green, but it does not yet achieve that intent because two explicit agent-facing safety/usability contracts and one external-input boundary contract fail independent runtime probes.

## Findings

| Finding | Severity | Evidence and violated contract | Required follow-up |
|---|---|---|---|
| **F1 — A reflected bearer token is emitted verbatim in `TOOL_ERROR`.** `api()` retains the resolved token but passes an API envelope message through unchanged, and `toToolError()` concatenates that message without redaction. An independent 422-envelope probe containing the active token produced `validation_error: reflected ROUND1_SECRET_TOKEN` with `tokenPresent:true`. This violates AC-17.3's negative case and the locked rule that the token never appears in tool results/errors. A local backend or error middleware that reflects authorization context would disclose the MCP bearer secret to the IDE/model. | High | `mcp-server/src/client.ts:23-44`, `mcp-server/src/client.ts:63-81`, `docs/execution/plans/2026-08-19-p5-mcp-server/implementation-plan.md:219-220`, `docs/execution/plans/2026-08-19-p5-mcp-server/implementation-plan.md:260`; `C:/Temp/av-kit/p5-mcp-exec-r1-token-redaction-oracle-2.txt` (exit 1). The existing non-leak test only uses an envelope message that never contains the token (`mcp-server/tests/client.test.ts:124-143`), so it false-passes this contract. | Redact every resolved token source before any public error/result text is formed, and add env-token and file-token reflection cases that assert exact absence from the handler-shaped `TOOL_ERROR`. |
| **F2 — The 46 M7 action descriptions are detached data, not registered action metadata.** The module maps contain 46 strings, but the discriminated-union options have no Zod descriptions and `registerTool()` publishes only one compound-tool description. The registration oracle found `exportedDescriptionKeys:46`, `registeredActionOptions:46`, and `registeredActionDescriptions:0`. Thus an MCP client cannot discover the per-action Workflow/Prerequisite/Returns/Errors text required by `ACTION_DESCRIPTIONS` and AC-18.7. | High | `mcp-server/src/toolsets/registry.ts:95-120`, `mcp-server/src/toolsets/registry.ts:239-249`, `docs/execution/plans/2026-08-19-p5-mcp-server/implementation-plan.md:128-130`, `docs/execution/plans/2026-08-19-p5-mcp-server/implementation-plan.md:322`; `C:/Temp/av-kit/p5-mcp-exec-r1-m7-registration-oracle.txt` (exit 1). `mcp-server/tests/m7-resource.test.ts:15-30` checks only the detached export, so it stays green when registration is broken. | Attach the corresponding description to every registered action schema/metadata entry, then make the 46-row test inspect the registered/list-tools surface rather than only `ACTION_DESCRIPTIONS`. |
| **F3 — MEU-17 accepts malformed discovery inputs that the approved boundary contract requires it to reject before fetch.** `AVKIT_API_BASE` is checked only with substring matching, so `not-a-url/api/v1` returns `{ok:true}` instead of `invalid_api_base`. `backend.json` is also trusted without enforcing `schema_version: 1`; a descriptor with `schema_version:999` is accepted. These are observable external-input validation failures, not documentation drift. | High | `mcp-server/src/config.ts:54-65`, `mcp-server/src/config.ts:68-105`, `docs/execution/plans/2026-08-19-p5-mcp-server/implementation-plan.md:245-252`; `C:/Temp/av-kit/p5-mcp-exec-r1-invalid-base-oracle.txt` and `C:/Temp/av-kit/p5-mcp-exec-r1-descriptor-schema-oracle.txt` (both exit 1). | Parse and validate the pinned/base URL before returning it, enforce descriptor schema version before consuming its fields, and add negative no-fetch tests for malformed pins and unsupported descriptor versions. |
| **F4 — The all-row ACTION_INDEX test does not verify request bodies for most body-bearing actions.** The 46-row loop asserts method and URL, but only `cookies_test` examines a body. Reorder and settings bodies are covered elsewhere; download add, transcript add, TTS prepare/generate, and model download/load can drop or rename fields while the advertised all-row parity test remains green. This is a test-rigor gap under AC-18.2, although current `httpBody()` inspection did not reveal a concrete body defect. | Medium | `mcp-server/tests/action-index.test.ts:50-78`, `mcp-server/tests/tools-parity.test.ts:137-176`, `docs/execution/plans/2026-08-19-p5-mcp-server/implementation-plan.md:317`; current implementation at `mcp-server/src/toolsets/registry.ts:146-168`. | Extend the per-row fixture with the exact expected body (or `undefined`) and assert it for all 46 actions. |

## Scope

The correlated project is `docs/execution/plans/2026-08-19-p5-mcp-server/`, whose approved plan names exactly two handoffs. This round reviewed both MEU handoffs together with the plan/task, `docs/build-plan/05-mcp-server.md`, named-set locks, all files under `mcp-server/src/` and `mcp-server/tests/`, the required Python regression surface, and the MEU/phase/hub SSOT fields. The workspace has no `.git` directory, so verification used current file state and isolated receipts rather than a diff.

Scope lock was preserved: MEU-17 and MEU-18 only. No Session 7, GUI, FastAPI rewrite, infrastructure implementation, or invented MEU was reviewed as delivered Session 6 work.

## IR-1–IR-7 Checklist

| Check | Result | Evidence |
|---|---|---|
| IR-1 — Live runtime evidence | Pass (contract-adapted) | The approved MCP contract requires mocked `fetch`; the real SDK server is constructed/registered and handler calls traverse Zod → client → mocked HTTP. Current receipts: 136 Vitest passes and 290 Python regression passes. No prohibited live YouTube/HF/Kokoro call was made. |
| IR-2 — Stub behavioral compliance | N/A | The reviewed MCP package is a stateless HTTP facade and owns no repositories/UoW/save-get stubs. Source scans confirm no direct SQLite/infrastructure implementation. |
| IR-3 — Error mapping completeness | Partial pass | 422/409 envelopes and generic fetch failures map to handler-shaped `{content,isError:true}`; route-layer NotFound/BusinessRule mapping remains covered by the retained Python regression. F1 is the unresolved error-sanitization failure. |
| IR-4 — Fix generalization | Pass / round-1 baseline | There is no prior implementation-review finding to recheck. Repo-wide MCP scans covered all current source/test files; no deprecated `tool()` registration, placeholder, skipped test, or forbidden direct library reference was found. |
| IR-5 — Test rigor audit | Fail | Most suites assert concrete values and negative paths, but the M7 test materially false-passes detached metadata (F2), the client leak test omits reflected-token input (F1), and the ACTION_INDEX body oracle is incomplete (F4). Ratings below. |
| IR-6 — Boundary validation coverage | Fail | All 46 action variants use `.strict()` and all four destructive variants enforce literal `confirm:true`, with strong negative census coverage. The config boundary fails URL/schema-version validation (F3). |
| IR-7 — Deferral and AC integrity | Pass | Independent extraction found MEU-17 plan/handoff `9/9` ACs and MEU-18 `14/14`, with zero missing. GUI/distribution deferrals MEU-19–25 all exist and are pending in phases 6/7. MCP Guard and HTTP MCP are explicitly sourced out-of-scope by the build plan; no MEU ID was invented. |

### IR-5 Per-File Test Ratings

| Test file | Rating | Rationale |
|---|---|---|
| `config.test.ts` | 🟡 Adequate | Strong discovery/token assertions for listed cases, but no malformed-URL or descriptor-version boundary case; F3 remains green. |
| `client.test.ts` | 🟡 Adequate | Strong shape, status, timeout, Bearer, and fetch-count assertions; token non-leak case does not supply a reflecting error and misses F1. |
| `runtime.test.ts` | 🟡 Adequate | Constructs the real server and asserts required instructions, but its in-test hexagonal scan covers only three MEU-17 files; the independent round scan covered all `src`. |
| `action-index.test.ts` | 🟡 Adequate | Exact 46-row method/path/tool census is strong; general request-body parity is not asserted (F4). |
| `strict-confirm.test.ts` | 🟢 Strong | All 46 extra-key cases assert `TOOL_ERROR` and fetch 0; missing/false confirm covers all destructive actions; non-destructive stops and empty variants have explicit fetch-count assertions. |
| `tools-parity.test.ts` | 🟢 Strong | Concrete positive/negative envelope, error, forbidden-field, voices, reorder-permutation, and settings-body assertions. |
| `m7-resource.test.ts` | 🔴 Weak | Counts a detached map and inspects registration internals only for the URI; it does not prove action-description attachment and false-passes the material F2 defect. |
| `fixtures.ts` | Support | Exact 46-row oracle and minimal inputs; not an executable test suite by itself. |

## Adversarial Verification Checklist

| Check | Result | Evidence |
|---|---|---|
| AV-1 — Failing-then-passing proof | Pass as recorded lifecycle evidence | Each MEU handoff records Red output before Green. This round did not reuse those old receipts as current proof; it reran the registered green gates. |
| AV-2 — No bypass hacks | Pass | Direct test audit found no early-return/try-except assertion bypass or mocked assertion function. |
| AV-3 — Changed paths asserted | Fail | M7 registration linkage and several action bodies are not asserted; F2/F4. |
| AV-4 — No skipped/xfail masking | Pass | `C:/Temp/av-kit/p5-mcp-exec-r1-scan-g36.txt` returned raw `rg` exit 1 (zero matches). |
| AV-5 — No unresolved placeholders | Pass | `C:/Temp/av-kit/p5-mcp-exec-r1-scan-placeholder-libs.txt` returned raw `rg` exit 1 (zero matches). |
| AV-6 — Source-backed criteria | Pass | All reviewed behaviors trace to the approved plan/spec/local-canon locks; no new product requirement was introduced by this review. |

## Contract Surfaces Confirmed

- Registered compound tool names are exactly the six `COMPOUND_TOOLS`; `ACTION_INDEX` and registered schema options both total 46. No `OLD_TOOL_NAMES`, console, or startup-metrics tool is registered.
- All 46 strict-extra cases and all destructive/non-destructive confirmation cases pass. `avkit_download.stop` uses `POST /downloads/stop`; cookie tests send paths/options, not cookie bytes.
- List actions reject bare arrays and accept the `{items, processor}` envelope; reorder preserves exact permutations; empty model variants fail before fetch; voices uses only `GET /tts/voices`.
- Settings `rail` reaches mocked fetch and surfaces API 422, theme is forwarded, and the resource has 32 locked leaves without rail/panel. Runtime construction produces the exact `yt_dlp_debug` key while the required raw `rg yt_dlp mcp-server/src` scan remains empty.
- `STALE_PIN` independently returns `stale_pin` with fetch count 0. Authenticated no-token and liveness-without-Bearer cases pass. `toToolError` has only `{content,isError:true}` publicly, and every HTTP call sets an `AbortSignal`.
- `registerTool()` is used; deprecated `tool()` is absent. No SQLite, SQLAlchemy, yt-dlp literal/import, Kokoro/avkit infrastructure, placeholder, or skipped-test reference appears in MCP source/tests under the required scans.
- SSOT is consistent: MEU-17/18 are `ready_for_review` and bound to the no-slash plan path; phase `"5"` contains the slash path; Hub Next is exactly `` `/create-plan p6-gui-shell` ``; rendered SSOT regions are drift-free.

## Commands Executed

All commands used PowerShell all-stream redirection and this round's `C:/Temp/av-kit/p5-mcp-exec-r1-*` receipts.

| Command / probe | Exit | Receipt / result |
|---|---:|---|
| `npx tsc --noEmit` | 0 | `p5-mcp-exec-r1-tsc.txt`; no TypeScript errors |
| `npx vitest run` | 0 | `p5-mcp-exec-r1-vitest.txt`; 7 files, 136 tests passed |
| `npm run build` | 0 | `p5-mcp-exec-r1-build.txt`; `tsc -p tsconfig.json` |
| Registered Python regression command | 0 | `p5-mcp-exec-r1-python-regression.txt`; 290 passed, 1 deprecation warning |
| Stale-pin no-fetch oracle | 0 | `p5-mcp-exec-r1-stale-pin-oracle.txt`; `stale_pin`, fetches 0 |
| Token-reflection oracle | 1 (finding reproduced) | `p5-mcp-exec-r1-token-redaction-oracle-2.txt`; token present in tool text |
| Registered-action M7 oracle | 1 (finding reproduced) | `p5-mcp-exec-r1-m7-registration-oracle.txt`; 46 exported, 46 actions, 0 registered action descriptions |
| Invalid pin URL oracle | 1 (finding reproduced) | `p5-mcp-exec-r1-invalid-base-oracle.txt`; malformed URL accepted |
| Unsupported descriptor-version oracle | 1 (finding reproduced) | `p5-mcp-exec-r1-descriptor-schema-oracle.txt`; schema version 999 accepted |
| Raw `rg -n yt_dlp mcp-server/src` | 1 (clean) | `p5-mcp-exec-r1-scan-yt-dlp.txt`; zero matches |
| Placeholder/direct-library scan | 1 (clean) | `p5-mcp-exec-r1-scan-placeholder-libs.txt`; zero matches |
| G36 skip/todo scan | 1 (clean) | `p5-mcp-exec-r1-scan-g36.txt`; zero matches |
| Registration API scan | 0 | `p5-mcp-exec-r1-scan-registration-api.txt`; only `registerTool(` at `registry.ts:241` |
| Supplementary M7 file scan | 0 | `p5-mcp-exec-r1-m7-file-scan.txt`; markers present, not used as the action-registration gate |
| Per-MEU AC coverage oracle | 0 | `p5-mcp-exec-r1-ir7-ac-coverage.txt`; 9/9 and 14/14, none missing |
| Scheduled-deferral oracle | 0 | `p5-mcp-exec-r1-ir7-deferrals.txt`; MEU-19–25 exist and are pending |
| Settings-resource oracle | 0 | `p5-mcp-exec-r1-settings-schema-oracle.txt`; `yt_dlp_debug`, 32 leaves, no rail/panel |
| SSOT / Hub Next oracle | 0 | `p5-mcp-exec-r1-ssot-oracle-2.txt`; exact plan/status/phase/hub values |
| `tools/meu_status.py render --check` | 0 | `p5-mcp-exec-r1-meu-render-check.txt`; 25 MEUs / 8 phases, no drift |
| `uv run python tools/check_exec_review.py --self-test` | 0 | `p5-mcp-exec-r1-review-self-test.txt`; checker self-test passed |
| Review frontmatter/marker/rolling-path oracle | 0 | `p5-mcp-exec-r1-review-structure-2.txt`; exact six keys, Intent Anchor first, IR-1–IR-7 present, one rolling file |
| Completion-preflight canonical task read | 0 | `p5-mcp-exec-r1-completion-preflight-task-2.txt`; H1-7 plus H2-1–H2-5 remain unchecked and are gated by this `changes_required` review |

## Open Questions and Assumptions

- No human decision is required to interpret these findings; all three High findings violate explicit approved-plan contracts.
- The test-suite use of mocked `fetch` is intentional and source-backed. No live external-service test is requested or recommended for this review.
- Because the workspace is not a git repository, this review does not claim historical authorship/diff evidence; it verifies the current file state only.
- H1-7 and H2 remain unchecked by design: a `changes_required` reviewer cannot mark the independent-review row approved or enter post-approval closeout. The review workflow hard-stops before `/execution-corrections`.

## Verdict

`changes_required` — F1, F2, and F3 are independently reproduced High behavioral/contract failures, satisfying the Materiality Gate. The green type/build/test receipts and confirmed parity surfaces do not override those false-passes. F4 is Medium and non-blocking by itself.

Follow-up belongs in `/execution-corrections`; this review does not authorize or apply any fix. After corrections, append round 2 to this same rolling file and rerun the failing oracles plus the full registered gates.

## Residual Risk

The untested surfaces are bounded to local mocked HTTP and current-file inspection; no live YouTube/HF/Kokoro behavior was exercised by design. Until F1 is corrected, MCP credentials can enter model-visible error text; until F2 is corrected, IDE agents do not receive the promised per-action guidance; until F3 is corrected, malformed discovery inputs can be trusted or misclassified before fetch.

## Corrections Applied — 2026-08-19 (implementer; not a review verdict)

Round-1 findings were verified against current files, then fixed with TDD. This section is `corrections_applied` only. Independent Codex must re-review; the implementer does not author `approved`.

| # | Severity | Verified? | Category | Fix |
|---|---|---|---|---|
| F1 | High | Yes — env/file token appeared in `TOOL_ERROR` text | error sanitization | `collectTokenSecrets` + `redactSecrets` on `api()` envelopes, `toToolError`, and handler result text. Tests: env + file reflection cases. |
| F2 | High | Yes — Zod options had `description` empty; `_meta` missing | detached metadata | `.describe(ACTION_DESCRIPTIONS[...])` on all 46 union options; `registerTool` `_meta.action_descriptions`. Test inspects registered Zod options + `_meta`, not only the export map. |
| F3 | High | Yes — `not-a-url/api/v1` and `schema_version:999` accepted | boundary validation | `parseHttpApiBase` requires http(s) URL + `/api/v1` path; descriptor consumed only when `schema_version === 1`. |
| F4 | Medium | Yes — all-row loop omitted bodies | weak body oracle | `expectedBody()` fixture + per-row body equality (GET/DELETE `undefined`). Current `httpBody()` already matched; oracle now locks it. |

Siblings searched: only `config.ts` reads `backend.json`; only `client.ts`/`registry.ts` form public tool text. No other token-reflection or descriptor parsers.

### Evidence

- Red: `C:/Temp/av-kit/fail-to-pass-exec-r1.txt` — 5 failed / 65 passed (F1×2, F3×2, F2×1). F4 assertions were already green.
- Green: `C:/Temp/av-kit/pytest-mcp-exec-r1-fix.txt` — `tsc --noEmit` + **141 passed** (7 files) + `npm run build` exit 0.

Conflict flagged: `execution-corrections.md` HARD STOP says do not auto-chain review; parent `/create-plan` H1-7 loop requires re-dispatch. Parent wins.
