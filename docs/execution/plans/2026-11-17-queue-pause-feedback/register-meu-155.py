"""Register MEU-155 (gui-queue-pause-feedback) and its build-plan home. Session 88, row 1.

meu_status.py has no add command, so this script adds the entry through the
same model the tool uses (tools.meu_status.model.load and save, which validate
against the schema and write the same bytes the tool writes). It also adds the
home section at the end of docs/build-plan/10-queue-card-ui.md and the matrix
row 10.10 in docs/build-plan/build-priority-matrix.md. Both are CRLF and stay CRLF.

Usage:
    register-meu-155.py --expect-sha256 <sha of meu-status.yaml at row 0> [--dry-run]
    register-meu-155.py --selftest

--dry-run writes the three results under SCRATCH and leaves the repository alone.
The script refuses when:
- the register's hash differs from --expect-sha256;
- a load and save of the unchanged register would change its bytes;
- MEU-155 or the new anchor already exists;
- an anchor line is not found exactly once;
- a CRLF file is not wholly CRLF.
The render of meu-registry.md and BUILD_PLAN.md is the next command in row 1.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from tools.meu_status import model  # noqa: E402

SCRATCH = Path("C:/Temp/av-kit/queue-pause-feedback/register")
SSOT = REPO / ".agent" / "context" / "meu-status.yaml"
DOC10 = REPO / "docs" / "build-plan" / "10-queue-card-ui.md"
MATRIX = REPO / "docs" / "build-plan" / "build-priority-matrix.md"

TODAY = "2026-11-17"
ANCHOR = "queue-pause-feedback-residual"


def j(*parts: str) -> str:
    """Join string pieces; keeps each source line short."""
    return "".join(parts)


ENTRY = {
    "row_key": "MEU-155",
    "id": "MEU-155",
    "slug": "gui-queue-pause-feedback",
    "phase": "10",
    "band": "P2",
    "matrix_item": "10.10",
    "build_ref": {
        "path": "build-plan/10-queue-card-ui.md",
        "anchor": ANCHOR,
        "text": "Phase 10 §Queue pause feedback (residual)",
    },
    "description": j(
        "The Convert and Downloader toolbar Pause reads Pause after this job; ",
        "after a click it shows Pausing… and the processor status says the queue ",
        "stops when the current job ends, until the queue pauses. Cancel still stops ",
        "the running job at once; Convert and Downloader keep pausing between jobs, ",
        "and Transcript's waits end on pause or stop.",
    ),
    "status": "pending",
    "status_labels": {"registry": "⬜ pending", "build_plan": "⬜"},
    "surface_overrides": None,
    "dependencies_raw": "MEU-45, MEU-46",
    "dependency_parse_status": "parsed",
    "depends_on": ["MEU-45", "MEU-46"],
    "execution_plan": None,
    "updated": TODAY,
    "closed_reason": None,
    "note": j(
        "Registered 2026-11-17 from QUEUE-PAUSE-NO-FEEDBACK ",
        "(grouping §3 Session 88, Mat's 2026-11-16 ruling), Session 88.",
    ),
}

PHASE_NOTE_ADD = " MEU-155 residual (queue pause feedback) registered 2026-11-17."
P2_OLD = "MEU-14–154"
P2_NEW = "MEU-14–155"
P2_TAIL_OLD = "post-rc.3 triage residuals MEU-145–154, with MEU-144 held for Session 74)"
P2_TAIL_NEW = j(P2_TAIL_OLD[:-1], "; 2026-11-17 queue pause feedback MEU-155)")

MATRIX_AFTER = j(
    "| 10.9 | MEU-49 | `gui-queue-dnd` | ",
    "[10 §Reorder model](10-queue-card-ui.md#reorder-model) | MEU-47 |",
)
MATRIX_ROW = j(
    "| 10.10 | MEU-155 | `gui-queue-pause-feedback` | ",
    "[10 §Queue pause feedback (residual)](10-queue-card-ui.md#queue-pause-feedback-residual)",
    " | MEU-45, MEU-46 |",
)

DOC10_SECTION_LINES = [
    "",
    "---",
    "",
    f'<a id="{ANCHOR}"></a>',
    "",
    "## Queue pause feedback (residual)",
    "",
    j(
        "> **MEU-155.** Registered 2026-11-17 from `QUEUE-PAUSE-NO-FEEDBACK`. ",
        "Pause is queue-level and takes effect between jobs (§Toolbar reduction), ",
        "so a click during a long Convert or Downloader job looked like nothing happened. ",
        "Mat's ruling (2026-11-16): ",
        '"Say what it does".',
    ),
    "",
    "| Rule | Contract | Source |",
    "|------|----------|--------|",
    j(
        "| Label | The toolbar toggle reads `Pause after this job` on the Convert and ",
        "Downloader pages; `Resume` is unchanged | ",
        'Human-approved 2026-11-16 ("Say what it does") |',
    ),
    j(
        "| Pending | After a pause request succeeds while a job runs, the toggle reads ",
        "`Pausing…` and is disabled until the queue reports `Paused` or `Idle`, or a ",
        "different job starts; a job that fails still ends `Paused`. The toggle keeps one ",
        "width in every state, so Clear finished does not move. The palette's pause shares ",
        "the same request and sends no second one | ",
        "Human-approved 2026-11-16; Session 88 D-1091, D-1092 |",
    ),
    j(
        "| Status | While pending, the processor status reads ",
        "`Queue stops when the current job ends` in place of the processor label | ",
        "Human-approved 2026-11-16 |",
    ),
    j(
        "| Cancel | Cancel stays enabled and stops the running job at once; it also ends ",
        "the pending state | Human-approved 2026-11-16 |",
    ),
    j(
        "| Between jobs | The Convert and Downloader services keep pausing between jobs; ",
        "no API route, OpenAPI document or MCP tool changes | ",
        "Human-approved 2026-11-16; §Toolbar reduction (queue-level only, no per-item pause) |",
    ),
    j(
        "| Transcript | The Transcript page keeps its own toolbar and its `Pause` label; ",
        "its waits between videos, between batches and before a retry end within a second ",
        "of a pause or stop | Session 88 D-1090; 11 TR1, TR2; 03 §Rate cap |",
    ),
    j(
        "| Tests | Electron E2E: the label, `Pausing…` while a real Convert job runs, the ",
        "queue paused after that job, Cancel during `Pausing…`, the Downloader pending ",
        "state and Clear finished staying put; pytest: Transcript's waits end on pause or stop | ",
        'Mat, 2026-11-16 ("This should be done with framework and scripts!") |',
    ),
]

MATRIX_MARK = b"| 10.10 | MEU-155 |"


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def is_crlf(b: bytes) -> bool:
    return b.count(b"\n") == b.count(b"\r\n") and b.count(b"\n") > 0


def roundtrip_bytes(path: Path) -> bytes:
    data = model.load(path)
    with tempfile.TemporaryDirectory(dir=str(SCRATCH)) as tmp:
        out = Path(tmp) / "roundtrip.yaml"
        model.save(data, out)
        return out.read_bytes()


def edit_ssot(data: dict) -> dict:
    data = copy.deepcopy(data)
    meus = data["meus"]
    keys = [m["row_key"] for m in meus]
    if "MEU-155" in keys:
        raise SystemExit("refused: MEU-155 is already registered")
    if keys.count("MEU-154") != 1:
        raise SystemExit("refused: MEU-154 is not found exactly once")
    meus.insert(keys.index("MEU-154") + 1, copy.deepcopy(ENTRY))

    phases = [p for p in data["phases"] if p["id"] == "10"]
    if len(phases) != 1:
        raise SystemExit("refused: phase 10 is not found exactly once")
    phase = phases[0]
    if "MEU-155" in phase["note"]:
        raise SystemExit("refused: phase 10 note already names MEU-155")
    phase["note"] = phase["note"] + PHASE_NOTE_ADD
    phase["last_updated"] = TODAY

    bands = [b for b in data["summary_bands"] if b["key"] == "P2"]
    if len(bands) != 1:
        raise SystemExit("refused: band P2 is not found exactly once")
    rng = bands[0]["range"]
    if rng.count(P2_OLD) != 1 or not rng.endswith(P2_TAIL_OLD):
        raise SystemExit("refused: the P2 range text is not the row-0 text")
    bands[0]["range"] = rng.replace(P2_OLD, P2_NEW).replace(P2_TAIL_OLD, P2_TAIL_NEW)
    return data


def edit_doc10(b: bytes) -> bytes:
    if not is_crlf(b):
        raise SystemExit("refused: 10-queue-card-ui.md is not wholly CRLF")
    if ANCHOR.encode() in b:
        raise SystemExit("refused: the anchor already exists in 10-queue-card-ui.md")
    if not b.endswith(b"\r\n"):
        raise SystemExit("refused: 10-queue-card-ui.md does not end with CRLF")
    add = "\r\n".join(DOC10_SECTION_LINES).encode("utf-8") + b"\r\n"
    return b + add


def edit_matrix(b: bytes) -> bytes:
    if not is_crlf(b):
        raise SystemExit("refused: build-priority-matrix.md is not wholly CRLF")
    after = MATRIX_AFTER.encode("utf-8") + b"\r\n"
    if b.count(after) != 1:
        raise SystemExit("refused: the 10.9 row is not found exactly once")
    if b"| 10.10 |" in b or b"MEU-155" in b:
        raise SystemExit("refused: the matrix already has 10.10 or MEU-155")
    return b.replace(after, after + MATRIX_ROW.encode("utf-8") + b"\r\n", 1)


def run(expect: str, dry_run: bool) -> int:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    before = SSOT.read_bytes()
    if sha256(before) != expect:
        print(f"refused: meu-status.yaml sha256 {sha256(before)} != expected {expect}")
        return 1
    if roundtrip_bytes(SSOT) != before:
        print("refused: a load and save of the unchanged register changes its bytes")
        return 1
    new_data = edit_ssot(model.load(SSOT))
    doc10 = edit_doc10(DOC10.read_bytes())
    matrix = edit_matrix(MATRIX.read_bytes())

    if dry_run:
        out_ssot = SCRATCH / "meu-status.yaml"
        out_doc10 = SCRATCH / "10-queue-card-ui.md"
        out_matrix = SCRATCH / "build-priority-matrix.md"
    else:
        out_ssot, out_doc10, out_matrix = SSOT, DOC10, MATRIX
    model.save(new_data, out_ssot)
    out_doc10.write_bytes(doc10)
    out_matrix.write_bytes(matrix)

    after = out_ssot.read_bytes()
    added = after.count(b"\n") - before.count(b"\n")
    anchors = doc10.count(ANCHOR.encode())
    rows = matrix.count(MATRIX_MARK)
    print("mode:", "dry-run" if dry_run else "apply")
    print("meu-status.yaml lines added:", added, "CR bytes:", after.count(b"\r"))
    print("meu-status.yaml sha256:", sha256(after))
    print("10-queue-card-ui.md CRLF:", is_crlf(doc10), "anchor count:", anchors)
    print("build-priority-matrix.md CRLF:", is_crlf(matrix), "MEU-155 rows:", rows)
    meu = model.get_meu(model.load(out_ssot), "MEU-155")
    ok = (
        meu is not None
        and meu["status"] == "pending"
        and b"\r" not in after
        and is_crlf(doc10)
        and is_crlf(matrix)
        and anchors == 1
        and rows == 1
    )
    shown = None if meu is None else (meu["status"], meu["matrix_item"], meu["depends_on"])
    print("MEU-155:", shown)
    print("register-meu-155:", "ok" if ok else "FAILED")
    return 0 if ok else 1


def refused(fn, arg: bytes) -> bool:
    try:
        fn(arg)
    except SystemExit:
        return True
    return False


def selftest() -> int:
    crlf = j("a\r\n", MATRIX_AFTER, "\r\n| 11.1 | x |\r\n").encode("utf-8")
    out = edit_matrix(crlf)
    assert out.count(MATRIX_MARK) == 1
    assert out.index(b"| 10.9 |") < out.index(b"| 10.10 |") < out.index(b"| 11.1 |")
    assert is_crlf(out)
    assert refused(edit_matrix, out), "a second matrix edit was not refused"
    assert refused(edit_matrix, b"a\n" + MATRIX_AFTER.encode() + b"\n"), "LF matrix accepted"
    doc = edit_doc10(b"x\r\nremain authoritative.\r\n")
    assert is_crlf(doc) and doc.count(ANCHOR.encode()) == 1 and doc.endswith(b"|\r\n")
    assert "## Queue pause feedback (residual)" in doc.decode("utf-8")
    assert refused(edit_doc10, doc), "a second doc 10 edit was not refused"
    data = {
        "phases": [{"id": "10", "note": "n.", "last_updated": "2026-09-16"}],
        "meus": [{"row_key": "MEU-153"}, {"row_key": "MEU-154"}, {"row_key": "MEU-200"}],
        "summary_bands": [{"key": "P2", "range": j("MEU-14–154 (x; ", P2_TAIL_OLD)}],
    }
    new = edit_ssot(data)
    keys = [m["row_key"] for m in new["meus"]]
    assert keys == ["MEU-153", "MEU-154", "MEU-155", "MEU-200"]
    phase = new["phases"][0]
    assert phase["note"].endswith("registered 2026-11-17.") and phase["last_updated"] == TODAY
    rng = new["summary_bands"][0]["range"]
    assert rng.startswith("MEU-14–155") and rng.endswith("queue pause feedback MEU-155)")
    assert data["meus"][2]["row_key"] == "MEU-200" and len(data["meus"]) == 3
    print("register-meu-155 selftest: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--expect-sha256")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.expect_sha256:
        ap.error("--expect-sha256 is required")
    return run(a.expect_sha256, a.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
