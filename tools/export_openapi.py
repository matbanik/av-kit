"""Export or check the committed OpenAPI document (G8)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

from avkit_api.main import create_app
from avkit_api.wiring import AppServices

EXPORT_TOKEN = "openapi-export-token"


class _ExportLifecycle:
    def recover_stale_processing(self) -> None:
        return None

    def stop_processing(self) -> None:
        return None

    def unload(self) -> None:
        return None

    def cancel_processing(self) -> None:
        return None

    def liveness(self) -> SimpleNamespace:
        return SimpleNamespace(ok=True)


def _export_services() -> AppServices:
    life = _ExportLifecycle()
    return AppServices(
        download=life,
        transcript=life,
        tts=life,
        models=life,
        settings=life,
        health=life,
        conversion=life,
        capture=life,
    )


def build_openapi() -> dict[str, object]:
    """Return the FastAPI schema using dummy services (no live network)."""
    app = create_app(
        tokens=frozenset({EXPORT_TOKEN}),
        services=_export_services(),
        engine_dispose=None,
    )
    return app.openapi()


def render_openapi(schema: dict[str, object]) -> str:
    """Stable JSON text for committed-file comparison."""
    return json.dumps(schema, indent=2, sort_keys=True) + "\n"


def write_openapi(path: Path, schema: dict[str, object] | None = None) -> None:
    """Write the schema to `path`."""
    document = render_openapi(schema if schema is not None else build_openapi())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document, encoding="utf-8")


def check_openapi(path: Path, schema: dict[str, object] | None = None) -> None:
    """Raise SystemExit(1) when the committed file drifts."""
    expected = render_openapi(schema if schema is not None else build_openapi())
    if not path.is_file():
        raise SystemExit(f"missing OpenAPI file: {path}")
    actual = path.read_text(encoding="utf-8")
    if actual != expected:
        raise SystemExit(f"OpenAPI drift: {path}")


def main(argv: list[str] | None = None) -> int:
    """CLI: `--check PATH` and/or `-o PATH`."""
    parser = argparse.ArgumentParser(description="Export or check av-kit OpenAPI")
    parser.add_argument("--check", metavar="PATH", help="Fail when PATH drifts from live schema")
    parser.add_argument("-o", "--output", metavar="PATH", help="Write live schema to PATH")
    args = parser.parse_args(argv)
    if args.check is None and args.output is None:
        parser.error("pass --check PATH and/or -o PATH")
    schema = build_openapi()
    if args.output is not None:
        write_openapi(Path(args.output), schema)
    if args.check is not None:
        check_openapi(Path(args.check), schema)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
