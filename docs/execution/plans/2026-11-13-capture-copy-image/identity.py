"""Session 69 input identity (implementation-plan.md §Verification Plan 1). A copy of Session 68's, with this plan's values. The pinned FFmpeg pair is bound as before; this session adds no real-FFmpeg module.

Prints the D6 input identity. The last line is ``tested_state <head>+<sha256>``: HEAD plus one
SHA-256 over

* the tracked diff and the untracked (not ignored) files of the whole work tree, minus the
  ``PROJECT_ARTIFACTS`` written after the gate -- so lockfiles, ``ui/tsconfig.json``,
  ``ui/electron.vite.config.ts``, the ``.agent/docs/commands.md`` manifest, fixtures and this
  plan's own scripts are all bound. So are the project documents the suites read (round 1
  F3): ``docs/build-plan/`` (``06-gui.md``, ``gui-actions-index.md``: layout-canon,
  gui-actions-audit; ``09`` and ``06``, which row 5 writes before the gate) and ``docs/BUILD_PLAN.md``, ``.agent/docs/emerging-standards.md``, ``.agent/context/meu-status.yaml`` and the grouping file, which row 6 writes (layout-canon,
  queue-canon), ``.agent/context/review-vocabulary.yaml`` and other sessions' handoffs
  (test_framework_adoption), ``ui/tests/e2e/test-ids.ts`` (AC-51.6 prefix hash) and
  ``meu-registry.md`` (the D6 ``state-render`` step). The exclusions are only this session's own closeout outputs, which no
  suite or gate step reads;
* the runtime identity observed live: the Python running this script and the SHA-256 of its
  installed distribution set (every ``name==version`` from ``importlib.metadata``),
  ``node --version``, the
  installed ``electron`` and ``@playwright/test`` versions read from ``ui/node_modules``, the
  ``segoeui.ttf`` SHA-256, the ``ELECTRON_RUN_AS_NODE`` value and the SHA-256 of the pinned
  ``packaging/ffmpeg-win64/ffmpeg.exe`` and ``ffprobe.exe``, which git ignores and the
  real-FFmpeg modules run (Session 54; Session 62's ``test_video_real_ffmpeg.py``; this
  Session 67's ``test_download_audio_extract_real_ffmpeg.py``), and the SHA-256 of the pinned
  ``packaging/deno-win64/deno.exe`` and ``LICENSE.md``, which git ignores (Session 66 fetched
  them; this session's gate does not run them, but the binding is kept). A Deno file that does
  not exist is the definite state ``<absent>``; one that exists but cannot be read raises.

``--state-only`` computes exactly the same value and prints only it, so the gate (H1-2) and
the reuse check (H1-6b) cannot disagree about what is hashed. Any input that cannot be read
raises, and an unreadable input never hashes as "absent". ``--selftest`` proves the binding
in a scratch git repository: each bound mutation changes the state and makes
``durable_evidence.evidence_problems`` refuse the earlier full record, while edits to
project artifacts leave the state unchanged. Run from the worktree root.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import pathlib
import subprocess
import sys
import tempfile

PLAN = "docs/execution/plans/2026-11-13-capture-copy-image"
#: This session's own closeout outputs, written after the H1-2 gate by H1-3..H2-5, which no
#: suite or D6 step reads. Everything else in the work tree is an input; the register, its
#: renders, the grouping tracker and the spec notes are written by rows 5 and 6, before H1-2,
#: so they stay bound. The plan folder's *.md files are
#: excluded as before; its scripts are .py and .ps1 files, so they stay bound.
PROJECT_ARTIFACTS = (
    f"{PLAN}/*.md",
    ".agent/context/handoffs/2026-11-13-capture-copy-image-*",
    "docs/execution/reflections/2026-11-13-capture-copy-image-*",
    "docs/execution/metrics.md",
    ".agent/context/current-focus.md",
)
#: Named since Session 66; both are also in the hashed distribution set.
NAMED_DISTRIBUTIONS: tuple[str, ...] = ("yt-dlp", "yt-dlp-ejs")
FONT = "C:/Windows/Fonts/segoeui.ttf"
#: The pinned FFmpeg pair the real-FFmpeg modules run (Session 54's extract module and Session 62's
#: test_video_real_ffmpeg.py, the gate's real-ffmpeg step); .gitignore keeps it out of the diff.
FFMPEG_PAIR = ("packaging/ffmpeg-win64/ffmpeg.exe", "packaging/ffmpeg-win64/ffprobe.exe")
#: The pinned Deno and its licence (Session 66, D-649); .gitignore keeps them out of the diff.
DENO_PIN = ("packaging/deno-win64/deno.exe", "packaging/deno-win64/LICENSE.md")


def _git(root: pathlib.Path, *args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, check=True).stdout


def _pathspec() -> list[str]:
    return ["--", ".", *(f":(exclude,glob){p}" if "*" in p else f":(exclude){p}" for p in PROJECT_ARTIFACTS)]


def _sha_file(path: pathlib.Path | str) -> str:
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def _sha_optional(path: pathlib.Path) -> str:
    # exists() is False only for a path that is not there; an unreadable file still raises below.
    if not path.exists():
        return "<absent>"
    return _sha_file(path)


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
    pins = sorted({f"{d.metadata['Name']}=={d.version}" for d in importlib.metadata.distributions()})
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
        **{f"{pathlib.Path(rel).stem}_sha256": _sha_file(root / rel) for rel in FFMPEG_PAIR},
        **{f"deno_pin_{pathlib.Path(rel).name}_sha256": _sha_optional(root / rel) for rel in DENO_PIN},
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
        "mcp-server/package-lock.json",
        "openapi.committed.json",
        "ui/tsconfig.json",
        "ui/electron.vite.config.ts",
        ".agent/docs/commands.md",
        f"{PLAN}/session-gate.ps1",
        f"{PLAN}/baseline.ps1",
        f"{PLAN}/red-check.py",
        f"{PLAN}/identity.py",
        f"{PLAN}/id-length.py",
        "packages/core/src/avkit_core/ports/capture.py",
        "packages/core/src/avkit_core/services/capture.py",
        "packages/infrastructure/src/avkit_infra/capture/adapter.py",
        "packages/api/src/avkit_api/routes/captures.py",
        "mcp-server/tests/capture.test.ts",
        "ui/src/renderer/src/features/capture/capture-image.ts",
        "ui/src/renderer/src/features/capture/capture-clipboard.ts",
        "ui/src/renderer/src/features/capture/capture-flatten.ts",
        "ui/src/renderer/src/features/capture/capture-toolbar.ts",
        "ui/src/renderer/src/features/capture/CapturePage.tsx",
        "ui/src/renderer/src/features/capture/capture-help-content.ts",
        "ui/src/renderer/src/features/settings/SettingsPage.tsx",
        "ui/tests/e2e/capture-inbox.test.ts",
        "ui/tests/unit/capture-copy-image.behavior.test.ts",
        "ui/tests/unit/capture-flatten.test.ts",
        "ui/tests/unit/capture-action-row.test.ts",
        "ui/tests/unit/capture-page.behavior.test.ts",
        "ui/tests/unit/capture-page.test.ts",
        "ui/tests/unit/capture-help-content.test.ts",
        "tests/unit/test_capture_render.py",
        "tests/e2e/test_api_capture_render.py",
        "tests/e2e/test_api_openapi.py",
        "tests/e2e/test_api_downloads.py",
        "docs/build-plan/09-screenshot-capture.md",
        "docs/build-plan/11-page-layout.md",
        "packages/x.py",
        # Project documents the suites read (round 1 F3).
        "docs/build-plan/06-gui.md",
        "docs/build-plan/gui-actions-index.md",
        "docs/build-plan/02-infrastructure.md",
        "docs/build-plan/build-priority-matrix.md",
        "docs/BUILD_PLAN.md",
        ".agent/docs/emerging-standards.md",
        ".agent/context/meu-status.yaml",
        ".agent/context/meu-registry.md",
        "ui/tests/e2e/test-ids.ts",
        ".agent/context/review-vocabulary.yaml",
        ".agent/context/handoffs/2026-09-26-framework-update-adoption-handoff.md",
        # Written by row 6 before the gate, so bound.
        ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md",
    )
    artifacts = (
        f"{PLAN}/walkthrough.md",
        f"{PLAN}/task.md",
        f"{PLAN}/implementation-plan.md",
        ".agent/context/handoffs/2026-11-13-capture-copy-image-MEU-104-handoff.md",
        ".agent/context/handoffs/2026-11-13-capture-copy-image-plan-critical-review.md",
        ".agent/context/handoffs/2026-11-13-capture-copy-image-implementation-critical-review.md",
        "docs/execution/reflections/2026-11-13-capture-copy-image-reflection.md",
        "docs/execution/metrics.md",
        ".agent/context/current-focus.md",
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
        # A bound path under tests/ may not exist in this session's list, so the folder is made here.
        (root / "tests").mkdir(exist_ok=True)
        (root / "tests" / "new_test.py").write_text("x\n", encoding="utf-8")
        untracked = tested_state(root, runtime) != old
        print(f"bound    tests/new_test.py (untracked): state_changed={untracked}")
        if not untracked:
            failures.append("untracked test file not detected")
        (root / "tests" / "new_test.py").unlink()
        for key, value in (
            ("node", "v1-selftest"),
            ("electron", "0.0.0-selftest"),
            ("python_distributions_sha256", "0" * 64),
            ("python_yt-dlp-ejs", "0.0.0-selftest"),
            ("ffmpeg_sha256", "0" * 64),
            ("ffprobe_sha256", "0" * 64),
            ("deno_pin_deno.exe_sha256", "0" * 64),
            ("deno_pin_LICENSE.md_sha256", "0" * 64),
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
        # The Deno pin is git-ignored: absent hashes as <absent>, and a present file by its bytes.
        pin = root / DENO_PIN[0]
        absent = _sha_optional(pin)
        pin.parent.mkdir(parents=True, exist_ok=True)
        pin.write_bytes(b"MZ-selftest")
        present = _sha_optional(pin)
        print(f"bound    {DENO_PIN[0]} (ignored): absent={absent} present_differs={present != absent}")
        if absent != "<absent>" or present == absent:
            failures.append("Deno pin presence not detected")
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
