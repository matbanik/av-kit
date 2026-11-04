"""Invoke PyInstaller on packaging/avkit-backend.spec (onedir)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_FILE = REPO_ROOT / "packaging" / "avkit-backend.spec"
PACK_DIST_DIR = REPO_ROOT / "packaging" / "dist" / "avkit-backend"
PACK_DIST_EXE = PACK_DIST_DIR / "avkit-backend.exe"
EXCLUDE_GLOBS = (
    "**/.avkit/models/**",
    "**/avkit.db",
    "**/.env",
    "**/*.onnx",
    "**/*.pth",
    "**/cuda/**",
    "**/cudnn/**",
)


def _write_layout_stub() -> None:
    """Create the onedir folder shape when PyInstaller is not installed."""
    internal = PACK_DIST_DIR / "_internal"
    internal.mkdir(parents=True, exist_ok=True)
    if not PACK_DIST_EXE.is_file():
        PACK_DIST_EXE.write_bytes(b"MZ")
    (internal / ".keep").write_text("onedir-support\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """Run PyInstaller -y --noconfirm on SPEC_FILE, or write a layout stub."""
    parser = argparse.ArgumentParser(description="Package avkit-backend onedir")
    parser.add_argument(
        "--stub-ok",
        action="store_true",
        help="If PyInstaller is missing, write PACK_DIST_DIR stub and exit 0",
    )
    args = parser.parse_args(argv)
    if not SPEC_FILE.is_file():
        print(f"missing spec: {SPEC_FILE}", file=sys.stderr)
        return 2
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        if not args.stub_ok:
            print("PyInstaller is not installed", file=sys.stderr)
            return 3
        _write_layout_stub()
        print(f"WARN: wrote layout stub at {PACK_DIST_DIR}")
        return 0
    work = REPO_ROOT / "packaging" / "build"
    dist = REPO_ROOT / "packaging" / "dist"
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "-y",
        "--noconfirm",
        "--workpath",
        str(work),
        "--distpath",
        str(dist),
        str(SPEC_FILE),
    ]
    return int(subprocess.call(cmd))


if __name__ == "__main__":
    raise SystemExit(main())
