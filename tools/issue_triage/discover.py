"""Issue Triage — TODO/FIXME/HACK discovery scanner.

Scans source files for TODO, FIXME, and HACK markers in comments.
Produces candidate findings for potential issue registration.
Pure Python — no external dependencies (pathlib + re).
"""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path
from typing import Any

# ─── Configuration ────────────────────────────────────────────────────────

# Patterns to scan for (case-insensitive match)
SCAN_PATTERNS = ("TODO", "FIXME", "HACK")

# Regex that matches any of the scan patterns
_PATTERN_RE = re.compile(
    r"\b(" + "|".join(SCAN_PATTERNS) + r")\b",
    re.IGNORECASE,
)

# Regex to extract issue IDs like TODO(MCP-ZODSTRIP) or FIXME[BUG-123]
_ISSUE_ID_RE = re.compile(
    r"\b(?:TODO|FIXME|HACK)\s*[\(\[]([A-Z][A-Z0-9_-]+[A-Z0-9])[\)\]]",
    re.IGNORECASE,
)

# Directories to exclude from scanning (both single-segment and multi-segment)
EXCLUDED_DIRS = frozenset(
    {
        "__pycache__",
        ".git",
        ".hg",
        ".svn",
        "node_modules",
        ".venv",
        "venv",
        ".env",
        ".tox",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "dist",
        "build",
        ".agent",
        ".hypothesis",
        ".kilo",
        # .gitignore's slash-free generated trees (D-948)
        "bin",
        "Bin",
        "obj",
        "Obj",
        "test-results",
        "playwright-report",
        "blob-report",
        ".playwright",
        "htmlcov",
    }
)

# Multi-segment directory exclusions: fnmatch patterns over the repository path, with
# forward slashes; `*` matches across `/`. They mirror .gitignore's generated, fetched and
# vendored trees (D-948).
EXCLUDED_PATHS = frozenset(
    {
        "docs/execution",
        "_inspiration/external_code",
        "mcp-server/bundle",
        "mcp-server/dist",
        "ui/out",
        "ui/out-e2e",
        "ui/dist",
        "packaging/build",
        "packaging/dist",
        "packaging/ffmpeg-win64",
        "packaging/deno-win64",
        "native/*/publish",
        ".serena/cache",
    }
)

# This module, which names the markers it scans for; it is never a candidate (D-948)
_SELF = Path(__file__).resolve()

# A file whose first bytes hold a NUL byte is binary and is skipped (D-948)
_BINARY_SNIFF_BYTES = 8000

# Binary file extensions to skip
BINARY_EXTENSIONS = frozenset(
    {
        ".pyc",
        ".pyo",
        ".pyd",
        ".so",
        ".dll",
        ".exe",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".bmp",
        ".ico",
        ".svg",
        ".webp",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".zip",
        ".tar",
        ".gz",
        ".bz2",
        ".7z",
        ".rar",
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".db",
        ".sqlite",
        ".sqlite3",
        ".wasm",
        ".map",
        ".lock",
    }
)

# Component inference from path prefixes
_COMPONENT_PREFIXES: dict[str, str] = {
    "packages/core": "core",
    "packages/infrastructure": "infrastructure",
    "packages/api": "api",
    "packages/application": "core",
    "ui": "ui",
    "tools/mcp_server": "mcp-server",
    "tools": "infrastructure",
}

# Comment prefix patterns per file extension
# Lines must start with one of these (after whitespace) to be considered comments
_COMMENT_PREFIXES: dict[str, tuple[str, ...]] = {
    # Python, shell, YAML, TOML, etc.
    ".py": ("#",),
    ".sh": ("#",),
    ".bash": ("#",),
    ".yaml": ("#",),
    ".yml": ("#",),
    ".toml": ("#",),
    ".cfg": ("#",),
    ".ini": ("#", ";"),
    ".conf": ("#",),
    # JavaScript/TypeScript family
    ".js": ("//", "/*", "*"),
    ".jsx": ("//", "/*", "*"),
    ".ts": ("//", "/*", "*"),
    ".tsx": ("//", "/*", "*"),
    ".mjs": ("//", "/*", "*"),
    ".cjs": ("//", "/*", "*"),
    ".css": ("/*", "*"),
    ".scss": ("//", "/*", "*"),
    # C-family
    ".c": ("//", "/*", "*"),
    ".h": ("//", "/*", "*"),
    ".cpp": ("//", "/*", "*"),
    ".rs": ("//", "/*", "*"),
    ".go": ("//", "/*", "*"),
    ".java": ("//", "/*", "*"),
    # Markup
    ".html": ("<!--",),
    ".xml": ("<!--",),
    ".svg": ("<!--",),
    ".md": ("<!--",),
    # Other
    ".sql": ("--", "/*", "*"),
    ".lua": ("--",),
    ".rb": ("#",),
    ".r": ("#",),
    ".ps1": ("#",),
    ".bat": ("REM", "rem", "::"),
    ".cmd": ("REM", "rem", "::"),
    # Data formats with NO comment syntax
    ".json": (),
    ".csv": (),
}

# Valid source values for --source
VALID_SOURCES = frozenset({"todo"})


# ─── Scanner ──────────────────────────────────────────────────────────────


def scan_todos(
    root: Path,
    *,
    existing_issue_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Scan a directory tree for TODO/FIXME/HACK markers in comments.

    Args:
        root: Root directory to scan.
        existing_issue_ids: Known issue IDs for deduplication. Comments
            mentioning these IDs get a ``linked_issue_id`` field instead
            of being treated as new candidates.

    Returns:
        List of findings, each with:
          - file_path: str (relative to root)
          - line_number: int (1-indexed)
          - pattern: str ("TODO" | "FIXME" | "HACK")
          - raw_text: str (trimmed line content)
          - component: str (inferred from path)
          - linked_issue_id: str | None (if matching existing issue)
    """
    existing_ids = existing_issue_ids or set()
    findings: list[dict[str, Any]] = []

    # Exclusions are matched against the repository path, whatever root is given (D-953).
    anchor = _repo_root(root)
    if _in_excluded_tree(root, anchor):
        return findings

    for file_path in _walk_source_files(root, anchor):
        if file_path.resolve() == _SELF:
            continue
        rel_path = file_path.relative_to(root)
        component = _infer_component(str(rel_path))
        comment_prefixes = _get_comment_prefixes(file_path.suffix.lower())

        try:
            raw = file_path.read_bytes()
        except OSError:
            continue
        if b"\x00" in raw[:_BINARY_SNIFF_BYTES]:
            continue
        text = raw.decode("utf-8", errors="ignore")

        for line_num, line in enumerate(text.splitlines(), start=1):
            # Only scan comment lines — skip string literals and code
            if not _is_comment_line(line, comment_prefixes):
                continue

            match = _PATTERN_RE.search(line)
            if match:
                pattern = match.group(1).upper()
                linked_id = _extract_linked_id(line, existing_ids)
                findings.append(
                    {
                        "file_path": str(rel_path),
                        "line_number": line_num,
                        "pattern": pattern,
                        "raw_text": line.strip(),
                        "component": component,
                        "linked_issue_id": linked_id,
                    }
                )

    return findings


# ─── Helpers ──────────────────────────────────────────────────────────────


def _repo_root(root: Path) -> Path:
    """The first of ROOT (resolved) and its parents that holds a `.git` entry, else ROOT."""
    start = root.resolve()
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    return start


def _excluded_path(rel: str) -> bool:
    """Whether the repository path REL matches one EXCLUDED_PATHS pattern."""
    return any(fnmatch.fnmatchcase(rel, pattern) for pattern in EXCLUDED_PATHS)


def _in_excluded_tree(root: Path, anchor: Path) -> bool:
    """Whether the scan ROOT itself lies in an excluded tree of the repository at ANCHOR."""
    try:
        parts = root.resolve().relative_to(anchor).parts
    except ValueError:
        return False
    if any(part in EXCLUDED_DIRS for part in parts):
        return True
    return any(_excluded_path("/".join(parts[:n])) for n in range(1, len(parts) + 1))


def _walk_source_files(directory: Path, anchor: Path) -> list[Path]:
    """Walk directory tree, excluding configured paths and binary files.

    Args:
        directory: Current directory being iterated.
        anchor: The repository root (`_repo_root`), preserved across recursion;
            multi-segment exclusions match each directory's path relative to it.
    """
    results: list[Path] = []

    if not directory.is_dir():
        return results

    for item in sorted(directory.iterdir()):
        if item.is_dir():
            # Single-segment exclusion (name-only)
            if item.name in EXCLUDED_DIRS:
                continue
            # Multi-segment exclusion (relative to the repository root)
            try:
                rel = item.resolve().relative_to(anchor).as_posix()
            except ValueError:
                rel = item.name
            if _excluded_path(rel):
                continue
            results.extend(_walk_source_files(item, anchor))
        elif item.is_file():
            if item.suffix.lower() in BINARY_EXTENSIONS:
                continue
            results.append(item)

    return results


def _infer_component(rel_path: str) -> str:
    """Infer component name from relative file path.

    Falls back to 'infrastructure' for paths that don't match any prefix,
    which is a valid component in the issue schema.
    """
    normalized = rel_path.replace("\\", "/")
    for prefix, component in _COMPONENT_PREFIXES.items():
        if normalized.startswith(prefix + "/") or normalized.startswith(prefix + "\\"):
            return component
    return "infrastructure"


def _get_comment_prefixes(extension: str) -> tuple[str, ...] | None:
    """Get comment prefix patterns for a file extension.

    Returns None for unknown extensions (conservative: scan all lines).
    Returns empty tuple for extensions with no comment syntax (e.g., JSON).
    """
    return _COMMENT_PREFIXES.get(extension)


def _is_comment_line(line: str, comment_prefixes: tuple[str, ...] | None) -> bool:
    """Check if a line contains a comment.

    If comment_prefixes is None (unknown file type), returns True (conservative).
    If comment_prefixes is empty (no comment syntax, e.g. JSON), returns False.
    Otherwise checks if the line starts with or contains a comment prefix.
    """
    if comment_prefixes is None:
        return True
    if not comment_prefixes:
        return False
    stripped = line.lstrip()
    # Check if line starts with a comment prefix (pure comment line)
    if any(stripped.startswith(prefix) for prefix in comment_prefixes):
        return True
    # Check for inline comments (e.g., `x = 1  # TODO: fix`)
    return any(
        f" {prefix}" in line or f"\t{prefix}" in line for prefix in comment_prefixes
    )


def _extract_linked_id(line: str, existing_ids: set[str]) -> str | None:
    """Extract linked issue ID from a TODO/FIXME comment if it matches known IDs."""
    match = _ISSUE_ID_RE.search(line)
    if match:
        candidate_id = match.group(1)
        if candidate_id in existing_ids:
            return candidate_id
    return None
