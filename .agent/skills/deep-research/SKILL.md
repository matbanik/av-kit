---
name: deep-research
description: Generate provider-tailored deep research prompts for any topic
---

# Deep Research Skill

Generate custom-tailored research prompts for ChatGPT, Gemini, and Claude based on any topic.

## When to Use

- When user says "research {topic}" or "deep research on {topic}"
- When gathering information for a new build phase
- When evaluating technology choices or alternatives
- Before implementing complex features that need current best practices

## Prerequisites

- Web access for provider capability search
- Write access to `_inspiration/research/` directory

## Execution

### Quick Flow

1. **Receive topic** from user
2. **Web search** each provider's current deep research capabilities:
   - `"ChatGPT deep research strengths {YEAR}"`
   - `"Gemini deep research strengths {YEAR}"`
   - `"Claude deep research extended thinking {YEAR}"`
3. **Generate 3 prompts** tailored to each provider's strengths
4. **Save** to `_inspiration/research/{topic-slug}/`
5. **Present** prompts to user for execution on native platforms

### Prompt Generation Rules

Each prompt must:
- Exploit the provider's specific strengths (breadth for ChatGPT, Google data for Gemini, synthesis for Claude)
- Include the topic context and specific questions
- Request citation rules: inline source URLs, model attribution tags
- End with a `## Sources` section
- Be ready to paste into the provider's native UI

### Output Files

```
_inspiration/research/{topic-slug}/
├── prompt-d1-chatgpt.md     # Breadth + quantitative focus
├── prompt-d2-gemini.md      # Trends + community signals focus
├── prompt-d3-claude.md      # Strategic synthesis focus
├── chatgpt-d1.md            # (User pastes output here)
├── gemini-d2.md             # (User pastes output here)
└── claude-d3.md             # (User pastes output here)
```

## Related

- Workflow: `.agent/workflows/deep-research.md` — Full workflow with steps and checklist
- Templates: `.agent/workflows/prompts/deep-research/` — Starter prompt templates
