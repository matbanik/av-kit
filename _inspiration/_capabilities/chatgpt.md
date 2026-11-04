---
provider: chatgpt
verified: 2026-10-17
source: pomera/tavily+exa
confidence: mixed
---

# ChatGPT — Deep Research Capability Snapshot

## Model

`latest model (vendor-abstracted)` for Deep Research. The Help Center wording "Deep research is
powered by the latest models… you can choose a legacy model" was last read 2026-10-12; on
2026-10-17 both help.openai.com and openai.com returned HTTP 403 to Pomera, so the model mapping
rests on dated articles that name OpenAI pages as their source:

- Since **2026-10-07** the Chat tab runs **GPT-6 Sol** for Plus, Pro, Business and Enterprise and
  **GPT-6 Luna** for Free and Go ("GPT-6 and Intelligent UI for everyone", openai.com/index/gpt-6-for-everyone,
  2026-10-07; via cellcog.ai and founderz.com, both dated October 2026, and Wikipedia "GPT-6").
- **GPT-6 Astra** (public 2026-09-04) "is still OpenAI's most capable model, used by the Pro
  reasoning option, Dots and the Ultrafast tier" [founderz.com, citing the ChatGPT release notes,
  read 2026-10-17]. Pro, Business and Enterprise also get GPT-6 Astra Pro; on Enterprise an admin
  must switch Astra on [thinkfacility.com, read 2026-10-17]. The 2026-10-12 snapshot recorded the
  picker label as "GPT-6 Pro".
- GPT-6.1 Sol (2026-09-29) powers ChatGPT Work and Codex, not the Chat tab [founderz.com].
- No source confirms which model runs behind Deep Research. "Astra runs Deep Research" stays
  **unverified**.

**Prompt-writer consequence:** the human requested GPT-6 Astra for this run. Tell them to select
the Pro reasoning option ("GPT-6 Pro" / GPT-6 Astra) where the picker shows it, pick the highest
reasoning tier, and leave Deep Research on its default model; ask the report to state the model
label and tier shown. Name Astra only as the *requested* model.

## Portal Affordances

Confirmed from OpenAI pages on 2026-10-12 (not re-readable on 2026-10-17, 403):

- **Entry:** `+` → **Deep research** in the composer.
- **Clarifying questions + editable research plan** before execution; real-time progress; the run
  can be interrupted and redirected [help.openai.com/en/articles/10500283].
- **Site scoping:** restrict to listed sites, or *prioritize* them while keeping full-web search.
- **File upload** into the research context.
- **Apps / MCP connectors:** read actions only [openai.com/index/introducing-deep-research].
- **Output:** cited report; "30-minute reports" [chatgpt.com/features/deep-research]; export as
  Markdown / Word / PDF.
- **Intelligent UI** (2026-10-07): answers can include charts and interactive widgets — a chat
  feature, not confirmed inside Deep Research reports.

## Constraints

- Usage: Limited (Free/Go) · Expanded (Plus) · Maximum (Pro), shown by an in-product counter. On
  2026-09-30 OpenAI halved ChatGPT Pro 200 usage, dropped the five-hour limit and added a $500
  plan [thinkfacility.com, secondary]. The in-product counter remains the only authority.
- Connectors are read-only.
- Runtime is minutes to ~30 minutes; the plan editor is the last cheap intervention point.
- Pomera cannot read openai.com or help.openai.com (403) — re-verify vendor wording in a browser
  when a prompt depends on it.

## Delta Since 2026-10-12

- ADDED: Chat-tab model split by plan since 2026-10-07 (Sol paid, Luna free); GPT-6 Instant with
  Intelligent UI.
- ADDED: Astra is the Pro reasoning option (secondary, names the vendor release notes).
- ADDED: Pro-plan usage halved 2026-09-30; $500 plan.
- CHANGED: requested model for D1 prompts is GPT-6 Astra (human request 2026-10-17).
- CONFIRMED (unchanged): Deep Research model still not vendor-named; any-MCP connectors; site
  prioritization; file upload.
- REMOVED: none.

## Prompt Implications

- Portal header: select GPT-6 Astra / "GPT-6 Pro" where offered; highest reasoning tier; default
  Deep Research model; record tier + label.
- Pre-empt the clarifying questions in the prompt body; make the question list survive plan edits.
- Use *prioritize* sites (not restrict) — D1's slant is breadth, so the open web must stay in.
- Ask for comparison tables with user counts, ratings and dated community quotes.

## Delta Check 2026-10-29 (av-kit, R1 only)

Copied from `P:/zorivest/_inspiration/_capabilities/chatgpt.md`; `verified:` left at 2026-10-17
(inside the 14-day TTL). R1 delta queries found no contradiction. tech-insider.org (secondary,
October 2026) says Deep Research runs on GPT-6 Astra; still not vendor-confirmed, so the snapshot
is unchanged. No full recon run.
