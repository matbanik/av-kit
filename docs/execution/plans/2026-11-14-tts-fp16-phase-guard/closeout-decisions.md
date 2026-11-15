# Closeout decisions (execution)

This is the question execution leaves to Mat, briefed under `.agent/docs/human-decision-protocol.md`. D-797 is the outcome that 03's Outcome rule (D-336) sends back with the spike's counts. A brief here authorizes nothing until Mat's ruling is recorded under it. Research receipts are `C:/Temp/av-kit/s73-hdp-research-d797a.txt`, `-d797b.txt` and `-d797c.txt`.

## D-797: What ships from the FP16 phase guard spike?   [Human-approved] [execution]

**Recommendation:** Ship the guarded graph, if the 12 pairs in the listening folder sound right to you. How it ships is a plan amendment with its own Red and review, as D-336 and D-333 require, not a row of this plan. FP16 stays never preselected while INT8 or FP32 can run (D-330, D-331), and `TTS-ONNX-FP16-NONFINITE-AUDIO` stays open until the fix lands. The guard is two nodes. It changes exactly the 12 jobs that fail today and turns all 12 into finite audio. The other 137 jobs come out byte for byte as they do today, on the same packaged build and at the same speed.

**What is known**

| Source | What it says |
|---|---|
| Inputs, row 0b (`C:/Temp/av-kit/s73-fresh-inputs.json`) | The seven inputs, downloaded fresh from Hugging Face at the app's pins, equal Session 52's cached copies. Your installed FP16 graph and the four voices and `config.json` equal them too, read only by hash; the installed INT8 graph is absent. |
| DENOM_COUNT, row 3 (`C:/Temp/av-kit/s73-count.json`) | Over the 12 failing jobs, `/decoder/decoder/generator/Div` sees 14 slots where both parts are 0. Each gives a NaN quotient, a NaN `Atan`, a NaN phase, and 1,981,200 non-finite waveform samples. Over the 137 passing jobs there are 0 such slots. The other zero counts don't matter: a real part of 0 over a non-zero imaginary part gives ±Inf, which `Atan` maps to the right ±π/2 (102 times in failing jobs, 1,287 in passing ones). |
| PATCH_COPY, row 2 (`C:/Temp/av-kit/s73-patch.json`) | PHASE_GUARD adds `IsNaN` and `Where` after node 1686, the `Div` (2,490 nodes to 2,492). A NaN quotient becomes FP16 +0, the value `atan2(0, 0)` has in C Annex F, fdlibm and torch. The checker passes, and the patch is deterministic (SHA-256 `9037c82b…6fd33`, 163,235,204 bytes). The source file is unchanged. |
| GRAPH_COMPARE, row 4 (`C:/Temp/av-kit/s73-compare.json`) | On the 149 jobs in ONNX Runtime: the original graph fails 12, and the guarded graph fails none. The changed jobs are exactly those 12, and 137 are bit-identical. |
| SENTENCE_SMOKE, row 5 (`C:/Temp/av-kit/s73-smoke-control.json`) | The packaged backend on the original FP16 graph fails 12 of 149, each on non-finite audio. The failure set equals Session 52's `s52-smoke-red.json`. |
| SENTENCE_SMOKE, row 6 (`C:/Temp/av-kit/s73-smoke-guarded.json`) | The same build on the guarded FP16 graph passes 149 of 149, each WAV with its full payload (AC-121.8). It ran in 2 min 46 s, the same as the control. |
| SENTENCE_SMOKE, row 7 (`C:/Temp/av-kit/s73-smoke-int8.json`) | INT8, the fresh-install default, passes 149 of 149 on the same build (2 min 45 s). |
| WAV_IDENTITY, row 8 (`C:/Temp/av-kit/s73-wavs.json`) | The 137 jobs the control passed are byte-identical between the control and guarded runs; none differ. The 12 guarded WAVs are complete 24 kHz audio, within 0.07 s of INT8's length for the same job. |
| What this spike did not measure | Whether the 12 guarded clips sound right, which is your listening. Also FP16's general quality: the `safwan-o` card's 18.5% WER for the official FP16 against FP32's 4.2% (Session 52, D-336) is about every FP16 job, and the guard leaves the other 137 unchanged. |

**Listening folder:** `C:/Temp/av-kit/s73/listen`. `listen.txt` lists 12 pairs, numbered by job. Each pair is the guarded FP16 WAV, then the INT8 WAV of the same sentence and voice, for comparison: 11 sentences across af_heart, am_michael, af_bella and bf_emma, and the 96-word passage (pair 12). Today's FP16 has no audio for these jobs to compare, because they fail.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ Ship the guarded graph. How it ships is a plan amendment with its own Red and review. FP16 stays never preselected, and the issue stays open until the fix lands. | — | — | `s73-compare.json`; `s73-smoke-guarded.json`; D-336 (`docs/execution/plans/2026-11-06-tts-load-fp16/closeout-decisions.md:5-53`); D-333 |
| ⚠️ Ship nothing. FP16 stays as shipped, and the issue stays open with the cause and the tested guard recorded. No follow-up is registered. | No new work. No new dependency or download step: the packaged backend has `onnxruntime` but not `onnx`, so patching at download needs either a new package or a hand-rolled protobuf edit. INT8 already covers a fresh install. | A user who picks FP16 still gets "generated audio must be finite" on 12 of 149 jobs (about 8%), although a measured two-node fix exists. The issue stays open with no path to closing. | `s73-smoke-control.json`; `pyproject.toml` runtime dependencies |
| ⚠️ Do nothing: don't rule now. | Leaves room to listen later. | Row 9 stays `[B]`, row 10's records wait, MEU-127 can't reach review, and the next session prompt carries D-797 as open. | `task.md` row 9 |

**Not part of the choice:**
- Posting to Hugging Face discussion 22. 03's Upstream rule (D-336) says nothing is posted, and nothing was.
- How the fix ships. The amendment chooses one of these, with its own research and Red:
  - patch the downloaded file at download or load time, checked by source and result hash;
  - keep `/decoder/decoder/generator` in FP32 (`node_block_list`);
  - fetch a guarded file from elsewhere.

**Precedent:**
- D-336 (`docs/execution/plans/2026-11-06-tts-load-fp16/closeout-decisions.md:53`): Mat accepted a guarded phase fix, spike first, with what ships coming back to Mat. That is 03's Outcome rule (`docs/build-plan/03-service-layer.md:697`).
- D-239 (`.agent/context/known-issues.yaml:4027`): nothing removes or disables FP16, and its outcome comes back to Mat.
- D-330 and D-331: FP16 stays offered and is never preselected while INT8 or FP32 can run (03 `:695`).
- D-333: a fix that changes the adapter needs its own Red and review, so shipping is an amendment.

**Research:** Pomera tavily (3 searches).
- https://www.adrianlyjak.com/p/onnx (practice): casting all of Kokoro to FP16 gave static and distortion, and the sensitive layers had to be kept out of FP16. A targeted local fix is the usual shape.
- https://onnxruntime.ai/docs/performance/model-optimizations/float16.html (official docs): `node_block_list` keeps named nodes in float32. That is the alternative way to ship, at the cost of a re-export.
- https://docs.openclaw.ai/plugins/onnx (practice): locally produced ONNX artifacts are checked against a declared source revision and file hashes. That is how a patch at download time could be verified.
- From Session 52's D-336, still current: sherpa-onnx issue 4086 sees the same 0/0 in bins 0 and 10, and HF discussion 22 identifies the exported `atan2`.

**Reversibility / risk:**
- Two-way. Shipping the guard changes only what a user who picks FP16 hears on the jobs that fail today, and an amendment can drop it.
- If the guarded clips sound wrong, the cost is the amendment's time, and it would stop at its own listening check.
- The guard maps only NaN, so it can't change a job that is finite today. Rows 4 and 8 measured exactly that on all 149 jobs.

**If you do not answer:** Ship nothing yet. FP16 stays as shipped, the issue stays open, row 9 stays `[B]`, and nothing in row 10 is written. The next session prompt lists D-797 as open. No follow-up is registered and nothing is posted.

**Mat's ruling:** USER_EXPLICIT "Ship guarded (Recommended)" (2026-11-15, after the listening folder was put to Mat through the Human Decision Protocol). The recommendation stands: the guarded graph ships, and how it ships is a plan amendment with its own Red and review, not a row of this plan. FP16 stays never preselected while INT8 or FP32 can run, `TTS-ONNX-FP16-NONFINITE-AUDIO` stays open until the fix lands, and nothing is posted to Hugging Face.
