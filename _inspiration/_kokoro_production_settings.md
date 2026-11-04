# Kokoro TTS — Battle-Tested Production Settings

> **Source**: `p:\matbanik.info\.agent\workflows\06-tts-workflow.md` + `.agent\skills\tts-generation\SKILL.md`
> **Battle-tested**: Hundreds of audio files generated across 8 languages in production.
> **Purpose**: Proven settings and pitfalls to adopt in av-kit's TTS module.

---

## 1. Voice Assignment Table

Kokoro-82M uses a **language code** for phoneme processing. The lang code MUST match the voice prefix.

| Lang Code | Language | Native Voices | Default |
|-----------|----------|---------------|---------|
| `a` | American English | `af_heart`, `af_bella`, `af_nicole`, `af_sarah`, `af_sky`, `am_adam`, `am_michael`, `am_eric` (20 total) | `am_eric` |
| `b` | British English | `bf_emma`, `bf_isabella`, `bm_george`, `bm_lewis` (8 total) | `bf_emma` |
| `e` | Spanish | `ef_dora`, `em_alex`, `em_santa` | `ef_dora` |
| `f` | French | `ff_siwis` | `ff_siwis` |
| `h` | Hindi | `hf_alpha`, `hf_beta`, `hm_omega`, `hm_psi` | `hf_alpha` |
| `i` | Italian | `if_sara`, `im_nicola` | `if_sara` |
| `j` | Japanese | `jf_alpha`, `jf_gongitsune`, `jm_kumo` (5 total) | `jf_alpha` |
| `p` | Brazilian Portuguese | `pf_dora`, `pm_alex`, `pm_santa` | `pf_dora` |

> **Critical rule**: Voice prefix first character = required lang_code.
> `af_heart` → lang_code `a`. `ef_dora` → lang_code `e`.
> Using `lang_code='a'` with `ef_dora` produces English-accented Spanish. WRONG.

**Total**: 54 voices across 8 languages, all pre-downloadable from HuggingFace.

---

## 2. Speed Settings

NOT a single fixed speed — content type determines optimal speed:

| Speed | Use Case | Description |
|-------|----------|-------------|
| `0.8` | Complex/technical content | Slower for clarity on dense material |
| `1.0` | Normal (default) | Standard narration pace |
| `1.1` | Casual/conversational | Slightly faster for lighter content |

---

## 3. Text Preparation Rules (Critical for Quality)

These rules are the result of hundreds of production files. Violating them produces audible artifacts.

### 3A. Number Handling
- **Spell out ALL numbers as words**: "thirty", not "30"; "four hundred fifty", not "450"
- Includes dollar amounts: "twenty thousand dollars"
- Includes percentages: "sixty percent"
- Includes ordinals: "thirty-sixth"
- **Why**: Kokoro mispronounces or awkwardly reads digit sequences

### 3B. Acronym Handling
- **Space-separate all acronyms**: "A I" not "AI", "M C P" not "MCP"
- **Why**: Kokoro pronounces "AI" as "eye", "TTS" as a single word
- **Exception**: Recognizable product names work natively (Docker, GitHub, Windows, PowerShell)
- For unknown brands, add phonetic hints on first use: "Pomera (POH-mer-uh)"

### 3C. Sentence Length
- **Keep sentences under 25 words**
- **Why**: Known text-audio misalignment issue with long sentences in Kokoro

### 3D. Unicode Cleanup
- Strip curly quotes (" ") → straight quotes
- Strip em-dashes (—) → hyphens
- Strip all non-ASCII punctuation
- **Why**: These characters cause unexpected pronunciation

### 3E. Punctuation as Pauses
- Comma = short pause
- Period = medium pause
- Double line break = long pause
- **Avoid ellipses (`...`)** — they confuse Kokoro

### 3F. Technical Content
- Narrate intent and outcome, never syntax
- Code blocks → one sentence describing what it does and why
- Binary/tool names → space-separate (NSSM → "N S S M")
- File paths → describe location, never read raw paths
- Port numbers → grouped words ("twenty-one-one-one-six" for 21116)

---

## 4. Script-Based Generation Pattern

> **NEVER use inline `python -c` for TTS generation.**
> PowerShell + conda mangles multiline strings silently.

**Always write a `.py` script file and run it:**

```python
# Template: generate_tts.py
from kokoro import KPipeline
import soundfile as sf
import numpy as np

pipe = KPipeline(lang_code='{KOKORO_LANG}')
text = open(r'{INPUT_TXT_PATH}', encoding='utf-8').read()
generator = pipe(text, voice='{VOICE_ID}', speed=1, split_pattern=r'\n+')
full = []
for i, (gs, ps, audio) in enumerate(generator):
    full.append(audio)
    if i % 10 == 0:
        print(f'  chunk {i}...')
print(f'Total chunks: {len(full)}')
sf.write(r'{OUTPUT_MP3_PATH}', np.concatenate(full), 24000, format='mp3')
print('Done: {OUTPUT_MP3_PATH}')
```

**Key parameters**:
- `split_pattern=r'\n+'` — paragraph-based chunking (critical for pacing)
- Sample rate: 24000 Hz (fixed by Kokoro model)
- Output format: `format='mp3'` via soundfile

**Run command**:
```bash
conda run -n kokoro_build --no-capture-output python generate_tts.py
```

---

## 5. Post-Generation Verification

**Always verify after generation — conda can return exit code 0 even on internal failure.**

### 5A. File Existence Check
```powershell
if (Test-Path 'output.mp3') { (Get-Item 'output.mp3').Length } else { Write-Error 'MISSING' }
```

### 5B. File Size Threshold
- Blog-length content: expect >100KB
- Single paragraph: expect >10KB
- If suspiciously small: regenerate

### 5C. Duration Variance
- Compare against baseline (e.g., English version)
- ±25% variance is investigation signal, not automatic failure
- Language expansion rates vary naturally (Japanese shorter, German longer)

---

## 6. Windows/PowerShell Pitfalls

### 6A. `--no-capture-output` Required
`conda run` without `--no-capture-output` silently swallows errors on Windows. Commands may exit with code 0 but produce no output files.

### 6B. Multi-Line Python Fails Silently
Multi-line Python scripts passed inline to `conda run` via PowerShell often fail without error. **Always write a `.py` file.**

### 6C. KeyboardInterrupt Contamination
If a `conda run` command is terminated mid-execution (Ctrl+C or IDE kill), the KeyboardInterrupt signal can persist across subsequent terminal sessions.

**Fix**: Close all terminals → restart IDE → retry.

**Alternative**: Wrap in `cmd /c` to isolate:
```bash
cmd /c "conda run -n kokoro_build --no-capture-output python generate_tts.py"
```

---

## 7. Model & Voice Storage

| Component | Location |
|-----------|----------|
| Kokoro package | `{conda_env}/lib/site-packages/kokoro/` |
| Voice files (.pt) | `~/.cache/huggingface/hub/models--hexgrad--Kokoro-82M/snapshots/.../` |
| Total voices | 54 across 8 languages |
| Auto-download | Voices downloaded from HuggingFace on first use |

---

## 8. Pre-Generation Checklist (from production use)

Before generating any audio:

- [ ] Numbers spelled out (no bare digits in text)
- [ ] Acronyms space-separated (AI → "A I")
- [ ] Sentences under 25 words
- [ ] Unicode cleaned (no curly quotes, em-dashes, ellipses)
- [ ] Lang code matches voice prefix
- [ ] Script written to .py file (not inline)
- [ ] `--no-capture-output` flag included in run command

After generation:

- [ ] File exists (not silently failed)
- [ ] File size reasonable (>100KB for long content)
- [ ] Duration within ±25% of baseline
