# Session 64 description eval run (task rows E-1 to E-4, under D-608 A or B)

The coordinator follows this file after Green (row 3), before row 6. Nothing here runs
under D-608 C. Each run's prompt is one block under §Prompts, with `{{DESCRIBE}}`, `{{ROOT}}` and
`{{MEDIA}}` replaced. Under A the six runs are `real-t1`, `real-t2`, `real-t3`, `meta-t1`,
`meta-t2`, `meta-t3`; under B the three `real-*` runs.

Paths:

- `BASE` = `C:/Temp/av-kit/s64/eval`;
- `MEDIA` = `BASE/media`;
- `KEY` = `C:/Temp/av-kit/s64/eval-key` (the answer key, outside `BASE`; no prompt names it);
- each run's `ROOT` = `BASE/<run>/root`.

## Coordinator steps

Run these from the repository root, with `PYTHONIOENCODING=utf-8` set and `ELECTRON_RUN_AS_NODE`
cleared:

1. **Seed.** Run `uv run python docs/execution/plans/2026-11-11-capture-export-copy/eval-seed.py C:/Temp/av-kit/s64/eval/media C:/Temp/av-kit/s64/eval-key > C:/Temp/av-kit/s64-E1-seed.txt 2>&1`.
   - It refuses a folder that already holds files.
   - It exits 1 when one of its own checks fails. That is S6.
2. **Build.** Run `npm --prefix mcp-server run build`, so that `mcp-server/dist/index.js` is this work tree's server.
3. **Describe.** From `mcp-server`, run `npx tsx ../docs/execution/plans/2026-11-11-capture-export-copy/eval-harness.ts C:/Temp/av-kit/s64/eval/describe/root describe > C:/Temp/av-kit/s64-E1-describe.txt 2>&1`.
   - The `real` surface is the receipt's text above the line `<!-- CUT: the real surface ends above this line -->`. That is what Claude Code shows a model: the server instructions, and each tool's description and flattened input schema.
   - The `meta` surface is the whole receipt with the CUT line deleted. It adds each tool's `_meta.action_descriptions`.
4. **Each run.** For each run, in the order above:
   1. Seed the run's root. From `mcp-server`, run `npx tsx ../docs/execution/plans/2026-11-11-capture-export-copy/eval-harness.ts <ROOT> seed > C:/Temp/av-kit/s64-E2-<run>-seed.txt 2>&1`.
      - For a `t3` run, put `C:/Temp/av-kit/s64/eval/media/dashboard-4k.png` after `seed`. `seed` copies it into the run's inbox and writes its shot id to `ROOT/seed/source-id.txt`.
   2. Build the prompt from §Prompts for the run's task, and save it to `C:/Temp/av-kit/s64-eval-<run>-prompt.md`.
   3. Dispatch one subagent with that prompt alone: `subagent_type: general-purpose`, with `model: haiku` under A and under B.
   4. Save its final message, unedited, to `C:/Temp/av-kit/s64-eval-<run>-report.txt`.
   5. Each run starts from a fresh agent. No run sees another run's prompt, root or report.
5. **Check.** Run `uv run python docs/execution/plans/2026-11-11-capture-export-copy/eval-check.py > C:/Temp/av-kit/s64-E4-check.txt 2>&1`.
   - Exit 1 is S13. Record the receipts, and brief Mat with the failing run's prompt, ledger and report.
   - Don't change any description text without Mat's words.

## What each run may do

- The harness allowlist is `avkit_capture` list, get, image, frames, sheet, export and crop, and `avkit_convert` probe.
- Any other action is refused without a call, and recorded in the ledger.
- An image result is saved under `ROOT/views/`. The agent may open those files with the Read tool, which shows it the picture. It may open no other file.
- No run uploads anything or reads from a network. The videos are read in place.

## Prompts

The shared opening is placed before each task block:

```text
You are testing a tool as an outside agent would use it. Use only what this message gives you.
Don't read files in the repository, search it, or run any command other than the one below. The
only files you may open are the images the harness saves for you.

The tools are avkit_capture and avkit_convert on a local av-kit server. This is everything their
server advertises about them:

{{DESCRIBE}}

You call the tools through a test harness. Run this from P:/av-kit/mcp-server with the Bash tool,
one call per command, with the tool's name and its arguments as one JSON object in single quotes:

  npx tsx ../docs/execution/plans/2026-11-11-capture-export-copy/eval-harness.ts {{ROOT}} call <tool> '<json>'

For example: ... eval-harness.ts {{ROOT}} call avkit_capture '{"action":"list"}'

The harness prints the tool's result. When the result is an image, it prints the path where it
saved the image; open that path with the Read tool to see it. The harness doesn't run remove,
flatten, revert, annotate or capture in this test.
```

### t1: the slide at a transcript time

```text
Task: {{MEDIA}}/meeting.mp4 is a one-hour recorded meeting. This is its transcript:

{{TRANSCRIPT}}

Which slide title was on screen when the speaker at 00:40:09 spoke? When you are done, reply
with the title on a line of its own, as `slide: <title>`, and one or two sentences on anything
in the tools' descriptions that was unclear.
```

`{{TRANSCRIPT}}` is the text of `MEDIA/meeting-transcript.txt`, pasted as it is.

### t2: a car's arrival in a long clip

```text
Task: {{MEDIA}}/driveway.mp4 is a two-hour clip from a camera facing an empty driveway. At some
point a car drives in and stays parked. Find the second the car first appears, to within five
seconds. When you are done, reply with that time on a line of its own, as `arrival: <seconds>`,
and one or two sentences on anything in the tools' descriptions that was unclear.
```

### t3: shrink a 4K screenshot

```text
Task: the test inbox holds a 3840x2160 screenshot named dashboard-4k. Make a JPEG copy of it
that is under 500 KB and at least 1280 px on its long edge, without changing dashboard-4k.
When you are done, reply with the new shot's id on a line of its own, as `new shot: <id>`, and
one or two sentences on anything in the tools' descriptions that was unclear.
```
