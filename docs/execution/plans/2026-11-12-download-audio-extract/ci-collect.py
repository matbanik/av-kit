"""Session 67 CI_DESELECT check (task row 4; implementation-plan.md §Plan-local scripts). A copy of Session 54's.

Reads the Tests step's ``run`` string from .github/workflows/ci.yml, not from a copy, splits it
with shlex and runs it with ``--collect-only`` and ``UV_OFFLINE=1``, so ``uv run --locked
--no-sync`` can't fetch. The step's own ``-q`` makes pytest list one node id per line. Exits 0
only when the run exits 0, no collected id is in the real-FFmpeg module, and the same run
without that one ``--deselect`` collects the module's ids (the control). Run from the
repository root.
"""

from __future__ import annotations

import os
import pathlib
import shlex
import subprocess
import sys

import yaml

WORKFLOW = pathlib.Path(".github/workflows/ci.yml")
MODULE = "tests/integration/test_download_audio_extract_real_ffmpeg.py"
TMP = r"C:\Temp\av-kit\s67\tmp"


def tests_step_argv() -> list[str]:
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    # Each CI job has a step named Tests; the pytest one is the python job's.
    steps = [step for step in workflow["jobs"]["python"]["steps"] if step.get("name") == "Tests"]
    if len(steps) != 1:
        raise SystemExit(f"ci-collect: {len(steps)} Tests steps in the python job; expected 1")
    return shlex.split(steps[0]["run"])


def collect(argv: list[str]) -> tuple[int, list[str]]:
    env = {**os.environ, "UV_OFFLINE": "1", "TMP": TMP, "TEMP": TMP}
    run = subprocess.run([*argv, "--collect-only"], capture_output=True, env=env)
    lines = run.stdout.decode("utf-8", errors="replace").splitlines()
    ids = [line.strip() for line in lines if "::" in line]
    return run.returncode, ids


def main() -> int:
    argv = tests_step_argv()
    pairs = [i for i, arg in enumerate(argv[:-1]) if arg == "--deselect" and argv[i + 1] == MODULE]
    print("tests step:", " ".join(argv))
    print(f"--deselect {MODULE}: {len(pairs)} occurrence(s)")
    if len(pairs) != 1:
        return 1
    code, ids = collect(argv)
    leaked = [node for node in ids if node.replace("\\", "/").startswith(MODULE)]
    print(f"as CI holds it: exit={code} collected={len(ids)} in the module={len(leaked)}")
    control = argv[: pairs[0]] + argv[pairs[0] + 2 :]
    control_code, control_ids = collect(control)
    found = [node for node in control_ids if node.replace("\\", "/").startswith(MODULE)]
    print(f"control without it: exit={control_code} collected={len(control_ids)} in the module={len(found)}")
    for node in found:
        print("  control collects", node)
    ok = code == 0 and ids and not leaked and control_code == 0 and found
    print("ci-collect:", "0 problem(s)" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
