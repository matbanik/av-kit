# D3: Claude — Strategic Synthesis

> **Platform**: Claude (Research mode — extended thinking + web search)
> **Strength exploited**: Analytical frameworks, structured synthesis, nuanced strategic reasoning

## Prompt Template

```
Provide a strategic analysis and synthesis for {TOPIC}.

PART 1 — ARCHITECTURAL ANALYSIS
- What are the fundamental design choices involved in {TOPIC}?
- What are the trade-offs between different approaches?
- What constraints does each approach impose on downstream decisions?
- Draw a decision tree: if you choose X, then Y follows

PART 2 — RISK ASSESSMENT
- What are the technical risks of each approach?
- What are the maintenance and longevity risks?
- What dependencies create lock-in or fragility?
- What failure modes exist and how severe are they?

PART 3 — RECOMMENDATION FRAMEWORK
- Given these constraints: [list project-specific constraints]
- Recommend a specific approach with full justification
- Explain what you would do differently if constraints changed
- Provide a phased adoption plan (what to do first, second, etc.)

PART 4 — PATTERN RECOGNITION
- What patterns from other domains/projects apply here?
- What anti-patterns should be avoided?
- What has historically worked well for similar problems?

CITATION RULES: Tag every factual claim with its source URL inline. End with a ## Sources section listing all URLs used.
```
