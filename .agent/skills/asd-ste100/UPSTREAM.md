# Upstream provenance: asd-ste100

> **Vendored, not forked.** Every file in this folder except this one is a byte copy of the upstream skill with no local change. Do not edit them here.

| Field | Value |
|-------|-------|
| Source | https://github.com/danyuchn/asd-ste100-skill |
| Commit | `32511c6992ecb5f1971e46a2943f2e6adceedafe` |
| Skill version | 0.4.0 (`SKILL.md` frontmatter) |
| License | MIT; see `LICENSE` (Copyright (c) 2026 Dustin Yuchen Teng) |
| Vendored on | 2026-11-20 (Session 99, MEU-162) |

## Files

| File | SHA-256 |
|------|---------|
| `SKILL.md` | `f9438cec8c97cf336558fda3159a9bfc93a392b37d96acf45149a13052a63eb2` |
| `LICENSE` | `c3ce5e692278b6e23e17120bb1813c35b2193a71e6705aa2aea5de6761f65e07` |
| `references/writing-rules.md` | `38bfeaf928089ba52f52600ab04ba534ac2ef1751a2406fb53a1343f5cd2a183` |
| `examples/before-after.md` | `42615abb96b0a02ac71ab631126fa22172a97a5093dacba237198854d6de24e4` |
| `examples/linter-edge-cases.md` | `38bd04067ba4c36ada2ed9ac8ba75e8b1cf770a16be929320e540c75bdb3c02c` |
| `scripts/ste-lint.py` | `dbc55b670d1fbe067472d13d974a7ca538dc8bdef9b107dd991f5ffe2fece807` |

Upstream's `README.md` is not copied: it holds install steps that do not apply to a vendored copy.

## How av-kit uses it

- `tools/help_guide_ste.py` loads `scripts/ste-lint.py` by path and runs it on the help card content: the quick start steps in Strict mode, and the intros, alt texts and unpinned topics with 0 `advisory-free` findings. `tests/tooling/test_help_guide_ste.py` runs that tool as a pytest gate.
- Read `SKILL.md` before writing or changing help card text.

## Updating

1. Clone upstream into a scratch folder and diff it against this folder.
2. Copy the changed files over as bytes, then update the commit row and the SHA-256 table above.
3. Run `uv run pytest tests/tooling/test_help_guide_ste.py`. If upstream renamed `lint()` or the finding fields, fix `tools/help_guide_ste.py`.
