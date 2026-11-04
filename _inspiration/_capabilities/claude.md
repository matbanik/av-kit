---
provider: claude
verified: 2026-10-17
source: pomera/tavily+exa
confidence: high
---

# Claude — Research Mode Capability Snapshot

## Model

`Claude Fable 5.1` — released **2026-09-01**, API id `claude-fable-5-1`, "available to Pro, Max,
Team, and Enterprise users" in the Claude apps [anthropic.com/claude/fable, read 2026-10-17].
Anthropic calls it "our most capable generally available model… best for ambitious, long-running,
asynchronous work" and lists "deep research and analysis" under enterprise workflows.

`Claude Opus 5.5` (2026-09-22) remains the cost-balanced alternative: "performs at the level of
Claude Fable 5.1 on most work" [anthropic.com/claude-opus-5-5]. Secondary guides say Anthropic
suggests Opus 5.5 first for most jobs and Fable 5.1 for multi-day research [coursiv.io, read
2026-10-17]. For this run the human requested Fable 5.1.

- The Claude 5.x line: Fable 5.1 (2026-09-01), Opus 5.5 (2026-09-22), Sonnet 5.5 (2026-09-28),
  Haiku 5.5 (2026-10-07).
- Fable 5.1 safeguards route cybersecurity queries to Opus 4.8 and biology queries to Opus 5
  (support.claude.com/en/articles/15363606). Irrelevant to marketing or product research topics;
  relevant if a prompt touches exploits or bio.
- Vendor prompting facts still hold: adaptive thinking is always on; Effort is the dial; "think
  carefully" lines are redundant; a `reasoning_extraction` refusal category exists; 1M context on
  Max, 200K on Pro; Fable 5.1 requires 30-day data retention.

## Portal Affordances

- **Research** mode (Pro and above): runs "five or more tool calls" per query; it can be combined
  with extended thinking; it reaches the web and, when connected, Gmail / Calendar / Google Docs
  [support.claude.com, Research article]. Architecture: orchestrator plus 3–5 parallel subagents
  and a separate CitationAgent [anthropic.com/engineering/multi-agent-research-system].
- **Model picker** (Fable 5.1 and Opus 5.5 by name) and an **Effort** selector
  (Low / Medium / High / Max).
- **Thinking cannot be switched off in the app** for the 5.x models — the user raises effort
  instead of toggling thinking [swapbiswas.com, as of 2026-10-03].
- **File upload**, Projects, Artifacts, code execution; MCP connectors.

## Constraints

- Research requires Pro or above; per-tier Research run counts are **unpublished (unknown)**.
- Accounts on the "new Claude experience" show **no separate web-search toggle**; Research mode
  is the web-research route.
- Research costs on the order of 15× a normal chat in tokens; Fable 5.1 is priced at 5× Opus 5.5
  per token, so a Fable Research run draws down a plan's limits fastest.
- Multi-agent research suits independent branches; heavily chained questions do poorly.
- Do not ask for "hidden reasoning" (`reasoning_extraction` refusal); ask for explicit argument.

## Delta Since 2026-10-12

- CHANGED: requested model for D3 prompts is **Fable 5.1** (human request 2026-10-17); the vendor
  page confirms app availability on Pro, Max, Team and Enterprise. Opus 5.5 stays the default pick
  when the human does not name a model.
- ADDED: Fable 5.1 safeguard fallback (cyber → Opus 4.8, bio → Opus 5) recorded as a prompt
  caveat.
- CONFIRMED (unchanged): Research = 5+ tool calls, combinable with extended thinking, web plus
  connected Google Workspace; multi-agent architecture; Effort is the only dial.
- REMOVED: none.

## Prompt Implications

- `## Portal Setup`: pick **Claude Fable 5.1** by name; Research **on**; Effort **Max** (High if
  Max is not offered). Thinking is always on; Effort is the control.
- Write the objective as independent branches so the 3–5 subagents can split it.
- Keep D3's slant: strategy, adjudication, ERRC grid, strongest counter-argument, explicit
  argument in the report.
- Uploaded repo files are Claude's distinctive advantage — name each attachment in the prompt.

## Delta Check 2026-10-29 (av-kit, R1 only)

Copied from `P:/zorivest/_inspiration/_capabilities/claude.md`; `verified:` left at 2026-10-17
(inside the 14-day TTL). R1 delta queries found nothing new: Fable 5.1 and Opus 5.5 are still in
the app picker, and Research is still Pro and above. The human named no model for this run, so D3
uses the default, Opus 5.5. No full recon run.
