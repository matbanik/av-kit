---
project: "2026-11-15-text-scrub-residuals"
date: "2026-11-15"
source: "grouping .agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md §3 Session 77; issues TRANSCRIPT-UNCLEANED-TITLE-FALLBACKS (triage D-804) and CONSOLE-HOME-SCRUB-SHORT-FORM (triage D-805, Mat's D-337)"
meus: ["MEU-147", "MEU-148"]
status: "draft"
template_version: "2.3"
grouping_source: ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md"
---

# Implementation Plan: Clean the transcript title fallbacks and scrub the home folder's short form

> **Project**: `2026-11-15-text-scrub-residuals`
> **Build Plan Section(s)**: 03 [§Transcript title cleaning (residual)](../../../build-plan/03-service-layer.md#transcript-title-cleaning-residual) (MEU-147, matrix 3.22) and 03 [§Console home short form (residual)](../../../build-plan/03-service-layer.md#console-home-short-form-residual) (MEU-148, matrix 3.23)
> **Status:** said to execute (USER_EXPLICIT 2026-11-15 'proceed with planning and execution for P:\av-kit\.agent\context\grouping\2026-11-15-post-rc3-triage-residuals-session-grouping.md like we did here. But use the new HDP process. Continue orchestrating the sessions.'). `plan_to_exec_gate: human`; the plan review was approved at round 2 (.agent/context/handoffs/2026-11-15-text-scrub-residuals-plan-critical-review.md).

---

## Goal

**Goal anchor:** a lone surrogate or a control character in a transcript channel's extract title or in a caption port's title never fails job creation or a fetch and never reaches a stored row or a written file, and on Windows the Console and the download log lines show the home folder's 8.3 short form as `~`, just as they show the long form.

This is Session 77 of the post-rc.3 grouping (§3, "both finish a text-cleaning rule that an earlier session set and left two paths short of"). Both MEUs are small service changes with unit tests and no renderer, API or MCP change. Order: MEU-147, then MEU-148 (grouping §3).

**MEU-147 (`TRANSCRIPT-UNCLEANED-TITLE-FALLBACKS`).** Session 53 (MEU-122, D-360) cleans the listed titles and the listed channel name in the YouTube adapter (`_clean_text`, `youtube/adapter.py:193-205`), and `ListedVideo` and `VideoListing` refuse unclean text (`_require_text_clean`, `domain/download.py:318-333`). Two older paths skip that cleaning:

- `add_channel` falls back to the extract title for the channel name (`services/transcript.py:173`, `name = listing.channel_name or info.title`), and `TranscriptJob.channel_name` has no guard.
- A fetch keeps the caption port's `TranscriptResult.title` when the item has no listed title (`:638`, `title = current.title or result.title`), then writes it into the raw Markdown (`:639`) and the stored item (`:644`).

The plan-time probe (`C:/Temp/av-kit/text-scrub-residuals/tsr-probe.txt`) shows the failure is real, not cosmetic: writing a lone surrogate as UTF-8 raises `UnicodeEncodeError`. So an unclean fallback fails the raw write and, through SQLite, the stored row. The fix moves D-360's cleaner into the domain as `clean_text`, and the service runs both fallbacks through it.

**MEU-148 (`CONSOLE-HOME-SCRUB-SHORT-FORM`).** `scrub_home` (`services/health.py:110-123`, `HOME_SCRUB`, D-335) matches the home folder only as `Path.home()` spells it. Windows can also name it by its 8.3 short form. Mat ruled on D-337 (Session 52, 2026-11-07, "all recommendations accepted"):

- `scrub_home` also matches the short form;
- the short form comes from `GetShortPathNameW`, read once and cached, on Windows only;
- the change is a plan row of its own with a Red, and the tests fake the lookup, because this PC's home folder has no short form.

`scrub_line` (`services/download.py:132-145`) reaches the short form through `_scrub` and, for a short form that a tab or control character splits, through `_scrub_split_home` (`:107-125`, D-627).

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-15). The change touches five named functions in four files, all read verbatim at plan time; that is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md`, the Claude Code block of `.agent/context/harness.local.md`).
  - Validation goes through `rtk proxy` with the receipt pattern.
  - Receipts go under `C:/Temp/av-kit/text-scrub-residuals/`, named `tsr-*`. Pytest runs with `TMP` and `TEMP` at `C:\Temp\av-kit\text-scrub-residuals\tmp`.
  - Every row sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, and clears `ELECTRON_RUN_AS_NODE`.
- **Working directory:** `P:/av-kit` on `main`. There are no branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** not applicable; the driver OS is the target OS. MEU-148's tests fake the lookup, so they also run on any OS (grouping §3 "Cloud/local: either").
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `tsr-plan-2026-11-15-text-scrub-residuals` and `tsr-execution-2026-11-15-text-scrub-residuals`.
  - Caps come from `.agent/review-limits.json`: plan 3 rounds, execution 6, token budgets off. This plan carries no `review_limits` block.
  - Claude wrote the plan, so the reviewer comes from a different vendor. The fallback is Mat.
- **Queue:** Session 87 runs and is committed first. Sessions 75 and 76 run before this one, and Mat has not said whether each is committed after it closes, so their changes may be uncommitted when this session starts. Baselines and scope checks are path-scoped and bound to content (§Verification Plan 1). Execution waits for Mat's message (`plan_to_exec_gate: human`).
- **Never in these rows without Mat's words:** commit, push, or writing an `approved` verdict.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-147 transcript title cleaning | `.agent/context/handoffs/2026-11-15-text-scrub-residuals-MEU-147-handoff.md` |
| MEU-148 Console home short form | `.agent/context/handoffs/2026-11-15-text-scrub-residuals-MEU-148-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-15-text-scrub-residuals-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-15-text-scrub-residuals-implementation-critical-review.md`

One handoff per MEU follows `2026-11-14-capture-shapes-steps`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `tsr-base-py.txt` |
| WP-2 | MEU-147: Red, then Green (rows 1 and 2) | WP-1 | shared | `tests/unit/test_transcript_title_cleaning.py`, `domain/download.py`, `youtube/adapter.py`, `services/transcript.py` |
| WP-3 | MEU-148: Red, then Green (rows 3 and 4, D-337's own rows) | WP-2 | shared | `tests/unit/test_console_home_short_form.py`, `services/health.py`, `services/download.py` |
| WP-4 | Registers and status (row 5) | WP-3 | shared | 03 Delivered notes, `known-issues.yaml` and `.md`, `meu-status.yaml`, `meu-registry.md`, `BUILD_PLAN.md`, grouping §6 row 77 |
| WP-5 | Closeout (H1, H2) | WP-4 | `compact_continue` | Two handoffs, the review, the reflection |

## User Review Required

> [!NOTE]
> **Nothing here needs your ruling.** Every decision is autonomous (§Decision Log), and none hits the §4a list. MEU-148 carries out your D-337 ruling as you gave it.
>
> **What changes for you:**
>
> - A transcript channel whose extract title holds a control character or a broken character now gets a clean name, and the job is created. A title that holds nothing else takes the channel's ID as its name (D-923).
> - A fetched transcript whose caption title holds such a character gets the cleaned title, and the video ID when nothing is left. Today that fetch can fail.
> - On Windows, a Console line or a download log line that names the home folder by its short form (for example `C:\Users\LONGNA~1`) now shows `~`. A home folder with no short form, like this PC's, behaves as today.
>
> **What this plan leaves out:** a transcript's text with a broken character (the same failure in `result.text`, not in either issue), and a home folder that `Path.home()` already gives in short form (§Out of Scope).

## Proposed Changes

### Single-statement contracts

- **`TEXT_CLEAN_SHARED` (MEU-147, D-922):** `avkit_core.domain.download.clean_text(value: object) -> str | None` is D-360's `_clean_text` moved verbatim: a non-`str` gives `None`; every character that is not whitespace and whose category is `Cc` or `Cs` is dropped; whitespace runs collapse to one space and the ends are trimmed; an empty result gives `None`. The YouTube adapter imports it and keeps no copy.
- **`CHANNEL_FALLBACK_CLEAN` (MEU-147, D-923):** `add_channel` names the job `listing.channel_name or clean_text(info.title) or channel_id`, where `channel_id` is the extract's `playlist_id` (a `PlaylistInfo`) or `video_id` (a `VideoInfo`). The output folder keeps `slugify(info.title)` (`SLUG_SOURCE`, AC-122.11).
- **`RESULT_TITLE_CLEAN` (MEU-147):** a fetch keeps `current.title or clean_text(result.title) or result.video_id`, and that one value goes to the raw Markdown and the stored item. The listed title still wins (`TITLE_KEPT`, AC-122.13).
- **`CLEAN_AT_ENTRY` (MEU-147, D-924):** the domain types `TranscriptJob`, `TranscriptItem` and `TranscriptResult` gain no refusal guard. The service cleans at its two entry points, so the values it builds pass `_require_text_clean`.
- **`SHORT_FORM_LOOKUP` (MEU-148, D-926):** a module flag in `health.py`, `sys.platform == "win32"`, read at call time, beside `HOME_IGNORES_CASE`.
- **`SHORT_PATH_API` (MEU-148, D-927):** `health._short_path_api()` returns the native `GetShortPathNameW` callable, loaded through `ctypes` inside an `if sys.platform == "win32":` block with `argtypes` `[LPCWSTR, LPWSTR, DWORD]` and `restype` `DWORD` (the `avkit_api/cli.py:28-55` shape). It returns `None` off Windows and when loading raises `OSError` or `AttributeError`. It does no lookup itself; it is the seam beneath `short_path_name` that AC-148.8 replaces.
- **`SHORT_PATH_NAME` (MEU-148, D-337, D-926, D-927):** `health.short_path_name(path: str) -> str` gets the callable from `_short_path_api()` at each call, then makes a size query (`api(path, None, 0)`), allocates `ctypes.create_unicode_buffer(size)` and fills it (`api(path, buffer, size)`). It returns `buffer.value` only when the size query is non-zero and the fill returns a length `0 < written < size`. It returns `""` when `_short_path_api()` gives `None`, when either call returns 0, when the fill does not fit, and on an `OSError` or `ValueError`. The downstream tests (AC-148.2 to AC-148.7) replace `short_path_name` with a counting fake; AC-148.8 runs the real `short_path_name` over a fake native callable.
- **`SHORT_FORM_CACHE` (MEU-148, D-337, D-926):** `health.home_forms() -> tuple[str, ...]` returns the home folder without trailing separators, then its short form when the short form is non-empty and differs from it in casefold. The lookup runs at most once per home value per process; the result, `""` included, is kept in the module dict `_SHORT_FORMS`, keyed by the long form. With `SHORT_FORM_LOOKUP` false, no lookup runs. An empty home gives `()`.
- **`SHORT_FORM_SCRUB` (MEU-148, D-337):** `scrub_home` applies its existing pattern to each form of `home_forms()` in order, long form first, each with the same boundary rule and case rule (D-335). A form with no separator is skipped, as today.
- **`SHORT_FORM_SPLIT` (MEU-148, D-925):** `download._scrub_split_home` applies its existing split-aware pattern to each form of `health.home_forms()`, read through the module at each call.

### MEU-147: the cleaner and the two fallbacks

1. **`domain/download.py` (CRLF).** Add `_UNCLEAN_CATEGORIES = frozenset({"Cc", "Cs"})` and `clean_text` (`TEXT_CLEAN_SHARED`) directly above `_require_text_clean`, with D-360's docstring. `_require_text_clean` is not changed.
2. **`youtube/adapter.py` (CRLF).**
   - Add `clean_text` to the `avkit_core.domain.download` import (`:18-29`).
   - Delete `_UNCLEAN_CATEGORIES` and `_clean_text` (`:190-205`).
   - Replace the three calls (`:244`, `:741` twice, `:745`) with `clean_text`.
   - Remove `import unicodedata` (`:8`); `:203` was its only use.
   - AC-122.2, AC-122.3 and AC-122.8 pin that the adapter's behaviour is unchanged.
3. **`services/transcript.py` (LF).**
   - Add `clean_text` to the `avkit_core.domain.download` import.
   - In `add_channel`, drop `_ = channel_id` and set `name = listing.channel_name or clean_text(info.title) or channel_id` (`CHANNEL_FALLBACK_CLEAN`). Keep the `SLUG_SOURCE` comment, extended to say the name is cleaned.
   - In the fetch path, `title = current.title or clean_text(result.title) or result.video_id` (`RESULT_TITLE_CLEAN`), and update the `TITLE_KEPT` comment.

### MEU-148: the short form

1. **`services/health.py` (CRLF).** Add `SHORT_FORM_LOOKUP`, `_SHORT_FORMS: dict[str, str] = {}`, `_short_path_api`, `short_path_name` and `home_forms` after `home_folder`, and change `scrub_home` to loop over `home_forms()` (§Single-statement contracts). `ctypes` is imported inside the two functions (`ctypes.wintypes` only inside the Windows block), so no module-level import is added. The docstring of `scrub_home` names the short form and D-337.
2. **`services/download.py` (CRLF).** `_scrub_split_home` loops over `health.home_forms()` with its existing pattern; the docstring says `health.home_forms` is read through the module at each call.

The existing tests that patch `health.home_folder` keep passing without a fake lookup:

- a synthetic home (`test_services.py:3308`, `test_download_failure_visibility.py:105`, `tests/e2e/test_api_download_visibility.py:70`) does not exist, so the real call returns `""` (probe: `last_error=2`);
- a home under `tmp_path` (`test_download_audio_extract.py:645-712`) can have a short form, but their text names only the long form, so the extra pattern finds nothing.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `TranscriptJob.channel_name` (stored, API read) | `domain/transcript.py` (`require_non_empty_str`) | Unchanged shape. New values from `add_channel` are clean (`CHANNEL_FALLBACK_CLEAN`); stored rows are read as before (D-924) | Unchanged |
| `TranscriptItem.title` (stored, raw Markdown front matter) | `domain/transcript.py` (`require_optional_str`) | Unchanged shape. New values from a fetch are clean (`RESULT_TITLE_CLEAN`) | Unchanged |
| Console field text, download log lines | `health.console_field`, `download.scrub_line` | Text only; a short-form home becomes `~` | Unchanged |

No API route, OpenAPI document, MCP tool shape or database schema changes.

### Acceptance Criteria

Tests are named `test_ac_<meu>_<n>_…`, so `red-check.py --require test_ac_147_1` matches each exactly.

- **AC-147.1 to AC-147.5** are in `tests/unit/test_transcript_title_cleaning.py` (new, LF). The fake-stack tests use `_transcript_stack` and `DownloadYouTube` from `tests.unit.test_services`. AC-147.5 uses real SQLite and `FilesystemAdapter`, as `test_ac_122_8_surrogate_title_survives_real_storage` does (`tests/integration/test_youtube_adapter.py:881`).
- **AC-148.1 to AC-148.9** are in `tests/unit/test_console_home_short_form.py` (new, LF).
  - The home is the synthetic `C:\Users\SYNTHETIC_HOME_USER` (the D-335 fixture, `test_services.py:3308`) and its short form the synthetic `C:\Users\SYNTHE~1`. No test reads or writes the real home folder.
  - A helper patches `health.home_folder`, `health.HOME_IGNORES_CASE`, `health.SHORT_FORM_LOOKUP`, `health.short_path_name` (a counting fake) and `health._SHORT_FORMS` (a fresh dict) through `monkeypatch`. AC-148.2 to AC-148.7 use it.
  - AC-148.8 and AC-148.9 do not replace `short_path_name`. They patch `health._short_path_api` to return a fake native callable that records each `(path, buffer is None, size)` call. Its default script: the size query returns `len(alias) + 1`; the fill writes the alias into the buffer (`buffer.value = alias`) and returns `len(alias)`. The alias is `C:\Users\SYNTHE~1`, which differs from the long form. AC-148.9's scripts return 0 from either call, return `size` from the fill, or raise `OSError`.
- **The empty-lookup mutant.** `mutant_empty_lookup.py` (plan folder) is a pytest plugin whose `pytest_configure` sets `avkit_core.services.health.short_path_name` to `lambda _path: ""`. Row 4 and the gate run `-k ac_148_8` under it and require a nonzero exit, no passed test in the receipt, and `red-check.py --require test_ac_148_8`, so an always-empty helper cannot pass the gate (R1-F1). AC-148.9 is not run under the mutant, because an empty result is what it expects.
- **Every test asserts the new names exist first** (`hasattr(download_domain, "clean_text")`, `hasattr(health, "home_forms")`, `hasattr(health, "short_path_name")`, and in AC-148.1, AC-148.8 and AC-148.9 `hasattr(health, "_short_path_api")`), before any patch, so Red fails by assertion, never by `AttributeError` in setup (Session 52 RULE-4).
- **AC-147.6 and the regression half of AC-148.6** run existing tests unchanged.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-147.1 | unit | `clean_text` exists in `avkit_core.domain.download`. Parametrized: a lone surrogate and a control character inside text are dropped; tabs, newlines and space runs collapse to one space and the ends are trimmed; U+200B (category `Cf`) is kept, as D-360 keeps it; text that holds only surrogates, controls or whitespace, `""`, `None` and `7` give `None`. Every non-`None` output passes `_require_text_clean`. The YouTube adapter module has no `_clean_text` or `_UNCLEAN_CATEGORIES`, and its `clean_text` is the domain's object. | Local Canon (D-360, MEU-122; D-922) | The unclean inputs are the negatives; an output that keeps a `Cs` or `Cc` character fails the guard check |
| AC-147.2 | unit | With no listed channel name, an extract title `Chan <U+D800> <U+0007>Name` gives a job whose `channel_name` is `Chan Name`, read back from the unit of work, and it passes `_require_text_clean`. The output folder name equals `slugify` of the raw extract title (`SLUG_SOURCE` unchanged). After a fetch, the raw Markdown's `channel:` front matter is `Chan Name`. The same holds for the `VideoInfo` branch (no playlist, no listed IDs). | Local Canon (03 §Transcript title cleaning: Clean; D-360) | In Red the stored name keeps the raw characters, so the equality fails |
| AC-147.3 | unit | An extract title that cleans to nothing (`<U+D800><U+0001>`) with no listed channel name gives `channel_name` equal to the playlist ID, and the video ID for the `VideoInfo` branch. The job is created. | Local Canon (03 §Transcript title cleaning: Fallback; D-923) | In Red the name is the raw title |
| AC-147.4 | unit | An item with no listed title, fetched with a port title `Talk <U+D800> <U+0007>title`, ends `Done` with the stored title `Talk title`. Its raw Markdown decodes as UTF-8 and its front matter title is `Talk title`. A port title that cleans to nothing stores the video ID, in the file and in the item. | Local Canon (03 §Transcript title cleaning: Clean, Fallback; MEU-122's ID fallback) | In Red the write raises `UnicodeEncodeError` or the stored title is raw, so the status or title assertion fails |
| AC-147.5 | integration | Real storage: SQLite under `tmp_path`, `SqlAlchemyUnitOfWork`, `FilesystemAdapter` and a fake extract and caption port. An extract title and a port title that each hold a lone surrogate and a control character: `add_channel` raises nothing (the error is recorded as a value), the job ends `Done`, the raw file decodes as UTF-8, and the job and item read back through a new unit of work hold the cleaned values. | Local Canon (issue `resolution_path`: "one real-storage regression (Session 53 RULE-1)") | In Red, `add_channel` or the fetch fails with `UnicodeEncodeError`, so `error is None` fails |
| AC-147.6 | integration | The MEU-122 tests pass unchanged: `tests/unit/test_transcript_metadata.py` and `pytest tests/integration/test_youtube_adapter.py -k ac_122`. | Local Canon (AC-122.2, AC-122.3, AC-122.8, AC-122.10, AC-122.11, AC-122.13) | A changed adapter cleaning, slug or listed-title rule fails one of them |
| AC-148.1 | unit | The real native path, without any fake. On Windows, `_short_path_api()` returns a callable; for a folder under `tmp_path` named `LongFolderNameForShortForm`, `short_path_name` returns `""` or a path for which `os.path.samefile` holds (a volume can disable 8.3 names, so this case proves only that a real call does not break; AC-148.8 proves success); for a missing synthetic path it returns `""`. Off Windows (`sys.platform` patched to `linux` in `health`'s view), `_short_path_api()` returns `None` and `short_path_name` returns `""`. No skip. | Research-backed (`GetShortPathNameW` returns 0 on failure and needs the path to exist; plan-time probe); Human-approved (D-337 "Windows only") | The missing path and the non-Windows case are the negatives |
| AC-148.2 | unit | With the fake returning the synthetic short form, `console_field` turns the short form into `~` when it starts a path joined by `\`, by `/` and by a doubled `\\`, and in lower case. `C:\Users\SYNTHE~10\a` and `X:\Users\SYNTHE~1` with a word character before it are kept (the D-335 boundary). `scrub_home` gives the same results. | Human-approved (D-337) | The two kept strings are the negatives |
| AC-148.3 | unit | The lookup is read once and cached: across several `console_field`, `scrub_home` and `scrub_line` calls, the fake runs once, with the long home. A fake that returns `""` also runs once. A second home value runs its own lookup once. | Human-approved (D-337 "read once and cached"); Local Canon (D-926) | A count above one fails |
| AC-148.4 | unit | A failed lookup (`""`), and a lookup that returns the long form in another case, leave `scrub_home` output equal to the long-form-only result for a fixed corpus of five lines; a short-form path in that corpus is kept. | Human-approved (D-337: "only the long form is matched") | The kept short-form line is the negative |
| AC-148.5 | unit | With `SHORT_FORM_LOOKUP` false, the fake never runs, the short form is kept and the long form still becomes `~`. | Human-approved (D-337 "Windows only") | A fake call count above zero fails |
| AC-148.6 | unit | One line that names the long form and the short form gives `~` for both, and the existing AC-119.10 tests pass unchanged (`pytest tests/unit/test_services.py -k ac_119_10`). | Local Canon (AC-119.10, D-335) | The long form left in place fails |
| AC-148.7 | unit | `scrub_line` turns the short form into `~` when it is plain, and when a tab, a control character (U+0001) or an ANSI CSI sequence splits the short name (D-627's shape, `download.py:85-104`). With a failed lookup the split short form is kept exactly as today's `scrub_line` keeps it. | Local Canon (03 §Console home short form: Reach; D-627; D-925) | The failed-lookup case is the negative |
| AC-148.8 | unit | The real `short_path_name` over a fake native callable (`_short_path_api` patched; `short_path_name` not patched). The default script gives `short_path_name(long) == "C:\Users\SYNTHE~1"`, with exactly two calls in order: `(long, None, 0)`, then `(long, buffer, len(alias) + 1)`. With the same fake, `SHORT_FORM_LOOKUP` true and a fresh `_SHORT_FORMS`, `home_forms()` is `(long, alias)` and `console_field` turns `C:\Users\SYNTHE~1\a` into `~\a`, so the real helper feeds the scrub. Under the empty-lookup mutant every AC-148.8 test fails by assertion. | Research-backed (`GetShortPathNameW`: size query with a zero buffer returns the size including the terminator; a fill returns the length without it; 0 on failure); Human-approved (D-337: the lookup is faked in tests); Local Canon (D-927; review R1-F1) | The mutant run is the negative: an always-empty helper fails every AC-148.8 test |
| AC-148.9 | unit | The real `short_path_name` over failing fake native callables. Each script gives `""`, and with it `console_field` keeps `C:\Users\SYNTHE~1\a`: size query 0 (one call, no fill), fill 0, fill equal to `size` (does not fit), an `OSError` from the callable, and `_short_path_api()` returning `None` (no call at all). | Research-backed (the same contract); Human-approved (D-337: "when the call fails … only the long form is matched") | Each script is a negative |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| What the cleaning does | Local Canon | D-360's cleaner, moved unchanged (D-922) |
| Where the cleaner lives | Local Canon | The domain, beside `clean_line` and `_require_text_clean` (D-922) |
| The channel name when the extract title cleans to nothing | Local Canon | The extract's ID (D-923) |
| Whether the transcript domain types refuse unclean text | Local Canon | No; the service cleans at entry (D-924) |
| Where the short form comes from, how often, on which OS | Human-approved | D-337 |
| The lookup seam and the cache key | Local Canon | D-926 |
| How a test proves the real lookup returns a short form | Local Canon | A fake native callable beneath `short_path_name`, and the empty-lookup mutant (D-927) |
| Whether the split-aware scrub matches the short form | Local Canon | D-925 |

#### Files Modified

| File | Action | Line endings | Summary |
|------|--------|--------------|---------|
| `packages/core/src/avkit_core/domain/download.py` | modify | CRLF, kept | `clean_text`, `_UNCLEAN_CATEGORIES` |
| `packages/infrastructure/src/avkit_infra/youtube/adapter.py` | modify | CRLF, kept | Imports `clean_text`; drops `_clean_text`, `_UNCLEAN_CATEGORIES`, `import unicodedata` |
| `packages/core/src/avkit_core/services/transcript.py` | modify | LF, kept | The two fallbacks cleaned |
| `packages/core/src/avkit_core/services/health.py` | modify | CRLF, kept | `SHORT_FORM_LOOKUP`, `_SHORT_FORMS`, `_short_path_api`, `short_path_name`, `home_forms`; `scrub_home` loops over the forms |
| `packages/core/src/avkit_core/services/download.py` | modify | CRLF, kept | `_scrub_split_home` loops over the forms |
| `tests/unit/test_transcript_title_cleaning.py` | new | LF | AC-147.1 to AC-147.5 |
| `tests/unit/test_console_home_short_form.py` | new | LF | AC-148.1 to AC-148.9 |
| `docs/build-plan/03-service-layer.md` | modify | CRLF, kept | A `Delivered (Session 77)` note under each of the two home sections |
| `.agent/context/known-issues.yaml` | modify (tool) | LF, kept | The two issues resolved through `issue-resolve.py` |
| `.agent/context/known-issues.md` | regenerate | LF | `issue_triage.py render` |
| `.agent/context/meu-status.yaml` | modify (tool) | LF, kept | MEU-147 and MEU-148: `ready_for_review`, then `approved` (H2-2) |
| `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md` | regenerate | LF | `meu_status.py render` |
| `.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md` | modify | LF, kept | §6 row 77 only: `executed (Session 77)` and this plan folder |

Line endings were measured with Python bytes (`C:/Temp/av-kit/text-scrub-residuals/tsr-eol.txt`). A CRLF file is read and written with `newline=""` from CRLF text, and the session gate checks every file in this table again.

### Project files

- **Plan-local scripts**, all in this plan folder: `baseline.ps1`, `red-check.py`, `identity.py`, `issue-resolve.py`, `mutant_empty_lookup.py` (row 3 writes it; row 4 and the gate's `meu-148-mutant` step load it with `-p` and `PYTHONPATH` at this plan folder), `session-gate.ps1`.
- **Row 0 data:** `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`.
- **State:** `docs/execution/metrics.md` (CRLF), `.agent/context/current-focus.md` (CRLF), the two handoffs, the rolling reviews and the reflection.

### Sibling overlap

The plan binds each shared file to its content at row 0 (`baseline-scope.json`), not to `HEAD`, and changes only its own entries or lines in it.

| File | Siblings | Rule |
|---|---|---|
| `.agent/context/known-issues.yaml`, `known-issues.md` | Sessions 75, 76, 78 to 83 close their own issues; Session 83 rewrites the lines that name the home folder (grouping §2 soft order) | Session 83 runs after this one. Row 5 changes only the two issues' `status`, `verification` and `resolution_path`, names no home path, and binds to the row-0 hash (S4) |
| `meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md` | Sessions 75, 80, 81, 82 | Only MEU-147's and MEU-148's rows change, through `meu_status.py` |
| Grouping §6 table | Every session of the grouping | Only row 77 changes |
| `docs/build-plan/03-service-layer.md` | None in this grouping | Only the two `Delivered (Session 77)` notes are added |
| `current-focus.md`, `metrics.md` | Every session | Read first; change only this session's lines |

No sibling session edits a product or test file of this plan. Session 76 (`tooling-test-hermeticity`) edits `tests/tooling/` only.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| A lone surrogate in a transcript's text (`result.text`), which fails the same raw write | out-of-scope | — | Neither issue names it (`known-issues.yaml` TRANSCRIPT-UNCLEANED-TITLE-FALLBACKS, triage D-804). The MEU-147 handoff names it as a residual risk for triage |
| A home folder that `Path.home()` already gives in short form, so the long form is never matched | out-of-scope | — | D-337 rules on the short form only, and rejected `GetLongPathNameW` for the models folder (`docs/execution/plans/2026-11-06-tts-load-fp16/closeout-decisions.md:55-88`) |
| A refusal guard on `TranscriptJob`, `TranscriptItem` or `TranscriptResult` | out-of-scope | — | D-924 |
| The renderer, the API, MCP and E2E | out-of-scope | — | No shape changes (§Boundary Inventory) |
| MEU-144 and the TTS model assets (Session 74) | out-of-scope | — | Session brief |

## BUILD_PLAN.md Audit

MEU-147 and MEU-148 are registered (`meu-status.yaml`, `pending`, matrix 3.22 and 3.23; dependencies MEU-122 and MEU-119 are `approved`). Row 5 sets both to `ready_for_review` with this plan's `execution_plan` through `tools/meu_status.py update`, and H2-2 sets both to `approved`. `meu-registry.md` and `docs/BUILD_PLAN.md` are regenerated by `tools/meu_status.py render`, never by hand:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/text-scrub-residuals/tsr-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/text-scrub-residuals/tsr-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. **Tree state.** It records `HEAD` in `baseline.sha` and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt`. Sessions 75 and 76 may be listed there.
2. **Path-scoped baseline.**
   - It writes `baseline-scope.json`: for each path in §Files Modified, its SHA-256, or `absent`. The two new test files must be `absent`.
   - It writes `baseline-dirty-hashes.json`: the SHA-256 of every `baseline-dirty.txt` path outside this scope, or `deleted`. S4 and the gate's `scope-paths` compare against it.
   - It checks the five product files and the 03 file against `git show HEAD:` for each. A product file that differs from `HEAD` is S2: an earlier session changed code this plan edits.
3. **Base receipts.** It runs `uv sync --frozen --all-packages` and the base Python suite (`tsr-base-py.txt`), with `TMP` and `TEMP` at `C:\Temp\av-kit\text-scrub-residuals\tmp`.
4. **Plan-local scripts.**
   - It copies `red-check.py` and `identity.py` from `docs/execution/plans/2026-11-15-framework-small-syncs/`, with this plan's `PLAN` and `PROJECT_ARTIFACTS`, and with `DECLARED_NEW` left at the selftest names.
   - It copies `issue-resolve.py` from `docs/execution/plans/2026-11-15-closeout-record-once/` with `SCRATCH` at `C:/Temp/av-kit/text-scrub-residuals/issue-resolve`.
   - It runs the `red-check.py` and `identity.py` selftests.

If any step fails, the row fails and nothing else runs.

### 2. Red, then Green

- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py --require test_ac_<meu>_<n>` checks every AC test of the row.
- **New names fail by assertion.** Each test asserts the new name exists before it patches or calls it.
- **D-337's own row.** MEU-148's Red is row 3 and its Green row 4. Neither row touches MEU-147's files.
- **Expectations stay immutable in Green.** A Green row that needs a changed expectation stops on S3.
- **Line endings.** The CRLF files are measured with Python bytes and written with `newline=""`.

### Session gate (H1-2)

`session-gate.ps1` follows the peer's shape (`2026-11-15-closeout-record-once/session-gate.ps1`):

- one receipt per step in `C:/Temp/av-kit/text-scrub-residuals/`, named `tsr-D6-<step>`;
- fail-fast, with later steps printed as `not_run`;
- the last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `py-lint` (`ruff check packages/ tests/`); `py-format` (`ruff format --check` on the seven changed or new Python files); `py-types` (`pyright packages/`); `task-contract`; `scope-paths` (every changed path is in §Files Modified, in this plan folder, in the closeout artifacts or in `baseline-dirty.txt`, and every `baseline-dirty.txt` path outside this scope keeps its row-0 content state); `line-endings` (each §Files Modified file keeps its row-0 kind); `red-check-selftest` |
| Targeted | `meu-147-tests` (the new file and AC-147.6's two runs); `meu-148-tests` (the new file, no skip, and `test_services.py -k ac_119_10` as its own invocation); `meu-148-mutant` (AC-148.8 under `mutant_empty_lookup.py`, then `red-check.py --require test_ac_148_8` on that receipt); `scrub-callers` (`test_download_failure_visibility.py`, `test_download_audio_extract.py`, `test_transcript_metadata.py`) |
| Fresh full | `py-tests` (`pytest tests/ --tb=short -q -rfE`); `state-render` (`meu_status.py render --check`); `issues-render-check` (`issue_triage.py render --check`); `ui-canon` (`ui/tests/unit/layout-canon.test.ts` and `queue-canon.test.ts`, run from pwsh in `ui/`, because they read `meu-status.yaml` and `BUILD_PLAN.md`, which row 5 changes) |
| Skipped, with reason | `ui-lint`, `ui-types`, `ui-tests` beyond `ui-canon`: nothing under `ui/` changes. `mcp-*`: no MCP change; the MCP Python tests run inside `py-tests`. `e2e`: no renderer or launch change. `openapi`: no `packages/api` change (H1-4). `build-record`: no build |

`py-tests` excuses only ids that row 0's receipt shows failing.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | Row 0 finds a product file of §Files Modified changed since `HEAD` | Stop. An earlier session changed code this plan edits; bring the diff to Mat |
| S3 | A Red receipt fails `red-check.py`, or a Green row needs a changed expectation | Fix the test setup; do not move to Green, and never edit an expectation in Green |
| S4 | A path outside this plan's scope and `baseline-dirty.txt` changes, or a `baseline-dirty.txt` path changes content, or `known-issues.yaml` no longer has its row-0 hash at row 5 | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | An existing test outside AC-147.6 and AC-148.6 fails after Green | Stop: that is an M-7 question (§4a), not a fix |
| S6 | Codex is unavailable or the ledger refuses | Mat |

## Decision Log

> [!NOTE]
> Every decision below is autonomous with `mandatory: none`: each passed the §4a list and the §4 test. There are no briefs, so no expert pass is needed. D-337 (Session 52, Mat's ruling) and D-335 are applied, not re-recorded. The grouping rows D-813 to D-816 stay in the grouping file's §8 and are not copied here; H2-2 reads them through `--decision-source` on the grouping file (this plan's `grouping_source`), and the issues' D-363, D-804 and D-805 through `--decision-issue`. The grouping's old "Carry-forward" wording (§9, "each row appears in its consuming session's reflection") is ignored under the new HDP §6: the reflection's `### Decisions Log` lists only this session's reversible autonomous choices. D-927 was added after plan review round 1 (R1-F1); D-928 to D-932 are left free for execution.

```yaml
decision_log:
  - id: D-922
    stage: planning
    question: "Where does the D-360 text cleaner live, so the transcript service can use it?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Move the adapter's _clean_text unchanged into avkit_core.domain.download as the public clean_text; the YouTube adapter imports it and keeps no copy."
    source_tag: Local Canon
    precedents:
      - "packages/infrastructure/src/avkit_infra/youtube/adapter.py:190-205 — D-360's cleaner, private to the adapter"
      - "packages/core/src/avkit_core/domain/download.py:121 — clean_line (D-627) already lives in the domain beside the TEXT_CLEAN guard at :318"
      - "docs/build-plan/03-service-layer.md:753 — the residual asks for the same cleaning as the listed title"
    research: { engine: none, sources: [] }
    reasoning: "The service is in core and cannot import the infrastructure adapter, so the one cleaner has to sit in core. The domain module already holds the TEXT_CLEAN guard and clean_line, so the cleaner sits beside the guard it satisfies. A second copy in the service lost because two copies can drift apart, which is how this issue began. Reusing clean_line lost because it drops Cf characters, which D-360 keeps. AC-122.2, AC-122.3 and AC-122.8 pin the adapter's behaviour unchanged. Two-way: an internal function move."
  - id: D-923
    stage: planning
    question: "What is a transcript channel's name when there is no listed name and the extract title cleans to nothing?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "The extract's own ID: the playlist ID for a PlaylistInfo, the video ID for a VideoInfo. add_channel already computes it as channel_id and leaves it unused."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/03-service-layer.md:754 — a value that cleans to nothing takes the fallback MEU-122 uses for that field"
      - "docs/build-plan/03-service-layer.md:671 — MEU-122 keeps the ID as the title's fallback"
      - "packages/core/src/avkit_core/services/transcript.py:163-170 — channel_id is computed and then discarded"
    research: { engine: none, sources: [] }
    reasoning: "MEU-122's channel chain ends at the extract title, so for a title that cleans to nothing it has no further fallback, and TranscriptJob.channel_name must not be empty. The ID is the fallback MEU-122 uses for the matching title field, and the service already holds it. The slug lost because it is lower-cased text built for a folder, and the literal word channel lost because it hides which channel the job is. The case needs a title made only of control or broken characters, so the choice is rare and changes nothing else. Two-way: one expression."
  - id: D-924
    stage: planning
    question: "Do the transcript domain types refuse unclean text, as ListedVideo and VideoListing do?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "No. TranscriptJob, TranscriptItem and TranscriptResult gain no refusal guard. The service cleans both fallbacks at entry, and the tests check the values it builds against _require_text_clean."
    source_tag: Local Canon
    precedents:
      - "packages/infrastructure/src/avkit_infra/database/mappers.py:190 — TranscriptJob is rebuilt from every stored row"
      - "docs/build-plan/03-service-layer.md:753 — the same cleaning and guard, so that unclean text never fails job creation and never reaches the stored row"
      - "packages/core/src/avkit_core/domain/download.py:337 — D-360 guards the listing types the adapter builds after cleaning"
    research: { engine: none, sources: [] }
    reasoning: "The home's Clean rule asks for the same cleaning and guard as the listed title, so that unclean text never fails job creation and never reaches the stored row. This plan reads the guard as a property of the values the service builds: every value clean_text returns passes _require_text_clean, and AC-147.1 to AC-147.5 run that guard on each built value. A guard in TranscriptJob also runs when a stored row is read. A row written before D-360 can hold a doubled space or a control character, and a guard would then make the user's existing jobs fail to load, which is the failure the rule exists to prevent. A guard in TranscriptResult would make a caption port fail the item where the rule asks for a clean value. Cleaning at the two entry points meets the rule, and the tests prove the built values pass the same guard. Two-way: a guard can be added later with a stored-row migration."
  - id: D-925
    stage: planning
    question: "Does the split-aware home scrub in scrub_line also match the short form?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Yes. download._scrub_split_home applies its pattern to each form from health.home_forms()."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/03-service-layer.md:767 — scrub_line gains the short form through scrub_home"
      - "packages/core/src/avkit_core/services/download.py:107-125 — D-627 matches the home before characters are removed, so a split name is still scrubbed"
    research: { engine: none, sources: [] }
    reasoning: "scrub_line first runs _scrub_split_home, which reads the home folder on its own, and only then scrub_home. Without this change a short form split by a tab or a control character would survive, while the same split long form is scrubbed, which breaks D-627's rule for one spelling only. Matching the long form alone there lost for that reason. Two-way: a loop over the same pattern."
  - id: D-926
    stage: planning
    question: "What shape do the short-form lookup, its cache and its test seam take?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A SHORT_FORM_LOOKUP flag beside HOME_IGNORES_CASE; one function, short_path_name, that the tests replace; and home_forms, which caches each lookup, an empty result included, in a module dict keyed by the long home."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-06-tts-load-fp16/closeout-decisions.md:55-88 — D-337: GetShortPathNameW, read once and cached, Windows only, faked in tests"
      - "packages/core/src/avkit_core/services/health.py:66 — HOME_IGNORES_CASE, a platform flag the D-335 tests patch"
      - "packages/api/src/avkit_api/cli.py:28-55 — the repository's ctypes kernel32 call shape inside a sys.platform block"
    research: { engine: none, sources: [] }
    reasoning: "D-337 fixes the source, the platform and the caching; this records only the seams. A platform flag read at call time lets a test run the Windows path on any OS and the non-Windows path on Windows, as the D-335 tests do with HOME_IGNORES_CASE. Keying the cache by the long home keeps the lookup to once per process in the app, where the home never changes, and gives each test home its own entry, so a test's fake never leaks into the next. A single cached value lost because a test that patches the home would read another test's short form. Caching the failure too means a home with no short form is never asked twice. Two-way: internal names."
  - id: D-927
    stage: planning
    question: "How does a test prove the real short_path_name returns a short form, without the host home or 8.3 names being enabled?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Split the native load into health._short_path_api, which returns the GetShortPathNameW callable or None. AC-148.8 runs the real short_path_name over a fake callable that answers the size query and fills a distinct alias, checks the two calls in order, and checks that the result reaches console_field. A plan-local pytest plugin replaces short_path_name with an always-empty function, and every AC-148.8 test must then fail by assertion. AC-148.9 covers the failing native results."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-06-tts-load-fp16/closeout-decisions.md:55-88 — D-337: the lookup is faked in tests, read once and cached, Windows only"
      - "packages/api/src/avkit_api/cli.py:28-55 — the repository's kernel32 load with argtypes and restype inside a sys.platform block"
      - "C:/Temp/av-kit/tsr-plan-review-round-1.md — R1-F1: an always-empty helper passed AC-148.1, and AC-148.2 to AC-148.7 replace the helper"
    research: { engine: none, sources: [] }
    reasoning: "A real call cannot prove success on every machine: a volume can have 8.3 names off, and this PC's home folder has no short form. Faking the native callable beneath the helper proves the size query, the buffer, the fit check and the return on any OS, and keeps D-337's faked lookup. A ctypes-level fake of kernel32 lost because it would patch ctypes itself for every caller in the process. A fake helper alone lost because it is what let the empty producer pass. The mutant run shows the proof is not vacuous. The real call in AC-148.1 stays, to show the native load and a real failure work. Two-way: a private seam and tests. Not an M-7 hit: no existing test changes."
  - id: D-928
    stage: execution
    question: "§Verification Plan 1 says DECLARED_NEW stays at the selftest names; task row 0 says it gains clean_text, home_forms and short_path_name. Which does the copied red-check.py follow?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Task row 0: DECLARED_NEW keeps the selftest names and gains clean_text, home_forms and short_path_name, so a Red that fails by AttributeError or NameError on one of them is refused as a setup failure."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-15-text-scrub-residuals/task.md row 0 — DECLARED_NEW extended with the three names"
      - "docs/execution/plans/2026-11-15-text-scrub-residuals/implementation-plan.md §Verification Plan 1 — DECLARED_NEW left at the selftest names"
      - "Session 52 RULE-4 — a new name fails Red by assertion, never by AttributeError in setup"
    research: { engine: none, sources: [] }
    reasoning: "Mine to decide: the two texts disagree only on how strict the Red check is. The task row is the stricter one, the row that runs, and the one the plan review approved with its command; extending the list can only refuse more setup failures, and the red-check.py selftest still passes with it (37 fixtures, 0 wrong). Leaving the list at the selftest names lost because a Red that failed by AttributeError on clean_text would then pass the check. Two-way: a plan-local script."
  - id: D-929
    stage: execution
    question: "How do the S4 check before each row and the gate's scope-paths and line-endings steps run, when the plan lists no script for them?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A plan-local scope-check.py, adapted from Session 76's (2026-11-15-tooling-test-hermeticity) without its content-bound HEAD rule: HEAD must equal baseline.sha, as the executor brief requires. --row N checks the §Files Modified paths no earlier row writes; --eol checks the row-0 kinds."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-15-tooling-test-hermeticity/scope-check.py — Session 76's S4 checker"
      - "docs/execution/plans/2026-11-15-text-scrub-residuals/task.md S4 note and §Session gate scope-paths and line-endings"
    research: { engine: none, sources: [] }
    reasoning: "Mine to decide: S4 and the two gate steps are defined in prose and need one script so the row checks and the gate check the same thing. Session 76's checker already does this; the only change is that a HEAD move is a stop, which the executor brief sets for this session. Writing the checks inline in each row lost because the row commands are fixed by the approved plan. Two-way: a plan-local script, disclosed in both handoffs."
  - id: D-930
    stage: execution
    question: "youtube/adapter.py and services/download.py were not ruff-formatted at HEAD (two and four layout hunks away from this plan's edits), so the gate's py-format step on the seven Python files would fail on lines this plan does not change. What is done?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Run ruff format on the two files, so the py-format step runs exactly as the plan writes it. The six extra hunks only re-wrap lines that fit in 100 columns; no token changes and both files stay CRLF."
    source_tag: Local Canon
    precedents:
      - "docs/execution/plans/2026-11-15-text-scrub-residuals/implementation-plan.md §Session gate — py-format is ruff format --check on the seven changed or new Python files"
      - "pyproject.toml [tool.ruff] line-length = 100; ruff 0.17.3 (uv.lock)"
      - "git show HEAD:packages/infrastructure/src/avkit_infra/youtube/adapter.py | ruff format --diff — the same two hunks at HEAD"
    research: { engine: none, sources: [] }
    reasoning: "Mine to decide: both files are in §Files Modified and the gate step is fixed by the approved plan. Formatting them keeps that step as written and adds only layout. Narrowing the step to new format drift against HEAD lost because it would change what a blocking gate step checks (an M-11 question). Leaving the step failing lost because the gate must end with every step at exit 0. Two-way: layout only, and the review reads it as six re-wrapped statements."
```

## Research References

- `GetShortPathNameW` (Microsoft Learn, fileapi.h): with a zero-size buffer it returns the size needed including the terminator; it returns 0 on failure, and the path must exist. The plan-time probe confirmed each (`C:/Temp/av-kit/text-scrub-residuals/tsr-probe.txt`, `nul-probe.txt`): a long folder name under `C:/Temp` gets a short form that `os.path.samefile` matches; a missing path returns `""` with error 2; this PC's home folder has no short form (lookup ok, same as the long form; the path is not recorded).
- Python `str.encode("utf-8")` refuses a lone surrogate (`UnicodeEncodeError`), measured in the same probe; `slugify` drops a surrogate, because it is not alphanumeric.

## Planning receipts

All under `C:/Temp/av-kit/text-scrub-residuals/`, read-only against the repository:

| Receipt | What it shows |
|---|---|
| `tsr-probe.txt` | The short-form lookup on a long folder, a missing synthetic home and the real home (booleans only); `slugify` and the UTF-8 write of a surrogate |
| `nul-probe.txt` | The lookup on an empty path, an embedded NUL and a surrogate path |
| `tsr-sweep.txt` | Precedent sweep: no `GetShortPathName`, `8dot3` or short-path code in `packages`, `tests` or `tools`; the `ctypes` precedent in `cli.py`; every `_clean_text` use; the pyright config; CI runs on `windows-latest` |
| `tsr-decision-probe.txt` | `decision_sources` on the grouping alone reads D-813 to D-817; with the two issues it adds D-363, D-804 and D-805 |
| `tsr-eol.txt` | Line endings, sizes and SHA-256 prefixes of every file in §Files Modified at `HEAD` `6aaf9b0` |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against the 03 home sections, D-337 and the two issues | `tsr-plan-2026-11-15-text-scrub-residuals` |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, against AC-147.1 to AC-148.9 | `tsr-execution-2026-11-15-text-scrub-residuals` |
