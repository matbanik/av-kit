# Human gate decisions (planning)

These are the three questions this plan puts to Mat at the plan gate (`implementation-plan.md` §User Review Required), briefed under `.agent/docs/human-decision-protocol.md`. D-373 was written with the plan. D-377 comes from plan review round 1's F1 (`.agent/context/handoffs/2026-11-07-convert-extract-index-plan-critical-review.md`). D-378 is the budget question that Mat's brief asks when round 1 costs more than 5.25M. The briefs authorize nothing until Mat's ruling is recorded under each, and their sources go into the decision log.

Mat ruled all three on 2026-11-07: "All recommendations accepted. But also file, and assign into session groupings So next sessions, can handle the new issues." Each brief below carries the ruling and how it ran.

## D-373: a Cut job saves an encoder it never uses   [product-preference] [planning]

**Mat's ruling (2026-11-07):** the recommendation: file `CONVERT-CUT-ENCODER-LABEL`, with no Cut change. Because Mat also asked to file and assign, the filing ran at plan time rather than in row 4. It went through `model.add_issue` and `model.save`, since `add` takes no priority or related list. It set P4, `related` `CONVERT-EXTRACT-ENCODER-LABEL` and `meu_links` MEU-123 (`C:/Temp/av-kit/s54-plan-register-file.txt`). D-380 placed it last in current-focus's debt queue. Its `conversion.py` cite was then pinned to `39ac742`, because row 2 moves those lines (`s54-plan-pin-cut-cite.txt`).

**Recommendation:** register `CONVERT-CUT-ENCODER-LABEL` for the next triage, and leave Cut unchanged here. The defect is real: `_dispatch` resolves an encoder for every job kind and saves it in `gpu_encoder` (`packages/core/src/avkit_core/services/conversion.py:486-495`). But Cut never reads it. Fast Copy is `-c copy` (`packages/infrastructure/src/avkit_infra/media/adapter.py:590-591`), and the re-encode is fixed at `libx265` with AAC audio (`:592-604`). A Cut stores no GPU preference (AC-112.4), so the GPU setting picks the label. So on an NVIDIA machine with the setting at Auto or NVIDIA, a Cut row in the queue reads `hevc_nvenc` either way. With the setting at Software it reads `libx265`, which is already right for a re-encode and still wrong for Fast Copy. Neither of this session's issues names Cut. Filing it keeps MEU-123 to the two issues it closes, and lets the next triage weigh it next to the rest of the Convert residuals.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ File `CONVERT-CUT-ENCODER-LABEL`, no Cut change | — | — | Session 52 D-337, D-344; `CONVERT-EXTRACT-ENCODER-LABEL` was itself filed as a P4 rider |
| ⚠️ Widen MEU-123: a re-encode Cut saves `libx265`, and a Fast Copy Cut saves none | The Cut label is right in this session, and the change sits next to the Extract one in `_dispatch`. Copy needing no encoder is FFmpeg's own model | It changes a stored value that neither issue names, and adds Red tests and a spec note to this MEU. It labels today's fixed `libx265` re-encode truly. It doesn't decide whether a later Cut should use the GPU (MEU-112 kept the choice to Compress, AC-112.4), and it doesn't change the adapter's Cut command | FFmpeg `OutputStream` (`stream_copy`, `encoding_needed`); `adapter.py:590-604` |
| ❌ Do nothing, unfiled | No register change | The label stays wrong and unrecorded. Anyone reading a Cut row's encoder on an NVIDIA machine sees an encoder the job didn't use | `conversion.py:486-495` |

**Precedent:**
- D-337 and D-344 (Session 52, Mat's rulings, "all recommendations accepted"): a neighbouring defect found during a session was filed for a later plan, not fixed in place (`docs/execution/reflections/2026-11-06-tts-load-fp16-reflection.md:128`, `:135`).
- D-354 (Session 53, Mat's ruling, "D-354 Flatten the tabs now"): Mat took the widen option over the recommendation to file. So the precedents point both ways, and that is why this comes to you.
- AC-112.4 (MEU-112): only a Compress job stores a GPU choice. Cut and Extract store none (`tests/unit/test_conversion_service.py:905-929`). The Cut question is therefore about the label, not about honouring a choice.
- D-242 (grouping §8): it placed `CONVERT-EXTRACT-ENCODER-LABEL` here as a rider because it is the same `_dispatch` line as this MEU's Extract work. Cut wasn't part of that triage.

**Research:** `pomera_web_search` (tavily).
- Official: [FFmpeg `ffmpeg.h`](https://www.ffmpeg.org/doxygen/2.4/ffmpeg_8h_source.html) gives an output stream separate `stream_copy` and `encoding_needed` flags. A copied stream runs no encoder, so a Fast Copy Cut has none to name.
- Community: [SRS FFmpeg guide](https://ossrs.io/lts/en-us/docs/v7/doc/ffmpeg) describes `copy` as "donot encoder the audio stream, copy it". It is the same model.
- No source covers how a queue UI should label a copied job. That part is av-kit's own choice.

**Obviousness test (§4):** not obvious. The precedents disagree (D-337 and D-344 against D-354), and the widen option changes a value users see that neither issue names.

**Reversibility / risk:** two-way. Filing adds one register entry. Widening changes only new Cut rows' `gpu_encoder`, and the next session could revert it. If you pick the recommendation and the label matters sooner, the cost is one more small session.

**If you do not answer:** no issue is filed, Cut stays as it is, and the closeout records D-373 as still open.

**What the recommendation would authorize:**
1. Row 4 runs `tools/issue_triage.py add --id CONVERT-CUT-ENCODER-LABEL --title "A cut is labelled with an encoder it does not use" --severity low --component core --add-status open --discovered 2026-11-07`, with `--root-cause` citing `conversion.py:486-495` and `adapter.py:590-604`, and `--blast-radius` naming the queue row's encoder segment and the API's `gpu_encoder`. This is before `issue_triage.py render` and `triage`. The priority is left to the next triage, and the rider's own priority (P4) is the expected band.
2. Row 4's check also requires that `CONVERT-CUT-ENCODER-LABEL` exists with status `open`.

It does not authorize any change to Cut's code, tests or spec text, or to how Cut picks its encoder.

**What the widen option would authorize instead:**
1. In row 2's `_dispatch`, a Cut with `CutCopyMode.FastCopy` saves `gpu_encoder=None` and a re-encode Cut saves `"libx265"`, without calling `detect_gpu`. Only the saved label changes. The adapter's Cut command stays as it is (`adapter.py:590-604`).
2. A new AC-123.14 in row 1 (Red) for both modes on NVIDIA caps, a line in the 08 Delivered note, and a mechanism id `CUT_ENCODER_LABEL`.
3. No issue filed. The amended plan goes to one recheck round of the plan review before row 0.

## D-378: the execution loop's token budget   [product-preference] [planning]

**Mat's ruling (2026-11-07):** the recommendation: H1-7 opens the execution loop at the default, 21,000,000 tokens and 6 rounds, with no `--token-budget`.

**Recommendation:** open `s54-execution-2026-11-07-convert-extract-index` at the execution default, 21,000,000 tokens and 6 rounds (`tools/review_ledger.py:100-106`). Plan round 1 cost 8,541,302, more than the brief's 5.25M line. That is about twice a Session 53 plan round (8.8M over 2). Session 53's execution took 10.3M plus a 2.6M correction round, and Session 52's took 15.0M plus 4.7M. At twice Session 53's rate, one execution round would cost about 20M. The default covers that, and also covers Session 52's 19.7M. If the loop reaches it, the ledger's token stop fires and the next round waits for your words (`review_ledger.py continue`), so the default caps the spend without ending the work.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ 21,000,000, the default | — | — | `review_ledger.py:100-106` |
| ⚠️ 15,000,000 | A lower ceiling. It covers Session 53's whole execution, 12.9M | At this plan round's rate, round 1 alone may pass it, and then the stop asks you again in the middle of the review | Session 53, Session 52 metrics |
| ❌ Do nothing | — | None: with no answer the loop opens at the default, which is the recommendation | `begin` without `--token-budget` |

**Precedent:** Session 52 RULE-3, compare the budget with the last comparable round. Session 53's execution is the closest, at one service change plus a real-stack test.

**Research:** none. These are av-kit's own measurements, and no outside source applies.

**Obviousness test (§4):** not obvious. Mat's brief makes it Mat's call.

**Reversibility / risk:** two-way. `review_ledger.py continue --tokens` raises the budget on your words, and a lower budget only stops sooner.

**If you do not answer:** H1-7 opens the loop at the default, 21,000,000.

**What the recommendation would authorize:** H1-7 runs `review_ledger.py begin` for the execution loop without `--token-budget`, and records the budget next to Session 53's 10.3M round.

## D-377: the backend's first log line puts the database path, user name included, in the Console   [product-preference] [planning]

**Mat's ruling (2026-11-07):** the recommendation: file `CONSOLE-STARTUP-DB-PATH`, with no change here. The filing ran at plan time, as for D-373, through `model.add_issue` and `model.save`. It set P3, `related` `CONSOLE-HOME-SCRUB-SHORT-FORM` and `meu_links` MEU-123 and MEU-124 (`C:/Temp/av-kit/s54-plan-register-file.txt`). The component is `infrastructure`, where `engine.py` lives, not `core` as item 1 below says. D-379 placed it as a rider in Session 55 (MEU-124), the last code session before rc.2 and the only one left in the database package.

**Recommendation:** register `CONSOLE-STARTUP-DB-PATH` for the next triage (P3 expected, as for `CONSOLE-HOME-SCRUB-SHORT-FORM`), with no change here. Plan review F1 asked whether the real-FFmpeg tests leak paths, and answering it turned up a production line outside this MEU:
- `build_services` creates the engine (`packages/api/src/avkit_api/wiring.py:135`) before it builds HealthService (`:205`). HealthService's constructor installs the processor that drops every field outside `CONSOLE_FIELDS` and scrubs the home folder (`packages/core/src/avkit_core/services/health.py:163-183`).
- `create_sqlite_engine` logs `engine.created` with `path=str(db_path)` (`packages/infrastructure/src/avkit_infra/database/engine.py:85`). No processor is installed yet, so structlog's default renderer prints it unchanged to stdout.
- The database is `%LOCALAPPDATA%\av-kit\avkit.db` (`engine.py:36-46`, `:49-51`), which is inside the user's profile folder.
- The desktop host forwards each line the backend prints to the Console without a scrub (`ui/src/main/index.ts:267-274`, `ui/src/main/python-manager.ts:133-145`, `ui/src/renderer/src/hooks/useBackendLogs.ts:69-80`). It isn't written to `console.log`, which only HealthService writes.

The probe (`C:/Temp/av-kit/s54-plan-startup-stdout-probe.txt`) ran `build_services` into a folder with a marker name and captured stdout. One line held the folder, this one. Nothing in the register covers it. Filing keeps MEU-123 to the two issues it closes and gives the fix a session that can choose between the two ways to fix it.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ File `CONSOLE-STARTUP-DB-PATH`, no change here | — | — | Session 52 D-337, which filed `CONSOLE-HOME-SCRUB-SHORT-FORM`, the closest neighbour (a home path in the Console) |
| ⚠️ Widen MEU-123: drop `path=` from `engine.created`, and add a test that `build_services` into a marker-named folder prints no line holding it | It closes the leak in this session. The probe shows it is the one line, and the test watches every line `build_services` prints before the install, so a later line with a path also fails it. Nothing waits for the `engine.created` text: the two UI tests use it only as a sample of a line that isn't the ready line (`ui/tests/unit/dev-spawn.test.ts:73`, `ui/tests/unit/ready-probe-guard.test.ts:34`) | It changes database code and a log line that neither issue names. It drops the database path from the startup output, which can help when debugging. The other fix, installing the processor before the engine, is a wiring change that this MEU shouldn't make. The amended plan goes to one recheck round | `engine.py:85`; `wiring.py:135`, `:205` |
| ❌ Do nothing, unfiled | No register change | The user name stays in the Console at every start and is unrecorded. That breaks the carried Session 50 RULE-1, which allows a raw value to reach the Console only when the row fixes it or it is raised with Mat, never as a residual | `s54-plan-startup-stdout-probe.txt` |

**Precedent:**
- D-337 (Session 52, Mat's ruling, "all recommendations accepted"): `CONSOLE-HOME-SCRUB-SHORT-FORM`, a home folder reaching the Console, was filed P3 for a later plan, not fixed in place.
- D-354 (Session 53, Mat's ruling, "D-354 Flatten the tabs now"): Mat took the widen option over the recommendation to file. So the precedents point both ways.
- Session 50 RULE-1 (`docs/execution/reflections/2026-11-05-transcript-failure-reason-reflection.md:137`): this brief is how the rule raises it.

**Research:** `pomera_web_search` (tavily).
- Official: [structlog Console Output](https://www.structlog.org/en/stable/console-output.html): "structlog's default configuration already uses `ConsoleRenderer`". Every field is rendered until `structlog.configure` installs something else.
- Official: [structlog API](https://www.structlog.org/en/stable/api.html): `PrintLoggerFactory`'s file defaults to `sys.stdout`, which is the pipe the host reads.

**Obviousness test (§4):** not obvious. The precedents disagree (D-337 against D-354), and the fix sits in database code that neither issue names.

**Reversibility / risk:** two-way. Filing adds one register entry. Widening removes one field from one log line, and a later session could restore it. Until it is fixed, anyone who copies the Console or shares a screenshot of it shows their Windows user name.

**If you do not answer:** no issue is filed, the line stays, and the closeout records D-377 as raised and still open.

**What the recommendation would authorize:**
1. Row 4 runs `tools/issue_triage.py add --id CONSOLE-STARTUP-DB-PATH --title "The backend's first log line shows the database path, user name included, in the Console" --severity low --component core --add-status open --discovered 2026-11-07`. Its `--root-cause` cites `engine.py:85` and `wiring.py:135`, `:205`. Its `--blast-radius` names the Console's stdout lines, the probe receipt and `CONSOLE-HOME-SCRUB-SHORT-FORM` as the neighbour, because `add` takes no related list (`C:/Temp/av-kit/s54-plan-triage-add-help.txt`). This runs before `issue_triage.py render` and `triage`. The priority is left to the next triage.
2. Row 4's check also requires that `CONSOLE-STARTUP-DB-PATH` exists with status `open`.

It does not authorize any change to `engine.py`, `wiring.py` or the host's Console code.

**What the widen option would authorize instead:**
1. A new row 2b: `engine.py:85` logs `engine.created` with no `path`.
2. A new AC-123.15 in row 1 (Red): `build_services` into a `tmp_path` folder with a marker name prints no stdout line holding the marker. A mechanism id `STARTUP_NO_PATH`, and `engine.py` added to Files Modified.
3. No issue filed. The amended plan goes to one recheck round of the plan review before row 0.
