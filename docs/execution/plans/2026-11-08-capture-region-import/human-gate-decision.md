# Human gate decisions (planning)

These are the three questions this plan puts to Mat at the plan gate (`implementation-plan.md` §User Review Required), briefed under `.agent/docs/human-decision-protocol.md`. A brief here authorizes nothing until Mat's ruling is recorded under it, and each brief's sources go into the decision log.

Refreshed on 2026-11-08 at Mat's request ("For 2 3 4 run HDP and give me recommendations again"). D-425 and D-426 had a second precedent sweep and new searches, and both are now classed `governance-value`, because each sets a new limit (§4 test 4). D-427 is new. The searches are saved in `C:/Temp/av-kit/s58-hdp-d425-web1.txt`, `s58-hdp-d425-web2.txt`, `s58-hdp-d426-web1.txt`, `s58-hdp-d426-web2.txt`, `s58-hdp-d427-web1.txt` and `s58-hdp-d427-web2.txt`, and `s58-hdp-claim-map.txt` maps each quoted claim to its URL. The sweeps are in `s58-hdp-d425-sweep-code.txt`, `s58-hdp-d427-sweep.txt`, `s58-hdp-d427-sweep2.txt`, `s58-hdp-d427-gitlog.txt` and `s58-d427-free.txt`.

## D-425: the largest file an import accepts   [governance-value] [planning]

**Mat's ruling (2026-11-08):** as recommended, 50 MB (`IMPORT_MAX_BYTES = 50_000_000`). Mat's words: "all recommendations accepted".

**Recommendation:** 50 MB (`IMPORT_MAX_BYTES = 50_000_000`), the starting point in the design and in 09 `:1009`. It takes any phone photo, any screenshot and a 12-megapixel photo saved as PNG (about 22 MB). A shot too big to read back whole can still be viewed: `max_edge` alone shrinks the whole image, and a region cuts out part of it, so the 15 MiB cap on reading back never strands an imported file. The new searches don't move the number. The model-facing limits they found (20 MB to 500 MB) cap what is sent to a model, and an import only reads a local file.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ 50 MB | — | — | design §6.6 (`:213`, `:217`); 09 `:1009` |
| ⚠️ 15 MiB, the same as `IMAGE_MAX_BYTES` | A byte-copied import reads back through `GET image` with no region or `max_edge`. An upright PNG made from a rotated JPEG can still pass 15 MiB (the round-1 plan review turned a 4,186,900 B JPEG into an 18,750,276 B PNG), so for those `max_edge` or a region stays the way past the 413 | Refuses a 12 MP photo saved as PNG (about 22 MB) and the larger edited PNGs (up to 20 MB), all of which a region view could serve | `routes/captures.py:48`; typical sizes below |
| ❌ No byte cap (do nothing): Pillow's pixel guard only | No refusal by size; one check fewer. ImageMagick, which agents use on this machine today, has no byte limit either | An image can have up to 89 million pixels at any byte size, so a 400 MB PNG is read into memory in full before the pixel check can refuse it. ImageMagick bounds that risk with memory, disk and time limits, which av-kit doesn't have. The design and 09 both ask for a cap | Pillow `MAX_IMAGE_PIXELS` 89,478,485 (`C:/Temp/av-kit/s58-plan-exif-probe.txt`); ImageMagick below |

**Precedent:**
- 09 `:1009` (Stage A, from design D-9): "within the import size cap (a tunable the plan fixes, starting from 50 MB)".
- Design §6.6 (`:217`) words the refusal "file is 212 MB; the import limit is 50 MB", which the plan keeps, reading the cap at call time (D-416, AC-129.8).
- No av-kit cap on incoming files exists. The tree's byte caps all bound what goes out or what is read as text: `IMAGE_MAX_BYTES` 15 MiB (`packages/api/src/avkit_api/routes/captures.py:48`), MCP's `IMAGE_MAX_BYTES` 7,800,000 B (`mcp-server/src/toolsets/capture.ts:12`, MEU-111) and `COMPILE_READ_MAX_BYTES` 20 MiB for transcript text (`packages/core/src/avkit_core/services/transcript.py:45`). All three stay as they are, and `OVERSIZE_HINT` names `max_edge` as the way past the first two.

**Research:** `pomera_web_search` (tavily): the design's searches, plus two in the refresh.
- Official, Anthropic: [Upload files to Claude](https://support.claude.com/en/articles/8241126-upload-files-to-claude) takes up to 500 MB per file in chat, and images up to 8000×8000 pixels.
- Official, Google: [Gemini image understanding](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/image-understanding) takes 7 MB per image inline and 30 MB from cloud storage, and the [Gemini API](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-api-new-file-limits) raised inline data from 20 MB to 100 MB in January 2026.
- Secondary, OpenAI: [AI file upload limits](https://otio.ai/blog/ai-file-upload-limits-research-workflows), quoting OpenAI's documentation as of 4 November 2026, says ChatGPT takes images up to 20 MB each.
- ImageMagick: limits are set by width, height, area, memory, disk and time, never by file bytes, and a stock `policy.xml` sets none ([discussion 6068](https://github.com/ImageMagick/ImageMagick/discussions/6068)). The sample [security policy](https://lovelace.cluster.earlham.edu/mounts/lovelace/software/imagemagick/ImageMagick-7.1.1-41/www/security-policy.html), a copy of the page shipped with 7.1.1-41, refuses an image over 8192 px wide or tall.
- Community: [hermes-agent issue 45780](https://github.com/NousResearch/hermes-agent/issues/45780) asked for 10 to 20 MB after a 9 MB PNG was refused, and the fix raised the cap to 25 MB. It also asked that the error show the file's size and the limit, which is what the plan's message does.
- Practice: [typical file sizes](https://imageresizerai.com/blog/image-file-size-explained) are 3 to 6 MB for a 12 MP phone JPEG, 200 KB to 2 MB for a screenshot, 5 to 20 MB for an edited PNG, and about 22 MB for a 4000×3000 photo saved as PNG.

**Obviousness test (§4):** fails test 4. It sets a new limit, and no av-kit limit on incoming files exists to follow, so it keeps the threshold sign-off whatever the sources say.

**Reversibility / risk:** two-way. It's one constant, and nothing stored depends on it. A larger cap only means a larger file is read into memory once, before the capture lock is taken for the copy.

**If you do not answer:** 50 MB stands, and the closeout records D-425 as unruled.

**What the recommendation would authorize:**
1. `IMPORT_MAX_BYTES = 50_000_000` in `packages/core/src/avkit_core/services/capture.py`, beside `SCAN_EXTENSIONS`.
2. The refusal `file is N MB; the import limit is L MB`, with L read from that constant when the call runs.
3. AC-129.8's over-cap case, which patches the constant to 1,000,000 so the test needs no large file.

It does not authorize: changing `IMAGE_MAX_BYTES`, the MCP cap or Pillow's pixel limit; a settings key for the cap; or any cap on a scanned file.

## D-426: the size a view comes back at   [governance-value] [planning]

**Mat's ruling (2026-11-08):** as recommended, `max_edge` 1568 by default, 64 to 2576 allowed, and a region enlarged at most 4×. Mat's words: "all recommendations accepted".

**Recommendation:** keep the design's numbers: `max_edge` 1568 by default, 64 to 2576 allowed, and a region enlarged at most 4×. The refresh corrects one premise. Current Claude models (4.7 and later) are on the high-resolution tier, which keeps up to 2576 px on the long edge and 4,784 visual tokens. 1568 px and 1,568 tokens is the standard tier, for the other models. So on a current model the 1568 default sends less than the model could keep. It is a cost choice, not a "nothing wasted" one, and it is still the right default:
- A default view costs at most 3,136 visual tokens (1568×1568) on a high-resolution model, and 1,792 for a 16:9 view.
- An agent that needs more passes `max_edge: 2576`, and MCP `image`'s description says so (AC-128.24).
- A region view gets detail by cutting out native pixels, not by enlarging them. In the newest study, native pixels were where a Claude model gained most.

The 4× cap stops a 30×20 region coming back as a 1568-pixel blur that costs tokens and shows nothing new. The reading probe the design asked for, a model reading small text at each size, still hasn't run, so these numbers rest on the vision documents and two papers.

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ 1568 default, 64 to 2576, at most 4× | — | — | design §6.1 (`:153`, `:159`), R-1; 09 `:990`, `:993` |
| ⚠️ A 2576 default, the same range and cap | A whole shot or a large region reaches a current model with up to 2.7 times the pixels it gets at 1568, without a second call | Every default view costs up to 4,784 tokens instead of 1,792 to 3,136. A standard-tier model shrinks it back to 1568 anyway. A mid-size region is enlarged further with no new pixels: 700×400 comes back at 2576×1472 rather than 1568×896 | [Claude vision](https://platform.claude.com/docs/en/build-with-claude/vision) tier table |
| ⚠️ The measured study's limits: a 1024 default and at most 2× | The only zoom limits a published study has measured with current models (arXiv 2610.09313). Fewer tokens per view: a 1024×576 view is 777 | Below what either Claude tier keeps, so a whole 4K shot loses detail a model would have used, and a 100×50 region comes back at 200×100. In the same study enlarging helped GPT-5.6 (+0.11 F1), so a lower cap gives up a gain some models show | [arXiv 2610.09313](https://doi.org/10.48550/arxiv.2610.09313) |
| ❌ Scale only when the caller passes `max_edge` (do nothing) | No resampling unless asked. The bytes are the region's own pixels, which the study found Claude used best | A small region comes back small, which defeats "looking closer", and a large region of a 4K shot comes back larger than the model keeps, so the model resizes it anyway. Every agent has to pick a size itself | R-5 (arXiv 2502.17422); arXiv 2610.09313 |

**Precedent:**
- 09 `:990` ("`max_edge` (64 to 2576)") and `:993` ("fitted inside `max_edge` (default 1568), upscaled at most 4×"), written in Stage A from design D-5.
- Design §6.1 (`:153`): "The cap and the filter are tunables to confirm with a reading probe at planning". That probe is the one not run.
- Design §6.1 (`:159`): "High-resolution models can pass `max_edge: 2576`. The description says so." The plan puts that sentence in MCP `image`'s description (AC-128.24).
- No size limit on a returned view exists in the tree today: `GET image` returns the stored file as it is.

**Research:** `pomera_web_search` (tavily, exa): the design's §5, plus two searches in the refresh.
- Official: [Claude vision](https://platform.claude.com/docs/en/build-with-claude/vision) puts "Claude 4.7 and later models" on the high-resolution tier (2,576 px, 4,784 visual tokens) and "all other models" on the standard tier (1,568 px, 1,568 tokens). Tokens are ⌈width/28⌉×⌈height/28⌉. A 3840×2160 shot becomes 1456×819 (1,560 tokens) on the standard tier and 2576×1449 (4,784) on the high-resolution tier. The model returns coordinates in the image it saw ([vision coordinates](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates)), which is why each view reports its frame.
- Community: [Claude reads screenshots at 2576px now](https://dev.to/gabrielanhaia/claude-reads-screenshots-at-2576px-now-the-same-png-can-cost-3x-the-tokens-4cp4) works through the same page: a large PNG can cost about three times the tokens on a 4.7 model, while a small image costs the same.
- Paper: [arXiv 2610.09313](https://doi.org/10.48550/arxiv.2610.09313), "Why VLMs Miss Small Objects, and When Zooming In Is Safe" (October 2026). Its zoom tool cut a rectangle from the native drawing, long side at most 1,024 px, enlarged at most 2×. Enlarging a crop, which adds no pixels, helped GPT-5.6 (+0.11 F1) but gave Claude Sonnet 5.5 no significant gain (+0.06, with an interval that crosses zero). Claude gained most from native pixels. Two of four agents counted about right but failed to convert positions from the crop back to the overview. The plan's frame headers and MCP frame item give the agent that conversion (`source_x = region.x + x / scale`).
- Paper: [arXiv 2502.17422](https://doi.org/10.48550/arxiv.2502.17422) found that a model reading small details does better from a zoomed crop than from the whole image (design R-5).
- No source gives a best enlargement cap for a Claude model. The 4× is the design's judgement, and the only measured cap is the study's 2×.

**Obviousness test (§4):** fails test 4. These are new limits on what every view costs and shows, and the probe that would have confirmed them wasn't run.

**Reversibility / risk:** two-way. These are four constants (`REGION_MAX_EDGE_DEFAULT`, `REGION_MAX_EDGE_MIN`, `REGION_MAX_EDGE_MAX`, `REGION_UPSCALE_MAX`), and nothing is stored. Changing the range later changes the MCP schema's bounds and the OpenAPI document, so the cost is one regeneration.

**If you do not answer:** the design's numbers stand, and the closeout records D-426 as unruled.

**What the recommendation would authorize:**
1. The four constants in `packages/core/src/avkit_core/domain/capture.py` at 1568, 64, 2576 and 4.
2. The same bounds on the route's `max_edge` query parameter, MCP `image`'s `max_edge`, and the sentence naming 2576 for high-resolution models.
3. AC-128.5, AC-128.12, AC-128.14, AC-128.23 and AC-128.24 as the plan words them.

It does not authorize: running the reading probe, which sends images to a model; a settings key for the default; or changing the MCP payload cap.

## D-427: commit the crop docs before execution   [two-way] [planning]

**Mat's ruling (2026-11-08):** as recommended, one exact-scope docs commit of the seven files below now, with no push. Mat's words: "all recommendations accepted". The push, starting execution and waiving the queue each still need Mat's words. Committed as `75617379f63c0885024b2c9f0dd9fc72de854b8b`. Mat directed the push separately on 2026-11-08 ("push and wait we will complete 56 and 57 first than resume executino for 58 here"), and it reached `origin/main`.

**Recommendation:** commit Stage A's seven files now, in one exact-scope docs commit, without this plan folder, without the review handoff and without a push. They register MEU-128 to MEU-132 and place them in Sessions 58 to 61, and no outcome of this plan's review changes them.
- Row 0 gets a clean baseline, and the H2-5 commit holds only this session's work.
- It fences the files off from a parallel session. `docs/execution/plans/2026-11-08-light-accent-contrast/` is in the tree, untracked, with a `matrix-rebaseline.py`, and the matrix is one of the seven.
- Each file's SHA-256 is checked against the table below just before the commit, so nothing that session writes goes into this commit, and anything it writes afterwards shows as its own diff.

The plan runs under every option: row 0 records whatever is still dirty.

| Path | State | SHA-256 at the refresh |
|---|---|---|
| `.agent/context/meu-registry.md` | modified | `d67bf0dfb586d45682197528643331fd38696949a5c9ce354e754225838f3f86` |
| `.agent/context/meu-status.yaml` | modified; the diff adds the MEU-128 to MEU-132 records and, for them, updates phase 9's `last_updated` and note and the P2 summary band's range. No other MEU changes | `d6310b3930d1092972b50b2418f0678241d04addbcf9b00fe33edf7b1cccdc12` |
| `docs/BUILD_PLAN.md` | modified | `7270efda173d369e8efd2f3968e0b85612c99ed36ca67519837175d4f1d5afe4` |
| `docs/build-plan/09-screenshot-capture.md` | modified | `f9ff0cc7b67835e2f862db894d8eed6f6a182b74025263bdbd6ba71398965019` |
| `docs/build-plan/build-priority-matrix.md` | modified | `d1bf261e87cc4f7ee0f1bd545cdc79b6fed4fb6a3c7214057ed03eff2050afa8` |
| `.agent/context/grouping/2026-11-08-capture-crop-session-grouping.md` | new | `4e8915848e1bc8481c5efae0a84cb5bb46021306140ef2179b9c31b95a532943` |
| `_inspiration/capture-crop/design.md` | new | `e9b7043395633c349994fc30953fbf594d9c0357facb90e78b9764f401dd2c63` |

**Why not the others**

| Option | Pros (vs. recommendation) | Cons (vs. recommendation) | Sources |
|---|---|---|---|
| ✅ Commit now: the seven files, exact scope, no push | — | — | D-276 (`docs/execution/plans/2026-11-04-rc2-fetch-uninstall/implementation-plan.md:387`), `83229ea`; `.agent/skills/git-workflow/SKILL.md:59` |
| ⚠️ The same commit after the plan is approved, just before row 0 | One stop for Mat instead of two: the commit and the start of execution are approved together | The seven files stay exposed to the parallel session for the rest of the review. If one changes, the SHA-256 check refuses, and the file has to be read again before anything is committed | same |
| ❌ Don't commit (do nothing) | Nothing to approve now, and the plan already copes: row 0 writes the files into `baseline-dirty.txt`, rows 6 and H1-2 check their SHA-256 before writing on top of them, and at H2-5 Mat decides whether they go in the session's commit or in one of their own | The session's commit mixes the registration of five MEUs with the code of two, unless it's split at H2-5. Another session's edit to one of the files makes row 6 or H1-2 refuse partway through execution rather than now | `implementation-plan.md` §User Review Required; `baseline.ps1` |

**Precedent:**
- D-276 (Session 49's plan, `:387`), Human-approved on 2026-11-05: "one exact-scope commit of this session's triage and planning records, without this plan folder and without a push. The push is a separate approval". It was committed as `83229ea`.
- `.agent/skills/git-workflow/SKILL.md:59`: the exact-scope signed commit mode is for a dirty worktree, and `-NoPush` is mandatory in it.
- `AGENTS.md:102`: "When another session's uncommitted work is in the tree, leave its files alone and commit only your own paths".

**Research:** `pomera_web_search` (tavily, exa).
- Practice: [Atomic commits](https://gitbybit.com/gitopedia/best-practices/atomic-commits) commits unrelated changes separately, so each commit is a logical unit that is easy to understand and to revert. [Git commit best practices](https://stackoverflow.com/questions/6543913/git-commit-best-practices) says a commit should hold one change only.
- Agents: [Git worktrees for parallel AI agents](https://www.augmentcode.com/guides/git-worktrees-parallel-ai-agent-execution) says parallel agents' uncommitted edits collide in a shared tree, and each run should be diffed against a known-good start. This repository forbids worktrees, so a commit is the way to get that start.

**Obviousness test (§4):** a commit is on the hard-gate list (AGENTS.md §Commits), so Mat rules it whatever else holds. The class follows D-276: the choice is two-way while nothing is pushed.

**Reversibility / risk:** two-way until a push: an unpushed commit can be undone locally, on Mat's word. The push stays a separate approval, because the repository is public and a pushed commit can't be taken back.

**If you do not answer:** nothing is committed. Unlike D-425 and D-426, an unanswered D-427 doesn't carry its recommendation, because a commit needs Mat's words (`GUARDRAILS.md` SIGN 3 (a)). The files stay as the do-nothing row describes, and the closeout records D-427 as unruled.

**What the recommendation would authorize:**
1. Checking `git status`, each of the seven files' SHA-256 against the table above, and that `meu-status.yaml`'s diff holds only the MEU-128 to MEU-132 records and those three fields (phase 9's `last_updated` and note, and the P2 band's range). If anything differs, stop and tell Mat, and commit nothing.
2. One commit of exactly those seven paths in the exact-scope signed commit mode (`.agent/skills/git-workflow/SKILL.md:59`) with `-NoPush`. The author is `MatBanik <219344396+matbanik@users.noreply.github.com>`, and the message has no AI attribution trailer. Subject: `docs(capture): record the crop design, MEU-128 to MEU-132 and their session grouping`.
3. Recording the commit's hash in the review handoff and the closeout.

It does not authorize: a push; committing this plan folder, the review handoff or any other session's file (`2026-11-08-light-accent-contrast/` included); starting execution; or waiving the queue (`baseline.ps1 -QueueWaived`).
