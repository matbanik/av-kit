# Closeout decisions (execution)

These are the three questions execution leaves to Mat, briefed under `.agent/docs/human-decision-protocol.md`. D-336 is the FP16-outcome brief that D-239 item 3 sends back once the spike stops without a fix (D-338, in the MEU-121 handoff). D-337 is the 8.3 limit the plan raised (`implementation-plan.md:425`, `docs/build-plan/03-service-layer.md:633`). D-340 is whether to fix the execution review's two non-blocking findings before the commit (D-339, in the MEU-121 handoff). A brief here authorizes nothing until Mat's ruling is recorded under it. Research receipts are `C:/Temp/av-kit/s52-hdp-research-d336a.txt`, `-d336b.txt`, `-d336c.md`, `-d337a.txt`, `-d337b.txt` and `-d340.txt`.

## D-336: what happens to ONNX FP16, now that the spike has found where it fails   [product-preference] [execution]

**Recommendation:** Keep FP16 as shipped: still offered, never preselected while INT8 or FP32 can run (D-330, D-331). Leave `TTS-ONNX-FP16-NONFINITE-AUDIO` open with the failure site recorded, and register one follow-up MEU that tests a guarded phase computation for the FP16 file under its own plan and review. E5 and two independent reports put the failure in the exporter's `atan2` emulation, `Div(imag, real)` at `/decoder/decoder/generator/Div`. That makes it a targeted fix that can be tested: the 149-job smoke is already its Red (12 failures) and its Green. Nothing shipped depends on it, because a fresh install preselects INT8, which passed 149 of 149.

**What is known**

| Source | What it says |
|---|---|
| E5, row 11 (`C:/Temp/av-kit/s52-spike-summary.json`) | In all 11 failing pairs, the first non-finite output in graph order is `/decoder/decoder/generator/Div`. Its numerator is `Gather_5_output_0` (largest absolute value about 0.6) and its denominator is `Gather_4_output_0` (about 1.4). Both are FP16 `[1, 11, N]` and hold no NaN or Inf. |
| onnx-community Kokoro discussion 22 (2026-10-12) | Same graph. `Gather_5` is the imaginary part of the harmonic source's STFT (n_fft 20, hop 5), and `Div → Atan → Greater/Less → Where` is the exported `atan2`. In bins 0 and 10 (DC and Nyquist) the imaginary part should be exactly 0, but ONNX Runtime returns rounding noise of about 1e-7. The post's two-node patch masks those bins' imaginary part to 0 and changes `Greater` to `GreaterOrEqual`. It fixes a DirectML tone, not a NaN. |
| sherpa-onnx issue 4086 | Same `Div` in sherpa's own INT8 export. In bins 0 and 10 the imaginary part is exactly 0, and at low precision the real part is sometimes exactly 0 too, so `0 / 0 = NaN`. Whether it happens depends on noise from two unseeded random ops in `m_source/l_sin_gen`. On x64, a later `DynamicQuantizeLinear` turns the NaN into an ordinary value. |
| What this session did not measure | How many zeros `Gather_4` holds where the output fails, and whether the `Div` output is NaN or Inf. A 0/0 fits E5's two finite inputs and both reports. A non-zero value over 0 gives ±Inf, which `Atan` maps to the finite ±π/2, so 0/0 is the reading that fits a non-finite clip. It stays a hypothesis until the follow-up's first step counts them. |

That reading also bears on the follow-up's design. Discussion 22's mask alone would keep a 0/0 wherever the real part is 0, so an FP16 fix needs a guard there, or that subgraph run in FP32. The ONNX Runtime float16 docs describe the second approach (`node_block_list`, nodes left in float32). How the app would apply a patch is the follow-up plan's question:
- patch the downloaded file, which needs the `onnx` package at download or load time;
- or fetch a patched file from elsewhere.

One third-party measurement points the other way. The `safwan-o/Kokoro-82M-split-ONNX` card scores the official FP16 model at 18.5% WER against FP32's 4.2%, on 15 passages with faster-whisper small.en. If that holds here, FP16 has a quality cost beyond the NaN, and the follow-up should listen and measure before it ships a patch.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ Keep as shipped; issue open with the site; one follow-up MEU for a guarded phase fix, spike first (count the zeros, patch, rerun the 149 jobs, listen) | — | — | D-239 (`known-issues.yaml:4011`); D-333 (`implementation-plan.md:642-651`); HF discussion 22; sherpa-onnx 4086 |
| ⚠️ Do nothing more: keep as shipped, issue open with the findings, no follow-up | No new work, no new dependency; INT8 already covers a fresh install | A user who picks FP16 still gets "generated audio must be finite" on about 8% of jobs (12 of 149), and the issue stays open with no path to closing | Row 9 receipt `s52-smoke-red.json` |
| ⚠️ Keep as shipped, and add a line on the FP16 row in the model list ("can fail on some sentences; INT8 is recommended") | A user learns why before choosing it | New UI copy and an E2E change; it fixes nothing, and a later fix makes it obsolete | 03 `:649` (nothing removes or disables FP16) |
| ❌ Hide or remove FP16 | Nobody meets the failure; one variant fewer to support | Reverses D-239's "Nothing here removes or disables it" just as the cause is located and looks fixable; a user who already downloaded it loses it; the WER card would support it only if a follow-up confirms the quality cost | D-239; safwan-o model card |

**Not part of the choice:** a comment on discussion 22 saying the same `Div` goes non-finite in `model_fp16.onnx`. It would be posted from your account, which is outward-facing. I won't post it without your words.

**Precedent:**
- D-239 (`known-issues.yaml:4011`, 03 `:649`): what happens to FP16 comes back to you, and nothing removes or disables it.
- D-330 (`implementation-plan.md:610`): a fresh install keeps FP16 when it is the only downloaded row.
- D-333 (`implementation-plan.md:642-651`): "A fix would change the adapter, so it needs its own Red and review." A cause that points at a fix comes back as an amendment, re-reviewed before any code changes.

**Research:** Pomera tavily (3 searches, 1 page read).
- https://github.com/k2-fsa/sherpa-onnx/issues/4086 (practice): the same `Div` gives 0/0 in bins 0 and 10 at low precision, triggered by unseeded random source noise.
- https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/discussions/22 (practice): the node names match E5's, the exported `atan2` is identified, and a verified two-node patch is given.
- https://onnxruntime.ai/docs/performance/model-optimizations/float16.html (official docs): `node_block_list` keeps named nodes in float32.
- https://huggingface.co/safwan-o/Kokoro-82M-split-ONNX (practice): the official FP16 model scores 18.5% WER against FP32's 4.2%.

**Reversibility / risk:**
- Two-way for the first three options. Removing FP16 is user-visible and hard to undo for anyone who has it downloaded.
- If the recommendation is wrong, the cost is one follow-up MEU's time. Any patch can change how FP16 sounds, so the follow-up needs a listening check as well as the smoke.
- INT8 passing 149 of 149 here does not prove its `Div` never hits 0/0, since sherpa saw that hidden on x64 by the next quantize step. The follow-up's zero count can cover INT8's `Div` at no extra cost.

**If you do not answer:** FP16 stays as shipped and the issue stays open, which is the do-nothing option and also the recommendation's state until a follow-up exists. No follow-up MEU is registered and nothing is posted. The next session prompt lists D-336 as open.

**Mat's ruling:** "all recommendations accepted", "proceed with changes", "commit and push" (2026-11-07). The recommendation stands: FP16 stays as shipped, `TTS-ONNX-FP16-NONFINITE-AUDIO` stays open with the failure site, and one follow-up MEU is registered for a guarded phase computation, spike first (MEU-127, task row C5). Nothing is posted to discussion 22.

## D-337: the home-folder scrub doesn't match an 8.3 short form of the home folder   [governance-value] [execution]

**Recommendation:** Make `scrub_home` match the short form too. On Windows it gets the home folder's 8.3 form once from `GetShortPathNameW`, which is empty when the volume makes no short names, and it replaces both forms with `~`. That closes the gap at the one place every Console detail passes through (`console_field`, `services/health.py:120-126`), and it doesn't change any stored setting. It is a small row with its own Red: patch a synthetic short form, because this PC's three-letter user folder has none. It needs a plan, either a follow-up MEU or the next session's, so this session's approved scope doesn't grow after review.

**What is known:**
- `scrub_home` (`services/health.py:104-117`) matches the long form `Path.home()` gives.
- An 8.3 form such as `C:\Users\FIRSTN~1` shows the first six characters of the user name in capitals.
- The default models folder, the Electron app-data folders and pytest's temp root are long forms.
- A `tts.models_directory` keeps the spelling it was saved with (`implementation-plan.md:425`). So a short form saved through the settings API or MCP reaches a missing-weight `detail` unscrubbed. The folder picker writes long paths.
- Some systems hold `TEMP` in its short form, but no Console field is built from `TEMP` today (`s52-d335-tempsources.txt`).

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ `scrub_home` also matches the short form (`GetShortPathNameW`, cached, Windows only) | — | — | D-335; 03 `:633`; Wikipedia, 8.3 filename |
| ⚠️ Turn the models folder into its long form when it is read (`GetLongPathNameW` or `Path.resolve`) | Fixes the source for the one path known to carry it; the setting then shows in the long form everywhere | Covers only that path, so any other short path in an error still reaches the Console. `resolve` also follows junctions, so it changes a folder the user chose. It's a change in `services/models.py`, outside D-335's scrub. | `implementation-plan.md:425`; Python `tempfile` docs |
| ❌ Do nothing: the app writes long paths, and a short form needs a setting someone saved by hand | No work | Leaves a known way for part of the user name to reach the Console. Your Session 50 rule says such a value is fixed or raised, never kept as a residual, so keeping it needs your words. | Session 52 prompt (the Session 50 rule) |

**Precedent:**
- D-335 (`implementation-plan.md:663`, your "D-335 scrub" on 2026-11-07): the home folder becomes `~` in a failed load's detail.
- The plan's §Out of Scope row (`implementation-plan.md:425`) and the Delivered note (03 `:633`) both record the 8.3 limit as raised with you.
- No other precedent: `git grep` for `GetShortPathName`, `8dot3` and "short path" finds only 03 `:633`.

**Research:** Pomera tavily (2 searches).
- https://en.wikipedia.org/wiki/8.3_filename (reference): a long name is cut to its first 6 characters, then `~1`.
- https://superuser.com/questions/1524767/powershell-uses-the-short-8-3-form-for-envtemp (practice): `$env:TEMP` holds the 8.3 form on some systems.
- https://docs.python.org/3/library/tempfile.html (official docs): `gettempdir` takes `TMPDIR`, `TEMP` or `TMP` as given, so a short `TEMP` reaches any path built from it.

**Reversibility / risk:** Two-way. If the recommendation is wrong, the cost is one ctypes call and a test. An unmatched short form leaks no more than it does today.

**If you do not answer:** Nothing changes this session. The limit stays recorded at 03 `:633` and in the MEU-119 handoff, and the next session prompt lists D-337 as open.

**Mat's ruling:** "all recommendations accepted", "proceed with changes", "commit and push" (2026-11-07). The recommendation stands: `scrub_home` gets the short form in a row of its own with a Red, in a later plan, not in this session. Row C5 files it as `CONSOLE-HOME-SCRUB-SHORT-FORM` for the next triage to place.

## D-340: fix the execution review's two non-blocking findings before the commit, or keep them filed   [governance-value] [closeout]

**Recommendation:** Fix both now, before the commit. Both are in code this session wrote, each fix is a few lines plus a test, and D-289 is this same question, which you answered "Fix it now". It needs your `continue` on the execution loop for at least 9M tokens (10M recommended), a fresh gate, and one recheck round scoped to F1 and F2.

**What is known**

| Finding | What it does | Fix the review recommends |
|---|---|---|
| F1, Medium (MEU-120), filed as `GUI-MODELS-PROBE-LEFTOVER-FILE` | If the probe's write creates its file and then throws, or `accessSync` fails after the write, `probeModelsDirWritable` returns `false` without deleting `.write-probe-*` (`ui/src/main/setup-readiness.ts:108`). On a fresh install, that file sits in the nearest existing folder, which can be your home folder. The answer stays `false`, so readiness errs safe. | Delete the probe in a `finally`, and add fault cases to `setup-readiness.test.ts` |
| F2, Medium (MEU-121), filed as `SMOKE-TTS-WAV-HEADER-TRUSTED` | The packaged smoke takes each WAV's frame count from its header (`tools/smoke_packaged_tts.py:357`, accepted at `:710`). A 44-byte header that declares 100 frames passes. The reviewer read every WAV from both INT8 runs and found 149 + 149 complete payloads, so this session's evidence stands. | Require a PCM payload of the declared length, and add a header-only negative fixture. `tools/` has no smoke tests yet, so this adds one test file |

- **Ledger.** Round 1 cost 14,996,767 of the loop's 21,000,000 tokens. The ledger holds back the last round's cost for the next round, so it refuses a round 2 until you add at least 8,993,534 (`C:/Temp/av-kit/s52-exec-ledger-state-r1.txt`). Rounds are 1 of 6.
- **Timing.** The gate takes a few minutes. Each 149-job smoke took about 3 minutes (`s52-smoke-red.json`, `s52-smoke-green.json`), so F2's new check can also be rerun on the real INT8 jobs.
- **Order.** Closeout has run on the approved round 1. A fix reopens execution: correction rows, the gate, round 2, then a short addendum to the reflection, the metrics row and the commit draft.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ Fix both now, then recheck in round 2 | — | — | D-289 (`docs/execution/reflections/2026-11-05-closeout-register-grammar-reflection.md:96`); codeant.ai |
| ⚠️ Keep them filed, and link both issues to MEU-125 so they are fixed before rc.2 repeats the smoke | No extra review round now; MEU-125's own review covers the fix; the commit goes as reviewed | Adds two unrelated fixes to the release-gate session; the stray-file path ships until then | D-315 (MEU-125 repeats the smoke); D-200 |
| ❌ Do nothing more: commit as reviewed, the two issues stay open, and the next triage places them | No tokens, no time, nothing reopened | F2's check stays able to pass a header-only WAV whenever the smoke is next relied on, unless a triage catches it first | D-200 (`docs/execution/reflections/2026-11-03-release-rc1-reflection.md:115`) |

**Precedent:**
- D-289 (`2026-11-05-closeout-register-grammar-reflection.md:96`): "Is review F1 … fixed now or registered as a known issue?" went to you, and you answered "Fix it now". Round 2 then cost 3,865,433 tokens, against round 1's 8,658,354 (`:23`).
- D-200 (`2026-11-03-release-rc1-reflection.md:115`): a non-blocking note was filed and not fixed. That behaviour predated the session and was never seen in the real app; F1 and F2 come from this session's own code.
- D-339 (MEU-121 handoff): both findings are filed already, so every option keeps a record.

**Research:** Pomera tavily (1 search, `C:/Temp/av-kit/s52-hdp-research-d340.txt`).
- https://codeant.ai/blogs/code-review-best-practices (practice): before merge, every requested change is addressed or explicitly deferred; fix-after-merge commits count as rework.
- https://docs.gitlab.com/development/code_review (official docs): review comments carry a `non-blocking:` label when they don't hold the merge.

**Reversibility / risk:** Two-way for all three. If the recommendation is wrong, the cost is the tokens and about an hour. If F1's fix breaks the probe, the new fault cases and the gate's existing probe tests catch it. If F2's check is too strict for a valid WAV, the rerun on the real INT8 jobs shows it before any commit.

**If you do not answer:** Nothing is committed without your words anyway. The commit draft stays as reviewed, both issues stay open, and the next session prompt lists D-340 as open.

**Mat's ruling:** "all recommendations accepted", "proceed with changes", "commit and push" (2026-11-07). The recommendation stands: both are fixed now (task rows C1 to C4), with the recommended continue of 10,000,000 tokens on `s52-execution-2026-11-06-tts-load-fp16`, recorded at 2026-11-07T16:34:19Z (`C:/Temp/av-kit/s52-exec-ledger-continue-1.txt`), a fresh gate (C6) and a round-2 recheck scoped to F1 and F2 (C8).
