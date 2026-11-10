# Session 60 D-494 run (task row 7, under D-521 A or B)

The coordinator follows this file in row 7. The agent's prompt is the block under §Prompt, with
`{{DESCRIBE}}` replaced. Nothing here runs under D-521 C.

## Coordinator steps

Run from the repository root, with `PYTHONIOENCODING=utf-8` and `ELECTRON_RUN_AS_NODE` cleared:

1. `uv run python docs/execution/plans/2026-11-10-gui-capture-crop-tool/d494-seed.py > C:/Temp/av-kit/s60-d494-seed.txt 2>&1`. It refuses a root that already holds files.
2. `npm --prefix mcp-server run build`, so `mcp-server/dist/index.js` is this work tree's server.
3. From `mcp-server`: `npx tsx ../docs/execution/plans/2026-11-10-gui-capture-crop-tool/d494-harness.ts seed > C:/Temp/av-kit/s60-d494-harness-seed.txt 2>&1`, then `... d494-harness.ts describe > C:/Temp/av-kit/s60-d494-describe.txt 2>&1`. `seed` writes chart-source's shot id to `seed/source-id.txt`, which the check binds the measured crop to.
4. Build the prompt: replace `{{DESCRIBE}}` with the describe receipt's text **above** the line `## Not shown to the agent: _meta.action_descriptions.crop`. That cut is what Claude Code shows a model: the server instructions, the tool description and the flattened input schema. Save the prompt to `C:/Temp/av-kit/s60-d494-prompt.md`.
5. Dispatch one subagent (`subagent_type: general-purpose`, `model: haiku` under A, `model: sonnet` under B) with that prompt alone. Save its final message, unedited, to `C:/Temp/av-kit/s60-d494-report.txt`.
6. `uv run python docs/execution/plans/2026-11-10-gui-capture-crop-tool/d494-check.py > C:/Temp/av-kit/s60-d494-check.txt 2>&1`. Exit 1 is S13: record the receipts and brief Mat, and don't change the description.

## Prompt

```text
You are testing a tool as an outside agent would use it. Use only what this message gives you.
Don't read files in the repository, search it, or run any command other than the one below.

The tool is avkit_capture on a local av-kit server. This is everything its server advertises
about it:

{{DESCRIBE}}

You call the tool through a test harness. Run this from P:/av-kit/mcp-server with the Bash
tool, one call per command, with the tool's arguments as one JSON object in single quotes:

  npx tsx ../docs/execution/plans/2026-11-10-gui-capture-crop-tool/d494-harness.ts call '<json>'

For example: ... d494-harness.ts call '{"action":"list"}'

The harness prints the tool's result. It doesn't run remove, flatten, revert or image in this
test, so you can't look at the picture. Work from the numbers you are given.

Task: in the test inbox there is a chart image named chart-source. It is 1200 px wide and
800 px tall. Its top-right panel spans 640 px to 1160 px across and 120 px to 440 px down.
Crop that panel into a new shot named chart. Don't change chart-source.

When you are done, reply with the new shot's id on a line of its own, as `new shot: <id>`, and
one or two sentences on anything in the tool's description that was unclear.
```
