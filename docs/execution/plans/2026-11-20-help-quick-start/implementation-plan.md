---
project: "2026-11-20-help-quick-start"
date: "2026-11-20"
source: "Mat's request, 2026-11-20 (USER_EXPLICIT): review the How it works section of each page and give first-time users a short guide with screenshots taken by script from the running app, with the steps in ASD-STE100 Simplified Technical English; parent canon docs/build-plan/06-gui.md:319-332 (### Help (per page))"
meus: ["MEU-162"]
status: "draft"
template_version: "2.3"
---

# Implementation Plan: a short quick start with marked screenshots in each page's How it works card

> **Project**: `2026-11-20-help-quick-start`
> **Build Plan Section(s)**: 06 §Help (per page) (`docs/build-plan/06-gui.md:319-332`) is the parent canon. Row 1 registers MEU-162 (`gui-help-quick-start`, phase 6, P2, matrix 6.23) with a new residual section `### Help quick start (residual)` (anchor `help-quick-start-residual`) before `## Validation Commands` (`06-gui.md:1731` at plan time).
> **Status**: `draft`. `plan_to_exec_gate: human`: the plan review approved at round 3, and Mat said in chat on 2026-11-20: "1289 A, 1290 A, execute".

---

## Goal

**Goal anchor:** when a first-time user opens the How it works card on any of the six pages (Downloader, Transcript, Text to speech, Convert, Capture, Settings), the card shows one sentence about the page, a numbered quick start of 4 or 5 steps in ASD-STE100 Strict style, and one screenshot (two on Settings) of the page with the same numbers marked on the controls. The screenshot matches the light or dark theme. Below the steps, the reference topics are short, plain and closed until opened. A tracked script takes the screenshots from the running app with demo data. Tests prove these things: every step names a control that exists, every image loads in both themes, no image is out of date with its steps, no image shows a home folder path, and the steps pass the STE linter. There is no manual check.

**Why.**

- **The cards do not teach the page.** Each card is a list of reference topics (`features/*/*-help-content.ts`, 1,642 words in all). It has no first steps and no images. Some topics are written for developers:
  - Settings `leaf-keys`: "PUT /settings/{namespace}".
  - Capture `mcp-png`: "GET /captures".
  - Capture `inbox-folder`: "capture.inbox_dir … the settings PUT".
  - TTS `paste`: "chunk_max_chars".
  - Settings `ffmpeg`: "ffmpeg.available".
  - Capture `four-tools`: one paragraph of 600 words.
- **Mat, 2026-11-20:** "Right now it is very inadequate guide on how to use each page. We need to create guides with images (which can be screenshot agenticly while the app is running) and use of p:\creative-writing\.agent\skills\asd-ste100\ skill for guided steps. The idea is for first time users get best onboarding experience and get them started so they can get gist of how each page works quickly. The guide document should not be too long just enough to get people curious."
- **Mat, 2026-11-16:** "This should be done with framework and scripts!" So the screenshots come from a script, and the checks are tests in the gate.

**What the code shows (plan-time reads at `HEAD` `e8207e1`, clean tree, one worktree, `hq99-probe.txt`):**

- **The card.** `components/help/HelpCard.tsx` (LF, 155 lines) takes `{ feature, tabKey, sections }`.
  - It keeps its open state in `localStorage` under `av-kit:<feature>-help:<tabKey>:state`. On a first visit the card is closed: only the stored value `'expanded'` opens it.
  - It handles the F1 toggle by route (MEU-158: `HELP_FEATURE_ROUTE`, `takeHeldHelpToggle`).
  - The header button reads "ℹ️ How it works", with the title "How it works (F1)".
  - When open, the card shows `help-search` and one `<article data-help-section={id}>` per topic. When nothing matches, it shows "No help topics match your search."
  - Each page mounts the card once: `DownloaderPage.tsx:574`, `TranscriptPage.tsx:487`, `TTSPage.tsx:307`, `ConvertPage.tsx:602`, `CapturePage.tsx:2652` and `SettingsPage.tsx:624`. This plan does not edit the pages. The card reads its quick start by `feature`.
- **Canon.** 06 §Help (per page) (`06-gui.md:319-332`) gives each page a table of minimum topics and says "Each page mounts a HelpCard (accessible disclosure, persist collapse)". The 08 and 09 wireframes show "Help (collapsed)".
  - The P6 plan (`docs/execution/plans/2026-08-21-p6-gui-settings-help/implementation-plan.md:77`) said "First visit expanded". The code now closes the card on a first visit, and the P8 and P9 ACs pin the collapse key and the reload restore.
  - MEU-158's Electron test (`ui/tests/e2e/help-f1-mount.test.ts`) expects F1 to open a card that starts closed.
- **Theme.** `lib/theme.ts` toggles the `dark` class on `document.documentElement`, and `styles.css` (CRLF) uses `:root:not(.dark)`.
- **Assets.** `src/renderer/src/env.d.ts` references `vite/client`, so `import x from '….png'` and `import.meta.glob` type-check (`Header.tsx:4` imports `assets/rottiboo.png`). `ui/tsconfig.json` (LF) has no `resolveJsonModule`.
- **The E2E seam.** `launchElectron()` (`ui/tests/e2e/electron-app.ts`) needs `AVKIT_APP_DATA` under the temp folder and sets `AVKIT_E2E=1`.
  - The main process still spawns the real backend (`spawnOwned`, `index.ts:267`) with the launch's environment, and `help-f1-mount.test.ts:152` polls `window.api.getBackendUrl()` until it is ready. After ready, the renderer's base URL is the real backend. Each spec fills the page by `page.addInitScript` replacing `window.fetch`, then `page.reload()`, so the renderer's requests go to the seam.
  - Main-process IPC is outside that seam. Settings calls `window.api.getSetupReadiness()` (`SettingsPage.tsx:371`). Its models-folder probe (`setup-readiness.ts`) falls back to `~/.avkit/models` under `os.homedir()` when the app data has no database or setting, and writes and deletes a `.write-probe-<uuid>` file in the nearest existing folder, which can be the home folder. Node's `os.homedir()` and Python's `Path.home()` on Windows read `USERPROFILE`; `launchElectron` merges extra env keys into the launch (`electron-env.ts:32`).
  - Some Settings text shows machine paths: the Console card shows the log file under `AVKIT_APP_DATA` (`SettingsPage.tsx:1116`), and the MCP card's prompt holds `AVKIT_APP_DATA`, the Electron path and the server path (`mcp-setup-prompt.ts:59`, `:78`). Rows 5, 8 and 9 set `TMP` to `C:/Temp/av-kit/help-quick-start/tmp`, so those paths are not under `Users\<name>`.
  - Settings sections render in one scrolling column in this order: Download, Transcript, TTS, Convert, Capture, Console, Appearance, Startup, Dependencies, Readiness, MCP (`settings-sections.ts:35-45`). The default window is 1280 × 800 (`index.ts:145`). Download and Readiness cannot share one clip; Readiness and MCP are next to each other.
  - Save modes differ by card (`settings-sections.ts:35-45`, `SAVE_MODE_CAPTIONS`): Download, Transcript, TTS and Console save as you type; Convert and Capture need Save; Appearance applies at once; Startup applies to the OS at once. Each card shows its mode next to its name (`settings-mode-<key>`).
  - Transcript: at Done the worker writes the raw ZIP (`transcript.py` `_zip_raw`) and the API returns `zip_path`, but never `compiled_path`; the renderer fills `compiled_path` only after Compile (`TranscriptPage.tsx:184`). The Done links are `view-compiled` then `open-zip`, each shown only when available (`transcript-card.ts:61`, `transcript-controls.ts`), so at Done before Compile only Open ZIP (`open-zip-link`) shows.
  - Convert: the preset control shows only for the Compress task (`ConvertPage.tsx:699`).
  - Convert's `queue-card-primary-action` is made by the shared `components/queue/QueueCard.tsx:619`, not by a feature folder.
  - Examples: `installSeam` and `seededQueue()` in `download-queue.test.ts`, `installTranscriptSeam` in `transcript-queue.test.ts`, `installTtsSeam` in `tts-generate.test.ts`, the Convert seam in `convert-queue.test.ts`, the Capture seam and `fixtures/capture-fidelity-original.png` in `capture-inbox.test.ts`, and the Settings seam in `settings.test.ts`.
  - Native dialogs return fake paths such as `C:/e2e/outdir`.
- **The STE skill.** `P:/creative-writing/.agent/skills/asd-ste100/` is a byte-identical copy of `danyuchn/asd-ste100-skill` at commit `32511c6`, under the MIT licence, with an `UPSTREAM.md`.
  - Its linter `scripts/ste-lint.py` exposes `lint(text) -> (findings, words)`, where each finding has `level`, `rule` and `message`. There are two levels. `advisory-free` is the hard level (`semicolon`, `phrasal-verb`, `marketing-adjective`, `nominalization`, `long-sentence`, `synonym-rotation`; `:36-45`; `:480` counts only it as hard). `advisory` (`passive-voice`, `present-perfect`) never fails the linter's own run. No level is named `hard`.
  - Its phrasal-verb rule finds `Spin up the job.` (`advisory-free`) and does not find `Set up the folder.`; `The file is downloaded by the app.` gives only an `advisory` passive finding (`hq99-ste-draft-r2.txt`).
  - Its sentence cap is 25 words (`MAX_WORDS`, `:73`). The Strict 20-word instruction cap and the one-instruction rule are not machine-checked ("undetectable without context"), so this plan adds them.
- **The draft content.** `quick-start-draft.json` in this plan folder holds the six intros, 27 steps and seven image alt texts. All 40 strings lint with 0 findings at any level. Every step has 2 sentences or fewer, every sentence has 20 words or fewer, and no step has a semicolon (`hq99-ste-draft-r2.txt`, which uses the real level names; the round 1 probe filtered on a `hard` level that does not exist). Round 2 changed the draft: Transcript step 4 uses Open ZIP, Convert steps 1 and 3 name the Compress task, and the Settings steps follow the page order with one shot per area. Every step target is a `data-testid` that exists in the renderer source. The Convert preset id is `convert-preset-balanced` (`convert-presets.ts:1`, `PRESET_DEFAULT`).

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and ui/graphify-out/ are absent (hq99-probe.txt, 2026-11-20). The change is one card component, six content modules, one stylesheet, new test and generator files and docs, all read at plan time; a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. See `.agent/docs/harness-profiles.md` and the Claude Code block of `.agent/context/harness.local.md`.
  - Validation goes through `rtk proxy` with the receipt pattern. Task-cell commands run in pwsh.
  - Receipts go to `C:/Temp/av-kit/help-quick-start/`. Execution receipts start `hq-`; planning receipts start `hq99-`.
  - Every row sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, and clears `ELECTRON_RUN_AS_NODE`.
  - Vitest runs from pwsh after `Set-Location 'P:\av-kit\ui'`, never from the Bash tool, and returns to `P:\av-kit`.
  - Playwright runs with `ELECTRON_RUN_AS_NODE` cleared and with `TMP` and `TEMP` set to `C:/Temp/av-kit/help-quick-start/tmp`. Each Electron launch uses a scratch `AVKIT_APP_DATA`. No row stops a process by image name.
  - Before each Electron step, the host-load probe must read 50 % or less. A receipt that holds `unhandled rejection:` is a failure. A failure with no recorded cause is rerun alone once (S5) and is never retried into a pass.
- **Working directory:** `P:/av-kit` on `main`. Use no branch and no worktree. Leave `.agent/fleet/hub` alone.
- **Cloud-local contract:** local, because the work runs Electron.
- **Reviewer:** Codex runs through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `hq-plan-2026-11-20-help-quick-start` and `hq-execution-2026-11-20-help-quick-start`.
  - Caps come from `.agent/review-limits.json`: 3 plan rounds and 6 execution rounds. This plan carries no `review_limits` block.
  - Claude wrote the plan, so the reviewer is from a different vendor. The fallback is Mat.
  - The dispatch console goes to `/dev/null` or its own console file, never into the run log.
- **Never in these rows without Mat's words:** commit, push, or writing an `approved` verdict. Mat pushes himself.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-162 Help quick start | `.agent/context/handoffs/2026-11-20-help-quick-start-MEU-162-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-20-help-quick-start-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-20-help-quick-start-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline, plan-local scripts, MEU registration (rows 0 and 1) | — | shared | `baseline.sha`, `baseline-scope.json`, `baseline-eol.json`, `baseline-pins.json`, `red-check.py`, `identity.py`, `eol-check.py`, `host-wait.py`, `meu-register.py`, the MEU-162 entries |
| WP-2 | Vendor the STE skill (row 2) | WP-1 | shared | `.agent/skills/asd-ste100/` |
| WP-3 | All Reds: the STE gate, the unit tests, the Electron tests and their stages (rows 3, 4 and 5) | WP-2 | shared | `tools/help_guide_ste.py`, `tests/tooling/test_help_guide_ste.py`, `help-quick-start.test.tsx`, `help-shots-privacy.test.ts`, `test-ids.ts`, `ui/tests/help-shots/stage.ts`, `ui/tests/e2e/help-quick-start.test.ts`, the Red hashes |
| WP-4 | Content Green: quick start JSON and plain topics (row 6) | WP-3 | shared | `components/help/quick-start.json`, `ui/tsconfig.json`, the six `*-help-content.ts` modules |
| WP-5 | Card Green (row 7) | WP-4 | shared | `quick-start.ts`, `help-shots.ts`, `HelpCard.tsx`, `styles.css` rules, `privacy.ts` |
| WP-6 | Generator and images (row 8) | WP-5 | `compact_continue` | `ui/tests/help-shots/help-shots.shots.ts`, `ui/playwright.help-shots.config.ts`, the `help:shots` script, `assets/help/*.webp`, `assets/help/manifest.json` |
| WP-7 | Electron proof (row 9) | WP-6 | shared | The run receipts |
| WP-8 | Canon, commands and status (row 10) | WP-7 | shared | 06 Delivered note, `commands.md`, MEU-162 `ready_for_review` |
| WP-9 | Closeout (H1, H2) | WP-8 | `compact_continue` | The handoff, the review, the reflection, the commit draft |

## User Review Required

> [!IMPORTANT]
> **Mat decided both** on 2026-11-20: "1289 A, 1290 A, execute" (§Decision Log).
>
> - **D-1289 (A): the card does not open by itself on a first visit.** The card stays closed, as it is now, and its header says "Quick start · N steps", so a new user sees where the guide is.
> - **D-1290 (A): every topic that no test pins is rewritten in plain words, and so is the Settings Console topic (it showed `log_level`, `console_visible` and `{app_data}`; the one assertion that pins it, AC-115.15, changes in row 4) and the one sentence "Save POSTs the full annotation list." in the Capture tools topic (no test pins it).** The other pinned text stays word for word. See `CONSOLE_AND_SAVE`.
>
> **What changes for you:**
>
> - Open **How it works** (or press F1) on any page. You see one sentence about the page, 4 or 5 numbered steps and a screenshot with the same numbers on the controls. On Settings, there are two screenshots.
> - The screenshots follow the app theme, light or dark.
> - Under the steps, the reference topics show as titles. Click a title to read it. Search works as now: when you type, the steps hide and the matching topics open.
> - `npm --prefix ui run help:shots` takes the screenshots again after a UI change. The tests fail when the steps change and the images were not taken again.
> - The images add about 1 MB or less to the app: 14 WebP files of 150 KB or less each.

## Proposed Changes

### Single-statement contracts

- **`QUICK_START_DATA` (D-1291):** `ui/src/renderer/src/components/help/quick-start.json` (LF, new) holds the quick start in the shape `quick-start-draft.json` uses (schema `help-quick-start/1`).
  - Each page entry is keyed by the card's `feature` (`downloader`, `transcript`, `tts`, `converter`, `capture`, `settings`). It has an `intro` (one sentence), `steps` (4 or 5 entries of `{ text, target }`, where `target` is a `data-testid` or `null`) and `shots` (1 or 2 entries of `{ name, steps, alt }`).
  - Every step with a target appears in exactly one shot's `steps`. Every `steps` number is a valid 1-based index. Every `name` is unique.
  - Row 6 copies the draft file byte for byte and changes only what row 0's re-read forces. Any change is named in the handoff.
  - `ui/tsconfig.json` gains `"resolveJsonModule": true` so that `tsc --noEmit` accepts the import. Vite imports JSON natively.
- **`QUICK_START_SCHEMA` (D-1291):** `components/help/quick-start.ts` (LF, new) exports these names:
  - `QUICK_START`: the JSON typed as `Record<HelpFeature, QuickStartPage>`.
  - `validateQuickStart(data)`: returns the list of problems. It checks the shape and the rules of `QUICK_START_DATA`: a step has 2 sentences or fewer, a sentence has 20 words or fewer, and a step has no `;`.
  - `quickStartHash(page)`: the SHA-256 hex of `JSON.stringify({ steps, shots })` for one page. It is computed with the Web Crypto `crypto.subtle` in the renderer and `node:crypto` in tests. A shared pure function `quickStartHashInput(page)` returns the exact string, and both hashers hash that string.
- **`HELP_SHOTS` (D-1292):** `components/help/help-shots.ts` (LF, new) maps each image name and theme to its URL. It uses `import.meta.glob('../../assets/help/*.webp', { eager: true, query: '?url', import: 'default' })`. `shotUrl(name, theme)` returns the URL of `assets/help/<name>-<theme>.webp`, or `null` if the file does not exist. It reads the manifest with `import.meta.glob('../../assets/help/manifest.json', { eager: true, import: 'default' })`, never a static import, so the renderer builds and type-checks with no manifest and no images (rows 6 and 7). `shotSize(name)` returns the manifest's `{ width, height }`, or `null`. A shot with a `null` URL or size renders no figure.
- **`CARD_QUICK_START` (D-1289, D-1290):** `HelpCard.tsx` keeps its props, its storage key, its first-visit closed state, its F1 handling and its `help-card` and `help-search` ids. It changes in four ways:
  - **Header.** The header button text stays "ℹ️ How it works". A `<span data-testid="help-quick-start-hint">` follows it, with `Quick start · N steps`, where N is the number of steps for the card's `feature`. The span is in the button, so a click anywhere on the header still toggles the card.
  - **When open and the search is empty:** under the search field, `<p data-testid="help-quick-start-intro">` holds the intro. `<ol data-testid="help-quick-start">` follows, with one `<li data-testid="help-quick-start-step" data-step={n}>` per step, in order. Then each shot renders a `<figure data-testid="help-shot" data-shot={name} data-shot-steps="2,3,4,5">`. The figure holds two `<img loading="lazy" decoding="async">` elements: one with the class `help-shot__img--light` and the light URL, one with `help-shot__img--dark` and the dark URL. Each has the shot's `alt` and the `width` and `height` from the manifest. A `<figcaption>` holds the same text as `alt`. A shot whose URL is `null` is not rendered, and `validateQuickStart` plus AC-162.7 make that a test failure.
  - **Topics.** After the shots, a `<h3>More about this page</h3>` heading, then one `<details data-help-section={id}>` per topic, with `<summary>` holding the title and `<p>` holding the body. When the search is empty, every topic is closed.
  - **When the search is not empty:** the intro, the steps, the shots and the "More about this page" heading are not rendered. The matching topics render with `open`, so their text shows, as the articles showed before. The no-match text is unchanged.
  - No step, intro or shot element carries `data-help-section`. So `help-search.spec.ts` W6-2 still counts only topics.
- **`THEME_SHOT_CSS` (D-1292):** `styles.css` (CRLF) gains two rules: `:root.dark .help-shot__img--light { display: none; }` and `:root:not(.dark) .help-shot__img--dark { display: none; }`. It also gains `.help-shot img { max-width: 100%; height: auto; }` plus the figure and step styles, which use the existing tokens only. A hidden lazy image is not fetched.
- **`HELP_SHOTS_GEN` (D-1292):** a generator writes the screenshots.
  - The config is `ui/playwright.help-shots.config.ts` (LF, new): `testDir: './tests/help-shots'`, `testMatch: '*.shots.ts'`, one worker, no retries. The normal `test:e2e` config (`testDir ./tests/e2e`) never runs it.
  - The spec `ui/tests/help-shots/help-shots.shots.ts` (LF, new), for each page and for `light` then `dark`, does these things:
    1. Launches the app through `launchElectron` with the isolated env of `DEMO_STAGE` and checks it (below).
    2. Runs that page's `stage(page)` from `ui/tests/help-shots/stage.ts`.
    3. Sets the theme by toggling the `dark` class on `document.documentElement`, as `lib/theme.ts` does.
    4. Closes the help card if it is open.
    5. For each shot, finds each target with `getByTestId(target).first()`, calls `scrollIntoView({ block: 'start' })` on the shot's first target, waits two animation frames, and measures every target box again. `shotClip(boxes, viewport)` from `ui/tests/help-shots/clip.ts` (LF, new) returns the clip, the union of the target boxes plus 24 px, or a named error. It never clamps a target away: a target box that is not fully inside the viewport is an error that names the target, and so is a union wider than 1280 or taller than 900 CSS px. Only the 24 px margin is clamped to the viewport. Any error fails the run and writes no file (S9).
    6. Injects an overlay with a 2 px outline in `--color-accent` around each target and a 22 px round badge with the step number at the target's top-left corner. Then it checks in the page that every badge box lies fully inside the clip; a badge outside it fails the run (S9). Then it takes `page.screenshot({ clip, mask, maskColor })`, where `mask` is the elements of `SHOT_MASKS` (`mcp-setup-prompt` and `settings-log-row`, the two elements that show machine paths) that meet the clip and `maskColor` is the computed `--color-bg-elevated`. A mask that meets a target box fails the run. It removes the overlay, and converts the PNG to WebP in the renderer: the PNG loads into an `Image`, is drawn on a canvas and is exported with `canvas.toDataURL('image/webp', q)`. `q` starts at 0.85 and drops by 0.05 to a floor of 0.5 until the file is 150 KB or smaller. Above the cap at 0.5, the run fails (S9).
  - Before it writes each file, it runs `PRIVACY_GUARD` on the clip's text from `clipText` (below), with `roots` set to the generator's `os.homedir()`, the scratch home, the scratch root, `os.tmpdir()` and the repository root.
  - Last, it writes `ui/src/renderer/src/assets/help/<name>-<theme>.webp` and `manifest.json` (LF): for each shot, `{ name, page, width, height, bytes: { light, dark }, stepsHash }`, where `stepsHash` is `quickStartHash(page)`.
  - `ui/package.json` (CRLF) gains `"help:shots": "playwright test -c playwright.help-shots.config.ts"`. The app must be built first, as for `test:e2e`.
- **`DEMO_STAGE` (D-1292):** `ui/tests/help-shots/stage.ts` (LF, new) exports `STAGES: Record<HelpFeature, (page) => Promise<void>>`. Each stage installs a `window.fetch` seam by `page.addInitScript` and reloads. The seam answers every request it knows and rejects any other with an error that names the path. It never passes a request to the real `fetch`, so the renderer never reaches the real backend. Row 5 writes it, copying the seam shapes from the existing specs as row 0 read them. It does not import those spec files, which this plan does not change. It then navigates to the page, waits for every step target to be visible, and reaches the state the steps describe:
  - **Isolation (F2).** `stage.ts` also exports `launchIsolated()`, which every generator run and every `help-quick-start.test.ts` launch uses. It makes a fresh scratch root with `mkdtemp` under `os.tmpdir()`, with `appdata/` and an empty `home/` in it. It launches through `launchElectron` with `AVKIT_APP_DATA` = `<root>/appdata`, `USERPROFILE` and `HOME` = `<root>/home`. Before any page shows, `app.evaluate(() => [process.env.USERPROFILE, process.env.HOME, process.env.AVKIT_APP_DATA])` must equal those three paths, or the run stops (S12). Then it polls `window.api.getBackendUrl()` until it is ready, as `help-f1-mount.test.ts:152` does, so the readiness IPC sees a ready backend. So the spawned backend, its database and the readiness probe use only the scratch root. Settings has no models setting in the scratch app data, so the probe uses `<root>/home/.avkit/models`. The launch prints `isolation: ok` once.
  - **Downloader:** two Done rows and one Queued row, with neutral titles and the URL field holding `https://www.youtube.com/watch?v=demo`.
  - **Transcript:** one channel row in Done with `zip_path` set and no `compiled_path`, as the worker leaves a job at Done, and one row in Queued. Open ZIP shows and View compiled does not. The stage never seeds a compiled path.
  - **Text to speech:** one model not yet downloaded, so Get shows, with demo text and a voice.
  - **Convert:** the Compress task, one Done row and one Queued row.
  - **Capture:** two shots from `ui/tests/e2e/fixtures/capture-fidelity-original.png`, the first selected, and one arrow drawn by a drag on `capture-draw-surface`, so Save shows.
  - **Settings:** the dependencies seam reports FFmpeg missing, so the Readiness card shows Fix for FFmpeg (`readiness-ffmpeg-link`). The other readiness rows come from main IPC on the scratch root and show only labels and chips. Every folder in the seeded settings is `D:\Media\av-kit`. The `settings-download` shot holds the Download card's save note and Browse; the `settings-setup` shot holds the Readiness count and the MCP card down to Copy prompt.
  - Every path in the seeds is under `D:\Media\av-kit` or `C:/e2e/`. No seed holds a user name, a home folder or a real channel name.
  - The generator and the Electron drift test use the same stages.
- **`PRIVACY_GUARD` (D-1292):** `ui/tests/help-shots/privacy.ts` (LF, new) exports `findPrivatePath(text, roots): string | null`, where `roots` is a list of folders.
  - It flags, with case ignored, each root in either slash form, and any `<drive>:\Users\<name>` or `<drive>:/Users/<name>` segment except `Users\Public`. It also flags `/Users/<name>/` and `/home/<name>/`.
  - It never matches a bare user name: "Format" must pass.
  - **What text it reads (F6).** The guard reads only text that the image can show. It never reads an element's `innerText`, because a container that meets the clip also holds the text of its off-clip and masked children, such as the Console card's log path.
    - `gatherShotText(masks)` runs in the page through `page.evaluate`. It has no imports and no closures.
      - It walks every text node under `document.body` with a `TreeWalker`. For each node it gives `{ text, rects, masked }`: `rects` are the node's `Range.getClientRects()`, and `masked` is true when the node is inside an element of `SHOT_MASKS` or inside an element whose computed `visibility` is not `visible`.
      - It gives one more item for each `input`, `textarea` and `select`: its `value`, or its `placeholder` when the value is empty, with that element's own rect and the same `masked` rule.
      - Each string is a single text node or a single control value, so no string comes into the list twice.
    - `clipText(items, clip)` in `privacy.ts` is pure and has no DOM. It keeps the items that are not masked and that have a rect with a non-zero area that meets the clip. It joins them with newlines.
    - `findPrivatePath(clipText(items, clip), roots)` gives the result. A hit fails the run and writes no file.
    - The clean Settings run proves that masked text and off-clip text do not block the image: the MCP prompt is masked, the Console log path is off the clip, and both hold the scratch root. The planted negative run (row 8) proves that a private path in the clip still blocks the image before any file is written.
- **`STE_GATE` (D-1293):** the STE skill is vendored and gated.
  - The skill goes into `.agent/skills/asd-ste100/` byte for byte: `SKILL.md`, `LICENSE`, `references/writing-rules.md`, `examples/before-after.md`, `examples/linter-edge-cases.md` and `scripts/ste-lint.py`, copied from the creative-writing copy and checked against it by SHA-256. A new `UPSTREAM.md` states the source, the commit, the licence and how this repo uses the skill.
  - `.agent/skills/README.md` (CRLF) gains one row.
  - `tools/help_guide_ste.py` (LF, new) loads the vendored linter by path. It reads `quick-start.json` and lints the parts:
    - **Levels.** A finding with level `advisory-free` is hard. A finding with level `advisory` is soft. Any other level, or a missing one, is a problem in every mode (fail closed). The tool never filters on a level named `hard`.
    - **Strict:** every step must have 0 findings at any level (so a passive step fails), 20 or fewer words per sentence, 2 or fewer sentences per step and no `;`.
    - **Flavored:** every `intro` and every shot `alt` must have 0 `advisory-free` findings.
    - **Known limit.** The linter does not find every phrasal verb (`Set up the folder.` passes). This plan adds no word list of its own; the negative oracle for phrasal verbs is `Spin up the job.`, which the linter finds.
  - It also parses the six `*-help-content.ts` modules for `id`, `title` and `body` literals, with a regex for single-quoted strings with `\'` escapes and a `--selftest` on fixtures. Every topic body whose id is not in `PINNED_TOPICS` must have 0 `advisory-free` findings and no unknown level. `PINNED_TOPICS` is `downloader:pause`, `transcript:blocked`, `capture:four-tools` and `capture:original-annotated` (D-1290 A removed `settings:console`).
  - It exits 1 on any failure and prints each finding.
  - `tests/tooling/test_help_guide_ste.py` (LF, new) runs it in process.
- **`PLAIN_TOPICS` (D-1290):** in the six content modules (all CRLF), every topic body not in `PINNED_TOPICS` is rewritten in STE-flavored plain words, under these rules:
  - Every `id` and the order of topics stay. Each pinned topic keeps its `title` and `body` byte for byte, except the one `four-tools` sentence of `CONSOLE_AND_SAVE`.
  - The API jargon goes: no `GET `, `PUT `, `POST`, `/settings/`, `{namespace}`, `capture.inbox_dir`, `chunk_max_chars`, `ffmpeg.available` or `quit intent` in an unpinned body.
  - Every fact in §Fact table stays, with its keyword.
  - The AC-23.16 keywords stay in each module's source (`help-card.test.ts:27-43`).
  - The word `Sample` appears in no Capture topic (AC-81.12).
  - Titles of unpinned topics become sentence case in plain words.
- **`CONSOLE_AND_SAVE` (D-1290 A, Mat 2026-11-20):** two pinned texts change, and nothing else pinned.
  - The Settings `console` topic is no longer pinned. Its body becomes `Set Log level, Log to file and Console visible on the Console card. Errors are always written to console.log in the logs folder of the app data. Log to file adds every other line. You cannot change that path. Open the Console panel from the header.` Its title stays "Console and logging". It follows `PLAIN_TOPICS` and §Fact table like any unpinned topic.
  - `ui/tests/unit/failure-reason-copy.test.ts` AC-115.15 changes only its `consoleHelp?.body` expectation to that body. Its other three assertions (the Settings hint, `Persist to`, and the Console panel line) stay. Row 4 makes this change before any product change, runs `-t AC-115.15` to see it fail by assertion, and records the file's hash with `red-record --row 4`. `row-check.py pins-unchanged` skips this one file, which `red-unchanged` covers instead.
  - In `capture:four-tools`, the sentence `Save POSTs the full annotation list.` becomes `Save stores all the marks on the shot.` Every other byte of the topic stays. No test pins that sentence (`rg "full annotation list" ui/tests` finds nothing). AC-162.9 compares the body with its row-0 value after this one replacement and checks that `POST` is gone.
- **`TEST_IDS` :** `ui/tests/e2e/test-ids.ts` (CRLF) gains, at its end, `HELP_QUICK_START = 'help-quick-start'`, `HELP_QUICK_START_STEP = 'help-quick-start-step'`, `HELP_QUICK_START_INTRO = 'help-quick-start-intro'`, `HELP_QUICK_START_HINT = 'help-quick-start-hint'` and `HELP_SHOT = 'help-shot'`. The AC-51.6 prefix before `// MEU-51 primitive harness IDs.` is unchanged (`layout-primitives.test.ts:200-214`).
- **`SERVICES_KEPT`:** no Python product code, API route, OpenAPI document, MCP tool, persisted setting or page component changes. The only Python files are `tools/help_guide_ste.py`, its test and the vendored linter.

### Fact table (`PLAIN_TOPICS`)

Each rewritten topic keeps these facts. The keyword in the right column must appear in the new body (case ignored). AC-162.9 checks this table.

| Page:topic | Facts kept | Keywords |
|---|---|---|
| downloader:url-types | Video, playlist and channel links work; the app reads the details before it downloads | `video`, `playlist`, `channel` |
| downloader:sabr | SABR limits quality and audio choices; the SABR check shows whether it blocks better formats | `SABR`, `check` |
| downloader:cookies | Browser or file cookies for videos that need a sign-in; test them before a large batch | `cookie`, `browser`, `file`, `test` |
| downloader:archive | Archive tracking in Settings skips videos already downloaded | `archive`, `Settings`, `skip` |
| transcript:resume | Resume starts from the last saved point and does not get finished videos again | `Resume` |
| transcript:cancelled | Stop marks running jobs Cancelled; finished transcripts stay on disk | `Stop`, `Cancelled` |
| transcript:requeue | Requeue puts a Cancelled or failed channel back in the queue with the same output folder | `requeue`, `folder` |
| transcript:compile | Compile puts all transcripts in one file; Zip packs it to share | `compile`, `zip` |
| transcript:rate | Requests per hour and batch delays in Settings keep you under YouTube's limits | `rate`, `Settings` |
| tts:prepare | Prepare cleans the text before Generate, for punctuation and spaces | `prepare`, `Generate` |
| tts:voice | The language filter makes the voice list shorter; speed presets change the speed | `voice`, `language`, `speed` |
| tts:download | Get downloads a Kokoro model to your models folder when it is not there | `download`, `Kokoro`, `models folder` |
| tts:load | Load puts the model in memory; Unload frees the memory before you change models | `load`, `Unload` |
| tts:paste | Paste or a .txt or .md file; long text is split into parts (size in Settings) | `paste`, `.txt`, `.md`, `Settings` |
| converter:what-convert-does | Compress, cut or extract audio from local files; files stay on your computer; never uploads to YouTube | `Compress`, `cut`, `audio`, `YouTube` |
| converter:presets-advanced | A preset is a named quality recipe; Advanced changes CQ, scale and audio; a new preset resets Advanced | `preset`, `Advanced`, `CQ` |
| converter:gpu-software | The encoder chip shows NVIDIA NVENC, AMD AMF, Intel QSV or Software; Refresh checks again; no FFmpeg disables Add and Start | `NVENC`, `AMF`, `QSV`, `Software`, `Refresh`, `FFmpeg` |
| converter:fast-cut | Fast cut copies and can move to a keyframe; Accurate encodes the part again for exact In and Out times | `Fast cut`, `keyframe`, `Accurate` |
| converter:extract-containers | Extract copies the first audio stream or all streams; the file type follows the codec (AAC to .m4a, PCM to .wav) | `first audio`, `.m4a`, `.wav` |
| converter:sequential-gpu | One file at a time so GPU encodes do not overlap | `one file at a time`, `GPU` |
| capture:what-capture-does | F2 or Capture region takes a region; PNGs go to your inbox; you can mark them; never uploads | `F2`, `PNG`, `inbox`, `never uploads` |
| capture:f2-sharex | If ShareX or another tool has F2, a banner shows; quit ShareX or pick another key | `ShareX`, `banner` |
| capture:inbox-folder | New shots are PNG files named by local time in the inbox folder; Browse picks it; Save keeps it (Settings → Capture) | `PNG`, `inbox`, `Browse`, `Save` |
| capture:mcp-png | MCP tools see the same shots and can list and read the files | `MCP`, `list`, `read` |
| capture:close-to-tray | With close to tray on, closing the window hides it and F2 still works; Quit in the tray menu exits | `tray`, `F2`, `Quit` |
| capture:never-uploads | Capture stays on your computer; nothing goes to YouTube | `YouTube` |
| settings:leaf-keys | Each card shows how it saves next to its name: most cards save as you type, Convert and Capture need Save, Appearance applies at once; one card does not change another | `Save`, `card`, `as you type` |
| settings:ffmpeg | Browse to FFmpeg and click Check dependencies before media jobs | `FFmpeg`, `Check dependencies` |
| settings:mcp | Copy the MCP setup for your client; the app shows only whether a token exists, never the token | `MCP`, `token` |
| settings:console | Errors always go to the log file; Log to file adds every other line; the path cannot change; the Console panel opens from the header | `Errors`, `always`, `Log to file`, `header` |
| settings:startup | Start when I sign in adds a per-user startup entry with no administrator approval; turn it off here or in Task Manager; Start minimized waits in the notification area so F2 still works | `sign in`, `administrator`, `Task Manager`, `Start minimized`, `F2` |

### MEU-162: Help quick start

1. Row 1 registers MEU-162 with the 06 section, the matrix row 6.23 and the status entry. This uses `meu-register.py`, adapted from Session 97's (`docs/execution/plans/2026-11-19-e2e-host-parity/meu-register.py`) for phase 6.
2. Row 2 vendors the STE skill.
3. Rows 3, 4 and 5 write every Red before any product change: row 3 adds `STE_GATE` and its pytest, row 4 the Vitest files and `TEST_IDS`, and row 5 `DEMO_STAGE` and the Electron test, run against a build of the unchanged app.
4. Row 6 adds `QUICK_START_DATA` and `PLAIN_TOPICS` (Green for AC-162.2 and AC-162.9).
5. Row 7 adds `QUICK_START_SCHEMA`, `HELP_SHOTS`, `CARD_QUICK_START`, `THEME_SHOT_CSS`, `PRIVACY_GUARD` and `clip.ts` (Green for AC-162.1, AC-162.3, `AC-162.4 css`, AC-162.5, AC-162.6 and AC-162.8). `AC-162.4 figures` and AC-162.7 need the images, so they stay red by assertion, unchanged, until row 8.
6. Row 8 adds `HELP_SHOTS_GEN` and takes the images (Green for `AC-162.4 figures`, AC-162.7 and AC-162.14, with the test file unchanged since row 4).
7. Row 9 runs the Electron proof (AC-162.10 to AC-162.13 and AC-162.16).
8. Row 10 adds the Delivered (Session 99) note, the `commands.md` row and the status update.

### The 06 residual section (written in row 1)

```markdown
### Help quick start (residual)

> **MEU-162.** Registered 2026-11-20 from Mat's request ("very inadequate guide on how to use each page"; D-1289 to D-1294). Each page's `HelpCard` gets a short quick start with marked screenshots taken by script, with the steps in ASD-STE100 Strict style.

| Rule | Contract | Source |
|------|----------|--------|
| Quick start | When the card is open, it shows one intro sentence, 4 or 5 numbered steps and one marked screenshot (two on Settings) before the topics | Human-approved: Mat 2026-11-20 |
| Style | Steps pass the vendored ASD-STE100 linter in Strict mode with 20 words or fewer per sentence; intros, alt texts and unpinned topics pass it with 0 `advisory-free` findings | Human-approved: Mat 2026-11-20 |
| Images | Light and dark WebP of 150 KB or less, taken by `npm --prefix ui run help:shots` from demo data, with no home folder path | Human-approved: Mat 2026-11-20; Mat 2026-11-16 ("This should be done with framework and scripts!") |
| First visit | The card stays closed on a first visit, and its header names the quick start | D-1289 |
| Drift | A unit test fails when a page's steps change and its images were not taken again; an Electron test proves every step target and image on the real app | Mat 2026-11-16 |
```

### Test pins

Each pin is cited by file, line and what it checks. Under D-1290 A as Mat ruled it (2026-11-20, "1290 A"), one existing assertion changes: AC-115.15's Console body (M-7, approved by that ruling). Row 0 records each pin file's SHA-256 in `baseline-pins.json`, and the gate checks that each one is unchanged, except `failure-reason-copy.test.ts`, whose row 4 hash `red-unchanged` checks.

| Pin | What it checks | After this change |
|---|---|---|
| `ui/tests/unit/help-card.test.ts` (CRLF), with AC-23.16 at `:93` | Card render, persistence, search and toggle; minimum topic keywords per module from source (`:27-43`) | Unchanged. The keywords are kept by `PLAIN_TOPICS` |
| `ui/tests/unit/help-f1-hold.test.tsx` | MEU-158 hold and route scope | Unchanged |
| `ui/tests/unit/capture-help-content.test.ts` (CRLF, constants `:7-163`) | `four-tools` and `original-annotated` sentences, order, start and end | Unchanged. Both topics are kept byte for byte apart from the one unpinned `four-tools` sentence of `CONSOLE_AND_SAVE` |
| `ui/tests/unit/capture-action-row.test.ts:713-719` (AC-81.12) | `four-tools` holds `HELP_EDIT_TEXT`; no Capture topic says `Sample` | Unchanged |
| `ui/tests/unit/capture-copy-image.behavior.test.ts:815` (AC-104.20) | Joined Capture bodies hold the copy sentence and the action names | Unchanged |
| `ui/tests/unit/capture-redact.behavior.test.ts:521` | `four-tools` redact sentence | Unchanged |
| `ui/tests/unit/capture-tool-style.test.ts:113`, `:240` | `four-tools` style sentence | Unchanged |
| `ui/tests/unit/failure-reason-copy.test.ts:28`, `:40-42` | Settings `console` body; Transcript ids in order and the `blocked` body | AC-115.15's `consoleHelp?.body` expectation changes to the `CONSOLE_AND_SAVE` body in row 4; the rest is unchanged |
| `ui/tests/unit/queue-pause-feedback.test.tsx:603` | Downloader `pause` title and body | Unchanged. The topic is pinned |
| `ui/tests/unit/layout-primitives.test.ts:200` (AC-51.6) | The test-id registry prefix hash | Unchanged. The new ids are added at the end |
| `ui/tests/unit/settings-rail.test.tsx`, `common-shortcuts.test.tsx`, `gui-actions-audit.test.ts`, `capture-page.test.ts`, `convert-page.test.ts` | HelpCard mounts and the F1 chord | Unchanged, except D-1296 (execution, Mat 2026-11-21): `capture-page.test.ts` AC-39.13, `convert-page.test.ts` AC-33.18 and `settings-page.test.ts` AC-61.16 pin topic wording, so each check names the new wording of the same topic |
| `ui/tests/e2e/help-search.spec.ts` W6-1, W6-2, W6-3 | The card is visible; search filters the `[data-help-section]` count; an off-route toggle opens Settings help | Unchanged. Steps and shots carry no `data-help-section` |
| `ui/tests/e2e/help-f1-mount.test.ts` (5 tests) | F1 on lazy pages opens a closed card once | Unchanged. The first visit stays closed (D-1289 A) |
| `ui/tests/e2e/keyboard-shortcuts.test.ts:68-105` | F1 toggles the mounted card | Unchanged |

Any other existing test that fails after a Green is S5: an M-7 question, not a fix.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `quick-start.json` | `components/help/quick-start.ts` (`validateQuickStart`) | Six feature keys; `intro` 1 sentence; 4 or 5 steps; `target` a test id or `null`; 1 or 2 shots; each targeted step in exactly one shot; sentence and step limits | An unknown key at any level is a validation problem (the unit test fails) |
| `assets/help/manifest.json` | `HELP_SHOTS_GEN` (writer), AC-162.7 test (reader) | One entry per shot; `width` ≤ 1280, `height` ≤ 900; `bytes` ≤ 153,600 each; `stepsHash` equal to `quickStartHash(page)` | Unknown keys fail the test |
| `npm run help:shots` | `ui/package.json`, `playwright.help-shots.config.ts` | Needs a build; writes only under `assets/help/` | Extra CLI arguments pass to Playwright |
| HelpCard DOM | `HelpCard.tsx` | New ids listed in `TEST_IDS`; `data-help-section` only on topics | — |

No API route, OpenAPI document, MCP tool, backend service, persisted setting or database schema changes (M-4 clear). The card's `localStorage` key and values are unchanged.

### Acceptance Criteria

- **Family.** MEU-162 uses AC-162.1 to AC-162.16. Vitest and Playwright titles start `AC-162.<n> ` with a space after, so `--require AC-162.1` never matches `AC-162.10`.
- **New names fail by assertion at Red.** `help-quick-start.test.tsx` imports `components/help/quick-start` through `import.meta.glob` with `eager: true` and asserts that the module exists and that `typeof mod.validateQuickStart === 'function'` before anything else. So no Red fails because a module is missing (Session 52 RULE-4).
- **Guards** pass at Red: AC-162.5's no-match case and AC-162.13.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-162.1 | unit | `validateQuickStart(QUICK_START)` returns `[]`. The data has the six feature keys, each with an intro, 4 or 5 steps and 1 or 2 shots, and every non-null `target` occurs as `data-testid="<target>"` (or as a template or constant that yields it) in the source that renders it on that page: the page's feature folder or a shared producer under `components/` that the page mounts (Convert's and Downloader's `queue-card-primary-action` comes from `components/queue/QueueCard.tsx`). The checks run on the source files of `features/<folder>/` and `components/`, read from disk. | Human-approved (Mat 2026-11-20); D-1291 | Fixtures with a 6-step page, a step in no shot, a step in two shots, a 21-word sentence, a `;`, an unknown key or an unknown target each give one named problem |
| AC-162.2 | unit (pytest) | `tests/tooling/test_help_guide_ste.py`: `tools/help_guide_ste.py` exits 0 on the repository. All steps pass Strict (0 findings at any level), and intros, alts and unpinned topics have 0 `advisory-free` findings; an unknown level fails. | Human-approved (Mat 2026-11-20, the asd-ste100 skill); D-1293 | Its selftest fixtures fail: a passive step ("The file is downloaded by the app.", an `advisory` finding that Strict counts), a step with a phrasal verb ("Spin up the job.", `advisory-free`), a 21-word sentence, an unpinned topic with an `advisory-free` finding, and a finding with an unknown level |
| AC-162.3 | unit | Rendered `<HelpCard feature="downloader" …>`, closed: the header holds `help-quick-start-hint` with `Quick start · 5 steps`. After a click on the header, `help-quick-start-intro` holds the intro, `help-quick-start` is an `<ol>` with five `help-quick-start-step` items whose text equals the JSON steps in order, and it comes before the first `[data-help-section]` in document order. No step, intro or figure has `data-help-section`. | Human-approved; D-1289, D-1291 | In Red the hint and the list are missing |
| AC-162.4 | unit | Two tests. `AC-162.4 css`: `styles.css` holds the two theme rules of `THEME_SHOT_CSS` exactly once each. `AC-162.4 figures`: each shot renders one `help-shot` figure with `data-shot-steps` equal to its step list joined by `,`, two `img` elements with `loading="lazy"`, the classes `help-shot__img--light` and `help-shot__img--dark`, `src` from `shotUrl(name, theme)`, the JSON `alt`, and `width` and `height` from the manifest. On Settings, two figures render. `AC-162.4 figures` needs the images, so it fails by assertion until row 8 and passes from row 8 unchanged. | D-1292 | In Red no figure renders and the rules are missing |
| AC-162.5 | unit | With the card open, typing `cookie` in `help-search` removes the intro, the list, the figures and the "More about this page" heading. Only the `cookies` topic stays, rendered `open`. Clearing the search brings them back, with every topic closed. Typing `zzzz` shows "No help topics match your search." | Local Canon (06 §Help (per page): search); D-1290 | In Red the pre-search list assertion fails |
| AC-162.6 | unit | With the search empty, every topic is a `<details data-help-section>` without `open`, with the title in `<summary>`. A click on a summary opens it and shows the body. | D-1290 | In Red topics are articles |
| AC-162.7 | unit | `assets/help/manifest.json`: one entry per shot in `QUICK_START` and no other. Each entry's `stepsHash` equals `quickStartHash(page)` (computed with `node:crypto` over `quickStartHashInput`). Both files `<name>-light.webp` and `<name>-dark.webp` exist. Each is 153,600 bytes or fewer, and its RIFF/WebP header gives the manifest's `width` and `height`, with width 1280 or less and height 900 or less. | D-1292, D-1294 | A copy of the data with one step's text changed gives a hash mismatch named by page; a missing file and an over-size file are each named |
| AC-162.8 | unit | `AC-162.8 privacy`: `findPrivatePath` flags `C:\Users\alex\Videos`, `c:/users/alex/x`, `/Users/alex/`, `/home/alex/` and, with `roots` `['C:/Temp/av-kit/x/tmp', 'P:/av-kit']`, `c:\temp\av-kit\x\tmp\avkit-1\logs\console.log` and `P:\av-kit\ui\out`. It returns `null` for `Format`, `C:/e2e/outdir`, `D:\Media\av-kit`, `C:\Users\Public\Videos` and an empty string. `AC-162.8 clip`: `shotClip` returns the union plus 24 px for boxes inside a 1280 × 800 viewport, and a named error for a target box partly below the viewport, a target box fully outside it, and a union taller than 900 px. `AC-162.8 text`: with the clip `{x:0,y:0,width:100,height:100}`, `clipText` keeps an item with a rect inside the clip and a control value inside it. It drops a masked item inside the clip, an item whose rects are all outside the clip, and an item whose only rect has zero area. Each dropped item holds `C:\Users\alex\x`, so `findPrivatePath` of the joined text is `null`. The same item, not masked and inside the clip, makes `findPrivatePath` flag it. | D-1292 (privacy rule: no home path in tracked files or images) | Each flagged input and each named clip error above is the negative |
| AC-162.9 | unit | `PLAIN_TOPICS`: every topic id and order per module equals its row-0 list (`baseline-pins.json`). Each pinned topic's title and body equal their row-0 values, with `four-tools` compared after the one `CONSOLE_AND_SAVE` replacement and holding no `POST`. Every unpinned body, `settings:console` included, holds its §Fact table keywords (case ignored) and none of the jargon tokens (also `log_level`, `log_to_file`, `console_visible` and `{app_data}`). | Human-approved (Mat 2026-11-20: "very inadequate guide"); D-1290 | In Red the jargon tokens are present (Settings `leaf-keys` holds `PUT `) |
| AC-162.10 | integration | Electron, fresh scratch app data, for each of the six pages: the help card is closed on the first visit (`aria-expanded="false"`) and the hint reads `Quick start · N steps` with N from the JSON. | D-1289 | Passes at Red for the closed state; the hint fails at Red |
| AC-162.11 | integration | Electron, per page, after its `stage`, light theme: open the card. The step texts equal the JSON. Every step `target` is visible (`getByTestId(target).first()`). Each figure's light image, after `scrollIntoViewIfNeeded`, has `naturalWidth > 0` and `complete`, and its dark image has computed `display: none`. Then set the `dark` class: the dark image loads with `naturalWidth > 0` and the light image is `display: none`. On Transcript, `view-compiled-link` is absent and `open-zip-link` is visible, with no compiled path in the seed. Every launch prints `isolation: ok`. | Human-approved; D-1292, D-1294 | In Red the targets are visible and the step list is missing |
| AC-162.12 | integration | Electron, Downloader: open the card. Before the search, `help-quick-start` is visible. Fill `help-search` with `SABR`. `help-quick-start` and every `help-shot` are absent, and the visible `[data-help-section]` count is 1. | Local Canon (W6-2 search) | In Red the pre-search list assertion fails |
| AC-162.13 | check | The pins in §Test pins pass unchanged, with their row-0 hashes, in the gate's `ui-tests` and in row 9's E2E runs (`help-search.spec.ts`, `help-f1-mount.test.ts`, `keyboard-shortcuts.test.ts`). | Local Canon | A failure is S5 |
| AC-162.14 | check | Row 8: `npm --prefix ui run help:shots` exits 0, writes 14 WebP files and `manifest.json`, and its log has one `isolation: ok` line per launch and one `privacy: clean <name>-<theme>` line per file. Running it a second time gives a manifest with the same `stepsHash`, `width` and `height` values. | Mat 2026-11-16 ("framework and scripts"); D-1292 | A planted `C:\Users\alex` value in the Settings stage (row 8's negative run, done in a copy of the stage under `C:/Temp`) makes the run exit 1 with `privacy: blocked settings-download-light` and writes no file |
| AC-162.15 | check | Row 2: each vendored skill file's SHA-256 equals the creative-writing copy's. `LICENSE` is the MIT text, and `UPSTREAM.md` names the upstream URL, commit `32511c6992ecb5f1971e46a2943f2e6adceedafe` and the licence. | D-1293 | A changed byte fails the row |
| AC-162.16 | check | Row 9: `help-quick-start.test.ts` passes 3 runs of 3, with no `flaky` and no `unhandled rejection:` line. | Mat 2026-11-16 | A failed run is S7 |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| A short first-run guide on each page, with images | Human-approved | Mat 2026-11-20; the quick start sits in the existing card (D-1291) |
| Steps in ASD-STE100 | Human-approved | Strict mode for steps, flavored for intros, alts and topics; vendored linter as a gate (D-1293) |
| Screenshots taken by script from the running app | Human-approved | `help:shots` generator with demo stages (D-1292) |
| "Not too long" | Human-approved | 1 intro sentence, 4 or 5 steps, 1 or 2 images, topics closed (D-1290) |
| First-visit open state | Local Canon (06/08/09 wireframes, P8/P9 ACs) + human brief | Stays closed; header hint (D-1289) |
| Topic rewrite scope | Human-approved (Mat 2026-11-20, "1290 A") | Unpinned topics and the Console topic in plain words; one `four-tools` sentence replaced; the other pinned text kept (D-1290) |
| Theme of the images | Local Canon (`lib/theme.ts`) | Light and dark pairs swapped by CSS (D-1292) |
| Images going stale | Agent decision | Manifest hash test plus Electron target check (D-1294) |
| No private data in images | Local Canon (privacy rule) | Demo stages plus `PRIVACY_GUARD` (D-1292) |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/components/help/HelpCard.tsx` (LF) | modify | `CARD_QUICK_START` |
| `ui/src/renderer/src/components/help/quick-start.json` (LF) | new | `QUICK_START_DATA` |
| `ui/src/renderer/src/components/help/quick-start.ts` (LF) | new | `QUICK_START_SCHEMA` |
| `ui/src/renderer/src/components/help/help-shots.ts` (LF) | new | `HELP_SHOTS` |
| `ui/src/renderer/src/assets/help/*.webp` (14) and `manifest.json` (LF) | new | Generated images and manifest |
| `ui/src/renderer/src/styles.css` (CRLF) | modify | `THEME_SHOT_CSS` and card styles |
| `ui/src/renderer/src/features/{downloader,transcript,tts,converter,capture,settings}/*-help-content.ts` (CRLF) | modify | `PLAIN_TOPICS` (unpinned bodies and titles only) |
| `ui/tsconfig.json` (LF) | modify | `resolveJsonModule: true` |
| `ui/package.json` (CRLF) | modify | `help:shots` script |
| `ui/playwright.help-shots.config.ts` (LF) | new | Generator config |
| `ui/tests/help-shots/help-shots.shots.ts`, `stage.ts`, `privacy.ts`, `clip.ts` (LF) | new | `HELP_SHOTS_GEN` (with `gatherShotText`), `DEMO_STAGE` (with `launchIsolated`), `PRIVACY_GUARD` (with `clipText`), `shotClip` |
| `ui/tests/unit/help-quick-start.test.tsx` (LF) | new | AC-162.1, AC-162.3 to AC-162.7, AC-162.9 |
| `ui/tests/unit/help-shots-privacy.test.ts` (LF) | new | AC-162.8 (privacy, clip and text) |
| `ui/tests/e2e/help-quick-start.test.ts` (LF) | new | AC-162.10 to AC-162.12 |
| `ui/tests/e2e/test-ids.ts` (CRLF) | modify | `TEST_IDS`, appended |
| `ui/tests/unit/failure-reason-copy.test.ts` | modify | AC-115.15's Console body expectation (`CONSOLE_AND_SAVE`, D-1290 A) |
| `.agent/skills/asd-ste100/**` | new | Vendored skill (byte-identical) and `UPSTREAM.md` |
| `.agent/skills/README.md` (CRLF) | modify | One row for the skill |
| `tools/help_guide_ste.py` (LF) | new | `STE_GATE` |
| `tests/tooling/test_help_guide_ste.py` (LF) | new | AC-162.2 |
| `docs/build-plan/06-gui.md` (CRLF) | modify | Residual section (row 1), Delivered note (row 10) |
| `docs/build-plan/build-priority-matrix.md` (CRLF) | modify | Row 6.23 |
| `.agent/context/meu-status.yaml` (LF) | modify | MEU-162 entry and status |
| `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md` | modify | Regenerated by `meu_status.py render` only |
| `.agent/docs/commands.md` (CRLF) | modify | `help:shots` row |

### Project files

- **Plan-local scripts** live in this plan folder. Row 0 writes `baseline.ps1`, `red-check.py`, `identity.py`, `eol-check.py`, `host-wait.py` and `load-run.py`, copied in shape from `2026-11-17-ui-small-fixes/` and taking any newer form from `2026-11-19-e2e-host-parity/`. Row 1 writes `meu-register.py`, adapted from Session 97's. H1-2 writes `session-gate.ps1`.
- **Row 0 data:** `baseline.sha`, `baseline-dirty.txt`, `baseline-scope.json`, `baseline-eol.json`, `baseline-skip-hashes.json` and `baseline-pins.json`, which holds the pin files' SHA-256 values and each module's topic ids, titles and pinned bodies.
- **Draft:** `quick-start-draft.json` (this plan's content draft, linted in `hq99-ste-draft-r2.txt`).
- **Read, never changed:** the six page components, `lib/theme.ts`, `ui/tests/e2e/electron-app.ts`, the seam spec files named in §Goal, `ui/playwright.config.ts`, the pin files and the creative-writing skill copy.
- **State:** `docs/execution/metrics.md` (CRLF), `.agent/context/current-focus.md` (CRLF), the handoff, the rolling reviews and the reflection.
- **New names (`DECLARED_NEW`):** `QUICK_START`, `validateQuickStart`, `quickStartHash`, `quickStartHashInput`, `shotUrl`, `shotSize`, `STAGES`, `launchIsolated`, `findPrivatePath`, `clipText`, `gatherShotText`, `shotClip`, `SHOT_MASKS`, `HELP_QUICK_START`, `HELP_QUICK_START_STEP`, `HELP_QUICK_START_INTRO`, `HELP_QUICK_START_HINT`, `HELP_SHOT`.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Rewording the four pinned topics (`downloader:pause`, `transcript:blocked`, `capture:four-tools` apart from its one Save sentence, `capture:original-annotated`) or splitting `four-tools` | out-of-scope | — | D-1290 A (Mat 2026-11-20); option C was not chosen |
| Opening the card on a first visit, or highlighting the hint until the first open | out-of-scope | — | D-1289 A (Mat 2026-11-20) |
| A separate guide document or README rewrite | out-of-scope | — | D-1291: the guide lives where the user needs it; Mat asked for the page guides |
| Retaking the README images | out-of-scope | — | `docs/images/readme/` is not the How it works section; Mat did not ask |
| A click-to-zoom view of the screenshots | out-of-scope | — | "not too long, just enough to get people curious" (Mat 2026-11-20); the images fit the card width |
| Running `help:shots` in CI | out-of-scope | — | The drift tests in the gate catch stale images; taking the images needs a desktop Electron run |

## BUILD_PLAN.md Audit

Row 1 registers MEU-162 (`gui-help-quick-start`, phase 6, P2, matrix 6.23, `06-gui.md`) as `pending`. Row 10 sets it to `ready_for_review` with this plan's `execution_plan`, and H2-2 sets it to `approved`, both through `tools/meu_status.py update`. `meu-registry.md` and `docs/BUILD_PLAN.md` are regenerated by `tools/meu_status.py render`, never by hand:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/help-quick-start/hq-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/help-quick-start/hq-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. Use `rtk proxy` for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` has the shape of `2026-11-17-ui-small-fixes/baseline.ps1`:

1. **Tree and host.** It prints `HEAD`, `git status --porcelain --untracked-files=all`, `git worktree list` and one host-load sample. It records `baseline.sha` and `baseline-dirty.txt`.
2. **Scope binding.** It records `baseline-scope.json`: the SHA-256 of each §Files Modified path and each "Read, never changed" path, or `absent`. The files that the parallel session av-kit-c4 may also write (`.agent/docs/commands.md`, `.agent/context/current-focus.md`, `docs/execution/metrics.md`, `.agent/context/known-issues.yaml` and `.md`) are recorded as `shared`, with no hash. S4 never fires on them. The row that writes one re-reads it just before the edit and changes only its own lines. Every new path must be `absent`. It also records `baseline-eol.json`, `baseline-skip-hashes.json` (every file under `packages/` and `mcp-server/`) and a byte copy of each scope file under `C:/Temp/av-kit/help-quick-start/baseline-copies/`.
3. **Pins.** It records `baseline-pins.json`: the SHA-256 of each §Test pins file, and for each content module the ordered topic ids, titles and the bodies of the pinned topics. Row 0 reads them with its own copy of the `STE_GATE` topic regex, and row 3 checks that `tools/help_guide_ste.py`'s parser gives the same result.
4. **Citations.** It re-reads each anchor this plan cites and records its current line in `baseline-citations.txt`. The anchors are: the six HelpCard mounts, `readExpanded` and `HELP_FEATURE_ROUTE` (`HelpCard.tsx`), the 06 `### Help (per page)` heading and `## Validation Commands`, matrix row `6.22`, every step target in `quick-start-draft.json` (found in its feature folder or in `components/`), `export async function launchElectron`, the seam functions named in §Goal, `// MEU-51 primitive harness IDs.` and `"test:e2e"`. A missing anchor is S2. An anchor that only moved is corrected in the handoff.
5. **Free ids.** MEU-162, matrix 6.23 and the anchor `help-quick-start-residual` are free. D-1289 to D-1298 are unclaimed outside this plan.
6. **Base receipt.** It runs the full Vitest suite (`hq-base-ui.txt`, pwsh in `ui/`) and the pytest suite for `tests/tooling` (`hq-base-tooling.txt`). Their failures are recorded, not fatal, and the gate excuses only those ids.
7. **Plan-local scripts.** It copies `red-check.py`, `identity.py`, `eol-check.py`, `load-run.py` (with `host_load_wait` at 50 %) and `host-wait.py` with this plan's `PLAN`, artifacts and `DECLARED_NEW`. The `red-check.py` fixtures use AC-162 (it must refuse `AC-162.1` matching `AC-162.10`). It runs their selftests and runs `ruff format --check` and `ruff check` on the plan folder's Python.
8. **Secrets and the fleet hub.** The scope walk drops `.mcp.json`, `mcp-token.txt`, `.claude.json`, `.env`, `.claude/settings.local.json` and `.agent/fleet/hub` before any stat or read.

If any step except the base receipts fails, the row fails and nothing else runs.

### 2. Red, then Green

- **Every Red comes before any product change.** Rows 3, 4 and 5 change no product file. Row 5 builds the unchanged app.
- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py --require` names AC-162.2 (row 3, pytest), AC-162.1 and AC-162.3 to AC-162.9 (row 4, Vitest) and AC-162.10 to AC-162.12 (row 5, Playwright). AC-162.10's closed-state half passes at Red. AC-162.11 must fail at the step or figure assertion: a failure that names a step target is S8, not a Red.
- **Expectations stay the same in Green** (S3). Rows 3, 4 and 5 record the hashes of the test-side files they write, and rows 6 to 9 check those hashes. `stage.ts` is test-side and stays unchanged after row 5, except by an S8 route back to the plan.
- **Green order.** Row 6 makes AC-162.2 and AC-162.9 pass. Row 7 makes AC-162.1, AC-162.3, `AC-162.4 css`, AC-162.5, AC-162.6 and AC-162.8 pass, with `AC-162.4 figures` and AC-162.7 still failing by assertion and named (`row-check.py only-failing`). The renderer builds and type-checks in that state because `HELP_SHOTS` reads the manifest through `import.meta.glob`. Row 8 makes `AC-162.4 figures` and AC-162.7 pass with the test file at its row 4 hash.
- **Line endings** are checked by `eol-check.py` after each Green. CRLF files get no bare LF, and LF files get no CR.

### 3. Generator run (row 8)

1. Build: `npm --prefix ui run build`.
2. Wait for the host load to read 50 % or less, then run `npm --prefix ui run help:shots` with `TMP` and `TEMP` at `C:/Temp/av-kit/help-quick-start/tmp`.
3. The row's Python reads `manifest.json`, lists the 14 files with their sizes and dimensions, checks the 14 `privacy: clean` lines, and writes `hq-row9-shots.txt`.
4. It runs the generator a second time and compares the manifests' `stepsHash`, `width` and `height` values.
5. **Negative run.** It copies `stage.ts` to `C:/Temp/av-kit/help-quick-start/neg/`, plants `C:\Users\alex\Videos` in the Settings download path, and runs the generator for the Settings page only against that copy, through the env var `AVKIT_HELP_SHOTS_STAGE` (read by the spec, test-only). The run must exit 1, with `privacy: blocked settings-download-light`, and no file under `assets/help/` may change; the row compares hashes before and after.
6. The coordinator looks at each of the 14 images (Read tool) and records one line per image in the handoff: the numbers sit on the right controls, the theme is right, and no text is cut. This is a review of generated output, not a manual app check.

### 4. Electron proof (row 9)

- `help-quick-start.test.ts` runs 3 times (`--repeat-each 3`, AC-162.16).
- `help-search.spec.ts`, `help-f1-mount.test.ts` and `keyboard-shortcuts.test.ts` run once each (AC-162.13).
- The row's Python counts `^ +ok +[0-9]+ .*AC-162\.` lines, and requires the `N passed` line and no `failed`, `flaky` or `unhandled rejection:` line. The counts go to `hq-row11-runs.txt`.

### Session gate (H1-2)

`session-gate.ps1` has the shape of `2026-11-17-ui-small-fixes/session-gate.ps1`: one receipt per step, `hq-D6-<step>`, fail-fast, with later steps printed as `not_run`. The last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `ui-types`, `ui-lint` (pwsh in `ui/`); `task-contract`; `scope-paths` (every changed path is in §Files Modified, this plan folder, the closeout artifacts or `baseline-dirty.txt`); `line-endings` (`eol-check.py`); `home-path` (`tools/check_home_path.py`); `skill-identity` (AC-162.15's SHA-256 check); `pins-unchanged` (`baseline-pins.json`); `red-check-selftest`; `eol-check-selftest`; `py-format` and `py-lint` (`ruff format --check` and `ruff check` on `tools/help_guide_ste.py`, its test and this plan folder's Python; the vendored linter is excluded, as it is a byte copy) |
| Targeted | `ste-gate` (`uv run pytest tests/tooling/test_help_guide_ste.py`); `help-unit` (`help-quick-start.test.tsx`, `help-shots-privacy.test.ts` and the §Test pins unit files) |
| Host load | `host-load` before every Electron step: waits until the load reads 50 % or less, re-sampling every 30 s for up to 10 minutes, and records the value |
| Fresh full | `ui-tests` (full Vitest); `py-tooling` (`uv run pytest tests/tooling`); `ui-build`; `e2e-help-quick-start`; `e2e-help-search`; `e2e-help-f1-mount`; `e2e-keyboard-shortcuts`; `state-render` (`meu_status.py render --check`) |
| Skipped, with reason | `py-types` and the full `py-tests`: no Python product file changes, and `tests/tooling` runs in full. `openapi` and `mcp-*`: every file under `packages/` and `mcp-server/` keeps its `baseline-skip-hashes.json` hash. The rest of `test:e2e`: only the help card changed, and its suites run. The generator is not a gate step; its output is checked by AC-162.7 and AC-162.11 |

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | Row 0 finds a citation anchor missing or doubled, MEU-162 or matrix 6.23 taken, or a step target missing from its feature folder and from `components/` | Stop and bring the receipt to Mat. A moved line is corrected, not a stop |
| S3 | A Red receipt fails `red-check.py`, or a Green row needs a changed expectation | Fix the test setup; never edit an expectation in Green |
| S4 | A path outside this plan's scope and `baseline-dirty.txt` changes, or a scope path other than the `shared` files of `baseline-scope.json` changes by another hand | Stop and re-baseline with Mat. Never commit, stash or revert another session's work |
| S5 | An existing test fails after a Green | Rerun it alone once. If it fails again, stop: that is an M-7 question, not a fix |
| S6 | Codex is unavailable or the ledger refuses | Mat |
| S7 | An Electron test fails in any of row 9's runs, or a receipt holds `unhandled rejection:` | Stop and bring the receipts to Mat. Never raise a timeout or add a retry |
| S8 | A step's target cannot be made visible by its stage with seam data alone (it needs a backend or a page change) | Stop and route back to the plan. A new brief chooses another target or another step |
| S9 | `shotClip` returns an error (a target not fully in the viewport after the scroll, or a union larger than 1280 × 900 CSS px), a badge lies outside the clip, a mask meets a target, or a WebP stays above 150 KB at quality 0.5 | Stop and route back to the plan. The fix is a shot split in the JSON, which is a content change for review |
| S10 | The privacy guard blocks a real (not planted) image | Stop: find which seed or app value holds the path, and fix the seed. Never weaken the guard |
| S11 | A rewritten topic cannot keep a §Fact table fact and pass the linter | Stop and bring the sentence to Mat with the linter finding |
| S12 | A step would need user data (the models folder, the app database, the settings file) or the network, or a launch's `USERPROFILE`, `HOME` or `AVKIT_APP_DATA` is not its scratch path | Stop. Every Electron run uses `launchIsolated()` |

## Decision Log

> [!NOTE]
> D-1291 to D-1294 are autonomous, with `mandatory: none`. Each passed the §4a list and the §4 test. D-1289 and D-1290 hit M-5 (a user-visible product choice that the canon does not settle). Mat decided both on 2026-11-20: "1289 A, 1290 A, execute".
>
> No other M item is hit:
>
> - No API, OpenAPI or MCP change (M-4 clear).
> - No user data is read or written (M-2 clear).
> - D-1290 A changes one existing assertion, AC-115.15's Console body (M-7). Mat approved it with the ruling.
>
> Execution added D-1296 (human, M-7: Mat 2026-11-21), D-1297 and D-1298 (autonomous, `mandatory: none`), and D-1295 after the execution review's round 1 (autonomous, `mandatory: none`).

```yaml
decision_log:
  - id: D-1289
    stage: planning
    question: "Should the How it works card open by itself on a page's first visit, now that it holds a quick start?"
    resolution: human
    class: product-preference
    mandatory: [M-5]
    chosen: "A (Mat, 2026-11-20: '1289 A, 1290 A, execute'): the card stays closed on a first visit, as now; its header gains the hint 'Quick start · N steps'."
    source_tag: Human-approved
    precedents:
      - "ui/src/renderer/src/components/help/HelpCard.tsx:28-38 — first visit closed ('the header stays visible as the affordance'); shipped in the first UI commit fb62636 (2026-09-02, history bundle 20261024) with no recorded ruling"
      - "docs/build-plan/06-gui.md:319-332 — adapt Zorivest *HelpCard.tsx; accessible disclosure, persist collapse"
      - "P:/zorivest .../AccountsHelpCard.tsx:32 opens on first visit; OptionsChainHelpCard.tsx:29 stays closed 'to save space'"
      - "docs/build-plan/08-video-conversion.md:75, 09-screenshot-capture.md:93 — wireframes 'Help (collapsed)'"
      - "docs/execution/plans/2026-08-21-p6-gui-settings-help/implementation-plan.md:77 — 'First visit expanded' (from the Zorivest pattern; never shipped)"
      - "ui/src/renderer/src/features/downloader/DownloaderPage.tsx:566-572 — the column is 'oversubscribed at the app's own 1280x800 default window'"
      - "No USER_EXPLICIT ruling on the first-visit state (sweep receipts hdp-sweep-*.txt)"
    research:
      engine: tavily
      sources:
        - "https://www.nngroup.com/articles/onboarding-tutorials — users skip pushed tutorials; pulled, contextual help preferred"
        - "https://www.nngroup.com/articles/mobile-app-onboarding — instructional onboarding 'brief, optional'"
        - "https://trevorcalabro.substack.com/p/onboarding-and-in-app-help-strategy — 'Do not hide essential guidance by default'"
    reasoning: "The Downloader column already lacks room at 1280x800, so an open card would hide the URL field and queue on a new user's first view; NN/g favours short, optional, pulled help, which a closed card with a 'Quick start · N steps' header gives. Opening on first visit (B) or once on Downloader (C) would reach only new installs, because HelpCard writes its state on every mount, and would change about 10 E2E and about 16 unit assertions (help-f1-mount, help-search W6-2, help-card AC-23.17, help-f1-hold AC-158.3-158.7) (M-7). Weakness: with no usage data, a user who never notices the hint cannot be detected. Expert pass (fresh context) held A; an accent on the hint until the first open was offered as an option."
  - id: D-1290
    stage: planning
    question: "How far does the rewrite of the existing help topics go?"
    resolution: human
    class: product-preference
    mandatory: [M-5]
    chosen: "A (Mat, 2026-11-20: '1289 A, 1290 A, execute'; the brief as revised by the HDP re-run): rewrite every unpinned topic in STE-flavored plain words with its facts kept (§Fact table); also rewrite the Settings Console topic (changing the AC-115.15 body assertion, keeping 'Errors are always written' and adding a settings:console Fact table row) and replace the unpinned sentence 'Save POSTs the full annotation list.' in four-tools (CONSOLE_AND_SAVE); keep all other pinned text byte for byte; render all topics as closed one-line titles under the quick start. The plan body was amended after the ruling (PINNED_TOPICS, CONSOLE_AND_SAVE, M-7 notes, Test pins, AC-162.9, Fact table, Files Modified, Out of Scope, task rows 4 and 6); the execution review covers the amendment, since the plan review rounds are used up."
    source_tag: Human-approved
    precedents:
      - "Mat 2026-11-20 — 'Right now it is very inadequate guide on how to use each page'"
      - "ui/tests/unit/capture-help-content.test.ts:7-186 — 18 constants pin the four-tools and original-annotated sentences, their order, start and end"
      - "ui/tests/unit/failure-reason-copy.test.ts:28, :40-42; queue-pause-feedback.test.tsx:603 — settings console, transcript blocked and downloader pause pinned exactly"
      - "ui/src/renderer/src/features/settings/settings-help-content.ts:20-23 — the Console body shows log_level, log_to_file, console_visible and an app-data path slot; only failure-reason-copy.test.ts:29-33 (AC-115.15) pins it"
      - "ui/src/renderer/src/features/capture/capture-help-content.ts:27 — 'Save POSTs the full annotation list.'; no test pins it (the four-tools pins are sentence checks)"
    research:
      engine: tavily
      sources:
        - "https://www.opm.gov/information-management/plain-language — everyday words, no undefined technical terms"
        - "https://www.stylemanual.gov.au/writing-and-designing-content/clear-language-and-writing-style/plain-language-and-word-choice — plain word choice"
    reasoning: "The earlier brief said the pinned text was already plain apart from its length; that is false for the Console topic, which shows setting keys and a path placeholder to users, and for one four-tools sentence that uses the API word POST. Both can go for one changed assertion and no other test change. Rewriting all five pinned topics and splitting four-tools changes more than 25 assertions in 7 test files (M-7) for gains the narrower rewrite already gets. Expert pass (fresh context) widened A by the POST sentence."
  - id: D-1291
    stage: planning
    question: "Where does the guide live, and in what form is its content kept?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Inside each page's existing HelpCard, before the topics; the content is one JSON file read by the card, typed and validated in TypeScript and linted by Python."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/06-gui.md:319-332 — help is per page, in the HelpCard"
      - "ui/src/renderer/src/components/help/HelpCard.tsx — F1, search and persistence already exist"
    research: { engine: none, sources: [] }
    reasoning: "The user is on the page when they need the steps, and F1 already opens the card. JSON lets the Python STE linter read the steps without parsing TypeScript and lets the card read them by feature, so no page component changes. Two-way: one data file and one component."
  - id: D-1292
    stage: planning
    question: "How are the screenshots made, stored and kept private?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "HELP_SHOTS_GEN, DEMO_STAGE and PRIVACY_GUARD: a tracked Playwright generator on the real Electron app with demo seams, a numbered overlay baked into each image, light and dark WebP (150 KB or less, 1280 x 900 or less) encoded by the renderer's canvas, in ui/src/renderer/src/assets/help/, swapped by CSS on the dark class; a guard refuses any image whose region text holds a home path."
    source_tag: Local Canon
    precedents:
      - "Mat 2026-11-16 — 'This should be done with framework and scripts!'"
      - "ui/tests/e2e/electron-app.ts launchElectron and the fetch seams in the page specs — the renderer's requests go to the seam; the spawned backend and main IPC run on the launch's scratch env"
      - "lib/theme.ts — the dark class on documentElement"
      - "memory rule: write no home path into tracked files or images"
    research: { engine: none, sources: [] }
    reasoning: "The existing E2E seams already fill every page with demo data, and a scratch app data folder plus a scratch USERPROFILE and HOME keep the spawned backend and the readiness probe off user data, so the generator reuses that pattern. Baked numbers keep the image and the step list in step without an overlay layer in the app. Canvas WebP needs no new dependency. Two images per shot cost about 1 MB in all. Two-way: generated files can be retaken or removed."
  - id: D-1293
    stage: planning
    question: "How does the repo use the ASD-STE100 skill?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "STE_GATE: vendor the skill byte for byte into .agent/skills/asd-ste100/ with a new UPSTREAM.md (MIT allows it, and creative-writing does the same), and gate the content with tools/help_guide_ste.py and a pytest; add the 20-word, two-sentence and no-semicolon step checks the linter leaves out; treat advisory-free as hard, count advisory findings in Strict steps, and fail closed on an unknown level."
    source_tag: Research-backed
    precedents:
      - "P:/creative-writing/.agent/skills/asd-ste100/UPSTREAM.md — vendored, not forked, byte-identical"
      - "P:/creative-writing/.agent/skills/asd-ste100/scripts/ste-lint.py:73 — MAX_WORDS 25; the instruction cap of 20 is not detected"
    research: { engine: none, sources: ["https://github.com/danyuchn/asd-ste100-skill — MIT, commit 32511c6"] }
    reasoning: "A tracked test cannot depend on another repository's path, so the linter must be in this repo. A byte copy with an UPSTREAM.md keeps updates simple. The extra checks cover the Strict rules the linter says it cannot see."
  - id: D-1294
    stage: planning
    question: "How do the tests catch images that no longer match the steps or the UI?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Two guards: the manifest stores a hash of each page's steps and shots, and a unit test fails when it differs from the data (AC-162.7); an Electron test proves every step target is visible and every image loads in both themes on the real app (AC-162.11)."
    source_tag: Local Canon
    precedents:
      - "Mat 2026-11-16 — framework and scripts, not manual checks"
    research: { engine: none, sources: [] }
    reasoning: "A text change without new images fails at once in Vitest. A UI change that removes or renames a target fails in Electron. A pixel diff of the images was rejected, because fonts and timing differ by host and it would be flaky."
  - id: D-1296
    stage: execution
    question: "Row 6 rewrote topics that three older tests pin by wording (capture-page AC-39.13, convert-page AC-33.18, settings-page AC-61.16); how is that fixed?"
    resolution: human
    class: two-way
    mandatory: [M-7]
    chosen: "Update the three tests: each check names the new wording of the same topic ('When F2 is in use', 'MCP sees the same shots', 'Close to tray keeps F2', 'add and start', 'startup entry for your user only'); refresh the two baseline-pins.json hashes; row 7 also runs settings-page.test.ts"
    source_tag: Human-approved
    precedents:
      - "implementation-plan.md:294 named capture-page and convert-page as unchanged mount tests; the pin scan missed their topic-text checks and settings-page AC-61.16"
      - "failure-reason-copy.test.ts: D-1290 A changed a pinned test in row 4"
    research: { engine: none, sources: [] }
    reasoning: "The topics still cover the same subjects, so pointing each check at the new words keeps the tests' intent and keeps the D-1290 A rewrite whole. Keeping the old wording leaves five non-STE topics and grows the pin list; reverting row 6 drops D-1290 A."
    human_message_reference: "USER_EXPLICIT 2026-11-21 'Update the 3 tests (Recommended)'"
  - id: D-1297
    stage: execution
    question: "The first image review found cut text (labels at the top, Capture's toolbar, a 191 px wide Settings strip without its Fix link), and the second found badges over the first letters of small targets and half rows at the clip edge. How does the generator frame a shot?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "In ui/tests/help-shots/help-shots.shots.ts only: centerTargets scrolls the targets' union to the middle of the scroll container (a union too tall starts 48 px below the top); contextBoxes adds each target's full-width section rows and its label boxes to the clip, with no badge or outline; the badge sits at x-16, y-16; tidyClip moves each clip edge off any unmasked text line or control it cuts, never past the viewport, and the 1280 x 900 cap is checked again. shotClip, stage.ts, the privacy guard and every test assertion are unchanged."
    source_tag: Local Canon
    precedents:
      - "HELP_SHOTS_GEN (plan Single-statement contracts): scrollIntoView({ block: 'start' }) and the union of the target boxes plus 24 px; this departs from that text"
      - "hq-row8-review.txt: the second set passed 14 of 14 (numbers on the right controls, right theme, no text cut, no personal data)"
    research: { engine: none, sources: [] }
    reasoning: "Mat asked for images that get a first-time user started; a label cut in half or a strip with no Fix link does not. The change touches only how the clip is framed. The target rule, the cap and the privacy check that reads the final clip are the plan's, so no acceptance criterion or test changes (no M item). The options not taken: a fixed per-page clip breaks when the layout moves; a full-page shot breaks the 1280 x 900 cap and the 150 KB limit."
  - id: D-1298
    stage: execution
    question: "The approved draft's Capture step 2 says the shot list is 'below the image', but the filmstrip is an aside at the left of the editor (CapturePage.tsx:2789-2790). Keep the draft text or correct it?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Correct the one sentence in quick-start.json to 'Click the new shot in the list at the left of the image.'; the plan's quick-start-draft.json keeps the old text; the STE gate is 0 problems and the capture stepsHash and images are retaken in row 8"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:2789-2790 — the filmstrip aside renders before the editor"
    research: { engine: none, sources: [] }
    reasoning: "A step that points to the wrong place fails the one thing the quick start is for. The change has one reading, no test pins the sentence, and the image drift test (AC-162.7) forces the images to follow, so no M item is hit."
  - id: D-1295
    stage: execution
    question: "The execution review (round 1, F1, Medium, non-blocking) found that the generator switches only the dark class, so tts-dark.webp keeps a white Format select and settings-setup-dark.webp white Client and Scope selects. Fix it now, or keep the images and register an issue?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Fix it now in ui/tests/help-shots/help-shots.shots.ts only: applyTheme does what applyDocumentTheme does (the dark class, colorScheme and the av-kit:theme-changed event), waits two frames, then refuses the shot when a select's inline background is still the other theme's G30 colour (SelectInput.tsx G30_PAIRS); selects styled by a CSS variable follow the class. A planted copy without the event fails tts dark with three white selects (hq-d1295-neg.txt). Retake the 14 images, rerun rows 8 and 9 and the gate, and ask the reviewer for a recheck. ui/tests/e2e/help-quick-start.test.ts stays unchanged: it is a Red-pinned file (red-unchanged, S3), and its class-only switch is enough for what it asserts, since the figure rule is :root.dark."
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/lib/theme.ts:54-76: applyDocumentTheme sets the class, colorScheme and dispatches THEME_CHANGED_EVENT"
      - "ui/src/renderer/src/components/ui/SelectInput.tsx:18-31: the G30 inline pair follows useDocumentTheme, which re-reads on the event"
      - "hq-exec-review-round-1.md F1: recommends the full theme switch, new images and a select-colour assertion"
    research: { engine: none, sources: [] }
    reasoning: "The goal anchor says each screenshot matches the light or dark theme, and a dark image with white selects does not. The change touches only the generator and the images it writes; no acceptance criterion, product file or Red-pinned test changes, so no M item is hit. The do-nothing option (keep the images, register an issue) ships a visible theme mismatch to every dark-mode first-time user. Also changing the E2E helper would edit a Red-pinned file for no gain in what that test proves."
open_decisions: []
```

### D-1289 (decided A): Should the How it works card open by itself the first time someone visits a page?

Mat, 2026-11-20: "1289 A, 1290 A, execute". The final brief (HDP re-run with expert pass, `C:/Temp/av-kit/help-quick-start/hdp-expert-pass.txt`):

**A (chosen): the card stays closed, as now, and its header says "Quick start · 4 steps" or "· 5 steps".** The Downloader column is already short of room at the 1280 x 800 default window (`DownloaderPage.tsx:566-572`); NN/g favours short help that users open themselves. Undo: one default in `readExpanded`.

- B: A plus a highlighted hint until the first open (one stored key and one test).
- C: open once, on Downloader at the first app start.
- D: open on each page's first visit (about 10 E2E and 16 unit assertions change; reaches only new installs).
- E: keep things as they are, with no hint.

Refs: `HelpCard.tsx:28-60`; P6 plan :77; Zorivest `AccountsHelpCard.tsx:32`, `OptionsChainHelpCard.tsx:29`; 08:75; 09:93; NN/g; M-5, M-7 (B to D).

### D-1290 (decided A): How far should the rewrite of the existing help topics go?

Mat, 2026-11-20: "1289 A, 1290 A, execute".

**A (chosen): rewrite every unpinned topic in plain words, plus the Settings Console topic (one assertion, AC-115.15, changes) and the one unpinned `four-tools` sentence "Save POSTs the full annotation list."; keep all other pinned text word for word** (`CONSOLE_AND_SAVE`). Undo: one string and one assertion.

- B: the reviewed plan: keep all five pinned topics word for word.
- C: rewrite all five pinned topics and split `four-tools` (more than 25 assertions in 7 test files).
- D: keep things as they are.

Refs: `settings-help-content.ts:20-23`; `failure-reason-copy.test.ts:29-33`; `capture-help-content.ts:27`; OPM plain language; M-5, M-7 (A, C), M-8 (A).

## Research References

- **ASD-STE100 skill:** `P:/creative-writing/.agent/skills/asd-ste100/SKILL.md` (Strict mode for procedures: one instruction per sentence, 20 words or fewer, active voice, no phrasal verbs). The upstream is `https://github.com/danyuchn/asd-ste100-skill`, MIT, commit `32511c6`.
- **Vite JSON and `import.meta.glob`:** Vite imports `.json` natively. `import.meta.glob(…, { eager: true, query: '?url', import: 'default' })` gives asset URLs at build time. TypeScript needs `resolveJsonModule` for the JSON import.
- **Canvas WebP:** in Chromium, `HTMLCanvasElement.toDataURL('image/webp', quality)` encodes lossy WebP, so the generator needs no image library.
- **WebP header:** a `RIFF….WEBP` file holds its size in the `VP8 `, `VP8L` or `VP8X` chunk. The AC-162.7 test reads it with a few lines of code and no dependency.
- **`<details>` and `<summary>`:** native disclosure, keyboard accessible, with the `open` attribute.
- **`loading="lazy"` on a `display: none` image:** the browser does not fetch it until it is shown, so only the theme's image loads.

## Planning receipts

All under `C:/Temp/av-kit/help-quick-start/`, read-only against the repository:

| Receipt | What it shows |
|---|---|
| `hq99-probe.py`, `hq99-probe.txt` | `HEAD` `e8207e1`, a clean tree and one worktree; no `graphify-out`; MEU-162 unclaimed (the only text hit is the grouping's "no MEU-162 or later"); max decision id D-1288; matrix 6.23 free; line endings and SHA-256 prefixes of the scope; the new paths absent; no `help:shots` script; no `resolveJsonModule` |
| `hq99-ste-draft.py`, `hq99-ste-draft.txt` | Round 1 draft probe. It filtered on a `hard` level that the linter does not use (review F3); superseded |
| `hq99-ste-draft-r2.py`, `hq99-ste-draft-r2.txt` | The 40 strings of the round 2 draft linted with the creative-writing linter at the real levels: 0 findings at any level; steps of 2 sentences or fewer, sentences of 20 words or fewer, no `;`; the negative oracles (passive in Strict, `Spin up the job.`, 21 words, three sentences, `;`) each flagged, and `Set up the folder.` not found (the documented limit) |
| `hq99-task-lint.txt` | `tools/lint_task_contract.py` on `task.md` with `RECEIPTS_DIR=C:/Temp/av-kit`: `OK: 28 row(s)`, 26 fully checked, 2 exempt (`view_file`: H1-5, H2-1); exit 0 |
| `hq99-task-lint-r2.txt` | The same lint after the round 1 corrections, with the `commands.md` arguments (`--allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task`): `OK: 28 row(s)`, 26 fully checked, 2 exempt; exit 0 |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan, `task.md` and `quick-start-draft.json`, against Mat's request, 06 §Help (per page), the code reads above and the skill | `hq-plan-2026-11-20-help-quick-start` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, plus the 14 images, against AC-162.1 to AC-162.16 | `hq-execution-2026-11-20-help-quick-start` |
