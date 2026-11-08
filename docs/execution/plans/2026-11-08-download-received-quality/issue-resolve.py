"""Session 55 register resolve (task row 6; plan §Plan-local scripts). A copy of Session 54's.

Session 49b's `register-rewrite.py --mode resolve`, for several issues. Each `--issue`
names one issue to resolve. `--set-file` names a JSON object keyed by those issue ids,
each value an object holding only RESOLVE_KEYS; any other issue or key is refused. The
run exits 1 unless every parsed difference is under RESOLVE_KEYS of a named issue.

Session 51 change: a named issue that lacks one of RESOLVE_KEYS gains it before `category`,
where the register's resolved issues hold `resolution_path`. `differences` reports an added
key at its own path, so that path must still be one of RESOLVE_KEYS of a named issue, and a
removed or reordered key is still refused.

The run holds the register through one Windows handle that denies other writers, from
the first read to the last, so another process's write in that interval fails loudly in
that process instead of being overwritten here. If another process already has the
register open for writing, the run refuses. `--expect-sha256` refuses unless the bytes
read through the handle have that hash (S4). The bytes read are kept in SCRATCH.

`model.save` writes to a staged copy in SCRATCH, which is checked: the parsed difference,
the parse back to the data saved, the validator's bounded grammar over the whole file,
and `issue_decision_log` reading every issue's decision ids and stages as the data hold
them. Only a staged copy with no problem replaces the register's contents, through the
held handle. `--target` copies the staged file to another path instead, and the register
is then never written.
"""

from __future__ import annotations

import argparse
import copy
import ctypes
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))

import validate_closeout_artifacts as validator  # noqa: E402
from issue_triage import model  # noqa: E402

REGISTER = ROOT / ".agent" / "context" / "known-issues.yaml"
SCRATCH = Path("C:/Temp/av-kit/s55")

RESOLVE_KEYS = ("status", "verification", "resolution_path")


class HandleRefused(Exception):
    """The register is open for writing in another process."""


class ExclusiveHandle:
    """A read-write handle on PATH that lets other processes read it but not write, replace or delete it."""

    GENERIC_READ, GENERIC_WRITE = 0x80000000, 0x40000000
    FILE_SHARE_READ, OPEN_EXISTING = 0x1, 3

    def __init__(self, path: Path) -> None:
        self.path = path

    def __enter__(self) -> ExclusiveHandle:
        if os.name != "nt":
            raise SystemExit("FAIL: the exclusive handle needs Windows; nothing written")
        import msvcrt
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateFileW.restype = wintypes.HANDLE
        kernel32.CreateFileW.argtypes = [
            wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
            wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
        ]
        handle = kernel32.CreateFileW(
            str(self.path), self.GENERIC_READ | self.GENERIC_WRITE, self.FILE_SHARE_READ,
            None, self.OPEN_EXISTING, 0, None,
        )
        if handle == wintypes.HANDLE(-1).value:
            raise HandleRefused(f"WinError {ctypes.get_last_error()} opening {self.path}")
        self.file = os.fdopen(msvcrt.open_osfhandle(handle, os.O_RDWR | os.O_BINARY), "r+b")
        return self

    def __exit__(self, *exc: object) -> None:
        self.file.close()

    def read(self) -> bytes:
        self.file.seek(0)
        return self.file.read()

    def replace(self, raw: bytes) -> None:
        self.file.seek(0)
        self.file.truncate()
        self.file.write(raw)
        self.file.flush()
        os.fsync(self.file.fileno())


def set_fields(issue: dict[str, Any], fields: dict[str, Any]) -> None:
    """Set FIELDS on ISSUE in place; a key the issue lacks goes before `category`, or last."""
    added = {key: value for key, value in fields.items() if key not in issue}
    items = list(issue.items())
    issue.clear()
    for key, value in items:
        if key == "category":
            issue.update(added)
            added = {}
        issue[key] = fields.get(key, value)
    issue.update(added)


def apply_resolve(data: dict[str, Any], issues: list[str], values: Any) -> list[str]:
    """Set RESOLVE_KEYS on each named issue from VALUES; return the problems found."""
    if not isinstance(values, dict) or sorted(values) != sorted(issues):
        named = sorted(values) if isinstance(values, dict) else type(values).__name__
        return [f"the set file must be keyed by exactly the --issue ids {sorted(issues)}; it holds {named}"]
    problems = []
    for issue_id in issues:
        fields = values[issue_id]
        if not isinstance(fields, dict) or not fields or sorted(set(fields) - set(RESOLVE_KEYS)):
            held = sorted(fields) if isinstance(fields, dict) else type(fields).__name__
            problems.append(f"{issue_id}: the set file must hold only {list(RESOLVE_KEYS)}; it holds {held}")
            continue
        issue = model.get_issue(data, issue_id)
        if issue is None:
            problems.append(f"the register has no issue {issue_id}")
            continue
        set_fields(issue, fields)
    if problems:
        return problems
    try:
        model.validate_strict(data)
    except model.IssueTriageError as exc:
        return [f"the resolved register fails validate_strict: {exc}"]
    return []


def differences(a: Any, b: Any, path: str = "") -> list[str]:
    """Every path at which two parsed values differ."""
    if isinstance(a, dict) and isinstance(b, dict):
        # A removed or reordered key is one difference at PATH; an added key is its own path.
        if [k for k in b if k in a] != list(a):
            return [f"{path}: keys differ"]
        added = [f"{path}.{k}" for k in b if k not in a]
        return added + [d for k in a for d in differences(a[k], b[k], f"{path}.{k}")]
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: lengths differ"]
        return [d for n, (x, y) in enumerate(zip(a, b)) for d in differences(x, y, f"{path}[{n}]")]
    return [] if type(a) is type(b) and a == b else [path or "<root>"]


def check_written(text: str, data: dict[str, Any], name: str) -> list[str]:
    problems = []
    try:
        validator.check_yaml_subset(text, name)
    except validator.Refuse as exc:
        problems.append(f"bounded grammar over the whole file: {exc}")
    logs = 0
    refused = 0
    for issue in data["issues"]:
        log = (issue.get("enrichment") or {}).get("decision_log")
        if not log:
            continue
        logs += 1
        expected = [(item["id"], item.get("stage")) for item in log]
        try:
            actual = validator.issue_decision_log(text, name, issue["id"])
        except validator.Refuse as exc:
            refused += 1
            problems.append(f"{issue['id']}: issue_decision_log refused: {exc}")
            continue
        if actual != expected:
            problems.append(f"{issue['id']}: issue_decision_log read {actual}, the data hold {expected}")
    print(f"decision logs read: {logs - refused} of {logs}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issue", action="append", required=True, help="an issue to resolve; once per issue")
    parser.add_argument("--set-file", type=Path, required=True, help="JSON object: issue id to RESOLVE_KEYS values")
    parser.add_argument("--target", type=Path, default=REGISTER, help="where to save; the register by default")
    parser.add_argument("--expect-sha256", required=True, help="refuse unless the register has this SHA-256 (S4)")
    args = parser.parse_args()
    if len(set(args.issue)) != len(args.issue):
        parser.error(f"--issue repeats an id: {args.issue}")

    try:
        with ExclusiveHandle(REGISTER) as handle:
            return resolve(args, handle)
    except HandleRefused as exc:
        print(f"FAIL: another process has the register open for writing ({exc}) (S4)")
        print("issue-resolve: nothing written")
        return 1


def resolve(args: argparse.Namespace, handle: ExclusiveHandle) -> int:
    raw_before = handle.read()
    before_sha = hashlib.sha256(raw_before).hexdigest()
    if before_sha != args.expect_sha256:
        print(f"FAIL: the register's sha256 is {before_sha}, not the expected {args.expect_sha256} (S4)")
        print("issue-resolve: nothing written")
        return 1
    (SCRATCH / "stage").mkdir(parents=True, exist_ok=True)
    kept = SCRATCH / "register-before-resolve.yaml"
    kept.write_bytes(raw_before)
    original = model.load(kept)
    data = copy.deepcopy(original)
    problems = apply_resolve(data, args.issue, json.loads(args.set_file.read_text(encoding="utf-8")))
    ids = [i["id"] for i in original["issues"]]
    allowed = tuple(
        f".issues[{ids.index(issue_id)}].{key}"
        for issue_id in args.issue
        if issue_id in ids
        for key in RESOLVE_KEYS
    )
    changed = set(differences(original, data))
    outside = sorted(p for p in changed if not p.startswith(allowed))
    if outside:
        problems.append(f"resolve changes paths outside {list(RESOLVE_KEYS)} of the named issues: {outside}")
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        print("issue-resolve: nothing written")
        return 1

    stage = SCRATCH / "stage" / REGISTER.name
    model.save(data, stage)
    text = stage.read_text(encoding="utf-8")
    written = model.load(stage)
    diff = set(differences(original, written))
    if diff != changed:
        problems.append(f"parsed differences {sorted(diff)} are not exactly the planned fields {sorted(changed)}")
    if written != data:
        problems.append("the file written does not parse back to the data saved")
    problems += check_written(text, written, REGISTER.name)

    raw = stage.read_bytes()
    print(f"issues={args.issue} target={args.target} staged={stage} kept={kept}")
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        print(f"issue-resolve: {len(problems)} problem(s); nothing written")
        return 1
    if args.target == REGISTER:
        handle.replace(raw)
        if handle.read() != raw:
            problems.append("the register does not hold the staged bytes after the write")
    else:
        args.target.write_bytes(raw)
        if handle.read() != raw_before:
            problems.append("the register changed although --target named another file")
    print(f"register sha256 before={before_sha}")
    print(f"target sha256 after={hashlib.sha256(raw).hexdigest()} CRLF={raw.count(bytes([13, 10]))} LF={raw.count(bytes([10]))}")
    print(f"parsed fields changed: {len(diff)}")
    for path in sorted(diff):
        print(f"  {path}")
    for problem in problems:
        print(f"FAIL: {problem}")
    print(f"issue-resolve: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
