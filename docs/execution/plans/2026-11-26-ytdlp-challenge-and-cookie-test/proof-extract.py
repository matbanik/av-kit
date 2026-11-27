"""Session 104 proof run (`PROOF_PAIR`, AC-168.4; task rows 1, 5 and 5b).

One extraction of the adapter's `SABR_PROBE_URL` with the client list of `COOKIE_EXTRACTOR_ARGS`
and no cookie option: no `cookiefile`, no `cookiesfrombrowser`. Deno is resolved as the packaged
app resolves it with no setting (D-1478): `JsRuntimeLocator(None, <bundle>)`, where the bundle is
`packaging/deno-win64/deno.exe`, the file `ui/electron-builder.yml` ships as `resources/deno`.

The script prints only these line kinds, in this order, and writes the same fields to `--out`:
`yt-dlp=`, `yt-dlp-ejs=`, `deno=`, `clients=`, `player=`, `variant=`, `challenge=` (a count per
fixed needle), `formats=`, `verdict=`, and `INCOMPLETE VERIFICATION` after a `blocked` verdict.
No log line of yt-dlp is printed, so no URL, path or cookie text reaches the receipt.

Verdict precedence (D-1479): `blocked` when the run met a network error, an HTTP 429, a bot check
or no player response; else `challenge-errors` when any challenge needle was logged; else `clean`
when the run returned at least one format; else `blocked`.

Exit: 0 when the verdict equals `--expect`, 1 when it differs, 4 when it is `blocked`, 2 on a usage
error or a refusal (the installed yt-dlp is not `--require-version`, or no Deno is found).
`--selftest` reaches no network.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.metadata
import io
import json
import pathlib
import re
import sys
from dataclasses import dataclass, field

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DENO_BUNDLE = ROOT / "packaging" / "deno-win64" / "deno.exe"

#: The fixed challenge needles: yt-dlp 2026.10.26 `_video.py` lines 3351 and 3355, and the two
#: texts of yt-dlp issue 18123.
NEEDLES: tuple[tuple[str, str], ...] = (
    ("n-challenge", "n challenge solving failed"),
    ("signature", "signature solving failed"),
    ("dispose-callback", "addondisposecallback"),
    ("page-reload", "page needs to be reloaded"),
)
#: A run that met one of these never proves anything (`blocked`).
BLOCKED_NEEDLES: tuple[str, ...] = (
    "http error 429",
    "too many requests",
    "sign in to confirm you",
    "confirm you're not a bot",
    "confirm you\u2019re not a bot",
    "failed to extract any player response",
    "unable to extract initial player response",
    "unable to download",
    "getaddrinfo failed",
    "timed out",
    "connection refused",
    "connection reset",
    "network is unreachable",
)
VERDICTS = ("challenge-errors", "clean", "blocked")
PLAYER_RE = re.compile(r"player[ /_-]([0-9a-f]{8})\b", re.IGNORECASE)
FIELDS = (
    "yt-dlp",
    "yt-dlp-ejs",
    "deno",
    "clients",
    "player",
    "variant",
    "challenge",
    "formats",
    "verdict",
)


@dataclass
class Run:
    """What one extraction gave: the logged lines (never printed), the formats and the error."""

    lines: list[str] = field(default_factory=list)
    formats: int = 0
    error: str | None = None


def challenge_counts(lines: list[str]) -> dict[str, int]:
    low = [line.lower() for line in lines]
    return {name: sum(needle in line for line in low) for name, needle in NEEDLES}


def classify(run: Run) -> str:
    text = [*run.lines, *([run.error] if run.error else [])]
    low = "\n".join(text).lower()
    if any(needle in low for needle in BLOCKED_NEEDLES):
        return "blocked"
    if any(challenge_counts(text).values()):
        return "challenge-errors"
    if run.formats > 0:
        return "clean"
    return "blocked"


def player_id(lines: list[str]) -> str:
    for line in lines:
        match = PLAYER_RE.search(line)
        if match:
            return match.group(1).lower()
    return "unknown"


def record(
    run: Run, *, ytdlp: str, ejs: str, deno: str, clients: list[str], variant: str
) -> dict[str, object]:
    counts = challenge_counts([*run.lines, *([run.error] if run.error else [])])
    return {
        "yt-dlp": ytdlp,
        "yt-dlp-ejs": ejs,
        "deno": deno,
        "clients": ",".join(clients),
        "player": player_id(run.lines),
        "variant": variant,
        "challenge": " ".join(f"{k}:{v}" for k, v in counts.items()),
        "formats": run.formats,
        "verdict": classify(run),
    }


def emit(data: dict[str, object], expect: str, out: pathlib.Path | None) -> int:
    for key in FIELDS:
        print(f"{key}={data[key]}")
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    if data["verdict"] == "blocked":
        print("INCOMPLETE VERIFICATION")
        return 4
    return 0 if data["verdict"] == expect else 1


class _Capture:
    """A yt-dlp logger that keeps every line in memory and prints none."""

    def __init__(self) -> None:
        self.lines: list[str] = []

    def debug(self, msg: str) -> None:
        self.lines.append(str(msg))

    info = warning = error = debug


def live_run(clients: list[str], variant: str | None, deno_path: pathlib.Path) -> Run:
    import yt_dlp

    from avkit_infra.youtube.adapter import SABR_PROBE_URL

    youtube: dict[str, object] = {"player_client": list(clients)}
    if variant is not None:
        youtube["player_js_variant"] = [variant]
    logger = _Capture()
    opts: dict[str, object] = {
        "quiet": False,
        "no_warnings": False,
        "logger": logger,
        "skip_download": True,
        "noplaylist": True,
        "extractor_args": {"youtube": youtube},
        "js_runtimes": {"deno": {"path": str(deno_path)}},
    }
    if "cookiefile" in opts or "cookiesfrombrowser" in opts:  # pragma: no cover - a guard
        raise SystemExit(2)
    run = Run(lines=logger.lines)
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:  # type: ignore[arg-type]
            info = ydl.extract_info(SABR_PROBE_URL, download=False, process=False)
        formats = (info or {}).get("formats") or []
        run.formats = len(formats)
    except Exception as exc:  # noqa: BLE001 - every failure is classified, none is printed
        run.error = str(exc).splitlines()[0] if str(exc) else type(exc).__name__
    return run


def _versions() -> tuple[str, str]:
    import yt_dlp

    try:
        ejs = importlib.metadata.version("yt-dlp-ejs")
    except importlib.metadata.PackageNotFoundError:
        ejs = "absent"
    return yt_dlp.version.__version__, ejs


def _default_variant() -> str:
    try:
        from yt_dlp.extractor.youtube._video import YoutubeIE

        return str(getattr(YoutubeIE, "_DEFAULT_PLAYER_JS_VARIANT", "") or "default")
    except Exception:  # noqa: BLE001
        return "default"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--require-version")
    parser.add_argument("--expect", choices=VERDICTS)
    parser.add_argument("--out", type=pathlib.Path)
    parser.add_argument("--variant", choices=("tv",))
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.require_version or not args.expect or args.out is None:
        print("usage: --require-version VERSION --expect VERDICT --out JSON [--variant tv]")
        return 2
    ytdlp, ejs = _versions()
    if ytdlp != args.require_version:
        print(f"refused: yt-dlp={ytdlp} is installed, not {args.require_version}")
        return 2
    from avkit_infra.youtube.adapter import COOKIE_EXTRACTOR_ARGS
    from avkit_infra.youtube.js_runtime import JsRuntimeLocator, probe_deno_version

    runtime = JsRuntimeLocator(None, DENO_BUNDLE).resolve()
    if runtime is None:
        print("refused: no Deno at the bundle path or on PATH")
        return 2
    deno = f"{probe_deno_version(runtime.path) or 'unknown'} ({runtime.source})"
    clients = [str(c) for c in COOKIE_EXTRACTOR_ARGS["youtube"]["player_client"]]  # type: ignore[union-attr]
    run = live_run(clients, args.variant, runtime.path)
    variant = args.variant or _default_variant()
    data = record(run, ytdlp=ytdlp, ejs=ejs, deno=deno, clients=clients, variant=variant)
    return emit(data, args.expect, args.out)


# --- selftest (no network)
COOKIE_VALUE = "SIDCC=made-up-cookie-value-0f9e8d7c"
HOME_PATH = "C:\\Users\\someone\\AppData\\Roaming\\made-up\\cookies.txt"


def _case(lines: list[str], formats: int, error: str | None = None) -> Run:
    return Run(lines=list(lines), formats=formats, error=error)


def selftest() -> int:
    failures: list[str] = []
    player = "[youtube] dQw4w9WgXcQ: Downloading player 0004de42-main"
    cases: list[tuple[str, Run, str]] = [
        (
            "clean",
            _case([player, "[youtube] dQw4w9WgXcQ: Downloading tv player API JSON"], 12),
            "clean",
        ),
        (
            "n challenge",
            _case([player, "WARNING: [youtube] dQw4w9WgXcQ: n challenge solving failed: x"], 9),
            "challenge-errors",
        ),
        (
            "signature",
            _case(["WARNING: [youtube] Signature solving failed: y"], 3),
            "challenge-errors",
        ),
        (
            "dispose",
            _case(["ERROR: addOnDisposeCallback is not a function"], 0),
            "challenge-errors",
        ),
        ("reload", _case(["WARNING: The page needs to be reloaded."], 4), "challenge-errors"),
        ("429", _case([player], 0, "ERROR: HTTP Error 429: Too Many Requests"), "blocked"),
        (
            "bot",
            _case([], 0, "ERROR: [youtube] x: Sign in to confirm you\u2019re not a bot"),
            "blocked",
        ),
        (
            "bot beats needle",
            _case(["n challenge solving failed", "Sign in to confirm you're not a bot"], 5),
            "blocked",
        ),
        ("no response", _case([], 0, "ERROR: Failed to extract any player response"), "blocked"),
        (
            "network",
            _case([], 0, "ERROR: Unable to download API page: getaddrinfo failed"),
            "blocked",
        ),
        ("nothing", _case([player], 0), "blocked"),
    ]
    for name, run, want in cases:
        got = classify(run)
        if got != want:
            failures.append(f"classify {name}: {got}, not {want}")
    if player_id([player]) != "0004de42" or player_id(["no id"]) != "unknown":
        failures.append("player_id")
    secret_run = _case(
        [player, f"[debug] cookie {COOKIE_VALUE} from {HOME_PATH}", "n challenge solving failed"], 7
    )
    for expect, run, want_code, want_tail in (
        ("challenge-errors", secret_run, 0, "verdict=challenge-errors"),
        ("clean", secret_run, 1, "verdict=challenge-errors"),
        ("clean", cases[5][1], 4, "INCOMPLETE VERIFICATION"),
        ("clean", cases[0][1], 0, "verdict=clean"),
    ):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            data = record(
                run,
                ytdlp="2026.11.23",
                ejs="0.8.0",
                deno="2.5.6 (bundled)",
                clients=["tv", "web_safari", "web"],
                variant="main",
            )
            code = emit(data, expect, None)
        out = buf.getvalue()
        lines = out.splitlines()
        kinds = [line.split("=", 1)[0] for line in lines if line != "INCOMPLETE VERIFICATION"]
        if code != want_code or lines[-1] != want_tail:
            failures.append(f"emit {expect}: exit {code} tail {lines[-1]!r}")
        if kinds != list(FIELDS):
            failures.append(f"emit {expect}: line kinds {kinds}")
        if "made-up-cookie-value" in out or "Users" in out or "someone" in out:
            failures.append(f"emit {expect}: a cookie value or home path reached the output")
    for name, failure in enumerate(failures):
        print(f"selftest failure {name + 1}: {failure}")
    print(
        f"proof-extract selftest: {len(cases)} classify cases, 4 emit cases, "
        f"{len(failures)} failure(s)"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
