---
provider: gemini
verified: 2026-10-17
source: pomera/tavily+exa
confidence: mixed
---

# Gemini — Deep Research Capability Snapshot

> ⚠️ **Portal ≠ API.** Deep Research and Deep Research Max on Gemini 3.1 Pro (blog.google,
> 2026-04-21; ids `deep-research-preview-04-2026`, `deep-research-max-preview-04-2026`; MCP,
> native charts, collaborative planning; 1M input / 65,536 output tokens) are **Gemini API /
> Interactions API** features. Never assert them as consumer-portal capabilities.

## Model

`Gemini 4 Argon` is in the Gemini app for Google AI Pro and Ultra subscribers since **2026-10-13**
("Try it starting today in the Gemini app and AI Mode in Search if you're a Google AI Ultra or Pro
subscriber") [blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-argon,
2026-10-13, read 2026-10-17]. Announced 2026-09-30 as the first Gemini with a codename instead of
a Pro/Flash tier; 1M unified input-output token limit [blog.google/.../gemini-4-argon, 2026-09-30].

**Which model runs portal Deep Research when Argon is selected: unknown.** The consumer Deep
Research page still says only "With the Gemini 3 model, Deep Research is even better"
[gemini.google/overview/deep-research, read 2026-10-17]. No vendor page links Argon to the app's
Deep Research agent. Deep Research is included in Google AI Pro ($19.99/mo); Deep Research Max
sits under AI Ultra [felloai.com, secondary, read 2026-10-17].

**Prompt-writer consequence:** tell the human to select **Gemini 4 Argon** in the model picker
(AI Pro or Ultra plan), then choose Deep Research; ask the report to state the model label shown.
Name Argon as the *requested* model, never as the verified Deep Research engine.

## Portal Affordances

- **Deep Research** in the Gemini app: proposes a **research plan the human edits** before launch;
  browses many sites; cited report.
- **Grounding in Gmail / Drive / Chat** (opt-in), **file upload**, **Canvas** transforms,
  **Audio Overview**, export to Docs [gemini.google/overview/deep-research].
- **Custom skills and scheduled tasks** are shown with Argon in the Gemini app (proposal-deck
  demo) [blog.google, 2026-10-13] — not needed for research prompts.
- Google Search grounding is the distinctive strength — trend, search-intent and community
  signals (D2's slant).

## Constraints

- Model behind portal Deep Research: **unknown**, even with Argon selected.
- Argon in the app needs a paid plan (AI Pro or Ultra). Free plan: about 5 Deep Research runs a
  month on 3 Flash [suprmind.ai, secondary, as of 2026-05-09].
- API-only features (MCP, native charts, Max agent, collaborative planning) must not be requested.
- Gemini prompting guidance: critical instructions first, long context *before* the final
  question, define ambiguous terms, explicit verbosity control. Argon "follows style instructions
  better" and "answers more directly with less hedging" [blog.google, 2026-10-13].

## Delta Since 2026-10-12

- ADDED: Gemini 4 Argon opened in the Gemini app for AI Pro and Ultra subscribers on 2026-10-13
  (vendor-confirmed). The 2026-10-12 "Argon / Flash / Omni / Gemma" line mention is now resolved
  to a selectable model.
- CHANGED: requested model for D2 prompts moves from "3.8 Flash if offered" to "Gemini 4 Argon"
  (human request 2026-10-17).
- CONFIRMED (unchanged): the portal Deep Research page still names only "Gemini 3"; API-only
  Deep Research Max stays API-only.
- REMOVED: none.

## Prompt Implications

- Portal header: choose **Gemini 4 Argon** in the picker, then Deep Research; edit the plan so
  every question survives; record the label shown.
- Put the long Context block before the questions.
- D2 slant: adoption velocity, People-Also-Ask style questions, community sentiment, recency;
  signal-strength rating per finding; reconcile conflicts instead of averaging.
- Never request MCP, charts or other API-only features.

## Delta Check 2026-10-29 (av-kit, R1 only)

Copied from `P:/zorivest/_inspiration/_capabilities/gemini.md`; `verified:` left at 2026-10-17
(inside the 14-day TTL). R1 delta queries found no contradiction. tech-insider.org (secondary,
October 2026) says portal Deep Research is still on Gemini 3.1 Pro, which matches "model behind
portal Deep Research: unknown". No full recon run.
