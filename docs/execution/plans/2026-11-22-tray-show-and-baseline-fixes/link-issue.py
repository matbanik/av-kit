# ruff: noqa: E501 -- one-shot edit script; its long lines are byte-exact edit literals.
"""Session 102 registration: link TRAY-DOUBLE-CLICK-NO-SHOW to MEU-164 in known-issues.yaml (CRLF, by bytes)."""

import sys
from pathlib import Path

import yaml

CR, LF, CRLF = b"\r", b"\n", b"\r\n"

P = Path("P:/av-kit/.agent/context/known-issues.yaml")
OUT = Path("C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/link-issue.txt")
ISSUE = "TRAY-DOUBLE-CLICK-NO-SHOW"
OLD_NOTES = (
    "    notes: 'Triage 2026-11-22 (D-1363): MEU-NEW P3, Mat''s request. A double-click on the tray icon runs "
    "the same function as the Show window menu item.'\n"
)
NEW_NOTES = (
    "    notes: 'Triage 2026-11-22 (D-1363): MEU-NEW P3, Mat''s request. MEU-164 gui-tray-double-click-show "
    "(09, matrix 9.47), Session 102 (grouping D-1364). A double-click on the tray icon runs the same function "
    "as the Show window menu item.'\n"
)

raw = P.read_bytes()
if raw.count(b"\n") != raw.count(b"\r\n"):
    sys.exit("known-issues.yaml is not CRLF-only")
text = raw.decode("utf-8").replace("\r\n", "\n")
start = text.index(f"  - id: {ISSUE}\n")
end = text.find("\n  - id: ", start + 1)
end = len(text) if end == -1 else end + 1
block = text[start:end]
for old, new in (
    ("    meu_links: []\n", "    meu_links:\n      - MEU-164\n"),
    (OLD_NOTES, NEW_NOTES),
):
    if block.count(old) != 1:
        sys.exit(f"anchor found {block.count(old)} times: {old[:40]!r}")
    block = block.replace(old, new)
text = text[:start] + block + text[end:]
doc = yaml.safe_load(text)
issue = next(i for i in doc["issues"] if i["id"] == ISSUE)
if issue["meu_links"] != ["MEU-164"]:
    sys.exit("parse check failed")
out = text.replace("\n", "\r\n").encode("utf-8")
P.write_bytes(out)
msg = f"{ISSUE} meu_links={issue['meu_links']}; CRLF only: {out.count(LF) == out.count(CRLF)}"
OUT.write_text(msg + "\n", encoding="utf-8")
print(msg)
