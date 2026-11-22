# ruff: noqa: E501 -- one-shot edit script; its long lines are byte-exact edit literals.
"""Session 102 registration: add MEU-164 to meu-status.yaml (LF), 09-screenshot-capture.md (CRLF)
and build-priority-matrix.md (CRLF), by bytes, keeping each file's line endings."""

import sys
from pathlib import Path

import yaml

CR, LF, CRLF = b"\r", b"\n", b"\r\n"

ROOT = Path("P:/av-kit")
OUT = Path("C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes/register-meu.txt")
STATUS = ROOT / ".agent/context/meu-status.yaml"
SPEC = ROOT / "docs/build-plan/09-screenshot-capture.md"
MATRIX = ROOT / "docs/build-plan/build-priority-matrix.md"

ENTRY = """- row_key: MEU-164
  id: MEU-164
  slug: gui-tray-double-click-show
  phase: '9'
  band: P2
  matrix_item: '9.47'
  build_ref:
    path: build-plan/09-screenshot-capture.md
    anchor: tray-double-click
    text: Phase 9 §Tray double-click
  description: A double-click on the tray icon runs the tray menu's Show window action, through one show function shared by the menu item and the double-click listener; the tray menu is unchanged.
  status: pending
  status_labels:
    registry: ⬜ pending
    build_plan: ⬜
  surface_overrides: null
  dependencies_raw: MEU-39
  dependency_parse_status: parsed
  depends_on:
  - MEU-39
  execution_plan: docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/implementation-plan.md
  updated: '2026-11-22'
  closed_reason: null
  note: Registered 2026-11-22 from TRAY-DOUBLE-CLICK-NO-SHOW (triage D-1363, Mat's request; grouping D-1364), Session 102.
"""

BAND_OLD = "range: MEU-14–163 ("
BAND_NEW = "range: MEU-14–164 ("
BAND_TAIL_OLD = "2026-11-21 transcript job resume MEU-163)"
BAND_TAIL_NEW = "2026-11-21 transcript job resume MEU-163; 2026-11-22 tray double-click MEU-164)"

SECTION = """## Residuals registered 2026-11-22

One residual MEU from the 2026-11-22 triage (grouping `.agent/context/grouping/2026-11-22-tray-show-and-baseline-fixes-session-grouping.md`; plan `docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/`). It changes the tray icon of §Electron OS surface (`ui/src/main/capture-tray.ts`).

<a id="tray-double-click"></a>

### Tray double-click

> **MEU-164.** From `TRAY-DOUBLE-CLICK-NO-SHOW` (triage D-1363, Mat's request; grouping D-1364). The tray icon has a context menu and no double-click action, so after close-to-tray the window comes back only through the right-click menu, while a double-click on the icon does nothing. A double-click runs the menu's Show window action.

| Rule | Contract | Source |
|------|----------|--------|
| Double-click | A `double-click` on the tray icon runs the same function as the tray menu's Show window item. | Human-approved: D-1363 |
| One function | The menu item and the double-click listener share one show function inside `startCaptureTray`; neither restates its steps. | Local Canon: D-1363 |
| Menu | The tray menu keeps its four items, in order: Show window, Capture region, Open inbox folder, Quit. A single click and a right-click keep today's behaviour. | Local Canon: §Electron OS surface tray row |

"""

ANCHOR_NEXT = "## Named deferrals (not this phase)\n"
MEU_ROW_AFTER = "| MEU-161 | `capture-text-plate-metrics` | [Text plate metrics](#text-plate-metrics) | MEU-82, MEU-102 |\n"
MEU_ROW = "| MEU-164 | `gui-tray-double-click-show` | [Tray double-click](#tray-double-click) | MEU-39 |\n"
MATRIX_AFTER = (
    "| 9.46 | MEU-161 | `capture-text-plate-metrics` | [09 §Text plate metrics](09-screenshot-capture.md#text-plate-metrics) "
    "| MEU-82, MEU-102 |\n"
)
MATRIX_ROW = (
    "| 9.47 | MEU-164 | `gui-tray-double-click-show` | [09 §Tray double-click](09-screenshot-capture.md#tray-double-click) "
    "| MEU-39 |\n"
)


def eol(raw: bytes) -> str:
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf == lf:
        return "crlf"
    if crlf == 0:
        return "lf"
    sys.exit("mixed line endings")


def once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        sys.exit(f"{label}: anchor found {text.count(old)} times")
    return text.replace(old, new)


lines = []

# meu-status.yaml (LF)
raw = STATUS.read_bytes()
if eol(raw) != "lf" or b"MEU-164" in raw:
    sys.exit("meu-status.yaml: not LF, or MEU-164 already present")
text = raw.decode("utf-8")
text = once(text, "summary_bands:\n", ENTRY + "summary_bands:\n", "status entry")
text = once(text, BAND_OLD, BAND_NEW, "band range")
text = once(text, BAND_TAIL_OLD, BAND_TAIL_NEW, "band tail")
doc = yaml.safe_load(text)
ids = [m["row_key"] for m in doc["meus"]]
if ids.count("MEU-164") != 1 or len(ids) != len(set(ids)):
    sys.exit("meu-status.yaml parse check failed")
STATUS.write_bytes(text.encode("utf-8"))
lines.append(
    f"meu-status.yaml: {len(ids) - 1} to {len(ids)} MEUs; LF only: {eol(text.encode()) == 'lf'}"
)

# 09-screenshot-capture.md (CRLF)
for path, edits in (
    (
        SPEC,
        [
            (ANCHOR_NEXT, SECTION + ANCHOR_NEXT, "09 section"),
            (MEU_ROW_AFTER, MEU_ROW_AFTER + MEU_ROW, "09 MEU row"),
        ],
    ),
    (MATRIX, [(MATRIX_AFTER, MATRIX_AFTER + MATRIX_ROW, "matrix row")]),
):
    raw = path.read_bytes()
    if eol(raw) != "crlf" or b"MEU-164" in raw:
        sys.exit(f"{path.name}: not CRLF, or MEU-164 already present")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new, label in edits:
        text = once(text, old, new, label)
    out = text.replace("\n", "\r\n").encode("utf-8")
    path.write_bytes(out)
    lines.append(
        f"{path.name}: lines {raw.count(CRLF)} to {out.count(CRLF)}; CRLF only: {eol(out) == 'crlf'}"
    )

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
