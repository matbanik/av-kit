"""STE gate for the help card content (MEU-162, STE_GATE, D-1293; AC-162.2).

    uv run python tools/help_guide_ste.py              # lint the repository, exit 1 on a problem
    uv run python tools/help_guide_ste.py --selftest   # run the fixtures below

It loads the vendored ASD-STE100 linter (`.agent/skills/asd-ste100/scripts/ste-lint.py`) by
path and lints the help card text:

- Strict, for each quick start step in `components/help/quick-start.json`: 0 findings at any
  level (so a passive step fails), 20 or fewer words per sentence, 2 or fewer sentences and
  no `;`.
- Flavored, for each page `intro`, each shot `alt` and each topic body in the six
  `*-help-content.ts` modules whose id is not in `PINNED_TOPICS`: 0 `advisory-free` findings.

Levels: `advisory-free` is hard and `advisory` is soft. Any other level, or a missing one, is
a problem in every mode (fail closed). Nothing filters on a level named `hard`.

Each problem prints as `<page>:<part>: <rule>: <message>`, and the last line is
`help-guide-ste: <n> problems`. A missing `quick-start.json` is one problem, never an
exception.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LINTER_PATH = ROOT / ".agent" / "skills" / "asd-ste100" / "scripts" / "ste-lint.py"
QUICK_START = ROOT / "ui" / "src" / "renderer" / "src" / "components" / "help" / "quick-start.json"
FEATURES = "ui/src/renderer/src/features"
MODULES = {
    "downloader": f"{FEATURES}/downloader/downloader-help-content.ts",
    "transcript": f"{FEATURES}/transcript/transcript-help-content.ts",
    "tts": f"{FEATURES}/tts/tts-help-content.ts",
    "converter": f"{FEATURES}/converter/convert-help-content.ts",
    "capture": f"{FEATURES}/capture/capture-help-content.ts",
    "settings": f"{FEATURES}/settings/settings-help-content.ts",
}
PINNED_TOPICS = (
    "downloader:pause",
    "transcript:blocked",
    "capture:four-tools",
    "capture:original-annotated",
)
HARD = "advisory-free"
SOFT = "advisory"
MAX_STEP_WORDS = 20
MAX_STEP_SENTENCES = 2
TOPIC_RE = {k: re.compile(k + r":\s*'((?:[^'\\]|\\.)*)'") for k in ("id", "title", "body")}
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

Lint = Callable[[str], Any]


def load_linter(path: Path = LINTER_PATH) -> Lint:
    spec = importlib.util.spec_from_file_location("ste_lint_vendored", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load the STE linter from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.lint


def unescape(text: str) -> str:
    return re.sub(r"\\(.)", lambda m: {"n": "\n", "t": "\t"}.get(m.group(1), m.group(1)), text)


def parse_topics(text: str) -> list[dict[str, str]]:
    """The `id`, `title` and `body` single-quoted literals of a help content module, in order."""
    found = {k: [unescape(m.group(1)) for m in rx.finditer(text)] for k, rx in TOPIC_RE.items()}
    counts = {k: len(v) for k, v in found.items()}
    if len(set(counts.values())) != 1:
        raise ValueError(f"id, title and body counts differ: {counts}")
    return [
        {"id": i, "title": t, "body": b}
        for i, t, b in zip(found["id"], found["title"], found["body"], strict=True)
    ]


def sentences(text: str) -> list[str]:
    return [s for s in SENTENCE_SPLIT.split(text.strip()) if s]


def lint_part(where: str, text: str, strict: bool, lint: Lint) -> list[str]:
    problems: list[str] = []
    findings, _words = lint(text)
    for f in findings:
        level = f.get("level") if isinstance(f, dict) else None
        rule = f.get("rule", "?") if isinstance(f, dict) else "?"
        message = f.get("message", "") if isinstance(f, dict) else repr(f)
        if level not in (HARD, SOFT):
            problems.append(f"{where}: unknown-level: {rule} has level {level!r} ({message})")
        elif level == HARD or strict:
            problems.append(f"{where}: {rule}: {message}")
    if strict:
        parts = sentences(text)
        if len(parts) > MAX_STEP_SENTENCES:
            problems.append(
                f"{where}: step-sentences: {len(parts)} sentences (cap {MAX_STEP_SENTENCES})"
            )
        for s in parts:
            n = len(s.split())
            if n > MAX_STEP_WORDS:
                problems.append(f"{where}: step-words: a sentence has {n} words (cap 20)")
        if ";" in text:
            problems.append(f"{where}: step-semicolon: a step has a ';'")
    return problems


def check_quick_start(data: Any, lint: Lint) -> list[str]:
    if not isinstance(data, dict) or not isinstance(data.get("pages"), dict):
        return ["quick-start.json: shape: no 'pages' object"]
    problems: list[str] = []
    for page, spec in data["pages"].items():
        if not isinstance(spec, dict):
            problems.append(f"{page}:page: shape: not an object")
            continue
        intro = spec.get("intro")
        if isinstance(intro, str):
            problems += lint_part(f"{page}:intro", intro, False, lint)
        else:
            problems.append(f"{page}:intro: shape: not a string")
        steps = spec.get("steps")
        if not isinstance(steps, list) or not steps:
            problems.append(f"{page}:steps: shape: not a list of steps")
            steps = []
        for n, step in enumerate(steps, 1):
            text = step.get("text") if isinstance(step, dict) else None
            if isinstance(text, str):
                problems += lint_part(f"{page}:step{n}", text, True, lint)
            else:
                problems.append(f"{page}:step{n}: shape: no text")
        for shot in spec.get("shots") or []:
            name = shot.get("name", "?") if isinstance(shot, dict) else "?"
            alt = shot.get("alt") if isinstance(shot, dict) else None
            if isinstance(alt, str):
                problems += lint_part(f"{page}:shot:{name}:alt", alt, False, lint)
            else:
                problems.append(f"{page}:shot:{name}:alt: shape: no alt")
    return problems


def check_topics(modules: dict[str, str], lint: Lint) -> list[str]:
    problems: list[str] = []
    for feature, text in modules.items():
        try:
            topics = parse_topics(text)
        except ValueError as exc:
            problems.append(f"{feature}:topics: parse: {exc}")
            continue
        for topic in topics:
            if f"{feature}:{topic['id']}" in PINNED_TOPICS:
                continue
            problems += lint_part(f"{feature}:topic:{topic['id']}", topic["body"], False, lint)
    return problems


def run(root: Path = ROOT, lint: Lint | None = None) -> list[str]:
    lint = lint or load_linter(root / LINTER_PATH.relative_to(ROOT))
    problems: list[str] = []
    quick_start = root / QUICK_START.relative_to(ROOT)
    if not quick_start.is_file():
        problems.append("quick-start.json missing")
    else:
        try:
            data = json.loads(quick_start.read_bytes().decode("utf-8"))
        except ValueError as exc:
            problems.append(f"quick-start.json: parse: {exc}")
        else:
            problems += check_quick_start(data, lint)
    modules = {f: (root / p).read_bytes().decode("utf-8") for f, p in MODULES.items()}
    problems += check_topics(modules, lint)
    return problems


def _page(steps: list[str], intro: str = "Click Start.", alt: str = "The page.") -> dict:
    return {
        "schema": "help-quick-start/1",
        "pages": {
            "demo": {
                "intro": intro,
                "steps": [{"text": s, "target": None} for s in steps],
                "shots": [{"name": "demo", "steps": [1], "alt": alt}],
            }
        },
    }


def negatives(lint: Lint) -> dict[str, list[str]]:
    """The five negative fixtures of AC-162.2; each must give at least one problem."""
    twenty_one = " ".join(["word"] * 20) + " end."

    def unknown(_text: str) -> tuple[list[dict[str, Any]], int]:
        return [{"rule": "mystery", "level": "severe", "message": "an unknown level"}], 1

    return {
        "passive step": check_quick_start(_page(["The file is downloaded by the app."]), lint),
        "phrasal verb step": check_quick_start(_page(["Spin up the job."]), lint),
        "21-word sentence": check_quick_start(_page([twenty_one]), lint),
        "unpinned topic": check_topics(
            {"settings": "{ id: 'leaf-keys', title: 'T', body: 'Spin up the job.' }"}, lint
        ),
        "unknown level": check_quick_start(_page(["Click Start."]), unknown),
    }


def selftest() -> list[str]:
    """Each case returns a failure message or nothing; the list is the failures."""
    lint = load_linter()
    failures: list[str] = []

    def expect(name: str, ok: bool) -> None:
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
        if not ok:
            failures.append(name)

    parsed = parse_topics(
        "{ id: 'a', title: 'It\\'s here', body: 'Don\\'t stop.' },\n"
        "{ id: 'b', title: 'B', body: 'Two.' }"
    )
    expect(
        "the parser reads \\' escapes",
        parsed[0] == {"id": "a", "title": "It's here", "body": "Don't stop."},
    )
    expect("the parser keeps the order", [t["id"] for t in parsed] == ["a", "b"])
    try:
        parse_topics("{ id: 'a', title: 'A' }")
        expect("the parser refuses uneven literals", False)
    except ValueError:
        expect("the parser refuses uneven literals", True)
    for name, problems in negatives(lint).items():
        expect(f"negative: {name} gives a problem", bool(problems))
    expect(
        "a passive step fails on its advisory finding",
        any("passive-voice" in p for p in negatives(lint)["passive step"]),
    )
    expect(
        "a three-sentence step fails",
        any(
            "step-sentences" in p
            for p in check_quick_start(_page(["Click A. Click B. Click C."]), lint)
        ),
    )
    expect(
        "a ';' in a step fails",
        any(
            "step-semicolon" in p
            for p in check_quick_start(_page(["Click Add; click Start."]), lint)
        ),
    )
    expect("a clean step passes", check_quick_start(_page(["Click Start."]), lint) == [])
    expect(
        "an advisory finding in an intro is soft",
        check_quick_start(_page(["Click Start."], intro="The file is downloaded."), lint) == [],
    )
    expect(
        "an advisory-free finding in an alt is hard",
        bool(check_quick_start(_page(["Click Start."], alt="Spin up the job."), lint)),
    )

    def level(value: Any) -> Lint:
        return lambda _t: ([{"rule": "r", "level": value, "message": "m"}], 1)

    for value in ("hard", None, "", "ADVISORY-FREE"):
        expect(
            f"level {value!r} fails closed in a flavored part",
            any(
                "unknown-level" in p
                for p in check_topics({"tts": "{ id: 'x', title: 'X', body: 'Y.' }"}, level(value))
            ),
        )
    expect(
        "a pinned topic is not linted",
        check_topics(
            {"capture": "{ id: 'four-tools', title: 'T', body: 'Spin up the job.' }"}, lint
        )
        == [],
    )
    expect("a broken JSON shape is a problem", bool(check_quick_start({"pages": []}, lint)))
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        for rel in MODULES.values():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_bytes(b"{ id: 'x', title: 'X', body: 'Click Start.' }")
        try:
            got = run(root, lint)
            expect("a missing quick-start.json is one problem", got == ["quick-start.json missing"])
        except Exception as exc:  # noqa: BLE001 - the case is that nothing raises
            expect(f"a missing quick-start.json raises nothing ({exc!r})", False)
    return failures


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        failures = selftest()
        print(f"help-guide-ste selftest: {len(failures)} failure(s)")
        return 1 if failures else 0
    if argv:
        print("usage: help_guide_ste.py [--selftest]")
        return 2
    problems = run()
    for p in problems:
        print(p)
    print(f"help-guide-ste: {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
