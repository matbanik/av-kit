"""Session 49b register rewrite (task rows 4, 5 and 7; plan §Register rewrite).

Three modes, each one save of `.agent/context/known-issues.yaml` through `model.save`:

  --mode reformat  Saves the register's own data unchanged, so only the layout moves.
                   It exits 1 unless the file it wrote parses equal to the data it read.
  --mode reword    Replaces the fields in REWORDS, each only if it still holds the
                   `before` text exactly. It exits 1 unless the only parsed difference
                   is those fields.
  --mode resolve   Sets RESOLVE_KEYS on RESOLVE_ISSUE from the JSON file `--set-file`
                   names. It exits 1 unless every parsed difference is under those keys.

The run holds the register through one Windows handle that denies other writers, from
the first read to the last, so another process's write in that interval fails loudly in
that process instead of being overwritten here. If another process already has the
register open for writing, the run refuses. `--expect-sha256` refuses unless the bytes
read through the handle have that hash (S4). The bytes read are kept in SCRATCH.

`model.save` writes to a staged copy in SCRATCH, which is checked: the parsed difference,
the parse back to the data saved, the validator's bounded grammar over the whole file,
`issue_decision_log` reading every issue's decision ids and stages as the data hold them,
and (after reword) no decision log matching the placeholder pattern. Only a staged copy
with no problem replaces the register's contents, through the held handle. `--target`
copies the staged file to another path instead, and the register is then never written.
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
SCRATCH = Path("C:/Temp/av-kit/s49b")

RESOLVE_ISSUE = "CLOSEOUT-CHECK-REFUSES-REGISTER"
RESOLVE_KEYS = ("status", "verification", "resolution_path")

# (issue, decision id, field path, before, after). The upper-case names stand for values.
REWORDS: tuple[tuple[str, str, tuple[str | int, ...], str, str], ...] = (
    (
        "CAPTURE-FLATTEN-WITH-BACKUP",
        "D-15",
        ("chosen",),
        "POST /captures/{id}/flatten copies original to {inbox}/.avkit-backup/{stem}.{YYYYMMDD-HHMMSS}.png, bakes over original_path, clears annotated_path + sidecar; POST .../revert restores the newest backup; settings capture.flatten_backup (default on) and capture.backup_dir (default {inbox}/.avkit-backup); no retention cap (the user prunes) so no governance number is introduced; MCP mirrors both actions",
        "POST /captures/ID/flatten copies original to INBOX/.avkit-backup/STEM.YYYYMMDD-HHMMSS.png (ID is the capture id, INBOX the capture inbox, STEM the original's file stem), bakes over original_path, clears annotated_path + sidecar; POST .../revert restores the newest backup; settings capture.flatten_backup (default on) and capture.backup_dir (default INBOX/.avkit-backup); no retention cap (the user prunes) so no governance number is introduced; MCP mirrors both actions",
    ),
    (
        "TTS-VOICE-PACK-LAZY-FETCH",
        "D-42",
        ("chosen",),
        "Yes: voices/<id>.pt is fetched through the existing managed-download path (on first selection or with the model), shown as ready/missing, and a generate with a missing pack fails fast with a named reason instead of fetching mid-run",
        "Yes: voices/ID.pt (ID is the voice id) is fetched through the existing managed-download path (on first selection or with the model), shown as ready/missing, and a generate with a missing pack fails fast with a named reason instead of fetching mid-run",
    ),
    (
        "MCP-TTS-GENERATE-SYNCHRONOUS",
        "D-44",
        ("chosen",),
        "POST /tts/generate queues the job and returns it at once (Queued/Running); synthesis runs in the background; clients poll the job and DELETE /tts/{id} cancels a running job between segments; MCP generate returns the job id and the GUI run bar polls",
        "POST /tts/generate queues the job and returns it at once (Queued/Running); synthesis runs in the background; clients poll the job and DELETE /tts/ID (ID is the job id) cancels a running job between segments; MCP generate returns the job id and the GUI run bar polls",
    ),
    (
        "MCP-SETUP-PROMPT",
        "D-47",
        ("chosen",),
        "Settings MCP card shows the prompt with the server command/path and per-client placement (project .mcp.json mcpServers for Claude Code/Cursor/Claude Desktop/Windsurf; .vscode/mcp.json servers+type stdio for VS Code) using ${AVKIT_API_TOKEN} expansion; the real token is injected only by the main process on Copy and never enters the renderer",
        "Settings MCP card shows the prompt with the server command/path and per-client placement (project .mcp.json mcpServers for Claude Code/Cursor/Claude Desktop/Windsurf; .vscode/mcp.json servers+type stdio for VS Code) using environment-variable expansion of AVKIT_API_TOKEN (a dollar sign and the name in braces); the real token is injected only by the main process on Copy and never enters the renderer",
    ),
    (
        "MCP-SETUP-PROMPT",
        "D-47",
        ("precedents", 1),
        "known-issues MCP-SETUP-PROMPT root_cause — Claude Code docs research 2026-10-03 (.mcp.json scope, mcpServers vs servers shapes, ${VAR} expansion)",
        "known-issues MCP-SETUP-PROMPT root_cause — Claude Code docs research 2026-10-03 (.mcp.json scope, mcpServers vs servers shapes, dollar-brace environment-variable expansion)",
    ),
    (
        "MCP-SETUP-PROMPT",
        "D-47",
        ("reasoning",),
        "Research in the issue converges on project .mcp.json + ${VAR}; keeping the token in main preserves the existing security boundary. Two-way.",
        "Research in the issue converges on project .mcp.json + dollar-brace environment-variable expansion; keeping the token in main preserves the existing security boundary. Two-way.",
    ),
    (
        "MCP-SETUP-PROMPT",
        "D-49",
        ("question",),
        "Does any setup-prompt block carry the token or a ${AVKIT_API_TOKEN} expansion?",
        "Does any setup-prompt block carry the token or a dollar-brace expansion of AVKIT_API_TOKEN?",
    ),
    (
        "MCP-SETUP-PROMPT",
        "D-49",
        ("chosen",),
        "No token in any block; the server reads {app_data}/mcp-token.txt itself; AVKIT_APP_DATA is emitted only when not the default; a regex test with a fixture token. The existing Copy MCP config and Pin buttons are unchanged. Supersedes the ${VAR}/inject-on-Copy part of D-47 for the prompt only.",
        "No token in any block; the server reads mcp-token.txt in the app data folder itself; AVKIT_APP_DATA is emitted only when not the default; a regex test with a fixture token. The existing Copy MCP config and Pin buttons are unchanged. Supersedes the dollar-brace expansion and inject-on-Copy part of D-47 for the prompt only.",
    ),
    (
        "MCP-SETUP-PROMPT",
        "D-49",
        ("reasoning",),
        "A file the server already reads beats both a literal token and ${VAR} expansion (which still needs the user to set an env var). Two-way.",
        "A file the server already reads beats both a literal token and dollar-brace expansion (which still needs the user to set an env var). Two-way.",
    ),
    (
        "MCP-SETUP-PROMPT",
        "D-52",
        ("chosen",),
        "The agent calls avkit_health, reports api_base and app_data, and ends with exactly one 'RESULT: connected <api_base>' or 'RESULT: failed (<step>, <error>)' line; no new instance_id.",
        "The agent calls avkit_health, reports api_base and app_data, and ends with exactly one 'RESULT: connected API_BASE' or 'RESULT: failed (STEP, ERROR)' line, the upper-case names standing for the values; no new instance_id.",
    ),
    (
        "MCP-SETUP-PROMPT",
        "D-53",
        ("chosen",),
        "Back up to <file>.avkit-backup-<UTC> and merge, never overwrite; conditional restart line ('If the tools do not appear, quit and reopen <client>, then reply Ready').",
        "Back up to FILE.avkit-backup-UTC and merge, never overwrite; conditional restart line ('If the tools do not appear, quit and reopen CLIENT, then reply Ready'), FILE being the client's config file, UTC a UTC timestamp and CLIENT the client's name.",
    ),
    (
        "MCP-SETUP-PROMPT",
        "D-57",
        ("precedents", 0),
        "ui/src/main/index.ts:150-151 — the app falls back to LOCALAPPDATA ?? <home>/AppData/Local, then av-kit",
        "ui/src/main/index.ts:150-151 — the app falls back to LOCALAPPDATA ?? the home folder's AppData/Local, then av-kit",
    ),
    (
        "MCP-SETUP-PROMPT",
        "D-58",
        ("chosen",),
        "avkit_health action=dependencies must return successfully (it needs the token; any dependency availability values count). liveness alone never yields connected. The prompt ends with exactly one 'RESULT: connected' or 'RESULT: failed (<step>, <error>)' line, where <error> is the server's error code (for example token_missing, app_not_running). No api_base/app_data reporting: no health response carries them.",
        "avkit_health action=dependencies must return successfully (it needs the token; any dependency availability values count). liveness alone never yields connected. The prompt ends with exactly one 'RESULT: connected' or 'RESULT: failed (STEP, ERROR)' line, where ERROR is the server's error code (for example token_missing, app_not_running) and STEP the step that failed. No api_base/app_data reporting: no health response carries them.",
    ),
    (
        "QUEUE-PILL-TOKEN-DRIFT",
        "D-72",
        ("chosen",),
        "Pin PILL_TOKEN_SOURCE to Zorivest commit 1f254832 (git show <sha>:ui/src/renderer/src/globals.css); re-porting becomes a deliberate bump of the sha and the hexes together",
        "Pin PILL_TOKEN_SOURCE to Zorivest commit 1f254832 (git show SHA:ui/src/renderer/src/globals.css, SHA being that commit); re-porting becomes a deliberate bump of the sha and the hexes together",
    ),
    (
        "CONVERT-EXTRACT-STREAM-INDEX-MISMATCH",
        "D-227",
        ("precedents", 1),
        "packages/infrastructure/src/avkit_infra/media/adapter.py:634-635 — a:{stream_index}",
        "packages/infrastructure/src/avkit_infra/media/adapter.py:634-635 — the stream specifier a: followed by the stream index",
    ),
)

REWORD_ISSUES = tuple(dict.fromkeys(issue_id for issue_id, *_ in REWORDS))


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


def entry(data: dict[str, Any], issue_id: str, decision_id: str) -> dict[str, Any]:
    issue = model.get_issue(data, issue_id)
    if issue is None:
        raise SystemExit(f"FAIL: the register has no issue {issue_id}")
    for item in (issue.get("enrichment") or {}).get("decision_log") or []:
        if item.get("id") == decision_id:
            return item
    raise SystemExit(f"FAIL: issue {issue_id} has no decision {decision_id}")


def apply_rewords(data: dict[str, Any]) -> list[str]:
    """Replace each REWORDS field in place; return the problems found."""
    problems = []
    for issue_id, decision_id, path, before, after in REWORDS:
        parent: Any = entry(data, issue_id, decision_id)
        for key in path[:-1]:
            parent = parent[key]
        if parent[path[-1]] != before:
            problems.append(f"{issue_id} {decision_id} {path}: the register no longer holds the planned before text")
            continue
        if validator.PLACEHOLDER.search(after):
            problems.append(f"{issue_id} {decision_id} {path}: the after text matches the placeholder pattern")
        parent[path[-1]] = after
    return problems


def apply_resolve(data: dict[str, Any], values: dict[str, Any]) -> list[str]:
    """Set RESOLVE_KEYS on RESOLVE_ISSUE from VALUES; return the problems found."""
    extra = sorted(set(values) - set(RESOLVE_KEYS))
    if extra or not values:
        return [f"the set file must hold only {list(RESOLVE_KEYS)}; it holds {sorted(values)}"]
    issue = model.get_issue(data, RESOLVE_ISSUE)
    if issue is None:
        return [f"the register has no issue {RESOLVE_ISSUE}"]
    issue.update(values)
    try:
        model.validate_strict(data)
    except model.IssueTriageError as exc:
        return [f"the resolved register fails validate_strict: {exc}"]
    return []


def differences(a: Any, b: Any, path: str = "") -> list[str]:
    """Every path at which two parsed values differ."""
    if isinstance(a, dict) and isinstance(b, dict):
        if list(a) != list(b):
            return [f"{path}: keys differ"]
        return [d for k in a for d in differences(a[k], b[k], f"{path}.{k}")]
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: lengths differ"]
        return [d for n, (x, y) in enumerate(zip(a, b)) for d in differences(x, y, f"{path}[{n}]")]
    return [] if type(a) is type(b) and a == b else [path or "<root>"]


def check_written(text: str, data: dict[str, Any], name: str, reworded: bool) -> list[str]:
    problems = []
    placeholder_only: list[str] = []
    try:
        validator.check_yaml_subset(text, name)
    except validator.Refuse as exc:
        problems.append(f"bounded grammar over the whole file: {exc}")
    logs = 0
    for issue in data["issues"]:
        log = (issue.get("enrichment") or {}).get("decision_log")
        if not log:
            continue
        logs += 1
        expected = [(item["id"], item.get("stage")) for item in log]
        try:
            actual = validator.issue_decision_log(text, name, issue["id"])
        except validator.Refuse as exc:
            # Before the reword, the only refusal allowed is the placeholder test on the
            # issues REWORDS changes; any other refusal is a grammar the reader can't read.
            if not reworded and issue["id"] in REWORD_ISSUES and "template placeholder" in str(exc):
                placeholder_only.append(issue["id"])
                continue
            problems.append(f"{issue['id']}: issue_decision_log refused: {exc}")
            continue
        if actual != expected:
            problems.append(f"{issue['id']}: issue_decision_log read {actual}, the data hold {expected}")
    refused = sum(1 for p in problems if "issue_decision_log" in p)
    print(f"decision logs read: {logs - refused - len(placeholder_only)} of {logs}")
    if not reworded:
        print(f"refused by the placeholder test only, as planned: {sorted(placeholder_only)}")
        if sorted(placeholder_only) != sorted(REWORD_ISSUES):
            problems.append(f"the placeholder-only refusals {sorted(placeholder_only)} are not the planned {sorted(REWORD_ISSUES)}")
    if reworded:
        hits = [
            issue["id"]
            for issue in data["issues"]
            for item in (issue.get("enrichment") or {}).get("decision_log") or []
            if any(validator.PLACEHOLDER.search(str(v)) for v in _strings(item))
        ]
        if hits:
            problems.append(f"decision logs still matching the placeholder pattern: {hits}")
    return problems


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [s for v in value.values() for s in _strings(v)]
    if isinstance(value, list):
        return [s for v in value for s in _strings(v)]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("reformat", "reword", "resolve"), required=True)
    parser.add_argument("--target", type=Path, default=REGISTER, help="where to save; the register by default")
    parser.add_argument("--expect-sha256", required=True, help="refuse unless the register has this SHA-256 (S4)")
    parser.add_argument("--set-file", type=Path, help="--mode resolve: JSON object of RESOLVE_KEYS values")
    args = parser.parse_args()
    if (args.mode == "resolve") != (args.set_file is not None):
        parser.error("--set-file goes with --mode resolve, and only with it")

    try:
        with ExclusiveHandle(REGISTER) as handle:
            return rewrite(args, handle)
    except HandleRefused as exc:
        print(f"FAIL: another process has the register open for writing ({exc}) (S4)")
        print("register-rewrite: nothing written")
        return 1


def rewrite(args: argparse.Namespace, handle: ExclusiveHandle) -> int:
    raw_before = handle.read()
    before_sha = hashlib.sha256(raw_before).hexdigest()
    if before_sha != args.expect_sha256:
        print(f"FAIL: the register's sha256 is {before_sha}, not the expected {args.expect_sha256} (S4)")
        print("register-rewrite: nothing written")
        return 1
    (SCRATCH / "stage").mkdir(parents=True, exist_ok=True)
    kept = SCRATCH / f"register-before-{args.mode}.yaml"
    kept.write_bytes(raw_before)
    original = model.load(kept)
    data = copy.deepcopy(original)
    problems: list[str] = []
    changed: set[str] = set()
    if args.mode == "resolve":
        problems += apply_resolve(data, json.loads(args.set_file.read_text(encoding="utf-8")))
        index = [i["id"] for i in original["issues"]].index(RESOLVE_ISSUE)
        changed = set(differences(original, data))
        outside = sorted(p for p in changed if not p.startswith(tuple(f".issues[{index}].{k}" for k in RESOLVE_KEYS)))
        if outside:
            problems.append(f"resolve changes paths outside {list(RESOLVE_KEYS)}: {outside}")
    if args.mode == "reword":
        problems += apply_rewords(data)
        changed = {
            "".join(
                [f".issues[{[i['id'] for i in original['issues']].index(issue_id)}]", ".enrichment.decision_log"]
                + [f"[{[d['id'] for d in model.get_issue(original, issue_id)['enrichment']['decision_log']].index(decision_id)}]"]
                + [f".{k}" if isinstance(k, str) else f"[{k}]" for k in path]
            )
            for issue_id, decision_id, path, _, _ in REWORDS
        }
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        print("register-rewrite: nothing written")
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
    problems += check_written(text, written, REGISTER.name, args.mode != "reformat")

    raw = stage.read_bytes()
    print(f"mode={args.mode} target={args.target} staged={stage} kept={kept}")
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        print(f"register-rewrite: {len(problems)} problem(s); nothing written")
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
    print(f"parsed fields changed: {len(diff)} (planned {len(changed)})")
    for problem in problems:
        print(f"FAIL: {problem}")
    print(f"register-rewrite: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
