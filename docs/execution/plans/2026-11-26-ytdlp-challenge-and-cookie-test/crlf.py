"""RULE-3: write known-issues.yaml and known-issues.md back to the endings git's index
expects. Session 104 (D-1476): triage-output.yaml is dropped from the list; row 19's render
writes only known-issues.md, and triage-output.yaml is another session's dirty file."""

import subprocess
from pathlib import Path

CR, LF, CRLF = b"\r", b"\n", b"\r\n"

ROOT = Path("P:/av-kit")
OUT = Path("C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test/crlf.txt")
lines = []
for rel in (
    ".agent/context/known-issues.yaml",
    ".agent/context/known-issues.md",
):
    p = ROOT / rel
    raw = p.read_bytes()
    head = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT, capture_output=True).stdout
    # Working copies under core.autocrlf=true are CRLF; the tools write LF.
    lf = raw.replace(b"\r\n", b"\n")
    new = lf.replace(b"\n", b"\r\n")
    if new != raw:
        p.write_bytes(new)
    lines.append(
        f"{rel}: was crlf={raw.count(CRLF)} lf={raw.count(LF)}; "
        f"now CRLF only={new.count(LF) == new.count(CRLF)}; "
        f"HEAD blob LF-only={head.count(CRLF) == 0}"
    )
text = "\n".join(lines) + "\n"
OUT.write_text(text, encoding="utf-8")
print(text, end="")
