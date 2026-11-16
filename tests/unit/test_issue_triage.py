"""Issue triage tool fixes (Session 79): cp1252 console, read-only path-shaped deep verify,
discover's generated trees and its anchor, and dismissed issues in triage's archive."""

from __future__ import annotations

import copy
import inspect
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml
from tools.issue_triage import discover, triage, verify

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "tools" / "issue_triage.py"
# The marker word is built here, so this file never becomes a discover candidate itself.
MARK = "TO" + "DO"
CP1252 = {"PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0"}
UTF8 = {"PYTHONIOENCODING": "utf-8"}


def _issue(issue_id: str, **fields: object) -> dict[str, object]:
    issue: dict[str, object] = {
        "id": issue_id,
        "title": f"fixture {issue_id}",
        "severity": "low",
        "component": "infrastructure",
        "status": "open",
        "discovered": "2026-11-15",
        "root_cause": "fixture",
        "blast_radius": "fixture",
    }
    issue.update(fields)
    return issue


def _register(path: Path, issues: list[dict[str, object]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump({"version": 1, "issues": issues}, sort_keys=False, allow_unicode=True)
    path.write_bytes(text.encode("utf-8"))
    return path


def _cli(args: list[str], cwd: Path, extra: dict[str, str]) -> subprocess.CompletedProcess[bytes]:
    env = dict(os.environ)
    env.pop("PYTHONUTF8", None)
    env.pop("PYTHONIOENCODING", None)
    env.update(extra)
    return subprocess.run(
        [sys.executable, str(CLI), *args], cwd=cwd, env=env, capture_output=True, timeout=120
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def _norm(p: str) -> str:
    return p.replace("\\", "/")


# The plan's AC-7 noise files, each with a marker the scanner would report from a source tree.
NOISE = {
    "_inspiration/external_code/x/a.properties": f"# {MARK} vendored\n",
    "mcp-server/bundle/index.mjs": f"// {MARK} bundled\n",
    "ui/out/main/index.js": f"// {MARK} built\n",
    "ui/out-e2e/main/index.js": f"// {MARK} built for e2e\n",
    "packaging/deno-win64/LICENSE.md": f"<!-- {MARK} fetched -->\n",
    "packaging/ffmpeg-win64/README.txt": f"{MARK} fetched\n",
    "native/region-picker/publish/a.xml": f"<!-- {MARK} published -->\n",
    "native/region-picker/obj/a.cs": f"// {MARK} intermediate\n",
    "ui/test-results/a.md": f"<!-- {MARK} test output -->\n",
    ".serena/cache/a.txt": f"{MARK} cache\n",
}
# The plan's AC-7 controls: source the scanner must still report.
CONTROLS = {
    "_inspiration/design.md": f"<!-- {MARK} -->\n",
    "mcp-server/src/a.ts": f"// {MARK} source\n",
    "ui/src/a.ts": f"// {MARK} source\n",
    "packaging/avkit-backend.spec": f"# {MARK} spec\n",
    "native/region-picker/a.cs": f"// {MARK} source\n",
}
JAR = b"PK\x03\x04\x00\x00\x00\x00\n" + f"{MARK} inside a jar\n".encode()


def _tree(root: Path, *, jar: bool = False) -> Path:
    (root / ".git").mkdir(parents=True)
    for rel, text in {**NOISE, **CONTROLS}.items():
        _write(root / rel, text)
    if jar:
        (root / "lib").mkdir()
        (root / "lib" / "x.jar").write_bytes(JAR)
    return root


def _paths(findings: list[dict[str, object]]) -> list[str]:
    return sorted(_norm(str(f["file_path"])) for f in findings)


# ─── AC-1, AC-2: the cp1252 console (D-944) ──────────────────────────────


def test_ac_1_help_under_cp1252_exits_0_with_utf8_bytes(tmp_path: Path) -> None:
    probe = subprocess.run(
        [sys.executable, "-c", "import sys; print(sys.stdout.encoding)"],
        cwd=tmp_path,
        env={**{k: v for k, v in os.environ.items() if k != "PYTHONUTF8"}, **CP1252},
        capture_output=True,
    )
    assert probe.stdout.strip().lower() == b"cp1252", repr(probe.stdout)
    f = _register(tmp_path / "known-issues.yaml", [])
    r = _cli(["--yaml", str(f), "--help"], tmp_path, CP1252)
    assert r.returncode == 0, repr(r.stderr.decode("utf-8", "replace")[-300:])
    assert b"\xe2\x86\x92" in r.stdout, repr(r.stdout[:200])


def test_ac_2_bucket_overlap_under_cp1252_exits_0(tmp_path: Path) -> None:
    issues = [
        _issue(i, category="MEU-NEW", priority="P3", related=["shared-tag"])
        for i in ("FIX-A", "FIX-B")
    ]
    f = _register(tmp_path / "known-issues.yaml", issues)
    r = _cli(["--yaml", str(f), "bucket"], tmp_path, CP1252)
    assert r.returncode == 0, repr(r.stderr.decode("utf-8", "replace")[-300:])
    out = r.stdout.decode("utf-8")
    assert "⚠ HAS RELATED OVERLAP" in out, repr(out[-300:])


# ─── AC-3 to AC-6: verify --deep (D-945, D-946, D-947) ───────────────────


def test_ac_3_path_like_and_strip_location(tmp_path: Path) -> None:
    assert hasattr(verify, "_is_path_like"), repr(sorted(dir(verify)))
    assert hasattr(verify, "_strip_location"), repr(sorted(dir(verify)))
    path_like = [
        "packages/core/nonexistent.py",
        "tools\\x.py",
        "README.md",
        "  ui/a.tsx  ",
        "tools/issue_triage.py:199",
        "C:\\x\\a.py:12:3",
    ]
    not_path_like = [
        "",
        "   ",
        "Fixed in Session 1 by editing tools/issue_triage.py and its tests",
        "https://example.com/a.py",
        "MEU-123",
        "deferred",
        None,
        42,
    ]
    wrong = [v for v in path_like if not verify._is_path_like(v)]
    wrong += [v for v in not_path_like if verify._is_path_like(v)]
    assert not wrong, repr(wrong)
    stripped = {
        "tools/issue_triage.py:199": "tools/issue_triage.py",
        "a.py:12:3": "a.py",
        "C:\\x\\a.py:7": "C:\\x\\a.py",
        "C:/x/a.py:7:1": "C:/x/a.py",
        "C:\\x\\a.py": "C:\\x\\a.py",
        "a.py:x": "a.py:x",
        ":12": ":12",
    }
    got = {k: verify._strip_location(k) for k in stripped}
    assert got == stripped, repr(got)


def test_ac_4_deep_checks_only_path_shaped_values(tmp_path: Path) -> None:
    (tmp_path / "present.py").write_bytes(b"x = 1\n")
    data = {
        "version": 1,
        "issues": [
            _issue("P-1", resolution_path="Fixed in Session 1 by changing the parser"),
            _issue("P-2", resolution_path="missing/file.py"),
            _issue("P-3", resolution_path="gone/other.py:9:2"),
            _issue("P-4", resolution_path="present.py"),
            _issue("P-5", resolution_path="present.py:3"),
        ],
    }
    findings = verify.verify_deep(data, project_root=tmp_path)
    got = sorted((f["issue_id"], f["type"], f["evidence_path"]) for f in findings)
    want = [
        ("P-2", "file_missing", str(tmp_path / "missing/file.py")),
        ("P-3", "file_missing", str(tmp_path / "gone/other.py")),
    ]
    assert got == want, repr(got)


def test_ac_5_deep_emits_no_test_coverage_finding(tmp_path: Path) -> None:
    _write(tmp_path / "tests" / "test_other.py", "def test_other():\n    assert True\n")
    data = {
        "version": 1,
        "issues": [
            _issue("COV-1", resolution_path="missing/file.py"),
            _issue("COV-2"),
        ],
    }
    types = {f["type"] for f in verify.verify_deep(data, project_root=tmp_path)}
    assert "no_test_coverage" not in types, repr(sorted(types))
    assert types <= {"file_missing"}, repr(sorted(types))


def test_ac_6_deep_is_read_only(tmp_path: Path) -> None:
    params = inspect.signature(verify.verify_deep).parameters
    assert "update_last_checked" not in params, repr(list(params))
    data = {"version": 1, "issues": [_issue("RO-1", resolution_path="missing/file.py")]}
    before = copy.deepcopy(data)
    verify.verify_deep(data, project_root=tmp_path)
    assert data == before, repr(data)

    missing = _register(tmp_path / "missing.yaml", data["issues"])
    raw = missing.read_bytes()
    r = _cli(["--yaml", str(missing), "verify", "--deep"], tmp_path, UTF8)
    assert (r.returncode, missing.read_bytes() == raw) == (1, True), repr(r.returncode)

    prose = _register(
        tmp_path / "prose.yaml", [_issue("RO-2", resolution_path="Fixed by a config change")]
    )
    raw = prose.read_bytes()
    r = _cli(["--yaml", str(prose), "verify", "--deep"], tmp_path, UTF8)
    assert (r.returncode, prose.read_bytes() == raw) == (0, True), repr(r.returncode)


# ─── AC-7 to AC-10: discover (D-948, D-953) ──────────────────────────────


def test_ac_7_discover_skips_generated_trees_from_any_root(tmp_path: Path) -> None:
    _tree(tmp_path)
    got = _paths(discover.scan_todos(tmp_path))
    assert got == sorted(CONTROLS), repr(got)
    assert hasattr(discover, "_repo_root"), repr(sorted(dir(discover)))
    assert discover._repo_root(tmp_path / "mcp-server") == tmp_path.resolve()
    sub = _paths(discover.scan_todos(tmp_path / "mcp-server"))
    assert sub == ["src/a.ts"], repr(sub)
    inside = [discover.scan_todos(tmp_path / p) for p in ("mcp-server/bundle", "ui/out")]
    assert inside == [[], []], repr(inside)


def test_ac_8_discover_skips_a_file_with_a_nul_byte(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "lib").mkdir()
    (tmp_path / "lib" / "x.jar").write_bytes(JAR)
    _write(tmp_path / "notes.txt", f"{MARK} a note\n")
    got = _paths(discover.scan_todos(tmp_path))
    assert got == ["notes.txt"], repr(got)


def test_ac_9_discover_skips_its_own_module_only(tmp_path: Path) -> None:
    assert hasattr(discover, "_SELF"), repr(sorted(dir(discover)))
    own = [
        p
        for p in _paths(discover.scan_todos(ROOT / "tools/issue_triage"))
        if p.endswith("discover.py")
    ]
    assert own == [], repr(own)
    (tmp_path / ".git").mkdir()
    _write(tmp_path / "discover.py", f"# {MARK} a copy that is not the scanner\n")
    got = _paths(discover.scan_todos(tmp_path))
    assert got == ["discover.py"], repr(got)


def _cli_candidates(out: str) -> tuple[int | None, list[str]]:
    m = re.search(r"New candidates: (\d+)", out)
    words = "|".join(discover.SCAN_PATTERNS)
    listed = re.findall(rf"^  (?:{words}) (.+?):\d+ -- ", out, re.MULTILINE)
    return (int(m.group(1)) if m else None), sorted(_norm(p) for p in listed)


def test_ac_10_discover_cli_counts_only_source(tmp_path: Path) -> None:
    tree = _tree(tmp_path / "tree", jar=True)
    f = _register(tmp_path / "known-issues.yaml", [])
    raw = f.read_bytes()
    got = []
    for root in (tree, tree / "mcp-server", tree / "mcp-server" / "bundle"):
        r = _cli(["--yaml", str(f), "discover", "--root", str(root), "--dry-run"], tmp_path, UTF8)
        got.append((r.returncode, *_cli_candidates(r.stdout.decode("utf-8", "replace"))))
    want = [(0, 5, sorted(CONTROLS)), (0, 1, ["src/a.ts"]), (0, 0, [])]
    assert got == want, repr(got)
    assert f.read_bytes() == raw, repr(len(f.read_bytes()))


# ─── AC-11: triage's archive (D-949) ─────────────────────────────────────


def test_ac_11_triage_archives_resolved_and_dismissed(tmp_path: Path) -> None:
    data = {
        "version": 1,
        "issues": [
            _issue("AR-1", status="resolved", category="TECH-DEBT"),
            _issue("AR-2", status="dismissed"),
            _issue("AR-3", category="TECH-DEBT"),
            _issue("AR-4", category="DEFER"),
        ],
    }
    out = tmp_path / "triage-output.yaml"
    triage.generate_triage_output(data, out)
    result = yaml.safe_load(out.read_text(encoding="utf-8"))
    got = {k: [e["id"] for e in result[k]] for k in ("archived", "actionable", "deferred")}
    want = {"archived": ["AR-1", "AR-2"], "actionable": ["AR-3"], "deferred": ["AR-4"]}
    assert got == want, repr(got)
