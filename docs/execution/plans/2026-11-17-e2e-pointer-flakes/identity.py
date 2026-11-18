"""Session 91 input identity (implementation-plan.md §Session gate). A copy of Session 90's
(2026-11-17-test-run-reliability), itself from Session 89's, 88's, 82's and 87's, with this
plan's PLAN, PROJECT_ARTIFACTS and selftest bound list (the e2e-pointer-flakes spec, harness,
new test-side and plan-script files), the other-plan skip covering 2026-11-15 to 2026-11-17
folders,
ELECTRON_RUN_AS_NODE cleared before anything is measured (Session 88 RULE-3: a value from a
shell that sets it is discarded, not reported), and secret-name filtering (Session 83 RULE-2):
``.mcp.json``, ``mcp-token.txt``, ``.claude.json``, ``.env``, ``.env.*``,
``.claude/settings.local.json`` and ``.agent/fleet/hub/`` are dropped from every enumeration by
pathspec and again by name before any read, so no host's ignore rules decide whether they are
opened.

Prints the D6 input identity. The last line is ``tested_state <head>+<sha256>``: HEAD plus one
SHA-256 over

* the tracked diff and the untracked (not ignored) files of the whole work tree, minus the
  ``PROJECT_ARTIFACTS`` written after the gate -- so lockfiles, ``ui/tsconfig.json``,
  ``ui/electron.vite.config.ts``, the ``.agent/docs/commands.md`` manifest, fixtures and this
  plan's own scripts are all bound. So are the project documents the suites read (round 1
  F3): ``docs/build-plan/`` (``06-gui.md``, ``gui-actions-index.md``: layout-canon,
  gui-actions-audit) and ``docs/BUILD_PLAN.md``, ``.agent/docs/emerging-standards.md``,
  ``.agent/context/meu-status.yaml`` and the grouping files (layout-canon, queue-canon),
  ``.agent/context/review-vocabulary.yaml`` and other sessions' handoffs
  (test_framework_adoption), ``ui/tests/e2e/test-ids.ts`` (AC-51.6 prefix hash) and
  ``meu-registry.md`` (the D6 ``state-render`` step). The exclusions are this session's own
  closeout outputs, which no suite or gate step reads, ``OTHER_PLAN_FOLDERS`` and the secret
  names;
* the runtime identity observed live: the Python running this script and the SHA-256 of its
  installed distribution set (every ``name==version`` from ``importlib.metadata``),
  ``node --version``, the
  installed ``electron`` and ``@playwright/test`` versions read from ``ui/node_modules``, the
  ``segoeui.ttf`` SHA-256 and the ``ELECTRON_RUN_AS_NODE`` value.

``--state-only`` computes exactly the same value and prints only it, so the gate (H1-2) and
the reuse check (H1-6b) cannot disagree about what is hashed. Any input that cannot be read
raises, and an unreadable input never hashes as "absent". ``--selftest`` proves the binding
in a scratch git repository: each bound mutation changes the state and makes
``durable_evidence.evidence_problems`` refuse the earlier full record, while edits to
project artifacts and secret-named files leave the state unchanged (and the secret files are
never read). Run from the worktree root.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

PLAN = "docs/execution/plans/2026-11-17-e2e-pointer-flakes"
#: This session's own closeout outputs, written after the H1-2 gate by H1-3..H2-5, which no
#: suite or D6 step reads. Everything else in the work tree is an input, including the files
#: earlier sessions left uncommitted, so they are bound by content.
PROJECT_ARTIFACTS = (
    f"{PLAN}/*.md",
    ".agent/context/handoffs/2026-11-17-e2e-pointer-flakes-*",
    "docs/execution/reflections/2026-11-17-e2e-pointer-flakes-*",
    "docs/execution/metrics.md",
    ".agent/context/current-focus.md",
)
#: New plan folders that other sessions' planners write while this session runs. A file is
#: skipped only when it is untracked, under ``docs/execution/plans/2026-11-1[5-7]-<slug>/`` with
#: a slug other than this plan's, and that folder is absent from HEAD. No suite or gate step
#: reads those folders (tests/ and tools/ name only fixed plan paths).
OTHER_PLAN = re.compile(r"^docs/execution/plans/2026-11-1[5-7]-[^/]+/")
#: Secret names (Session 83 RULE-2): never enumerated into the hash and never opened.
SECRET_GLOBS = (
    "**/.mcp.json",
    "**/mcp-token.txt",
    "**/.claude.json",
    "**/.env",
    "**/.env.*",
    "**/.claude/settings.local.json",
    ".agent/fleet/hub/**",
)


def _secret(name: str) -> bool:
    parts = name.split("/")
    base = parts[-1]
    if base in (".mcp.json", "mcp-token.txt", ".claude.json", ".env"):
        return True
    if base.startswith(".env."):
        return True
    if len(parts) >= 2 and parts[-2] == ".claude" and base == "settings.local.json":
        return True
    return name.startswith(".agent/fleet/hub/")


def _other_plan_file(name: str, head_folders: set[str]) -> bool:
    m = OTHER_PLAN.match(name)
    if not m or name.startswith(PLAN + "/"):
        return False
    folder = m.group(0).rstrip("/")
    return folder not in head_folders


#: Session 91 changes no Python dependency; the whole distribution set is still hashed.
NAMED_DISTRIBUTIONS: tuple[str, ...] = ()
FONT = "C:/Windows/Fonts/segoeui.ttf"


def _git(root: pathlib.Path, *args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, check=True).stdout


def _pathspec() -> list[str]:
    return [
        "--",
        ".",
        *(f":(exclude,glob){p}" if "*" in p else f":(exclude){p}" for p in PROJECT_ARTIFACTS),
        *(f":(exclude,glob){p}" for p in SECRET_GLOBS),
    ]


def _sha_file(path: pathlib.Path | str) -> str:
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def _installed(root: pathlib.Path, package: str) -> str:
    manifest = root / "ui" / "node_modules" / package / "package.json"
    return json.loads(manifest.read_text(encoding="utf-8"))["version"]


def _distribution_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        # Not installed is a definite state of the environment, not an unreadable input.
        return "<not installed>"


def _distribution_set_sha256() -> str:
    pins = sorted(
        {f"{d.metadata['Name']}=={d.version}" for d in importlib.metadata.distributions()}
    )
    return hashlib.sha256("\n".join(pins).encode()).hexdigest()


def runtime_identity(root: pathlib.Path) -> dict[str, str]:
    node = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
    return {
        "python": sys.version,
        "python_distributions_sha256": _distribution_set_sha256(),
        **{f"python_{name}": _distribution_version(name) for name in NAMED_DISTRIBUTIONS},
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
    tree = _git(root, "ls-tree", "--name-only", "-z", "HEAD", "docs/execution/plans/")
    head_folders = {n for n in tree.decode().split("\0") if n}
    names = (n for n in untracked.decode().split("\0") if n)
    kept = (n for n in names if not _secret(n) and not _other_plan_file(n, head_folders))
    for name in sorted(kept):
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
        "mcp-server/package-lock.json",
        "openapi.committed.json",
        "ui/tsconfig.json",
        "ui/electron.vite.config.ts",
        ".agent/docs/commands.md",
        f"{PLAN}/session-gate.ps1",
        "packages/x.py",
        # Project documents the suites read (round 1 F3).
        "docs/build-plan/06-gui.md",
        "docs/build-plan/gui-actions-index.md",
        "docs/build-plan/07-distribution.md",
        "docs/build-plan/build-priority-matrix.md",
        "docs/BUILD_PLAN.md",
        ".agent/docs/emerging-standards.md",
        ".agent/context/meu-status.yaml",
        ".agent/context/meu-registry.md",
        "ui/tests/e2e/test-ids.ts",
        ".agent/context/review-vocabulary.yaml",
        ".agent/context/handoffs/2026-09-26-framework-update-adoption-handoff.md",
        # Other sessions' uncommitted files, bound by content.
        ".agent/context/known-issues.yaml",
        ".agent/context/known-issues.md",
        ".agent/context/triage-output.yaml",
        ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md",
        ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md",
        ".agent/context/grouping/2026-11-17-post-session-88-triage-session-grouping.md",
        # Session 91's spec, harness, new test-side and plan-script files.
        "ui/tests/e2e/download-queue.test.ts",
        "ui/tests/e2e/convert-queue.test.ts",
        "ui/tests/e2e/capture-inbox.test.ts",
        "ui/tests/e2e/electron-app.ts",
        "ui/tests/e2e/electron-env.ts",
        "ui/tests/e2e/main-error-watch.cjs",
        "ui/tests/e2e/pointer-settle.ts",
        "ui/tests/e2e/e2e-diag.ts",
        "ui/tests/e2e/e2e-diag.test.ts",
        "ui/tests/unit/e2e-pointer.test.ts",
        "ui/package.json",
        "ui/playwright.config.ts",
        "ui/src/renderer/src/components/queue/QueueList.tsx",
        f"{PLAN}/red-check.py",
        f"{PLAN}/eol-check.py",
        f"{PLAN}/issue-resolve.py",
        f"{PLAN}/flake-run.py",
        f"{PLAN}/assert-check.py",
        f"{PLAN}/meu-register.py",
        f"{PLAN}/baseline-scope.json",
    )
    artifacts = (
        f"{PLAN}/walkthrough.md",
        f"{PLAN}/task.md",
        ".agent/context/handoffs/2026-11-17-e2e-pointer-flakes-handoff.md",
        ".agent/context/handoffs/2026-11-17-e2e-pointer-flakes-implementation-critical-review.md",
        "docs/execution/reflections/2026-11-17-e2e-pointer-flakes-reflection.md",
        "docs/execution/metrics.md",
        ".agent/context/current-focus.md",
    )
    #: Secret-named files in the scratch repository (Session 83 RULE-2), untracked and not
    #: ignored there: the state must not move, as it would if a file were enumerated and read.
    secrets = (
        ".mcp.json",
        "mcp-token.txt",
        "sub/mcp-token.txt",
        ".claude.json",
        ".env",
        ".env.local",
        "ui/.env.production",
        ".claude/settings.local.json",
        ".agent/fleet/hub/state.json",
    )
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
        _git(
            root,
            "-c",
            "user.email=s@t",
            "-c",
            "user.name=s",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-qm",
            "base",
        )
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
            refused = evidence_problems(
                handoff, scratch_roots=(), require_full=True, expected_state=new
            )
            print(f"bound    {rel}: state_changed={new != old} historical_refused={bool(refused)}")
            if new == old or not refused:
                failures.append(f"{rel} mutation not detected")
            path.write_text("v1\n", encoding="utf-8")
        (root / "tests").mkdir(exist_ok=True)
        (root / "tests" / "new_test.py").write_text("x\n", encoding="utf-8")
        untracked = tested_state(root, runtime) != old
        print(f"bound    tests/new_test.py (untracked): state_changed={untracked}")
        if not untracked:
            failures.append("untracked test file not detected")
        (root / "tests" / "new_test.py").unlink()
        for rel, want_bound in (
            ("docs/execution/plans/2026-11-15-other-planner/implementation-plan.md", False),
            ("docs/execution/plans/2026-11-15-other-planner/sub/x.py", False),
            ("docs/execution/plans/2026-11-16-other-planner/implementation-plan.md", False),
            ("docs/execution/plans/2026-11-17-other-planner/task.md", False),
            ("docs/execution/plans/2026-11-18-later-planner/task.md", True),
            ("docs/execution/plans/2026-11-14-earlier-planner/task.md", True),
            (f"{PLAN}/new-check.py", True),
            ("docs/build-plan/2026-11-15-not-a-plan.md", True),
        ):
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("x\n", encoding="utf-8")
            changed = tested_state(root, runtime) != old
            print(
                f"{'bound   ' if want_bound else 'excluded'} {rel} (untracked): "
                f"state_changed={changed}"
            )
            if changed != want_bound:
                failures.append(f"untracked {rel}: state_changed={changed}, expected {want_bound}")
            path.unlink()
        for key, value in (
            ("node", "v1-selftest"),
            ("electron", "0.0.0-selftest"),
            ("python_distributions_sha256", "0" * 64),
        ):
            changed_runtime = tested_state(root, {**runtime, key: value}) != old
            print(f"bound    runtime {key}: state_changed={changed_runtime}")
            if not changed_runtime:
                failures.append(f"runtime {key} change not detected")
        for rel in artifacts:
            (root / rel).write_text("v2\n", encoding="utf-8")
            same = tested_state(root, runtime) == old
            print(f"artifact {rel}: state_unchanged={same}")
            if not same:
                failures.append(f"{rel} artifact edit changed the state")
        for rel in secrets:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("secret\n", encoding="utf-8")
            same = tested_state(root, runtime) == old
            print(f"secret   {rel} (untracked): state_unchanged={same}")
            if not same:
                failures.append(f"secret {rel} entered the state")
        for name, want in (
            (".mcp.json", True),
            ("ui/.env", True),
            ("a/.env.test", True),
            (".claude/settings.local.json", True),
            (".agent/fleet/hub/x/y.md", True),
            (".claude/settings.json", False),
            ("docs/env.md", False),
            ("ui/.envrc", False),
            (".agent/fleet/other.md", False),
        ):
            if _secret(name) != want:
                failures.append(f"_secret({name!r}) is {not want}, expected {want}")
    for f in failures:
        print("SELFTEST FAIL:", f)
    print(f"identity selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main() -> int:
    # Session 88 RULE-3: a value inherited from a shell that sets it is discarded, never hashed.
    os.environ.pop("ELECTRON_RUN_AS_NODE", None)
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
