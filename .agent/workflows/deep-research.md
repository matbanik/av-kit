---
description: "Deep research workflow — generate custom-tailored prompts for 3 AI providers"
---

# Deep Research Workflow

> **Adapted from**: `p:\matbanik.info\.agent\workflows\01b-deep-research.md`
> **Purpose**: Take any {topic} or {question}, research each provider's current capabilities, and generate 3 custom-tailored deep research prompts.

---

## Overview

Generate and run 3 custom-tailored deep research prompts — one per AI provider. Each prompt is designed to exploit that provider's specific web search strengths. All 3 run in parallel on the provider's native platform.

| Prompt | Platform | Native Mode | Focus |
|--------|----------|-------------|-------|
| D1 | ChatGPT | Deep Research | Breadth — multi-source crawling, quantitative data |
| D2 | Gemini | Deep Research | Trends — Google Search grounding, community signals |
| D3 | Claude | Research (extended thinking + web) | Strategy — analytical synthesis, pattern recognition |

---

## Step 0: Receive Topic

The user directs what needs research. Examples:
- "Research SABR bypass strategies in yt-dlp 2026"
- "Research Kokoro model quantization options and performance"
- "Research Electron + Python backend bundling approaches"

**Output**: `{topic}` string and `{topic-slug}` for file naming.

---

## Step 1: Research Provider Capabilities

**Before generating prompts**, web search each provider's current deep research capabilities:

```
search: "ChatGPT deep research strengths capabilities {YEAR} web browsing"
search: "Gemini deep research strengths capabilities {YEAR} web search grounding"
search: "Claude deep research web search extended thinking capabilities {YEAR}"
```

Use the results to build a current strengths table:

| Provider | Typical Strengths | Tailor Prompt For |
|----------|------------------|-------------------|
| **ChatGPT** | Multi-platform crawling breadth, iterative agent research plans, full-page content reading, quantitative aggregation | Counting, quoting, and quantifying across many forums |
| **Gemini** | Google Search grounding, People Also Ask data, autocomplete patterns, real-time search index access | What people actually type into Google, search intent gaps |
| **Claude** | Extended thinking, multi-branch reasoning, search ↔ think interleaving, structural analysis | Strategic synthesis, narrative framing, pattern recognition |

> **Note**: Provider capabilities evolve. Always web search current strengths before generating prompts — do not rely on cached assumptions.

---

## Step 2: Generate Prompt Files

Using the {topic} and provider strength research, generate 3 custom-tailored prompts:

1. **D1 prompt** → Save to `_inspiration/research/{topic-slug}/prompt-d1-chatgpt.md`
2. **D2 prompt** → Save to `_inspiration/research/{topic-slug}/prompt-d2-gemini.md`
3. **D3 prompt** → Save to `_inspiration/research/{topic-slug}/prompt-d3-claude.md`

Each prompt must:
- Be tailored to the provider's current web search strengths
- Include the {topic} context and specific questions to answer
- Follow citation rules: source URLs inline, model attribution tags `[GPT]`, `[Gemini]`, `[Claude]`
- End with a `## Sources` section listing all URLs used
- Be ready to paste directly into the provider's native UI

Use prompt templates in `.agent/workflows/prompts/deep-research/` as starting points.

---

## Step 3: Execute on Native Platforms

### D1: ChatGPT
**Platform**: [chatgpt.com](https://chatgpt.com) → Deep Research mode
1. Paste `prompt-d1-chatgpt.md` into ChatGPT Deep Research
2. Review the research plan before execution
3. Let it run to completion (10-30 minutes)
4. Save output to `_inspiration/research/{topic-slug}/chatgpt-d1.md`

### D2: Gemini
**Platform**: [gemini.google.com](https://gemini.google.com) → Deep Research mode
1. Paste `prompt-d2-gemini.md` into Gemini Deep Research
2. Review the research plan
3. Let it run to completion (5-15 minutes)
4. Save output to `_inspiration/research/{topic-slug}/gemini-d2.md`

### D3: Claude
**Platform**: [claude.ai](https://claude.ai) → Research mode (extended thinking + web search)
1. Paste `prompt-d3-claude.md` into Claude Research
2. Let it run with extended thinking enabled
3. Save output to `_inspiration/research/{topic-slug}/claude-d3.md`

---

## Error Handling

### Model output missing required sections
- Re-run the prompt with explicit section headers in the instructions
- If truncated, split into two calls with section-specific follow-ups

### Provider UI changes or mode unavailable
- Web search for current provider interface instructions
- Fall back to standard chat with explicit "search the web and provide cited sources"

---

## Research Checklist

- [ ] Topic received from user
- [ ] Provider strengths web-searched for current capabilities
- [ ] D1 prompt generated, tailored to ChatGPT strengths
- [ ] D2 prompt generated, tailored to Gemini strengths
- [ ] D3 prompt generated, tailored to Claude strengths
- [ ] D1 executed on chatgpt.com → output saved
- [ ] D2 executed on gemini.google.com → output saved
- [ ] D3 executed on claude.ai → output saved
- [ ] All outputs follow citation rules (URLs, model attribution, sources section)
