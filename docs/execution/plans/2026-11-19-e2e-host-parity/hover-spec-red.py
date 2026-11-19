"""Session 97 (task row 1; AC-161.2; expert pass M3): real AC-126.8 under hover-none.

    uv run --no-sync python <plan>/hover-spec-red.py OUT_DIR

Before any tracked change, it copies `ui/tests/e2e/electron-app.ts` with row 4's planned `args`
option and `ui/tests/e2e/settings.test.ts` with `launchApp()` passing `EHP_HOVER_ARGS` into OUT_DIR
(which must not exist), every relative import made absolute, and runs only `AC-126.8` twice with
Playwright and the tracked global setup: natively, and with the hover-none Blink setting. A
junction `OUT_DIR/node_modules` to `ui/node_modules` lets the copies resolve their packages; it
is removed afterwards, also on an error. No tracked file is written; no clipboard spec runs.

Exit 0 when the native run passes and the hover-none run fails at the hover expectation with
`rgb(21, 94, 117)`, the second host's value: the setting survives the spec's own flow. Exit 1
otherwise, 2 on usage or an existing OUT_DIR.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
E2E = (ROOT / "ui/tests/e2e").as_posix()
HOVER_NONE = (
    "--blink-settings=primaryHoverType=1,availableHoverTypes=1,"
    "primaryPointerType=1,availablePointerTypes=1"
)
REST = "rgb(21, 94, 117)"


def sub(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"REFUSED: {old!r} occurs {text.count(old)} times")
    return text.replace(old, new)


def copies(out: Path) -> None:
    nl = "\r\n"
    app = (ROOT / "ui/tests/e2e/electron-app.ts").read_bytes().decode("utf-8")
    app = sub(app, "from './e2e-diag'", f"from '{E2E}/e2e-diag'")
    app = sub(app, "} from './electron-env'", f"}} from '{E2E}/electron-env'")
    app = sub(app, "const here = dirname(fileURLToPath(import.meta.url))", f"const here = '{E2E}'")
    app = sub(
        app, "  pointerShield?: false\n}", "  pointerShield?: false\n  args?: readonly string[]\n}"
    )
    app = sub(
        app,
        "{ main, env = {}, pointerShield }: LaunchOptions",
        "{ main, env = {}, pointerShield, args }: LaunchOptions",
    )
    app = sub(app, "main ?? DEFAULT_MAIN],", "main ?? DEFAULT_MAIN, ...(args ?? [])],")
    spec = (ROOT / "ui/tests/e2e/settings.test.ts").read_bytes().decode("utf-8")
    spec = sub(spec, "from './electron-app'", f"from '{out.as_posix()}/electron-app.copy'")
    spec = sub(spec, "from './test-ids'", f"from '{E2E}/test-ids'")
    spec = sub(spec, "} from './theme-probe'", f"}} from '{E2E}/theme-probe'")
    tail = f"-settings-')),{nl}    }},{nl}  }})"
    spec = sub(
        spec,
        tail,
        f"-settings-')),{nl}    }},{nl}"
        f"    args: process.env.EHP_HOVER_ARGS ? [process.env.EHP_HOVER_ARGS] : [],{nl}  }})",
    )
    if "from './" in app or "from './" in spec:
        raise SystemExit("REFUSED: a relative import is left")
    (out / "electron-app.copy.ts").write_bytes(app.encode("utf-8"))
    (out / "settings.copy.test.ts").write_bytes(spec.encode("utf-8"))
    (out / "package.json").write_bytes(b'{ "type": "module", "private": true }\n')
    config = (
        "import { defineConfig } from '@playwright/test'\n"
        "export default defineConfig({\n"
        f"  testDir: '{out.as_posix()}',\n"
        "  testMatch: ['settings.copy.test.ts'],\n"
        f"  globalSetup: '{E2E}/global-setup.ts',\n"
        f"  globalTeardown: '{E2E}/global-teardown.ts',\n"
        "  timeout: 60_000,\n  fullyParallel: false,\n  workers: 1,\n"
        "  reporter: [['list'], ['json', { outputFile: process.env.EHP_HOVER_JSON }]],\n"
        "  use: { trace: 'off' },\n})\n"
    )
    (out / "playwright.copy.config.ts").write_bytes(config.encode("utf-8"))


def run(out: Path, mode: str) -> tuple[dict, str]:
    env = {k: v for k, v in os.environ.items() if k != "ELECTRON_RUN_AS_NODE"}
    env.pop("EHP_HOVER_ARGS", None)
    if mode == "none":
        env["EHP_HOVER_ARGS"] = HOVER_NONE
    report = out / f"hover-{mode}.json"
    env["EHP_HOVER_JSON"] = str(report)
    cli = ROOT / "ui/node_modules/@playwright/test/cli.js"
    config = out / "playwright.copy.config.ts"
    r = subprocess.run(
        ["node", str(cli), "test", "--config", str(config), "-g", r"AC-126\.8 "],
        cwd=ROOT / "ui",
        env=env,
        capture_output=True,
        check=False,
    )
    text = (r.stdout + r.stderr).decode("utf-8", "replace")
    (out / f"hover-{mode}.txt").write_text(text, encoding="utf-8")
    stats = json.loads(report.read_text(encoding="utf-8"))["stats"] if report.is_file() else {}
    return stats, text


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    out = Path(argv[0]).resolve()
    if out.exists():
        print(f"REFUSED: {out} exists")
        return 2
    out.mkdir(parents=True)
    copies(out)
    link = out / "node_modules"
    subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(ROOT / "ui/node_modules")],
        check=True,
        capture_output=True,
    )
    try:
        native, _ = run(out, "native")
        none, text = run(out, "none")
    finally:
        os.rmdir(link)
    received = re.findall(r'Received: "([^"]+)"', text)
    at_hover = "toHaveCSS('background-color', 'rgb(22, 78, 99)')" in text
    ok_native = native.get("expected") == 1 and native.get("unexpected") == 0
    ok_none = none.get("unexpected") == 1 and received == [REST] and at_hover
    print("native:", native.get("expected"), "expected,", native.get("unexpected"), "unexpected")
    print(
        "hover-none:",
        none.get("expected"),
        "expected,",
        none.get("unexpected"),
        "unexpected; received",
        received,
    )
    print("junction removed:", not link.exists())
    print(f"hover-none fails at the hover expectation with {REST}:", ok_native and ok_none)
    return 0 if ok_native and ok_none and not link.exists() else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
