# Text-to-TTS Cleanup Pipeline — Pseudo Logic

> **Source**: `p:\prep-text-for-tts\` (tts_preprocessor_gui.py: 2,804 lines + multi_pass_processor.py: 597 lines)
> **User Intent**: "Programmatically clean up text so it is TTS-friendly — handling OCR artifacts, punctuation, symbols, numbers, and chunking."
> **This document captures functional intent and transformation rules — NOT code.**

---

## Pipeline Overview

```
Raw Text (OCR, markdown, pasted, or file)
    ↓
╔══════════════════════════════════════════════════════╗
║  PART 1: Text Cleaning (5-stage OCR processor)      ║
║    Stage 1 → Semantic Cleaning                       ║
║    Stage 2 → Deterministic Cleaning                  ║
║    Stage 3 → Sentence Reconstruction                 ║
║    Stage 4 → Edge Case Collection                    ║
║    Stage 5 → Edge Case Handling                      ║
╚══════════════════════════════════════════════════════╝
    ↓
╔══════════════════════════════════════════════════════╗
║  PART 2: TTS Normalization (10-step pipeline)       ║
║    1. Punctuation normalization                      ║
║    2. Symbol conversion                              ║
║    3. Number expansion                               ║
║    4. Currency formatting                            ║
║    5. ALL CAPS normalization                         ║
║    6. Chapter marker standardization                 ║
║    7. URL/email removal                              ║
║    8. Page number removal                            ║
║    9. Whitespace normalization                       ║
║    10. Smart TTS chunking                            ║
╚══════════════════════════════════════════════════════╝
    ↓
Clean TTS-Ready Text
```

---

## Part 1: Text Cleaning (5-Stage OCR Processor)

> **Note for av-kit**: OCR cleaning is relevant when text comes from scanned sources. For transcript text or user-pasted text, many Stage 1/2 rules still apply (Unicode fixing, apostrophe normalization, whitespace cleanup). The pipeline should be modular — users can skip OCR-specific stages.

### Stage 1: Semantic Cleaning

**Purpose**: Remove meaningless artifacts, fix encoding issues.

| Rule | What | Why |
|------|------|-----|
| **ftfy** | Fix mojibake, HTML entities, Unicode normalization | Text may have encoding mix-ups from copy-paste or OCR |
| **Line endings** | Normalize CRLF/CR/LF → LF | Consistent processing across platforms |
| **Page headers** | Remove recurring headers/footers | OCR scans include page headers that interrupt text flow |
| **Page numbers** | Remove standalone number-only lines (≤3 digits) | OCR captures page numbers as text |
| **Short all-caps lines** | Remove lines <30 chars that are ALL CAPS with ≤3 words | Likely OCR page headers |
| **Excessive blank lines** | Collapse 3+ blank lines → 2 | Preserve paragraph breaks, remove artifacts |

### Stage 2: Deterministic Cleaning

**Purpose**: Fix high-confidence text errors programmatically.

#### OCR Artifact Replacement
| Artifact | Replacement | Reason |
|----------|-------------|--------|
| `·` (middle dot) | `'` (apostrophe) | OCR misreads apostrophes as middle dots |
| `■` (box) | *(remove)* | OCR artifact |
| `●` (circle) | *(remove)* | OCR artifact |
| `∙` (bullet operator) | *(remove)* | OCR artifact |
| `•` (bullet) | *(remove)* | OCR artifact |
| `′` (prime) | `'` (apostrophe) | OCR misread |
| `` ` `` (backtick) | `'` (apostrophe) | Used in contractions by OCR |

#### Apostrophe Spacing Fix
- `don ' t` → `don't` | `child ' s` → `child's`
- Handles straight `'` and curly `'` `'` apostrophes
- Remove spaces before AND after apostrophes

#### Word Fragment Merging (Conservative)
Only merge when there's *explicit evidence* of a fragment:
1. **Hyphenated line breaks**: `com-\npleted` → `completed` (always merge)
2. **Trailing space + short suffix**: `drop \nping` → `dropping` (last word ≤5 chars, first word of next line ≤4 chars, lowercase)
3. **NOT merged**: `dog\nwith` stays as `dog with` (no evidence of fragment)

#### Merged Word Detection
OCR sometimes merges two words without a space. Detection via pattern library:

| Pattern | Example | Fix |
|---------|---------|-----|
| Verb past tense + article | `racedthrough` | `raced through` |
| Verb -ing + preposition | `lookingat` | `looking at` |
| been/had/was + adjective | `beenkilled` | `been killed` |
| Preposition + article | `intothe` | `into the` |
| Noun + `and` | `timeand` | `time and` |
| Proper name + verb | `Johnsaid` | `John said` |

### Stage 3: Sentence Reconstruction

**Purpose**: Merge OCR line breaks into proper paragraphs.

**Rules**:
1. Blank line = paragraph boundary
2. Within a paragraph, merge consecutive lines into one
3. If a buffer does NOT end with terminal punctuation (`.!?`), ignore blank lines and keep building the sentence
4. Preserve paragraph structure from input

### Stage 4: Edge Case Collection

**Purpose**: Flag anomalies for review (not auto-fix).

| Anomaly | Detection | Confidence |
|---------|-----------|------------|
| Very short "sentence" | <20 chars + ends with `.!?` | Medium |
| Missing punctuation | >50 chars + no terminal punctuation | Low |
| Suspiciously long word | 15+ consecutive lowercase letters | Medium |

### Stage 5: Edge Case Handling

**Purpose**: Log collected edge cases with statistics.

- Group by type (short_sentence, missing_punctuation, suspicious_long_word)
- Count instances per type
- Future: ML-based or dictionary-based auto-resolution

---

## Part 2: TTS Normalization (10-Step Pipeline)

> **These 10 steps are the core TTS cleanup logic** — applicable to ANY text input, not just OCR. av-kit should implement all 10 as a configurable preprocessing step before Kokoro generation.

### Step 1: Punctuation Normalization

| Input | Output | Rule |
|-------|--------|------|
| `???` | `?` | Collapse repeated question marks |
| `!!!` | `!` | Collapse repeated exclamation marks |
| `....` | `…` | 4+ dots → single ellipsis character |
| `---` | `—` | Three hyphens → em dash |
| `--` | `—` | Two hyphens → em dash |
| ` - ` | ` — ` | Spaced hyphen (likely em dash intent) |
| `...` | `…` | Three dots → ellipsis character |
| `. . .` | `…` | Spaced dots → ellipsis |

### Step 2: Symbol Conversion

| Symbol | Replacement | Context |
|--------|-------------|---------|
| `™` | ` trademark` | TTS can't read ™ |
| `®` | ` registered` | TTS can't read ® |
| `©` | ` copyright` | TTS can't read © |
| `&` | ` and ` | Read as word |
| `@` (standalone) | ` at ` | Not in email context |
| `#5` | `number 5` | Hashtag-number pattern |

### Step 3: Number Expansion

**Ordinals** → words (dictionary-based, 1st through 31st):
- `1st` → `first`, `2nd` → `second`, `3rd` → `third`
- `20th` → `twentieth`, `21st` → `twenty-first`

**Decades**:
- `1990s` → kept as-is (TTS engines handle these)
- `'90s` → `90s` (remove leading apostrophe)

### Step 4: Currency Formatting

| Input | Output | Pattern |
|-------|--------|---------|
| `$100` | `100 dollars` | Dollar sign + digits |
| `$1,000.50` | `1,000.50 dollars` | Handles comma formatting |
| `€50` | `50 euros` | Euro sign |
| `£25` | `25 pounds` | Pound sign |
| `¢` | ` cents` | Cent sign |

### Step 5: ALL CAPS Normalization

**Strategy**: Don't blindly lowercase — preserve acronyms.

1. **Detect ALL CAPS sentences**: >70% uppercase characters
2. **For each word in ALL CAPS sentence**:
   - Word ≤4 characters → **keep CAPS** (likely acronym: NASA, FBI, USA)
   - Word >4 characters → **convert to Title Case** (CHAPTER → Chapter)
3. **Remaining standalone ALL CAPS words** >4 chars → Title Case

### Step 6: Chapter Marker Standardization

| Input | Output |
|-------|--------|
| `CHAPTER` | `Chapter` |
| `PART` | `Part` |
| `SECTION` | `Section` |
| `Chapter I` | `Chapter 1` |
| `Part III` | `Part 3` |
| `Chapter XVIII` | `Chapter 18` |

Roman numeral conversion: I through XX (20 values).

### Step 7: URL/Email Removal

| Input | Output | Reason |
|-------|--------|--------|
| `https://example.com/path` | `[link]` | TTS reads URLs character-by-character |
| `www.example.com` | `[link]` | Same issue |
| `user@example.com` | `[email]` | TTS struggles with email format |

### Step 8: Page Number Removal

- Remove lines containing only digits: `^\s*\d+\s*$`
- Collapse resulting 3+ blank lines → 2

### Step 9: Whitespace Normalization

| Rule | What |
|------|------|
| Line endings | CRLF/CR → LF |
| Multiple spaces | Collapse to single space |
| Leading/trailing spaces | Remove per line |
| Excessive blank lines | Max 2 consecutive (paragraph break) |

### Step 10: Smart TTS Chunking

**Deepgram-style hybrid approach** — critical for TTS pacing.

**Algorithm**:
1. Split text into **paragraphs** (double newline)
2. For each paragraph, use **spaCy** for sentence segmentation
   - Handles abbreviations correctly (Dr., Mr., U.S.A.)
   - Context-aware sentence boundary detection
3. Combine sentences into **chunks** while under `max_chars` (default: 250)
4. If a single sentence exceeds `max_chars`:
   - Split at **commas** (min 3 words per chunk)
   - Fallback: split at **spaces** if no commas
   - Last resort: hard-split extremely long words
5. Preserve paragraph breaks between chunk groups

**Why 250 chars?** Matches natural speech pauses. TTS engines produce better prosody with chunks that fit a single breath.

---

## Orphaned Apostrophe Fix

**Specific OCR issue** where quotes/dialogue marks are misread:
- `people'and` → `people and`
- `me'from` → `me from`
- `feeling'both` → `feeling both`

**Rule**: If apostrophe appears between a word and a common non-contraction word, remove it and add a space.

---

## Implementation Notes for av-kit

### What to Adopt Directly
1. **All 10 TTS normalization steps** — these are universal, not OCR-specific
2. **Smart chunking** (Step 10) — critical for Kokoro TTS quality
3. **Symbol and number expansion** — Kokoro has the same limitations as other TTS engines
4. **ALL CAPS handling** — preserving acronyms while normalizing shouting

### What to Make Optional/Configurable
1. **OCR cleaning stages** (Part 1) — only needed when processing OCR text
2. **URL/email removal** — user may want URLs preserved in some contexts
3. **Chapter marker normalization** — only relevant for book content
4. **Max chunk size** — should be configurable (default 250 chars)

### Synergy with Kokoro Production Settings
The [_kokoro_production_settings.md](_kokoro_production_settings.md) has complementary rules:
- **Number spelling** — this pipeline does ordinals; Kokoro settings say spell ALL numbers
- **Acronym spacing** — this pipeline preserves short CAPS; Kokoro settings say space-separate ("A I" not "AI")
- **Sentence length** — this pipeline chunks at 250 chars; Kokoro settings say <25 words

**Recommendation**: Merge both rule sets into a unified `TextPreparationService` with a 2-pass approach:
1. Pass 1: General TTS normalization (this pipeline's 10 steps)
2. Pass 2: Kokoro-specific rules (number spelling, acronym spacing, sentence length limits)

### Dependencies
- **ftfy** — Unicode/mojibake fixing (pip install ftfy)
- **spaCy** — Sentence segmentation (pip install spacy + en_core_web_sm model)
- Both are lightweight and production-ready
