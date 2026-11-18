"""Session 74 packaged-smoke checks (task rows 2, 3, 7 and 8, and the gate's
``smoke-check-selftest`` step; implementation-plan.md §Verification Plan 3).

Modes, each exiting 0 only when every check holds:

* ``copies --run RUN_DIR --models DIR``: ``RUN_DIR/avkit-backend/avkit-backend.exe`` is a file
  and ``_internal`` a folder; no ``torch``, ``kokoro``, ``phonemizer`` or ``espeakng_loader``
  folder is directly under ``_internal`` (Session 73 row 1's check); the FP16 file in DIR has
  SHA-256 ``ba4527a8…`` and 163,234,740 bytes.
* ``control SMOKE_JSON``: ``passed`` is false, ``jobs`` is 149, ``variant_id`` is
  ``kokoro-onnx-fp16``, there are 12 failures, each "generated audio must be finite", the failure
  set by ``(kind, index, voice)`` equals both Session 52's and Session 73's control smoke JSONs,
  ``errors`` and ``forbidden_dirs`` are empty and ``proxy.HTTPS_PROXY`` is the dead proxy
  (AC-144.13).
* ``green SMOKE_JSON --variant ID``: ``passed`` is true, ``jobs`` is 149, ``failures``,
  ``errors`` and ``forbidden_dirs`` are empty, the variant matches and the dead proxy is set
  (AC-144.14, AC-144.15).
* ``wavs RUN_DIR --against S73_RUN --expect-done N --out JSON``: copies each run's
  ``app-data/avkit.db*`` under ``tmp/wavs-db/`` (never opened in place), keys rows by
  ``(text_hash, voice)`` (``WAV_BY_JOB``: an output name carries a collision suffix, so a name is
  not a job), requires 149 keys with one row each in both runs, the same keys ``Done`` in both,
  exactly N of them, each Done WAV inside its own run folder and byte-equal across the runs;
  for N 149 every key is Done.
* ``snapshot DIR --out JSON`` and ``snapshot DIR --compare JSON``: each file's relative path,
  size, SHA-256 and ``st_mtime_ns``; compare exits 0 only on equality, no file added or removed
  (``NO_FILE_WRITE``).
* ``--selftest``: every mode on synthetic JSON, SQLite and folder fixtures in a scratch folder.

Reads only; writes the ``--out`` file and the database copies. Run from the repository root.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any

SCRATCH = Path("C:/Temp/av-kit/tts-fp16-guard-ship")
DB_COPIES = SCRATCH / "tmp" / "wavs-db"
FP16_REL = "kokoro-v1.0-onnx/onnx/model_fp16.onnx"
FP16_SHA256 = "ba4527a874b42b21e35f468c10d326fdff3c7fc8cac1f85e9eb6c0dfc35c334a"
FP16_BYTES = 163234740
FORBIDDEN = ("torch", "kokoro", "phonemizer", "espeakng_loader")
JOBS = 149
FINITE = "generated audio must be finite"
DEAD_PROXY = "http://127.0.0.1:9"
CONTROL_REFS = (
    Path("C:/Temp/av-kit/s52-smoke-red.json"),
    Path("C:/Temp/av-kit/s73-smoke-control.json"),
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def report(mode: str, checks: dict[str, Any]) -> int:
    ok = all(v is True for v in checks.values())
    for name, value in checks.items():
        print(f"{mode} {name}: {value}")
    print(f"smoke-check {mode}: {'pass' if ok else 'FAIL'}")
    return 0 if ok else 1


def copies_checks(
    run: Path, models: Path, want_sha: str = FP16_SHA256, want_bytes: int = FP16_BYTES
) -> dict[str, Any]:
    backend = run / "avkit-backend"
    internal = backend / "_internal"
    fp16 = models / FP16_REL
    found = [n for n in FORBIDDEN if (internal / n).is_dir()]
    return {
        "exe": (backend / "avkit-backend.exe").is_file(),
        "internal": internal.is_dir(),
        "no_forbidden": True if not found else f"found {found}",
        "fp16_bytes": True
        if fp16.is_file() and fp16.stat().st_size == want_bytes
        else f"{fp16.stat().st_size if fp16.is_file() else 'missing'}",
        "fp16_sha256": True if fp16.is_file() and sha256(fp16) == want_sha else "differs",
    }


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def failure_keys(data: dict[str, Any]) -> list[tuple[str, int, str]]:
    return sorted((f["kind"], f["index"], f["voice"]) for f in data.get("failures", []))


def _common(data: dict[str, Any], variant: str) -> dict[str, Any]:
    proxy = (data.get("proxy") or {}).get("HTTPS_PROXY")
    return {
        "jobs": True if data.get("jobs") == JOBS else data.get("jobs"),
        "variant": True if data.get("variant_id") == variant else data.get("variant_id"),
        "errors_empty": True if data.get("errors") == [] else data.get("errors"),
        "forbidden_dirs_empty": True
        if data.get("forbidden_dirs") == []
        else data.get("forbidden_dirs"),
        "dead_proxy": True if proxy == DEAD_PROXY else proxy,
    }


def control_checks(data: dict[str, Any], refs: list[dict[str, Any]]) -> dict[str, Any]:
    failures = data.get("failures", [])
    keys = failure_keys(data)
    checks: dict[str, Any] = {
        "passed_false": True if data.get("passed") is False else f"passed={data.get('passed')}"
    }
    checks.update(_common(data, "kokoro-onnx-fp16"))
    checks["failures_12"] = True if len(failures) == 12 else len(failures)
    other = sorted({f.get("error_message") for f in failures} - {FINITE})
    checks["all_not_finite"] = True if not other else f"other messages {other}"
    for n, ref in enumerate(refs):
        checks[f"same_failures_as_ref{n}"] = (
            True if keys == failure_keys(ref) else f"differs: {keys} vs {failure_keys(ref)}"
        )
    return checks


def green_checks(data: dict[str, Any], variant: str) -> dict[str, Any]:
    checks: dict[str, Any] = {
        "passed_true": True if data.get("passed") is True else data.get("passed")
    }
    checks.update(_common(data, variant))
    failures = data.get("failures")
    checks["failures_empty"] = True if failures == [] else failures
    return checks


def run_rows(run: Path, copy_dir: Path) -> dict[tuple[str, str], list[tuple[str, str | None]]]:
    """The run's tts_jobs rows by (text_hash, voice), read from a copy of its database."""
    if copy_dir.exists():
        shutil.rmtree(copy_dir)
    copy_dir.mkdir(parents=True)
    for path in sorted((run / "app-data").glob("avkit.db*")):
        shutil.copy2(path, copy_dir / path.name)
    if not (copy_dir / "avkit.db").is_file():
        raise SystemExit(f"FAIL: no avkit.db under {run.as_posix()}/app-data")
    rows: dict[tuple[str, str], list[tuple[str, str | None]]] = {}
    db = sqlite3.connect(copy_dir / "avkit.db")
    try:
        for text_hash, voice, status, output in db.execute(
            "SELECT text_hash, voice, status, output_path FROM tts_jobs"
        ):
            rows.setdefault((text_hash, voice), []).append((status, output))
    finally:
        db.close()
    return rows


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def wav_checks(
    run: Path, against: Path, expect_done: int, copies: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    ours = run_rows(run, copies / "ours")
    theirs = run_rows(against, copies / "against")
    checks: dict[str, Any] = {
        "jobs_ours": True if len(ours) == JOBS else len(ours),
        "jobs_against": True if len(theirs) == JOBS else len(theirs),
        "same_keys": True if set(ours) == set(theirs) else "the two runs hold different keys",
    }
    not_one = sorted(
        f"{label} {k[0]}:{k[1]} rows={len(v)}"
        for label, rows in (("ours", ours), ("against", theirs))
        for k, v in rows.items()
        if len(v) != 1
    )
    checks["one_row_per_key"] = True if not not_one else not_one
    done_ours = {k for k, v in ours.items() if len(v) == 1 and v[0][0] == "Done"}
    done_theirs = {k for k, v in theirs.items() if len(v) == 1 and v[0][0] == "Done"}
    checks["same_done_keys"] = (
        True
        if done_ours == done_theirs
        else f"ours only {len(done_ours - done_theirs)}, theirs only {len(done_theirs - done_ours)}"
    )
    checks["done_count"] = (
        True
        if len(done_ours) == expect_done == len(done_theirs)
        else [len(done_ours), len(done_theirs)]
    )
    if expect_done == JOBS:
        checks["every_key_done"] = True if len(done_ours) == len(ours) == JOBS else len(done_ours)
    by_key: dict[str, Any] = {}
    differ: list[str] = []
    outside: list[str] = []
    for key in sorted(done_ours & done_theirs):
        a, b = Path(str(ours[key][0][1])), Path(str(theirs[key][0][1]))
        if not _inside(a, run):
            outside.append(f"ours {key[0]}:{key[1]}")
        if not _inside(b, against):
            outside.append(f"against {key[0]}:{key[1]}")
        sa = sha256(a) if a.is_file() else None
        sb = sha256(b) if b.is_file() else None
        by_key[f"{key[0]}:{key[1]}"] = {"ours": sa, "against": sb}
        if sa is None or sa != sb:
            differ.append(f"{key[0]}:{key[1]}")
    checks["wavs_inside_their_run"] = True if not outside else outside
    checks["wavs_byte_equal"] = True if not differ else differ
    payload = {
        "run": run.as_posix(),
        "against": against.as_posix(),
        "jobs": len(ours),
        "done": {"ours": len(done_ours), "against": len(done_theirs)},
        "equal": len(by_key) - len(differ),
        "checks": checks,
        "by_key": by_key,
    }
    return checks, payload


def snapshot(root: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        st = path.stat()
        out[path.relative_to(root).as_posix()] = {
            "bytes": st.st_size,
            "sha256": sha256(path),
            "mtime_ns": st.st_mtime_ns,
        }
    return out


def snapshot_compare(now: dict[str, Any], before: dict[str, Any]) -> dict[str, Any]:
    added = sorted(set(now) - set(before))
    removed = sorted(set(before) - set(now))
    changed = sorted(k for k in set(now) & set(before) if now[k] != before[k])
    return {
        "files": True if now and len(now) == len(before) else [len(now), len(before)],
        "none_added": True if not added else added,
        "none_removed": True if not removed else removed,
        "none_changed": True if not changed else changed,
    }


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(payload, indent=1) + "\n").encode("utf-8"))


# --- selftest -----------------------------------------------------------------------------


def _smoke(passed: bool, failures: list[tuple[str, int, str, str]], **over: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "passed": passed,
        "jobs": JOBS,
        "variant_id": "kokoro-onnx-fp16",
        "failures": [
            {"kind": k, "index": i, "voice": v, "status": "Failed", "error_message": m}
            for k, i, v, m in failures
        ],
        "errors": [],
        "forbidden_dirs": [],
        "proxy": {"HTTPS_PROXY": DEAD_PROXY},
    }
    data.update(over)
    return data


def _make_run(root: Path, jobs: list[tuple[str, str, str, bytes | None]], extra: int = 0) -> Path:
    """A run folder with app-data/avkit.db and out/ WAVs; EXTRA repeats the first job's row."""
    (root / "app-data").mkdir(parents=True)
    (root / "out").mkdir()
    db = sqlite3.connect(root / "app-data" / "avkit.db")
    db.execute("CREATE TABLE tts_jobs (text_hash TEXT, voice TEXT, status TEXT, output_path TEXT)")
    for n, (text_hash, voice, status, wav) in enumerate(jobs):
        out = None
        if wav is not None:
            target = root / "out" / f"job-{n}.wav"
            target.write_bytes(wav)
            out = str(target)
        db.execute("INSERT INTO tts_jobs VALUES (?, ?, ?, ?)", (text_hash, voice, status, out))
    for _ in range(extra):
        db.execute("INSERT INTO tts_jobs VALUES (?, ?, ?, ?)", (*jobs[0][:3], None))
    db.commit()
    db.close()
    return root


def selftest() -> int:
    wrong: list[str] = []
    cases = 0

    def expect(name: str, checks: dict[str, Any], want: bool) -> None:
        nonlocal cases
        cases += 1
        got = all(v is True for v in checks.values())
        bad = [f"{k}={v}" for k, v in checks.items() if v is not True][:1]
        print(
            f"{name}: {'pass' if got else 'refused'} "
            f"(expected {'pass' if want else 'refused'}) {bad}"
        )
        if got != want:
            wrong.append(name)

    twelve = [("sentence", i, "af_heart", FINITE) for i in range(12)]
    ref = _smoke(False, twelve)
    expect("control-ok", control_checks(_smoke(False, twelve), [ref, ref]), True)
    expect("control-passed", control_checks(_smoke(True, twelve), [ref, ref]), False)
    expect("control-eleven", control_checks(_smoke(False, twelve[:11]), [ref, ref]), False)
    other_msg = [*twelve[:11], ("sentence", 11, "af_heart", "boom")]
    expect("control-other-message", control_checks(_smoke(False, other_msg), [ref, ref]), False)
    moved = [*twelve[:11], ("sentence", 40, "af_heart", FINITE)]
    expect("control-other-job", control_checks(_smoke(False, moved), [ref, ref]), False)
    expect(
        "control-int8",
        control_checks(_smoke(False, twelve, variant_id="kokoro-onnx-int8"), [ref]),
        False,
    )
    expect("control-live-proxy", control_checks(_smoke(False, twelve, proxy={}), [ref]), False)
    expect("control-errors", control_checks(_smoke(False, twelve, errors=["x"]), [ref]), False)
    expect(
        "control-forbidden",
        control_checks(_smoke(False, twelve, forbidden_dirs=["torch"]), [ref]),
        False,
    )
    expect("control-148-jobs", control_checks(_smoke(False, twelve, jobs=148), [ref]), False)
    expect("green-ok", green_checks(_smoke(True, []), "kokoro-onnx-fp16"), True)
    expect(
        "green-int8-ok",
        green_checks(_smoke(True, [], variant_id="kokoro-onnx-int8"), "kokoro-onnx-int8"),
        True,
    )
    expect("green-failed", green_checks(_smoke(False, []), "kokoro-onnx-fp16"), False)
    expect("green-one-failure", green_checks(_smoke(True, twelve[:1]), "kokoro-onnx-fp16"), False)
    expect("green-wrong-variant", green_checks(_smoke(True, []), "kokoro-onnx-int8"), False)
    expect(
        "green-live-proxy",
        green_checks(_smoke(True, [], proxy={"HTTPS_PROXY": ""}), "kokoro-onnx-fp16"),
        False,
    )

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        # copies
        run = base / "run"
        (run / "avkit-backend" / "_internal").mkdir(parents=True)
        (run / "avkit-backend" / "avkit-backend.exe").write_bytes(b"exe")
        models = base / "models"
        (models / FP16_REL).parent.mkdir(parents=True)
        (models / FP16_REL).write_bytes(b"fp16")
        good_sha = hashlib.sha256(b"fp16").hexdigest()
        expect("copies-ok", copies_checks(run, models, good_sha, 4), True)
        expect("copies-wrong-sha", copies_checks(run, models, "0" * 64, 4), False)
        expect("copies-wrong-size", copies_checks(run, models, good_sha, 5), False)
        (run / "avkit-backend" / "_internal" / "torch").mkdir()
        expect("copies-forbidden", copies_checks(run, models, good_sha, 4), False)
        expect("copies-no-exe", copies_checks(base / "nowhere", models, good_sha, 4), False)

        # wavs: 149 jobs; WAV bytes per key; a failed job has no WAV.
        def jobs(done: int, flip: int | None = None) -> list[tuple[str, str, str, bytes | None]]:
            out: list[tuple[str, str, str, bytes | None]] = []
            for n in range(JOBS):
                wav = f"wav-{n}".encode() + (b"!" if n == flip else b"")
                out.append(
                    (
                        f"h{n}",
                        "af_heart",
                        "Done" if n < done else "Failed",
                        wav if n < done else None,
                    )
                )
            return out

        a149 = _make_run(base / "a149", jobs(JOBS))
        b149 = _make_run(base / "b149", jobs(JOBS))
        c137 = _make_run(base / "c137", jobs(137))
        d137 = _make_run(base / "d137", jobs(137))
        flip = _make_run(base / "flip", jobs(JOBS, flip=5))
        dup = _make_run(base / "dup", jobs(JOBS), extra=1)
        copies = base / "db"
        expect("wavs-149-ok", wav_checks(a149, b149, JOBS, copies)[0], True)
        expect("wavs-137-ok", wav_checks(c137, d137, 137, copies)[0], True)
        expect("wavs-137-vs-149", wav_checks(c137, b149, 137, copies)[0], False)
        expect("wavs-149-expected-137", wav_checks(a149, b149, 137, copies)[0], False)
        expect("wavs-one-differs", wav_checks(flip, b149, JOBS, copies)[0], False)
        expect("wavs-two-rows", wav_checks(dup, b149, JOBS, copies)[0], False)
        # A Done row whose WAV lies in the other run's folder is refused.
        cross = _make_run(base / "cross", jobs(JOBS))
        db = sqlite3.connect(cross / "app-data" / "avkit.db")
        db.execute(
            "UPDATE tts_jobs SET output_path = ? WHERE text_hash = 'h0'",
            (str(b149 / "out" / "job-0.wav"),),
        )
        db.commit()
        db.close()
        expect("wavs-outside-run", wav_checks(cross, b149, JOBS, copies)[0], False)

        # snapshot
        snap_dir = base / "snap"
        (snap_dir / "sub").mkdir(parents=True)
        (snap_dir / "a.bin").write_bytes(b"a")
        (snap_dir / "sub" / "b.bin").write_bytes(b"b")
        before = snapshot(snap_dir)
        expect("snapshot-equal", snapshot_compare(snapshot(snap_dir), before), True)
        (snap_dir / "c.bin").write_bytes(b"c")
        expect("snapshot-added", snapshot_compare(snapshot(snap_dir), before), False)
        (snap_dir / "c.bin").unlink()
        (snap_dir / "a.bin").write_bytes(b"A")
        expect("snapshot-changed", snapshot_compare(snapshot(snap_dir), before), False)
        (snap_dir / "a.bin").unlink()
        expect("snapshot-removed", snapshot_compare(snapshot(snap_dir), before), False)
        expect("snapshot-empty", snapshot_compare({}, {}), False)
    print(f"smoke-check selftest: {cases} case(s), {len(wrong)} wrong: {wrong}")
    return 1 if wrong else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="mode", required=True)
    p = sub.add_parser("copies")
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--models", type=Path, required=True)
    p = sub.add_parser("control")
    p.add_argument("smoke_json", type=Path)
    p = sub.add_parser("green")
    p.add_argument("smoke_json", type=Path)
    p.add_argument("--variant", required=True)
    p = sub.add_parser("wavs")
    p.add_argument("run", type=Path)
    p.add_argument("--against", type=Path, required=True)
    p.add_argument("--expect-done", type=int, required=True)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("snapshot")
    p.add_argument("dir", type=Path)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--out", type=Path)
    group.add_argument("--compare", type=Path)
    args = parser.parse_args(argv)

    if args.mode == "copies":
        return report("copies", copies_checks(args.run, args.models))
    if args.mode == "control":
        return report(
            "control", control_checks(_load(args.smoke_json), [_load(p) for p in CONTROL_REFS])
        )
    if args.mode == "green":
        return report("green", green_checks(_load(args.smoke_json), args.variant))
    if args.mode == "wavs":
        label = args.run.name
        checks, payload = wav_checks(args.run, args.against, args.expect_done, DB_COPIES / label)
        _write_json(args.out, payload)
        print(
            f"wavs jobs={payload['jobs']} done_ours={payload['done']['ours']} "
            f"done_against={payload['done']['against']} equal={payload['equal']}"
        )
        return report("wavs", checks)
    if args.mode == "snapshot":
        now = snapshot(args.dir)
        total = sum(v["bytes"] for v in now.values())
        print(f"snapshot {args.dir.as_posix()}: {len(now)} file(s), {total} bytes")
        if args.out:
            _write_json(args.out, now)
            return report("snapshot", {"files": True if now else 0})
        return report("snapshot-compare", snapshot_compare(now, _load(args.compare)))
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
