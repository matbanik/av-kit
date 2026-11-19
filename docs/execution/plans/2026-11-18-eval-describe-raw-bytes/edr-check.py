"""Session 95 (eval-describe-raw-bytes) plan-local checks for the describe capture.

The guard is Session 92's: MOJIBAKE, CUT and build() come from
docs/execution/plans/2026-11-17-mcp-audit-refresh/eval-rerun.py (D-1186); this file holds no
second pattern.

    old E1 STEP3FORM          both old-redirect reproductions must show mojibake (row 1, AC-8)
    live RECEIPT ROOT OUT     an independent npx read on another root; RECEIPT must equal it,
                              be clean and keep its tail after CUT (AC-9)
    doc RECEIPT               eval-run.md is its row-0 bytes plus the note and new step 3 (AC-10)
    records [--record]        the record files keep their SHA-256; both selftests pass (AC-11)
    --selftest                the pure functions on fixtures

Run with `uv run python` (eval-check.py imports PIL). Output is ASCII. Exit 0 when every check
passes, 1 when one fails, 2 on a usage or input error or when Session 92's guard cannot load.
The guard loads with bytecode writing off, so no .pyc lands in Session 92's folder.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
PLAN = Path(__file__).resolve().parent
S64 = REPO / "docs/execution/plans/2026-11-11-capture-export-copy"
S92 = REPO / "docs/execution/plans/2026-11-17-mcp-audit-refresh"
EVAL_RUN = S64 / "eval-run.md"
EVAL_RUN_REL = "docs/execution/plans/2026-11-11-capture-export-copy/eval-run.md"
MCP_DIR = REPO / "mcp-server"
HARNESS_REL = "../docs/execution/plans/2026-11-11-capture-export-copy/eval-harness.ts"
D = Path("C:/Temp/av-kit/eval-describe-raw-bytes")
COPIES = D / "baseline-copies"
BASE = "C:/Temp/av-kit/s64/eval/"
S64_RECEIPT = "C:/Temp/av-kit/s64-E1-describe.txt"
RECORDS_FILE = PLAN / "baseline-records.json"
RECORDS = (
    "docs/execution/plans/2026-11-17-mcp-audit-refresh/eval-rerun.py",
    "docs/execution/plans/2026-11-17-mcp-audit-refresh/capture-description.expected.txt",
    "docs/execution/plans/2026-11-11-capture-export-copy/eval-check.py",
    "docs/execution/plans/2026-11-11-capture-export-copy/eval-harness.ts",
    "docs/execution/plans/2026-11-11-capture-export-copy/eval-seed.py",
    "docs/execution/plans/2026-11-11-capture-export-copy/task.md",
    "docs/execution/plans/2026-11-11-capture-export-copy/implementation-plan.md",
    "mcp-server/scripts/audit/backend.ts",
    S64_RECEIPT,
)
TIMEOUT_S = 300
ARROW = "\u2192"
DASH = "\u2013"
MOJ_ARROW = "\u0393\u00e5\u00c6"  # E2 86 92 read through cp437
MOJ_DASH = "\u0393\u00c7\u00f4"  # E2 80 93 read through cp437
STEP3_HEAD = "3. **Describe.**"
STEP3 = (
    "3. **Describe.** Run `uv run python docs/execution/plans/2026-11-11-capture-export-copy/"
    "eval-describe.py capture C:/Temp/av-kit/s64/eval/<label>/root <receipt>`, with a new "
    "`<label>` (Session 64 used `describe`) and a `<receipt>` path that does not exist yet. Step 2 "
    "builds first. It runs `eval-harness.ts` `describe` from `mcp-server` in a subprocess and "
    "writes the server's stdout bytes to `<receipt>` unchanged, and its stderr to "
    "`<receipt>.stderr.txt`. It refuses output that is not UTF-8 or holds a BOM, a CR byte or "
    "cp437 mojibake, or lacks exactly one CUT line: it exits 1 with a named reason, writes no "
    "receipt and keeps the bytes as `<receipt>.refused`. It never overwrites a file (exit 2). "
    "Never capture `describe` through a shell redirect: a PowerShell redirect that merges stderr "
    "decodes the bytes through the console code page, and older PowerShell decodes every "
    "redirect."
)
TAIL_HEAD = "## avkit_convert action notes"
NOTE = (
    "> Changed 2026-11-18 (Session 95, issue `EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE`): step 3 used "
    "to capture `describe` with a shell redirect. PowerShell decoded the server's UTF-8 through "
    "the console code page (cp437), so Session 64's receipt holds 9 mojibake arrows and 2 "
    "mojibake en dashes and no real one, and the eval prompts built from it read that text. "
    "Step 3 now runs `eval-describe.py`, which keeps the raw bytes and refuses mojibake with the "
    "guard from Session 92's `eval-rerun.py` (D-1186). Session 64's task rows and receipts are "
    "kept as they ran."
)


GUARD_PATH = S92 / "eval-rerun.py"
GUARD_ERRORS = (ImportError, OSError, SyntaxError)


def load_guard(path: Path = GUARD_PATH):
    """Session 92's eval-rerun.py as a module; no .pyc is written into its folder."""
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("s92_eval_rerun", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path.as_posix()}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    missing = [n for n in ("MOJIBAKE", "CUT", "build") if not hasattr(module, n)]
    if missing:
        raise ImportError(f"{path.as_posix()} lacks {missing}")
    return module


try:
    GUARD = load_guard()
    GUARD_ERROR = ""
except GUARD_ERRORS as exc:
    GUARD, GUARD_ERROR = None, f"{GUARD_PATH.as_posix()}: {type(exc).__name__}: {exc}"
MOJIBAKE = GUARD.MOJIBAKE if GUARD else None
CUT = GUARD.CUT if GUARD else ""


def decode_receipt(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")
    return raw.decode("utf-8")


def analyse_old(text: str) -> dict[str, int]:
    """Counts in an old-redirect receipt, with rtk notice lines dropped and CRLF normalised."""
    lines = [ln for ln in text.replace("\r\n", "\n").split("\n") if not ln.startswith("[rtk]")]
    body = "\n".join(lines)
    return {
        "mojibake": len(MOJIBAKE.findall(body)),
        "moj_arrows": body.count(MOJ_ARROW),
        "moj_dashes": body.count(MOJ_DASH),
        "arrows": body.count(ARROW),
        "dashes": body.count(DASH),
        "cut": lines.count(CUT),
    }


def cp437_trap(data: bytes) -> int:
    """MOJIBAKE matches in the bytes as a cp437 console would decode them."""
    return len(MOJIBAKE.findall(data.decode("cp437")))


def expected_doc(base_text: str) -> str:
    """eval-run.md's row-0 text with the dated note after the intro and step 3 replaced."""
    lines = base_text.split("\n")
    heads = [i for i, ln in enumerate(lines) if ln.startswith(STEP3_HEAD)]
    if len(heads) != 1:
        raise ValueError(f"expected one step 3 line, found {len(heads)}")
    lines[heads[0]] = STEP3
    return "\n".join(lines[:6] + ["", NOTE] + lines[6:])


def live_findings(
    receipt: bytes, direct: bytes, plan_text: str, transcript: str, expected: str
) -> list[tuple[str, bool, str]]:
    out: list[tuple[str, bool, str]] = [
        ("equal-direct", receipt == direct, f"receipt {len(receipt)} B, direct {len(direct)} B")
    ]
    try:
        text = receipt.decode("utf-8")
    except UnicodeDecodeError as exc:
        return out + [("utf8", False, f"not UTF-8 at byte {exc.start}")]
    out.append(("utf8", True, "strict decode"))
    out.append(("no-bom", not text.startswith("\ufeff"), "first char checked"))
    crs = receipt.count(b"\r")
    out.append(("no-cr", crs == 0, f"CR bytes {crs}"))
    moj = len(MOJIBAKE.findall(text))
    out.append(("no-mojibake", moj == 0, f"MOJIBAKE matches {moj}"))
    bad = text.count(MOJ_ARROW) + text.count(MOJ_DASH)
    out.append(("no-moj-sequences", bad == 0, f"mojibake arrows and dashes {bad}"))
    arrows, dashes = text.count(ARROW), text.count(DASH)
    out.append(("real-text", arrows >= 2 and dashes >= 2, f"arrows {arrows}, en dashes {dashes}"))
    parts = text.split("\n")
    cuts = parts.count(CUT)
    out.append(("cut-once", cuts == 1, f"CUT lines {cuts}"))
    tail = parts[parts.index(CUT) + 1 :] if cuts == 1 else []
    whole = TAIL_HEAD in tail and text.endswith("\n")
    out.append(("tail-kept", whole, f"{TAIL_HEAD!r} after CUT and a final LF: {whole}"))
    trap = cp437_trap(receipt)
    out.append(("cp437-trap", trap >= 1, f"MOJIBAKE matches after a cp437 decode {trap}"))
    try:
        prompts = GUARD.build(plan_text, text, transcript, expected)
    except ValueError as exc:
        return out + [("build", False, ascii(str(exc)))]
    clean = all(not MOJIBAKE.search(p) and expected in p for p in prompts.values())
    out.append(("build", len(prompts) == 3 and clean, f"{len(prompts)} prompts, clean {clean}"))
    return out


def show(findings: list[tuple[str, bool, str]]) -> int:
    for name, ok, detail in findings:
        print(f"{'PASS' if ok else 'FAIL'} {name}: {detail}")
    failed = [n for n, ok, _ in findings if not ok]
    print(f"edr-check: {len(findings) - len(failed)} pass, {len(failed)} fail {failed}")
    return 1 if failed else 0


def reproduced(counts: dict[str, int]) -> bool:
    return counts["mojibake"] >= 1 and counts["cut"] == 1


def cmd_old(e1: Path, step3: Path) -> int:
    missing = [p.as_posix() for p in (e1, step3) if not p.is_file()]
    if missing:
        print(f"usage: missing {missing}")
        return 2
    failed = []
    for label, path in (("e1", e1), ("step3", step3)):
        raw = path.read_bytes()
        counts = analyse_old(decode_receipt(raw))
        ok = reproduced(counts)
        print(f"{label}: {len(raw)} B {json.dumps(counts, sort_keys=True)}")
        print(f"old: {label} -> {'reproduced' if ok else 'NOT reproduced'}")
        if not ok:
            failed.append(label)
    print(f"old: {2 - len(failed)} of 2 forms reproduced, not {failed}")
    return 1 if failed else 0


def kill_tree(proc: subprocess.Popen) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
    else:
        proc.kill()


def direct_read(root: str, out: Path) -> bytes:
    npx = shutil.which("npx.cmd") or shutil.which("npx")
    if npx is None:
        raise ValueError("npx is not on PATH")
    env = {k: v for k, v in os.environ.items() if k != "ELECTRON_RUN_AS_NODE"}
    argv = [npx, "tsx", HARNESS_REL, root, "describe"]
    proc = subprocess.Popen(
        argv, cwd=MCP_DIR, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    try:
        stdout, stderr = proc.communicate(timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        kill_tree(proc)
        proc.communicate()
        raise ValueError(f"the direct read timed out after {TIMEOUT_S} s") from None
    with open(str(out) + ".stderr.txt", "xb") as fh:
        fh.write(stderr)
    with open(out, "xb") as fh:
        fh.write(stdout)
    if proc.returncode != 0:
        raise ValueError(f"the direct read exited {proc.returncode}")
    return stdout


def cmd_live(receipt: Path, root: str, out: Path) -> int:
    norm = root.replace("\\", "/")
    if not norm.lower().startswith(BASE.lower()) or Path(root).exists():
        print(f"usage: the direct root must be new and under {BASE}")
        return 2
    side = [Path(str(receipt) + ".stderr.txt"), Path(str(receipt) + ".refused")]
    if not receipt.is_file() or out.exists():
        print("usage: the receipt must exist and the direct output must not")
        return 2
    direct = direct_read(root, out)
    plan_text = EVAL_RUN.read_text(encoding="utf-8")
    transcript = GUARD.TRANSCRIPT.read_text(encoding="utf-8").strip("\n")
    expected = GUARD.EXPECTED.read_bytes().decode("utf-8")
    findings = live_findings(receipt.read_bytes(), direct, plan_text, transcript, expected)
    findings.append(("stderr-file", side[0].is_file(), side[0].name))
    findings.append(("no-refused", not side[1].exists(), side[1].name))
    return show(findings)


def cmd_doc(receipt: Path) -> int:
    base = COPIES / EVAL_RUN_REL
    if not base.is_file() or not receipt.is_file():
        print("usage: the row-0 copy of eval-run.md and the receipt must exist")
        return 2
    now = EVAL_RUN.read_bytes()
    want = expected_doc(base.read_bytes().decode("utf-8")).encode("utf-8")
    crs = now.count(b"\r")
    findings = [
        ("exact-bytes", now == want, f"now {len(now)} B, expected {len(want)} B"),
        ("lf-only", crs == 0, f"CR bytes {crs}"),
        ("ascii-note", NOTE.isascii() and STEP3.isascii(), "note and step 3"),
    ]
    transcript = GUARD.TRANSCRIPT.read_text(encoding="utf-8").strip("\n")
    expected = GUARD.EXPECTED.read_bytes().decode("utf-8")
    try:
        describe = receipt.read_text(encoding="utf-8")
        prompts = GUARD.build(now.decode("utf-8"), describe, transcript, expected)
        findings.append(("build-new-text", len(prompts) == 3, f"{len(prompts)} prompts"))
    except ValueError as exc:
        findings.append(("build-new-text", False, ascii(str(exc))))
    return show(findings)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(rel: str) -> Path:
    return Path(rel) if rel.startswith("C:/") else REPO / rel


def cmd_records(record: bool) -> int:
    now = {rel: sha(resolve(rel)) if resolve(rel).is_file() else "absent" for rel in RECORDS}
    findings = []
    if record:
        if RECORDS_FILE.exists():
            print(f"usage: {RECORDS_FILE.name} exists; it is written once at row 0")
            return 2
        RECORDS_FILE.write_bytes((json.dumps(now, indent=2) + "\n").encode("utf-8"))
        findings.append(("recorded", "absent" not in now.values(), f"{len(now)} files"))
    else:
        base = json.loads(RECORDS_FILE.read_text(encoding="utf-8"))
        changed = sorted(r for r in set(base) | set(now) if base.get(r) != now.get(r))
        findings.append(("records-unchanged", not changed, f"changed {changed}"))
    selftests = (("eval-rerun", S92 / "eval-rerun.py"), ("eval-check", S64 / "eval-check.py"))
    for name, path in selftests:
        proc = subprocess.run([sys.executable, str(path), "--selftest"], capture_output=True)
        tail = proc.stdout.decode("utf-8", "replace").strip().splitlines()[-1:]
        findings.append((f"{name}-selftest", proc.returncode == 0, ascii(tail)))
    return show(findings)


def selftest() -> int:
    global GUARD, GUARD_ERROR
    failures = []

    def expect(label: str, cond: bool) -> None:
        print(f"{'ok' if cond else 'FAIL'} {label}")
        if not cond:
            failures.append(label)

    clean = f"## Server instructions\n\nA {ARROW} B {DASH} C {ARROW} D {DASH}\n{CUT}\n- x: y\n"
    data = clean.encode("utf-8")
    moj = data.decode("cp437")
    expect("cp437 decode makes the sequences", MOJ_ARROW in moj and MOJ_DASH in moj)
    expect("trap fires on clean bytes", cp437_trap(data) >= 4)
    expect("trap is quiet on ASCII", cp437_trap(b"plain\n") == 0)
    a = analyse_old("[rtk] note\r\n" + moj.replace("\n", "\r\n"))
    expect("old: rtk dropped, CRLF normalised", a["cut"] == 1 and a["mojibake"] >= 4)
    expect("old: counts", a["moj_arrows"] == 2 and a["moj_dashes"] == 2 and a["arrows"] == 0)
    expect("old: clean text has none", analyse_old(clean)["mojibake"] == 0)
    base = "\n".join(f"intro {i}" for i in range(6)) + "\n\nPaths:\n3. **Describe.** old > f\n- a\n"
    doc = expected_doc(base)
    lines = doc.split("\n")
    expect("doc: note after the intro", lines[6] == "" and lines[7] == NOTE and lines[8] == "")
    expect("doc: step 3 replaced", STEP3 in lines and "old > f" not in doc)
    expect("doc: the rest kept", doc.endswith("\n- a\n") and lines[:6] == base.split("\n")[:6])
    try:
        expected_doc(base.replace("3. **Describe.**", "3. Describe"))
        expect("doc: missing step 3 refused", False)
    except ValueError:
        expect("doc: missing step 3 refused", True)
    expect("note and step 3 are ASCII", NOTE.isascii() and STEP3.isascii())
    expect("note has no text block", "```" not in NOTE and "```" not in STEP3)
    exp = "EXPECTED TEXT"
    surface = f"## i\n\nA {ARROW} B {DASH} C {ARROW} D {DASH}\n{GUARD.LEAD} {GUARD.ZOOM}\n{exp}\n"
    notes = f"\n{CUT}\n\n- avkit_capture.crop: c\n\n{TAIL_HEAD}\n\n- avkit_convert.x: y\n"
    receipt = (surface + notes).encode("utf-8")
    plan = "\n".join(f"```text\nB{i} {{{{DESCRIBE}}}} {{{{ROOT}}}}\n```" for i in range(4))
    good = live_findings(receipt, receipt, plan, "T", exp)
    expect("live: clean receipt passes", all(ok for _, ok, _ in good) and len(good) == 11)
    cut_off = receipt[: receipt.index(TAIL_HEAD.encode())]
    bad = dict((n, ok) for n, ok, _ in live_findings(cut_off, cut_off, plan, "T", exp))
    expect("live: a clean but truncated capture fails", not bad["tail-kept"])
    expect("old: both counts needed", reproduced(a) and not reproduced(analyse_old(clean)))
    bad = dict((n, ok) for n, ok, _ in live_findings(receipt, receipt + b"x", plan, "T", exp))
    expect("live: byte difference fails", not bad["equal-direct"])
    m = receipt.decode("cp437").encode("utf-8")
    bad = dict((n, ok) for n, ok, _ in live_findings(m, m, plan, "T", exp))
    expect("live: mojibake fails", not bad["no-mojibake"] and not bad["build"])
    crlf = receipt.replace(b"\n", b"\r\n")
    bad = dict((n, ok) for n, ok, _ in live_findings(crlf, crlf, plan, "T", exp))
    expect("live: CR fails", not bad["no-cr"])
    bad = dict((n, ok) for n, ok, _ in live_findings(b"\xff\xfe", b"\xff\xfe", plan, "T", exp))
    expect("live: not UTF-8 fails", bad.get("utf8") is False)
    plain = receipt.replace(ARROW.encode(), b"->").replace(DASH.encode(), b"-")
    bad = dict((n, ok) for n, ok, _ in live_findings(plain, plain, plan, "T", exp))
    expect("live: no real arrow or dash fails", not bad["real-text"] and not bad["cp437-trap"])
    expect("guard is Session 92's", MOJIBAKE is GUARD.MOJIBAKE and CUT == GUARD.CUT)
    expect("guard path is Session 92's file", Path(GUARD.__file__).resolve() == GUARD_PATH)
    expect("guard loaded with bytecode writing off", sys.dont_write_bytecode is True)
    try:
        load_guard(PLAN / "no-such-eval-rerun.py")
        expect("guard: a missing file raises", False)
    except GUARD_ERRORS:
        expect("guard: a missing file raises", True)
    kept = GUARD, GUARD_ERROR
    GUARD, GUARD_ERROR = None, "no-such-eval-rerun.py: FileNotFoundError: x"
    sink = io.StringIO()
    try:
        with contextlib.redirect_stdout(sink):
            code = main(["old", "a", "b"])
    finally:
        GUARD, GUARD_ERROR = kept
    said = sink.getvalue()
    expect("guard: not loaded exits 2", code == 2 and said.startswith("error: guard not loaded"))
    expect("guard: the message is ASCII, no traceback", said.isascii() and "Traceback" not in said)
    print(f"selftest: {len(failures)} failures")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--record", action="store_true")
    parser.add_argument("command", nargs="?", choices=["old", "live", "doc", "records"])
    parser.add_argument("args", nargs="*")
    args = parser.parse_args(argv)
    if GUARD is None:
        print(f"error: guard not loaded: {ascii(GUARD_ERROR)}")
        return 2
    try:
        if args.selftest:
            return selftest()
        if args.command == "old" and len(args.args) == 2:
            return cmd_old(Path(args.args[0]), Path(args.args[1]))
        if args.command == "live" and len(args.args) == 3:
            return cmd_live(Path(args.args[0]), args.args[1], Path(args.args[2]))
        if args.command == "doc" and len(args.args) == 1:
            return cmd_doc(Path(args.args[0]))
        if args.command == "records" and not args.args:
            return cmd_records(args.record)
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        print(f"error: {ascii(str(exc))}")
        return 2
    parser.print_usage()
    return 2


if __name__ == "__main__":
    sys.exit(main())
