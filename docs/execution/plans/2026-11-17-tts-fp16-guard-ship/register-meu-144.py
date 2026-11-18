"""Register MEU-144 (svc-tts-fp16-guard-ship) and its build-plan home. Session 74, rows 1 and 9.

Shaped like 2026-11-17-queue-pause-feedback/register-meu-155.py (Session 88). meu_status.py has
no add command, so this script adds the entry through the same model the tool uses
(tools.meu_status.model.load and save, which validate against the schema and write the same
bytes the tool writes). It also adds the home section to docs/build-plan/03-service-layer.md
before the `download-failure-reason-residual` anchor, and matrix row 3.21 after row 3.20 in
docs/build-plan/build-priority-matrix.md. Both are CRLF and stay CRLF. Two texts in the
register already name MEU-144 as held for Session 74; they are reworded, not extended
(implementation-plan.md §Registration and records; D-1135 A, D-801).

Usage:
    register-meu-144.py --expect-sha256 <sha of meu-status.yaml at row 0> [--dry-run]
    register-meu-144.py --delivered NOTE_FILE [--dry-run]
    register-meu-144.py --selftest

The 03 and matrix hashes are read from this plan's baseline-scope.json (row 0).
--dry-run writes the results under SCRATCH and leaves the repository alone.
The register step refuses when:
- the register's hash differs from --expect-sha256, or 03's or the matrix's hash differs from
  baseline-scope.json (S2, S4);
- a load and save of the unchanged register would change its bytes;
- MEU-144, the new anchor or matrix row 3.21 already exists;
- an anchor line or a reworded text is not found exactly once;
- a CRLF file is not wholly CRLF.
--delivered (row 9) appends the CRLF `> **Delivered (Session 74).**` note to the new 03 section,
just before the `download-failure-reason-residual` anchor, and refuses when the MEU-144 section
is not there exactly once, a Session 74 note is already there, 03 is not wholly CRLF, or the
note file is empty, does not start with the note's head, or holds a CR on its own.
The render of meu-registry.md and BUILD_PLAN.md is the next command in row 1.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from tools.meu_status import model  # noqa: E402

PLAN = REPO / "docs" / "execution" / "plans" / "2026-11-17-tts-fp16-guard-ship"
SCRATCH = Path("C:/Temp/av-kit/tts-fp16-guard-ship/register")
SSOT = REPO / ".agent" / "context" / "meu-status.yaml"
DOC03 = REPO / "docs" / "build-plan" / "03-service-layer.md"
MATRIX = REPO / "docs" / "build-plan" / "build-priority-matrix.md"
SCOPE_JSON = PLAN / "baseline-scope.json"
DOC03_KEY = "docs/build-plan/03-service-layer.md"
MATRIX_KEY = "docs/build-plan/build-priority-matrix.md"

TODAY = "2026-11-17"
ANCHOR = "tts-fp16-guard-ship-residual"
NEXT_ANCHOR = b'<a id="download-failure-reason-residual"></a>'
PLAN_REL = "docs/execution/plans/2026-11-17-tts-fp16-guard-ship/"
DELIVERED_HEAD = "> **Delivered (Session 74).**"


def j(*parts: str) -> str:
    """Join string pieces; keeps each source line short."""
    return "".join(parts)


ENTRY = {
    "row_key": "MEU-144",
    "id": "MEU-144",
    "slug": "svc-tts-fp16-guard-ship",
    "phase": "3",
    "band": "P2",
    "matrix_item": "3.21",
    "build_ref": {
        "path": "build-plan/03-service-layer.md",
        "anchor": ANCHOR,
        "text": "Phase 3 §TTS FP16 guard ship (residual)",
    },
    "description": j(
        "ONNX FP16 loads Session 73's guarded graph, built in memory from the user's ",
        "unmodified download and checked by its two hashes, so the sentences that gave ",
        "non-finite audio pass; any other file loads as shipped.",
    ),
    "status": "pending",
    "status_labels": {"registry": "⬜ pending", "build_plan": "⬜"},
    "surface_overrides": None,
    "dependencies_raw": "MEU-127",
    "dependency_parse_status": "parsed",
    "depends_on": ["MEU-127"],
    "execution_plan": PLAN_REL,
    "updated": TODAY,
    "closed_reason": None,
    "note": j(
        "Registered 2026-11-17 in Session 74 from TTS-ONNX-FP16-NONFINITE-AUDIO on D-797 ",
        '(Mat, "Ship guarded") and D-801 (MEU-144 and matrix row 3.21 held for it); ',
        "D-1135 A, plan ",
        PLAN_REL,
        ".",
    ),
}

PHASE_OLD = "matrix row 3.21 is held for Session 74's MEU-144."
PHASE_NEW = (
    "MEU-144 residual (TTS FP16 guard ship) registered 2026-11-17 in Session 74 on matrix row 3.21."
)
P2_OLD = "with MEU-144 held for Session 74"
P2_NEW = "with MEU-144 registered in Session 74"

MATRIX_AFTER = j(
    "| 3.20 | MEU-142 | `svc-download-audio-extract` | ",
    "[03 §Download audio extract (residual)](03-service-layer.md#download-audio-extract-residual)",
    " | MEU-8, MEU-10, MEU-78, MEU-137 |",
)
MATRIX_ROW = j(
    "| 3.21 | MEU-144 | `svc-tts-fp16-guard-ship` | ",
    "[03 §TTS FP16 guard ship (residual)](03-service-layer.md#tts-fp16-guard-ship-residual)",
    " | MEU-127 |",
)
MATRIX_MARK = b"| 3.21 | MEU-144 |"

DOC03_SECTION_LINES = [
    f'<a id="{ANCHOR}"></a>',
    "",
    "## TTS FP16 guard ship (residual)",
    "",
    j(
        "> **MEU-144.** Registered 2026-11-17 in Session 74 from `TTS-ONNX-FP16-NONFINITE-AUDIO` ",
        "on Mat's D-797 and D-801 rulings: the guarded FP16 graph that Session 73 built and Mat ",
        "heard (MEU-127, §TTS FP16 phase guard (residual)) ships, and MEU-144 and matrix row 3.21 ",
        "were held for it. Depends on MEU-127. Plan `",
        PLAN_REL,
        "`.",
    ),
    "",
    "| Rule | Contract | Source |",
    "|------|----------|--------|",
    j(
        "| Ships guarded | Session 73's guarded graph ships: `IsNaN` and `Where` after ",
        "`/decoder/decoder/generator/Div`, so a NaN phase quotient becomes +0. It ships through ",
        "this session's own Red and review, since it changes the adapter. | ",
        "Human-approved: D-797; D-333 |",
    ),
    j(
        "| Delivery | The guarded graph is built in memory each time ONNX FP16 loads, from the ",
        "user's downloaded file, and only when that file has Session 73's size and source hash; ",
        "the result must have Session 73's guarded hash. Any other file, or a splice that fails ",
        "or gives another hash, loads as shipped, and a failed splice logs one `tts.phase_guard` ",
        "warning with no path. Nothing is written to the models folder. | ",
        "Human-approved: D-1136 A |",
    ),
    j(
        "| FP16 stays | FP16 stays offered, and is never preselected while INT8 or FP32 ",
        "can run. | ",
        "Human-approved: D-330, D-331 |",
    ),
    j(
        "| Upstream | Nothing is posted to the model's Hugging Face discussion. | ",
        "Human-approved: D-336 |",
    ),
    j(
        "| Tests | The packaged `--phase sentences` smoke, 149 jobs, on what the app loads: FP16 ",
        "passes 149 of 149 with each WAV equal by job to Session 73's guarded run, and INT8 ",
        "passes 149 of 149 unchanged. | Local Canon |",
    ),
    "",
    "",
]


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def is_crlf(b: bytes) -> bool:
    return (
        b.count(b"\n") == b.count(b"\r\n")
        and b.count(b"\n") > 0
        and b.count(b"\r") == b.count(b"\r\n")
    )


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
    if "MEU-144" in keys:
        raise SystemExit("refused: MEU-144 is already registered")
    if keys.count("MEU-143") != 1 or keys.count("MEU-145") != 1:
        raise SystemExit("refused: MEU-143 or MEU-145 is not found exactly once")
    at = keys.index("MEU-143") + 1
    if keys[at] != "MEU-145":
        raise SystemExit("refused: MEU-145 does not follow MEU-143")
    meus.insert(at, copy.deepcopy(ENTRY))

    phases = [p for p in data["phases"] if p["id"] == "3"]
    if len(phases) != 1:
        raise SystemExit("refused: phase 3 is not found exactly once")
    phase = phases[0]
    if phase["note"].count(PHASE_OLD) != 1 or not phase["note"].endswith(PHASE_OLD):
        raise SystemExit("refused: the phase 3 note does not end with the row-0 held sentence")
    phase["note"] = phase["note"][: -len(PHASE_OLD)] + PHASE_NEW
    phase["last_updated"] = TODAY

    bands = [b for b in data["summary_bands"] if b["key"] == "P2"]
    if len(bands) != 1:
        raise SystemExit("refused: band P2 is not found exactly once")
    rng = bands[0]["range"]
    if rng.count(P2_OLD) != 1:
        raise SystemExit("refused: the P2 range does not hold the row-0 held text once")
    bands[0]["range"] = rng.replace(P2_OLD, P2_NEW)
    return data


def edit_doc03(b: bytes) -> bytes:
    if not is_crlf(b):
        raise SystemExit("refused: 03-service-layer.md is not wholly CRLF")
    if ANCHOR.encode() in b or b"MEU-144" in b:
        raise SystemExit("refused: 03-service-layer.md already has the anchor or MEU-144")
    before = NEXT_ANCHOR + b"\r\n"
    if b.count(before) != 1:
        raise SystemExit(
            "refused: the download-failure-reason-residual anchor is not found exactly once"
        )
    if not b[: b.index(before)].endswith(b"\r\n\r\n"):
        raise SystemExit(
            "refused: no blank line before the download-failure-reason-residual anchor"
        )
    add = "\r\n".join(DOC03_SECTION_LINES).encode("utf-8")
    return b.replace(before, add + before, 1)


def edit_matrix(b: bytes) -> bytes:
    if not is_crlf(b):
        raise SystemExit("refused: build-priority-matrix.md is not wholly CRLF")
    after = MATRIX_AFTER.encode("utf-8") + b"\r\n"
    if b.count(after) != 1:
        raise SystemExit("refused: the 3.20 row is not found exactly once")
    if b"| 3.21 |" in b or b"MEU-144" in b:
        raise SystemExit("refused: the matrix already has 3.21 or MEU-144")
    return b.replace(after, after + MATRIX_ROW.encode("utf-8") + b"\r\n", 1)


def add_delivered(b: bytes, note: str) -> bytes:
    if not is_crlf(b):
        raise SystemExit("refused: 03-service-layer.md is not wholly CRLF")
    head = f'<a id="{ANCHOR}"></a>'.encode()
    if b.count(head) != 1:
        raise SystemExit("refused: the MEU-144 section is not found exactly once")
    if b"Delivered (Session 74)" in b:
        raise SystemExit("refused: a Session 74 Delivered note is already in 03")
    text = note.replace("\r\n", "\n")
    if "\r" in text:
        raise SystemExit("refused: the note file holds a lone CR")
    text = text.strip("\n")
    if not text or not text.startswith(DELIVERED_HEAD):
        raise SystemExit(f"refused: the note is empty or does not start with {DELIVERED_HEAD!r}")
    start = b.index(head)
    end = b.index(NEXT_ANCHOR + b"\r\n", start) if NEXT_ANCHOR + b"\r\n" in b[start:] else -1
    if end < 0:
        raise SystemExit("refused: the MEU-144 section is not followed by the download anchor")
    if not b[:end].endswith(b"\r\n\r\n"):
        raise SystemExit("refused: no blank line ends the MEU-144 section")
    add = text.replace("\n", "\r\n").encode("utf-8") + b"\r\n\r\n"
    return b[:end] + add + b[end:]


def scope_hashes() -> dict:
    return json.loads(SCOPE_JSON.read_text(encoding="utf-8"))


def run(expect: str, dry_run: bool) -> int:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    before = SSOT.read_bytes()
    if sha256(before) != expect:
        print(f"refused: meu-status.yaml sha256 {sha256(before)} != expected {expect}")
        return 1
    scope = scope_hashes()
    raw03 = DOC03.read_bytes()
    rawmx = MATRIX.read_bytes()
    for name, raw, key in (("03", raw03, DOC03_KEY), ("matrix", rawmx, MATRIX_KEY)):
        if sha256(raw) != scope.get(key):
            print(f"refused: {name} sha256 {sha256(raw)} != baseline-scope.json {scope.get(key)}")
            return 1
    if roundtrip_bytes(SSOT) != before:
        print("refused: a load and save of the unchanged register changes its bytes")
        return 1
    new_data = edit_ssot(model.load(SSOT))
    doc03 = edit_doc03(raw03)
    matrix = edit_matrix(rawmx)

    if dry_run:
        out_ssot = SCRATCH / "meu-status.yaml"
        out_doc03 = SCRATCH / "03-service-layer.md"
        out_matrix = SCRATCH / "build-priority-matrix.md"
    else:
        out_ssot, out_doc03, out_matrix = SSOT, DOC03, MATRIX
    model.save(new_data, out_ssot)
    out_doc03.write_bytes(doc03)
    out_matrix.write_bytes(matrix)

    after = out_ssot.read_bytes()
    added = after.count(b"\n") - before.count(b"\n")
    anchors = doc03.count(ANCHOR.encode())
    rows = matrix.count(MATRIX_MARK)
    text = after.decode("utf-8")
    print("mode:", "dry-run" if dry_run else "apply")
    print("meu-status.yaml lines added:", added, "CR bytes:", after.count(b"\r"))
    print("meu-status.yaml sha256:", sha256(after))
    print(
        "held texts left:",
        text.count("held for Session 74"),
        "reworded:",
        text.count("registered in Session 74"),
    )
    print(
        "03-service-layer.md CRLF:", is_crlf(doc03), "anchor count:", anchors, "bytes:", len(doc03)
    )
    print(
        "build-priority-matrix.md CRLF:",
        is_crlf(matrix),
        "MEU-144 rows:",
        rows,
        "bytes:",
        len(matrix),
    )
    loaded = model.load(out_ssot)
    meu = model.get_meu(loaded, "MEU-144")
    keys = [m["row_key"] for m in loaded["meus"]]
    order = keys[keys.index("MEU-143") : keys.index("MEU-143") + 3] if "MEU-143" in keys else None
    ok = (
        meu is not None
        and meu["status"] == "pending"
        and order == ["MEU-143", "MEU-144", "MEU-145"]
        and b"\r" not in after
        and "held for Session 74" not in text
        and is_crlf(doc03)
        and is_crlf(matrix)
        and anchors == 1
        and rows == 1
    )
    shown = (
        None
        if meu is None
        else (meu["status"], meu["phase"], meu["band"], meu["matrix_item"], meu["depends_on"])
    )
    print("MEU-144:", shown, "order:", order)
    print("register-meu-144:", "ok" if ok else "FAILED")
    return 0 if ok else 1


def run_delivered(note_file: Path, dry_run: bool) -> int:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    if not note_file.is_file():
        print(f"refused: no note file {note_file.name}")
        return 1
    raw03 = DOC03.read_bytes()
    new03 = add_delivered(raw03, note_file.read_bytes().decode("utf-8"))
    out = SCRATCH / "03-service-layer-delivered.md" if dry_run else DOC03
    out.write_bytes(new03)
    got = out.read_bytes()
    ok = (
        is_crlf(got)
        and got.count(b"Delivered (Session 74)") == 1
        and got.count(ANCHOR.encode()) == 1
    )
    print("mode:", "dry-run" if dry_run else "apply")
    print("03-service-layer.md bytes:", len(raw03), "->", len(got), "CRLF:", is_crlf(got))
    print("Session 74 note count:", got.count(b"Delivered (Session 74)"), "sha256:", sha256(got))
    print("register-meu-144 --delivered:", "ok" if ok else "FAILED")
    return 0 if ok else 1


def refused(fn, *args) -> bool:
    try:
        fn(*args)
    except SystemExit:
        return True
    return False


def selftest() -> int:
    checks: list[tuple[str, bool]] = []

    def check(name: str, ok: bool) -> None:
        checks.append((name, ok))
        print(f"{name}: {'ok' if ok else 'WRONG'}")

    mx = j("a\r\n", MATRIX_AFTER, "\r\n| 3.22 | MEU-147 | x |\r\n").encode("utf-8")
    out = edit_matrix(mx)
    check("matrix-row-once", out.count(MATRIX_MARK) == 1 and is_crlf(out))
    check("matrix-order", out.index(b"| 3.20 |") < out.index(b"| 3.21 |") < out.index(b"| 3.22 |"))
    check("matrix-second-refused", refused(edit_matrix, out))
    check("matrix-lf-refused", refused(edit_matrix, b"a\n" + MATRIX_AFTER.encode() + b"\n"))
    check("matrix-no-anchor-refused", refused(edit_matrix, b"a\r\nb\r\n"))

    d03 = (
        b"x\r\n\r\n| Tests | y |\r\n\r\n"
        + NEXT_ANCHOR
        + b"\r\n\r\n## Download failure reason (residual)\r\n"
    )
    doc = edit_doc03(d03)
    s = doc.decode("utf-8")
    check("doc03-crlf-anchor-once", is_crlf(doc) and doc.count(ANCHOR.encode()) == 1)
    check(
        "doc03-before-next",
        s.index("## TTS FP16 guard ship (residual)") < s.index("download-failure-reason-residual"),
    )
    check("doc03-blank-before-next", b"| Local Canon |\r\n\r\n" + NEXT_ANCHOR in doc)
    check("doc03-second-refused", refused(edit_doc03, doc))
    check("doc03-lf-refused", refused(edit_doc03, d03.replace(b"\r\n", b"\n")))
    check("doc03-lone-cr-refused", refused(edit_doc03, d03 + b"z\r"))
    check("doc03-no-next-refused", refused(edit_doc03, b"x\r\n\r\n"))
    check("doc03-two-next-refused", refused(edit_doc03, d03 + NEXT_ANCHOR + b"\r\n"))

    note = DELIVERED_HEAD + " MEU-144, plan x.\n> - one\n"
    dd = add_delivered(doc, note)
    t = dd.decode("utf-8")
    check("delivered-once-crlf", is_crlf(dd) and dd.count(b"Delivered (Session 74)") == 1)
    check(
        "delivered-in-section",
        t.index("## TTS FP16 guard ship")
        < t.index("Delivered (Session 74)")
        < t.index("download-failure-reason"),
    )
    check("delivered-blank-before-next", b"> - one\r\n\r\n" + NEXT_ANCHOR in dd)
    check("delivered-second-refused", refused(add_delivered, dd, note))
    check("delivered-no-section-refused", refused(add_delivered, d03, note))
    check("delivered-bad-head-refused", refused(add_delivered, doc, "> **Delivered.** x\n"))
    check("delivered-empty-refused", refused(add_delivered, doc, "\n\n"))
    check("delivered-lone-cr-refused", refused(add_delivered, doc, DELIVERED_HEAD + " a\rb\n"))
    check("delivered-crlf-note", add_delivered(doc, note.replace("\n", "\r\n")) == dd)

    data = {
        "phases": [
            {
                "id": "3",
                "note": "x registered 2026-11-15; " + PHASE_OLD,
                "last_updated": "2026-11-15",
            }
        ],
        "meus": [{"row_key": "MEU-142"}, {"row_key": "MEU-143"}, {"row_key": "MEU-145"}],
        "summary_bands": [{"key": "P2", "range": "MEU-14–159 (a; MEU-145–154, " + P2_OLD + "; b)"}],
    }
    new = edit_ssot(data)
    keys = [m["row_key"] for m in new["meus"]]
    check("ssot-order", keys == ["MEU-142", "MEU-143", "MEU-144", "MEU-145"])
    phase = new["phases"][0]
    check(
        "ssot-phase-note",
        phase["note"] == "x registered 2026-11-15; " + PHASE_NEW and phase["last_updated"] == TODAY,
    )
    rng = new["summary_bands"][0]["range"]
    check("ssot-p2-range", rng == "MEU-14–159 (a; MEU-145–154, " + P2_NEW + "; b)")
    check(
        "ssot-input-unchanged",
        len(data["meus"]) == 3 and data["phases"][0]["note"].endswith(PHASE_OLD),
    )
    check("ssot-second-refused", refused(edit_ssot, new))
    gap = copy.deepcopy(data)
    gap["meus"].insert(2, {"row_key": "MEU-150"})
    check("ssot-gap-refused", refused(edit_ssot, gap))
    tail = copy.deepcopy(data)
    tail["phases"][0]["note"] = PHASE_OLD + " more."
    check("ssot-note-not-last-refused", refused(edit_ssot, tail))
    nop2 = copy.deepcopy(data)
    nop2["summary_bands"][0]["range"] = "MEU-14–159 (a)"
    check("ssot-p2-missing-refused", refused(edit_ssot, nop2))
    check(
        "entry-shape",
        ENTRY["band"] == "P2" and ENTRY["matrix_item"] == "3.21" and ENTRY["phase"] == "3",
    )
    wrong = [n for n, ok in checks if not ok]
    print(f"register-meu-144 selftest: {len(checks)} case(s), {len(wrong)} wrong: {wrong}")
    return 1 if wrong else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--expect-sha256")
    ap.add_argument("--delivered", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.delivered is not None:
        return run_delivered(a.delivered, a.dry_run)
    if not a.expect_sha256:
        ap.error("--expect-sha256 is required")
    return run(a.expect_sha256, a.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
