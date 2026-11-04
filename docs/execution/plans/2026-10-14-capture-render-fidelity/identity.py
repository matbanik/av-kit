"""Session 36 input identity (implementation-plan.md §Validation stage contract, ``INPUT_IDENTITY``).

Prints the D6 input identity. The last line is ``tested_state <head>+<sha256>``: HEAD plus one
SHA-256 over

* the tracked diff and the untracked (not ignored) files of the whole work tree, minus the
  ``PROJECT_ARTIFACTS`` written after the gate -- so lockfiles, ``ui/tsconfig.json``,
  ``ui/electron.vite.config.ts``, the ``.agent/docs/commands.md`` manifest, fixtures and this
  plan's own scripts are all bound;
* the runtime identity observed live: the Python running this script, ``node --version``,
  the installed ``electron`` and ``@playwright/test`` versions read from ``ui/node_modules``,
  the ``segoeui.ttf`` SHA-256 and the ``ELECTRON_RUN_AS_NODE`` value.

``--state-only`` computes exactly the same value and prints only it, so the gate (row 8) and
the reuse check (H1-6b) cannot disagree about what is hashed. Any input that cannot be read
raises, and an unreadable input never hashes as "absent". ``--selftest`` proves the binding
in a scratch git repository: each bound mutation changes the state and makes
``durable_evidence.evidence_problems`` refuse the earlier full record, while edits to
project artifacts leave the state unchanged. Run from the worktree root.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile

PLAN = "docs/execution/plans/2026-10-14-capture-render-fidelity"
#: Written after the gate by H1-3..H2-5. Everything else in the work tree is an input.
PROJECT_ARTIFACTS = (
    f"{PLAN}/*.md",
    ".agent/context",
    "docs/execution/reflections",
    "docs/execution/metrics.md",
    "docs/build-plan",
    "docs/BUILD_PLAN.md",
)
FONT = "C:/Windows/Fonts/segoeui.ttf"


def _git(root: pathlib.Path, *args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, check=True).stdout


def _pathspec() -> list[str]:
    return ["--", ".", *(f":(exclude,glob){p}" if "*" in p else f":(exclude){p}" for p in PROJECT_ARTIFACTS)]


def _sha_file(path: pathlib.Path | str) -> str:
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def _installed(root: pathlib.Path, package: str) -> str:
    manifest = root / "ui" / "node_modules" / package / "package.json"
    return json.loads(manifest.read_text(encoding="utf-8"))["version"]


def runtime_identity(root: pathlib.Path) -> dict[str, str]:
    node = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
    return {
        "python": sys.version,
        "node": node.stdout.strip(),
        "electron": _installed(root, "electron"),
        "playwright_test": _installed(root, "@playwright/test"),
        "segoeui_sha256": _sha_file(FONT),
        "ELECTRON_RUN_AS_NODE": os.environ.get("ELECTRON_RUN_AS_NODE") or "<unset>",
    }


def tested_state(root: pathlib.Path, runtime: dict[str, str]) -> str:
    head = _git(root, "rev-parse", "HEAD").decode().strip()
    digest = hashlib.sha256()
    digest.update(_git(root, "diff", "HEAD", "--binary", *_pathspec()))
    untracked = _git(root, "ls-files", "--others", "--exclude-standard", "-z", *_pathspec())
    for name in sorted(n for n in untracked.decode().split("\0") if n):
        digest.update(name.encode())
        digest.update((root / name).read_bytes())
    digest.update(json.dumps(runtime, sort_keys=True).encode())
    return f"{head}+{digest.hexdigest()}"


def selftest() -> int:
    sys.path.insert(0, str(pathlib.Path.cwd() / "tools"))
    from durable_evidence import evidence_problems

    runtime = {"node": "v0-selftest"}
    bound = (
        "uv.lock",
        "ui/package-lock.json",
        "ui/tsconfig.json",
        "ui/electron.vite.config.ts",
        ".agent/docs/commands.md",
        f"{PLAN}/session-gate.ps1",
        "packages/x.py",
    )
    artifacts = (f"{PLAN}/walkthrough.md", ".agent/context/handoffs/h.md", "docs/build-plan/09.md")
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        for rel in bound + artifacts:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text("v1\n", encoding="utf-8")
        _git(root, "init", "-q")
        _git(root, "-c", "user.email=s@t", "-c", "user.name=s", "add", "-A")
        # The scratch fixture must not inherit commit signing (an absent signing key fails
        # the commit before any assertion runs); the override is local to this one command.
        _git(root, "-c", "user.email=s@t", "-c", "user.name=s", "-c", "commit.gpgsign=false", "commit", "-qm", "base")
        old = tested_state(root, runtime)
        record = json.dumps(
            {
                "schema_version": "evidence.v1",
                "check_id": "gate",
                "command": "session-gate.ps1",
                "cwd": "wt",
                "scope": "D6",
                "phase": "full",
                "result": "pass",
                "exit_code": 0,
                "fresh": True,
                "tested_state": old,
                "output": "all steps exit 0",
            }
        )
        handoff = f"```json\n{record}\n```\n"
        if evidence_problems(handoff, scratch_roots=(), require_full=True, expected_state=old):
            failures.append("control: the unchanged state was refused")
        for rel in bound:
            path = root / rel
            path.write_text("v2\n", encoding="utf-8")
            new = tested_state(root, runtime)
            refused = evidence_problems(handoff, scratch_roots=(), require_full=True, expected_state=new)
            print(f"bound    {rel}: state_changed={new != old} historical_refused={bool(refused)}")
            if new == old or not refused:
                failures.append(f"{rel} mutation not detected")
            path.write_text("v1\n", encoding="utf-8")
        (root / "tests").mkdir()
        (root / "tests" / "new_test.py").write_text("x\n", encoding="utf-8")
        untracked = tested_state(root, runtime) != old
        print(f"bound    tests/new_test.py (untracked): state_changed={untracked}")
        if not untracked:
            failures.append("untracked test file not detected")
        (root / "tests" / "new_test.py").unlink()
        changed_runtime = tested_state(root, {"node": "v1-selftest"}) != old
        print(f"bound    runtime node version: state_changed={changed_runtime}")
        if not changed_runtime:
            failures.append("runtime change not detected")
        for rel in artifacts:
            (root / rel).write_text("v2\n", encoding="utf-8")
            same = tested_state(root, runtime) == old
            print(f"artifact {rel}: state_unchanged={same}")
            if not same:
                failures.append(f"{rel} artifact edit changed the state")
    for f in failures:
        print("SELFTEST FAIL:", f)
    print(f"identity selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main() -> int:
    if "--selftest" in sys.argv[1:]:
        return selftest()
    root = pathlib.Path.cwd()
    runtime = runtime_identity(root)
    state = tested_state(root, runtime)
    if "--state-only" in sys.argv[1:]:
        print(state)
        return 0
    for key, value in runtime.items():
        print(key, value.replace("\n", " "))
    print("uv_lock_sha256", _sha_file(root / "uv.lock"))
    print("ui_package_lock_sha256", _sha_file(root / "ui" / "package-lock.json"))
    print("tested_state", state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
