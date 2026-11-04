#!/usr/bin/env bash
# Exact validation procedures for 2026-10-10-gui-polish-residuals (Session 31). Helpers are copied verbatim from
# Session 29's validate-task.sh (plan folder 2026-10-01-capture-viewport-chrome), with the receipt prefix s31.
# Kept in one script so task.md cells stay lintable (tools/lint_task_contract.py).
# Runs from the repo root. Every procedure writes its raw tool output under $RECEIPTS_DIR and
# exits nonzero on the first failed check. It is executable only during the authorized
# execution session, because it runs product tests and builds.
# Stage ids match validate-task.ps1 exactly; windows-gate-check asserts that order.
set -uo pipefail

PLAN=docs/execution/plans/2026-10-10-gui-polish-residuals
RD="${RECEIPTS_DIR:-/tmp/av-kit}"
mkdir -p "$RD"
CHECK="${1:-}"

fail() { echo "FAIL: $*"; exit 1; }

# require_failed_title <json> <title-token> <expect-needle>: the named spec itself must have failed
# on an expect() whose message contains <expect-needle> (Session 27 Review R1 F1: a sibling spec's failure
# cannot stand in for it).
require_failed_title() {
  python3 - "$1" "$2" "$3" <<'PY' || exit 1
import json, sys
path, title, needle = sys.argv[1], sys.argv[2], sys.argv[3]
j = json.load(open(path, encoding="utf-8"))
def specs(suite):
    yield from suite.get("specs", [])
    for child in suite.get("suites", []):
        yield from specs(child)
hits = []
for suite in j.get("suites", []):
    for spec in specs(suite):
        if title not in spec.get("title", ""):
            continue
        for test in spec.get("tests", []):
            for res in test.get("results", []):
                msgs = [e.get("message", "") for e in res.get("errors", [])] + [(res.get("error") or {}).get("message", "")]
                if res.get("status") == "failed" and any(needle in m for m in msgs):
                    hits.append(spec["title"])
if not hits:
    sys.exit(f"FAIL: no spec titled {title} failed on an expect containing {needle!r} (see the plan's Stop conditions S3/S4)")
print(f"PASS {title} RED on {needle}: {hits}")
PY
}

run() { # run <receipt-id> <cmd...>: exact receipt, propagate exit
  local id="$1"; shift
  "$@" > "$RD/$id.txt" 2>&1
  local rc=$?
  tail -n 25 "$RD/$id.txt"
  [ "$rc" -eq 0 ] || fail "$id exit $rc (receipt $RD/$id.txt)"
  echo "PASS $id"
}

# sandbox_env: Chromium refuses to run as root with its sandbox on (the container runs as root).
sandbox_env() { if [ "$(id -u)" = "0" ]; then export ELECTRON_DISABLE_SANDBOX=1; fi; }

# electron: Playwright against real Electron; headless display when none exists.
electron() {
  unset ELECTRON_RUN_AS_NODE AVKIT_E2E_OUT_DIR
  sandbox_env
  if [ -z "${DISPLAY:-}" ]; then xvfb-run -a npm --prefix ui run test:e2e -- "$@"
  else npm --prefix ui run test:e2e -- "$@"; fi
}

harness_build() { AVKIT_PRIMITIVE_HARNESS_BUILD=1 npm --prefix ui run build -- --outDir "$(pwd)/ui/out-e2e"; }

# ENV_BOUND_TESTS (implementation-plan.md §Environment-bound census). WINDOWS_GATE tolerates none.
vitest_env_ok() { # vitest_env_ok <receipt-id> [vitest args...]
  local id="$1"; shift
  local json="$RD/$id.json"
  rm -f "$json"
  npm --prefix ui run test -- "$@" --reporter=json --outputFile="$json" > "$RD/$id.txt" 2>&1
  local rc=$?
  [ -f "$json" ] || fail "$id: Vitest JSON missing (exit $rc)"
  python3 - "$id" "$json" "$rc" <<'PY' || exit 1
import hashlib, json, os, re, subprocess, sys
rid, path, rc = sys.argv[1], sys.argv[2], int(sys.argv[3])
j = json.load(open(path, encoding="utf-8"))
suites = j.get("testResults", [])
load = [s["name"] for s in suites if s.get("message")]
if load:
    sys.exit(f"FAIL: {rid} suite load errors {load}")
if j.get("numPendingTests", 0) or j.get("numTodoTests", 0):
    sys.exit(f"FAIL: {rid} pending/todo present")
def crlf_proof():
    t = open("ui/tests/e2e/test-ids.ts", "rb").read()
    if b"\r" in t:
        return False
    head, _, tail = t.partition(b"// MEU-51 primitive harness IDs.")
    h = hashlib.sha256(head.replace(b"\n", b"\r\n")).hexdigest().upper()
    if h != "819760B9840EE4BF38633B3628DC2E7820D4B87E05A0EC720B75B61C89D28A73":
        return False
    prior = re.findall(r"^export const \w+ = '([^']+)'", head.decode(), re.M)
    new = re.findall(r"^export const \w+ = '([^']+)'", tail.decode(), re.M)
    return len(set(new)) == len(new) and not any(v in prior for v in new)
env_bound = {
    "MEU-51 shared layout primitives AC-51.6 adds unique primitive IDs while preserving the exact prior registry prefix":
        lambda msgs: crlf_proof() and any("819760B9840EE4BF" in m for m in msgs),
    "Phase 10 queue-card canon (MEU-41) AC-41.3 both themes declare the ported status tokens with Zorivest hexes":
        lambda msgs: (not os.path.exists("P:/zorivest") and any("P:/zorivest" in m for m in msgs)
                      and subprocess.run(["git", "diff", "--quiet", "f7d3134", "--",
                                          "ui/src/renderer/src/styles.css"]).returncode == 0),
}
failed = [a for s in suites for a in s.get("assertionResults", []) if a.get("status") == "failed"]
real = [a["fullName"] for a in failed
        if not (a["fullName"] in env_bound and env_bound[a["fullName"]](a.get("failureMessages", [])))]
if real:
    sys.exit(f"FAIL: {rid} real failures: {real}")
if rc != 0 and not failed:
    sys.exit(f"FAIL: {rid} exit {rc} with no failed assertion (runner error)")
print(f"PASS {rid}: {j.get('numPassedTests')} passed of {j.get('numTotalTests')}, env-bound tolerated: {[a['fullName'][:40] for a in failed]}")
PY
}

# electron_env_ok <receipt-id> [args...]: tolerates only the capture-picker stub-missing failures
# off Windows (ENV_BOUND_E2E).
electron_env_ok() {
  local id="$1"; shift
  local json="$RD/$id.json"
  rm -f "$json"
  electron "$@" --reporter=json --outputFile="$json" > "$RD/$id.txt" 2>&1
  local rc=$?
  [ -f "$json" ] || fail "$id: Playwright JSON missing (exit $rc)"
  python3 - "$id" "$json" "$rc" <<'PY' || exit 1
import json, os, sys
rid, path, rc = sys.argv[1], sys.argv[2], int(sys.argv[3])
j = json.load(open(path, encoding="utf-8"))
if j.get("errors"):
    sys.exit(f"FAIL: {rid} top-level Playwright errors {j['errors'][:1]}")
stub = "native/region-picker-stub/publish/avkit-region-picker-stub.exe"
def specs(suite):
    yield from ((suite.get("file", ""), s) for s in suite.get("specs", []))
    for child in suite.get("suites", []):
        yield from specs(child)
real, tolerated, passed, flaky = [], [], 0, 0
for top in j.get("suites", []):
    for file, spec in specs(top):
        for test in spec.get("tests", []):
            results = test.get("results", [])
            status = results[-1].get("status") if results else "missing"
            if test.get("status") == "flaky":
                flaky += 1
            if status in ("passed", "skipped") and test.get("status") not in ("unexpected", "flaky"):
                passed += status == "passed"
                continue
            msgs = " ".join(e.get("message", "") for r in results for e in r.get("errors", []))
            stub_error = ("the deterministic sidecar stub is missing" in msgs
                          or ("ENOENT" in msgs and "avkit-region-picker-stub.exe" in msgs))
            env = (file.endswith("capture-picker.test.ts") and os.name != "nt"
                   and not os.path.exists(stub) and stub_error)
            (tolerated if env else real).append(f"{file}: {spec.get('title')}")
if real:
    sys.exit(f"FAIL: {rid} real Electron failures (flaky counts as real): {real}")
if rc != 0 and not tolerated:
    sys.exit(f"FAIL: {rid} exit {rc} with no failed spec (runner error)")
print(f"PASS {rid}: {passed} passed, env-bound tolerated: {tolerated}")
PY
}

# electron_repeat <id> <spec files...>: cloud-local §3.1 item 2, into a separate output dir.
electron_repeat() {
  local id="$1"; shift
  electron "$@" --repeat-each=20 --output="$RD/s31-repeat-$id" --reporter=json --outputFile="$RD/s31-repeat-$id.json" > "$RD/s31-repeat-$id.txt" 2>&1
  local rc=$?
  [ "$rc" -eq 0 ] || fail "repeat $id exit $rc (receipt $RD/s31-repeat-$id.txt)"
  echo "PASS repeat-each=20 $id"
}

# pytest_env_ok <receipt-id>: full Python suite; the failed set must be a subset of the
# baseline failed set captured by `baseline` before any product edit (ENV_BOUND_PY).
pytest_env_ok() {
  local id="$1"
  [ -f "$RD/s31-baseline-pytest.txt" ] || fail "baseline pytest receipt missing: run 'baseline' first"
  uv run pytest tests/ -q --tb=no -p no:cacheprovider -rfE > "$RD/$id.txt" 2>&1
  python3 - "$RD/s31-baseline-pytest.txt" "$RD/$id.txt" <<'PY' || exit 1
import re, sys
def failed(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    if not re.search(r"\d+ (passed|failed)", text):
        sys.exit(f"FAIL: {path} has no pytest summary (collection/runner error)")
    return {l.split(" - ")[0] for l in text.splitlines() if l.startswith(("FAILED ", "ERROR "))}, text
base, _ = failed(sys.argv[1])
head, text = failed(sys.argv[2])
new = sorted(head - base)
if new:
    sys.exit(f"FAIL: new pytest failures versus baseline.sha: {new}")
m = re.search(r"(\d+) passed", text)
print(f"PASS pytest: no new failures (baseline env-bound {len(base)}, head {len(head)}, passed {m.group(1) if m else '?'})")
PY
}

# pytest_paths_ok <receipt-id> <paths...>: targeted pytest under the same ENV_BOUND_PY rule as
# pytest_env_ok (failed set must be a subset of the baseline failed set; container only).
pytest_paths_ok() {
  local id="$1"; shift
  [ -f "$RD/s31-baseline-pytest.txt" ] || fail "baseline pytest receipt missing: run 'baseline' first"
  uv run pytest "$@" -q --tb=short -p no:cacheprovider -rfE > "$RD/$id.txt" 2>&1
  python3 - "$RD/s31-baseline-pytest.txt" "$RD/$id.txt" "$id" <<'PY' || exit 1
import re, sys
def failed(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    if not re.search(r"\d+ (passed|failed)", text):
        sys.exit(f"FAIL: {path} has no pytest summary (collection/runner error)")
    return {l.split(" - ")[0] for l in text.splitlines() if l.startswith(("FAILED ", "ERROR "))}, text
base, _ = failed(sys.argv[1])
head, text = failed(sys.argv[2])
new = sorted(head - base)
if new:
    sys.exit(f"FAIL: {sys.argv[3]} new pytest failures versus baseline.sha: {new}")
m = re.search(r"(\d+) passed", text)
print(f"PASS {sys.argv[3]}: {m.group(1) if m else '?'} passed; env-bound baseline failures tolerated: {sorted(head)}")
PY
}

# vitest_red <ac-tag> <json> <new-file|-> <files...>: assertion-level Red; a declared new file may
# fail only with a missing-module message.
vitest_red() {
  local tag="$1" json="$2" newf="$3"; shift 3
  rm -f "$json"
  npm --prefix ui run test -- "$@" --reporter=json --outputFile="$json" > "$RD/$(basename "$json" .json).txt" 2>&1
  local rc=$?
  [ "$rc" -ne 0 ] || fail "$tag Red expected a failing run, got exit 0"
  [ -f "$json" ] || fail "$tag Red JSON report missing"
  python3 - "$tag" "$json" "$newf" <<'PY' || exit 1
import json, sys
tag, path, newf = sys.argv[1], sys.argv[2], sys.argv[3]
j = json.load(open(path, encoding="utf-8"))
suites = j.get("testResults", [])
for s in suites:
    if s.get("message"):
        allowed = newf != "-" and s["name"].endswith(newf.split("/")[-1]) and (
            "Failed to resolve import" in s["message"] or "Cannot find module" in s["message"])
        if not allowed:
            sys.exit(f"FAIL: {tag} suite load/collection error in {s['name']}: {s['message'][:200]}")
if j.get("numPendingTests", 0) or j.get("numTodoTests", 0):
    sys.exit(f"FAIL: {tag} pending/todo tests present")
failed = [a for s in suites for a in s.get("assertionResults", []) if a.get("status") == "failed"]
decisive = [a for a in failed if tag in a.get("fullName", "") and any(
    "expected" in m.lower() or "assert" in m.lower() for m in a.get("failureMessages", []))]
other = [a["fullName"][:60] for a in failed if a not in decisive]
if not decisive:
    sys.exit(f"FAIL: {tag} no failed {tag} assertion (only setup/import errors?)")
print(f"PASS {tag} RED: {len(decisive)} failing {tag} assertions, {j.get('numPassedTests')} passing; "
      f"other failing (must be TA-amended, dispositioned in walkthrough): {other}")
PY
}

# electron_red <ac-tag> <json> <files...>: fresh build, then at least one AC expect() failure.
electron_red() {
  local tag="$1" json="$2"; shift 2
  rm -f "$json"
  npm --prefix ui run build > "$RD/$(basename "$json" .json)-build.txt" 2>&1 || fail "$tag Red build failed"
  electron "$@" -g "$tag" --reporter=json --outputFile="$json" > "$RD/$(basename "$json" .json).txt" 2>&1
  local rc=$?
  [ "$rc" -ne 0 ] || fail "$tag E2E Red expected a failing run, got exit 0"
  [ -f "$json" ] || fail "$tag E2E Red JSON missing"
  python3 - "$tag" "$json" <<'PY' || exit 1
import json, sys
tag, path = sys.argv[1], sys.argv[2]
j = json.load(open(path, encoding="utf-8"))
if j.get("errors"):
    sys.exit(f"FAIL: {tag} E2E top-level errors (collection/launch): {j['errors'][:1]}")
def specs(suite):
    yield from suite.get("specs", [])
    for child in suite.get("suites", []):
        yield from specs(child)
decisive = []
for suite in j.get("suites", []):
    for spec in specs(suite):
        if tag not in spec.get("title", ""):
            continue
        for test in spec.get("tests", []):
            for res in test.get("results", []):
                msgs = [e.get("message", "") for e in res.get("errors", [])] + [(res.get("error") or {}).get("message", "")]
                if res.get("status") == "failed" and any("expect(" in m or "Expected" in m for m in msgs):
                    decisive.append(spec["title"])
if not decisive:
    sys.exit(f"FAIL: {tag} E2E has no failed {tag} spec with an expect() assertion error")
print(f"PASS {tag} E2E RED: {len(decisive)} failing {tag} specs")
PY
}

# Test sets. REG*: suites that pin sources or contracts on the files each MEU modifies.
UNIT69=(tests/unit/header-toggles.test.ts)
UNIT70=(tests/unit/settings-tail-spacer.test.ts tests/unit/settings-rail.test.tsx)
# UNIT70E: EMPHASIS_TESTS (implementation-plan.md §Single-statement contracts). Red at row 5, first required
# green at row 7 (green70); never part of REGSET, UNIT70 or green70-rail (Review R1 F1; plan_checks.py item 9).
UNIT70E=(tests/unit/settings-emphasis.test.tsx)
# REGHDR: suites that read Header.tsx / AppShell.tsx or click the header controls (census rows).
REGHDR=(tests/unit/chrome-zorivest.test.ts tests/unit/app-shell-wiring.test.ts tests/unit/console-polish.test.ts
        tests/unit/capture-page.test.ts tests/unit/convert-page.test.ts tests/unit/persist-ui.test.ts)
# REGSET: the Settings suites plus the doc/registry suites that read SettingsPage.tsx or test-ids.ts.
REGSET=(tests/unit/settings-page.test.ts tests/unit/settings-rail.test.tsx tests/unit/help-card.test.ts
        tests/unit/layout-primitives.test.ts tests/unit/layout-canon.test.ts tests/unit/gui-actions-audit.test.ts
        tests/unit/e2e-wiring.test.ts)
E2EHDR=(tests/e2e/console-chrome.test.ts tests/e2e/command-palette-nav.spec.ts)
E2ESET=(tests/e2e/settings.test.ts)
REPEAT_GREP="AC-69|AC-70|AC-58.12|A-6|C1-"
AUDIT_SRC=(ui/src/renderer/src/components/layout/Header.tsx ui/src/renderer/src/components/layout/AppShell.tsx
           ui/src/renderer/src/features/settings/SettingsRail.tsx ui/src/renderer/src/features/settings/SettingsPage.tsx
           ui/src/renderer/src/features/settings/settings-tail-spacer.ts ui/src/renderer/src/features/settings/settings-section-frame.ts
           ui/src/renderer/src/features/settings/StartAtSignInControl.tsx)
PREFIX_AUDIT='TODO|FIXME|transition-all|bg-\[#|console\.log\(|@ts-ignore|@ts-expect-error|: any\b'
PLAN_REVIEW=.agent/context/handoffs/2026-10-10-gui-polish-residuals-plan-critical-review.md

case "$CHECK" in
  prereq)
    [ ! -e graphify-out ] && [ ! -e graphify-out-research ] || fail "graph present: re-run the context-tool gate with the human (S1)"
    uv run python - <<'PY' || fail "MEU state (S1)"
import sys, yaml
rows = {r["id"]: r.get("status") for r in yaml.safe_load(open(".agent/context/meu-status.yaml", encoding="utf-8"))["meus"]}
want = {"MEU-19": "approved", "MEU-26": "approved", "MEU-58": "approved", "MEU-69": "pending", "MEU-70": "pending"}
bad = {k: rows.get(k) for k, v in want.items() if rows.get(k) != v}
if bad:
    sys.exit(f"REFUSED: {bad}")
print("PASS MEU state", want)
PY
    bash "$0" review-check "$PLAN_REVIEW" plan 3 || fail "plan review not approved by the authorized route (S1)"
    grep -q "^Source: \`USER_EXPLICIT\`" "$PLAN/human-gate-decision.md" || fail "gate decision record missing"
    ! grep -q "^Pending\. Record the user's exact execution message" "$PLAN/human-gate-decision.md" || fail "execution message not recorded (plan_to_exec_gate: human)"
    [ -z "$(git status --porcelain -- ui packages mcp-server tests)" ] || fail "product or test tree already edited before row 0 (TA-1/TA-2 must follow the recorded authorization)"
    [ -d .venv ] || fail ".venv missing: run 'uv sync' first"
    [ -d ui/node_modules ] || fail "ui/node_modules missing: run 'npm --prefix ui ci' first"
    [ -d mcp-server/node_modules ] || fail "mcp-server/node_modules missing: run 'npm --prefix mcp-server ci'"
    [ -x ui/node_modules/electron/dist/electron ] || fail "Electron binary missing: run electron-setup"
    node -e "const l=require('./ui/node_modules/lucide-react');for(const n of ['SquareTerminal','Command'])if(!l[n]){console.error('missing icon '+n);process.exit(1)}" \
      || fail "a HEADER_ICONS icon is missing from the installed lucide-react"
    unset ELECTRON_RUN_AS_NODE; sandbox_env
    xvfb-run -a ui/node_modules/electron/dist/electron --version || fail "Electron cannot start under xvfb"
    echo "PASS prereq"
    ;;
  electron-setup)
    [ -d ui/node_modules/electron ] || fail "run 'npm --prefix ui ci' first"
    # Session 29 A-2: the package's own installer, run once and serially before any test. It is
    # checksum-pinned to the package's checksums.json and exits 0 when the binary is already installed.
    node ui/node_modules/electron/install.js || fail "electron install.js failed"
    [ -x ui/node_modules/electron/dist/electron ] && [ -f ui/node_modules/electron/path.txt ] \
      || fail "install.js exited 0 but the binary or path.txt is missing"
    echo "Electron installed: $(cat ui/node_modules/electron/dist/version)"
    unset ELECTRON_RUN_AS_NODE; sandbox_env
    xvfb-run -a ui/node_modules/electron/dist/electron --version || fail "Electron cannot start under xvfb"
    echo "PASS electron-setup"
    ;;
  baseline)
    # Pre-edit baseline: must run before any product edit. It records HEAD and the env-bound sets.
    [ -z "$(git status --porcelain -- ui packages mcp-server tests)" ] || fail "product tree already edited; baseline must precede row 2"
    git rev-parse HEAD > "$PLAN/baseline.sha"
    uv run pytest tests/ -q --tb=no -p no:cacheprovider -rfE > "$RD/s31-baseline-pytest.txt" 2>&1
    grep -qE "[0-9]+ (passed|failed)" "$RD/s31-baseline-pytest.txt" || fail "baseline pytest produced no summary"
    grep -E "^[0-9]+ (passed|failed)|passed|failed" "$RD/s31-baseline-pytest.txt" | tail -n 1
    vitest_env_ok s31-baseline-vitest
    run s31-baseline-build npm --prefix ui run build
    run s31-baseline-harness-build harness_build
    electron_env_ok s31-baseline-e2e
    echo "PASS baseline at $(cat "$PLAN/baseline.sha")"
    ;;
  census)
    # Every test that pins something this plan touches. TEST_AMENDMENTS holds TA-1/TA-2 only: every
    # other hit must be 'unaffected'.
    rg -n -e header-console-btn -e header-palette-btn -e HEADER_CONSOLE -e HEADER_PALETTE -e 'Settings:' -e 'Ctrl\+K' \
      -e 'Open command palette' -e 'Header.tsx' -e headerPath -e 'onConsoleToggle' -e 'onPaletteToggle' -e previousElementSibling \
      -e settings-rail -e SettingsRail -e revealSection -e data-settings-section -e aria-current -e data-current \
      -e scroll-mt -e settings-page -e 'SettingsPage.tsx' -e settingsPagePath -e 'max-w-\[60rem\]' -e 'grid-cols-\[11rem' \
      -e mcp-access-card -e readiness-card -e 'scrollTo' -e IntersectionObserver -e ResizeObserver -e setSize \
      -e start-at-sign-in-panel -e StartAtSignInControl -e loginItemGet -e settings-mode-startup \
      -e 'test-ids.ts' -e 'MEU-51 primitive harness IDs' \
      ui/tests > "$RD/s31-census.txt" 2>&1
    rc=$?; [ "$rc" -le 1 ] || fail "census rg exit $rc"
    wc -l < "$RD/s31-census.txt"; echo "PASS census written: $RD/s31-census.txt (disposition every hit in walkthrough.md §Census)"
    ;;
  red69)
    vitest_red AC-69 "$RD/s31-69-red-vitest.json" - "${UNIT69[@]}" || exit 1
    electron_red AC-69 "$RD/s31-69-red-e2e.json" "${E2EHDR[@]}" || exit 1
    require_failed_title "$RD/s31-69-red-e2e.json" AC-69.5 toHaveAttribute || exit 1
    ;;
  green69)
    vitest_env_ok s31-69-green "${UNIT69[@]}" "${REGHDR[@]}"
    ;;
  gate69)
    run s31-69-typecheck npm --prefix ui run typecheck
    run s31-69-lint npm --prefix ui run lint
    bash "$0" ta-check || exit 1
    vitest_env_ok s31-69-vitest "${UNIT69[@]}" "${REGHDR[@]}" "${REGSET[@]}"
    run s31-69-build npm --prefix ui run build
    run s31-69-harness-build harness_build
    electron_env_ok s31-69-e2e "${E2EHDR[@]}"
    electron_repeat 69-header "${E2EHDR[@]}" -g "$REPEAT_GREP"
    ;;
  red70)
    vitest_red AC-70 "$RD/s31-70-red-vitest.json" tests/unit/settings-tail-spacer.test.ts "${UNIT70[@]}" "${UNIT70E[@]}" || exit 1
    electron_red AC-70 "$RD/s31-70-red-e2e.json" "${E2ESET[@]}" || exit 1
    require_failed_title "$RD/s31-70-red-e2e.json" AC-70.2 toHaveAttribute || exit 1
    ;;
  green70-rail)
    # RAIL_STAGE_TESTS only: no EMPHASIS_TESTS member runs before row 7 (D-21).
    vitest_env_ok s31-70-green-rail tests/unit/settings-tail-spacer.test.ts "${REGSET[@]}"
    run s31-70-green-rail-build npm --prefix ui run build
    electron_env_ok s31-70-green-rail-e2e "${E2ESET[@]}" -g "AC-70.2|AC-58.12|A-6"
    ;;
  green70)
    vitest_env_ok s31-70-green "${UNIT69[@]}" "${UNIT70[@]}" "${UNIT70E[@]}" "${REGSET[@]}"
    run s31-70-green-build npm --prefix ui run build
    electron_env_ok s31-70-green-e2e "${E2ESET[@]}" -g "AC-70"
    ;;
  gate70)
    run s31-70-typecheck npm --prefix ui run typecheck
    run s31-70-lint npm --prefix ui run lint
    vitest_env_ok s31-70-vitest "${UNIT69[@]}" "${UNIT70[@]}" "${UNIT70E[@]}" "${REGHDR[@]}" "${REGSET[@]}"
    run s31-70-build npm --prefix ui run build
    run s31-70-harness-build harness_build
    electron_env_ok s31-70-e2e "${E2ESET[@]}"
    electron_env_ok s31-70-e2e-header "${E2EHDR[@]}"
    electron_repeat 70-settings "${E2ESET[@]}" -g "$REPEAT_GREP"
    ;;
  ta-check)
    # AC-69.6: TEST_AMENDMENTS TA-1/TA-2 are the only changes to these two files since baseline.sha.
    [ -f "$PLAN/baseline.sha" ] || fail "baseline.sha missing: run row 0 first"
    python3 - "$(cat "$PLAN/baseline.sha")" <<'PY' || exit 1
import subprocess, sys
base = sys.argv[1]
allowed = {
    "ui/tests/unit/chrome-zorivest.test.ts": {
        ("it('AC-26.4 header breadcrumb and Settings: Ctrl+K palette trigger', async () => {",
         "it('AC-26.4 header breadcrumb and Commands Ctrl+K palette trigger', async () => {"),
        ("expect(palette?.textContent).toMatch(/Settings:/)", "expect(palette?.textContent).toMatch(/Commands/)"),
    },
    "ui/tests/unit/app-shell-wiring.test.ts": {
        ("expect(palette.textContent).toMatch(/Settings:/)", "expect(palette.textContent).toMatch(/Commands/)"),
    },
}
for path, pairs in allowed.items():
    diff = subprocess.run(["git", "diff", "-U0", base, "--", path], capture_output=True, text=True, check=True).stdout
    removed = sorted(l[1:].strip() for l in diff.splitlines() if l.startswith("-") and not l.startswith("---"))
    added = sorted(l[1:].strip() for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++"))
    if removed != sorted(o for o, _ in pairs) or added != sorted(n for _, n in pairs):
        sys.exit(f"FAIL: {path} changes are not exactly TA-1/TA-2:\n removed={removed}\n added={added}")
print("PASS ta-check: TA-1 and TA-2 applied exactly, nothing else changed in those files")
PY
    ;;
  hub)
    python3 - "$(cat "$PLAN/baseline.sha")" <<'PY' || exit 1
import subprocess, sys
base = sys.argv[1]
b06 = open("docs/build-plan/06-gui.md", encoding="utf-8").read()
console = b06.split("A shared log viewer as a right side sheet.", 1)[1].split("\n\n", 1)[0]
if "Commands Ctrl+K" not in console or "Settings: Ctrl+K" in console:
    sys.exit("FAIL: 06 §ConsolePanel still names the old palette label")
hdr = b06.split("### Header toggles (residual)", 1)[1].split("\n## ", 1)[0]
for need in ("Session 31 plan D-11", "Session 31 plan D-12"):
    if need not in hdr:
        sys.exit(f"FAIL: 06 §Header toggles lacks {need!r}")
b11 = open("docs/build-plan/11-page-layout.md", encoding="utf-8").read()
emp = b11.split("### Settings section emphasis (residual)", 1)[1].split("\n## ", 1)[0]
if "All nine section ids" in emp or "SETTINGS_SECTION_SET" not in emp:
    sys.exit("FAIL: 11 §Settings section emphasis Test IDs row still says nine (D-18)")
for need in ("Human-approved 2026-10-10", "Session 31 plan D-9", "D-17", "Session 31 plan D-14"):
    if need not in emp:
        sys.exit(f"FAIL: 11 §Settings section emphasis lacks {need!r}")
if subprocess.run(["git", "diff", "--quiet", base, "--", "docs/build-plan/gui-actions-index.md"]).returncode != 0:
    sys.exit("FAIL: gui-actions-index.md changed; the plan says no change")
print("PASS hub reconciliation")
PY
    run s31-hub-render-check uv run python tools/meu_status.py render --check
    # The ST rows stay untouched (AC-50.1/50.4 lock); prove the doc-reading suites still pass.
    vitest_env_ok s31-hub-doc-tests tests/unit/layout-canon.test.ts tests/unit/queue-canon.test.ts tests/unit/gui-actions-audit.test.ts tests/unit/capture-page.test.ts
    ;;
  task-state)
    python3 - "$PLAN/task.md" <<'PY' || exit 1
import re, sys
rows = [l for l in open(sys.argv[1], encoding="utf-8") if re.match(r"^\| [0-9]+ \|", l)]
if len(rows) != 10:
    sys.exit(f"FAIL: expected 10 implementation rows (0-9), got {len(rows)}")
for l in rows:
    s = l.rstrip().rstrip("|").split("|")[-1].strip().strip("`")
    if s == "[x]" or (s == "[B]" and "follow-up" in l and "B-" in l):
        continue
    sys.exit(f"FAIL: unfinished row: {l[:60]}")
print("PASS implementation rows 0-9")
PY
    ;;
  pregate)
    echo "== input identity"; git rev-parse HEAD; git status --porcelain | sha256sum
    sha256sum ui/package-lock.json mcp-server/package-lock.json uv.lock; node --version; npm --prefix ui ls electron --depth=0 || true
    run s31-gate-py-types uv run pyright packages/
    run s31-gate-py-lint uv run ruff check packages/ tests/
    run s31-gate-ui-types npm --prefix ui run typecheck
    run s31-gate-ui-lint npm --prefix ui run lint
    run s31-gate-mcp-types npm --prefix mcp-server run typecheck
    run s31-gate-plan-static python3 "$PLAN/plan_checks.py" static
    run s31-gate-task-contract uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task "$PLAN/task.md"
    pytest_env_ok s31-gate-py-tests
    vitest_env_ok s31-gate-ui-tests
    run s31-gate-ui-build npm --prefix ui run build
    run s31-gate-ui-harness-build harness_build
    run s31-gate-mcp-build npm --prefix mcp-server run build
    run s31-gate-mcp-tests npm --prefix mcp-server run test
    run s31-gate-openapi uv run python tools/export_openapi.py --check openapi.committed.json
    run s31-gate-state-render uv run python tools/meu_status.py render --check
    electron_env_ok s31-gate-ui-electron
    for f in "${AUDIT_SRC[@]}"; do [ -f "$f" ] || fail "audited source missing: $f"; done
    if grep -nE "$PREFIX_AUDIT" "${AUDIT_SRC[@]}"; then fail "source audit hits"; fi
    echo "PASS container pre-gate (authoritative: windows-gate + CHROME_LOOK)"
    ;;
  ssot-review)
    for n in 69 70; do
      run "s31-meu-$n-rfr" uv run python tools/meu_status.py update "MEU-$n" ready_for_review --plan "$PLAN"
    done
    run s31-render uv run python tools/meu_status.py render
    run s31-render-check uv run python tools/meu_status.py render --check
    grep -qE '^\| 31 \| `gui-polish-residuals` \| MEU-69, MEU-70 \| P4 \| in review \| `docs/execution/plans/2026-10-10-gui-polish-residuals/`' \
      .agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md || fail "grouping Session 31 not in review"
    grep -q 'gui-polish-residuals' .agent/context/current-focus.md && grep -q 'ready_for_review' .agent/context/current-focus.md \
      || fail "focus does not record Session 31 ready_for_review"
    echo "PASS SSOT review state"
    ;;
  api-scope)
    # PRODUCT_SCOPE (implementation-plan.md §Single-statement contracts).
    run s31-api-openapi uv run python tools/export_openapi.py --check openapi.committed.json
    python3 - "$(cat "$PLAN/baseline.sha")" "$PLAN/implementation-plan.md" <<'PY' || exit 1
import re, subprocess, sys
base, plan = sys.argv[1], open(sys.argv[2], encoding="utf-8").read()
def changed(*paths):
    out = set(subprocess.run(["git", "diff", "--name-only", base, "HEAD", "--", *paths],
                             capture_output=True, text=True, check=True).stdout.split())
    out |= {l[3:] for l in subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "--", *paths],
                                          capture_output=True, text=True, check=True).stdout.splitlines()}
    return out
frozen = sorted(changed("packages", "mcp-server", "openapi.committed.json", "tools", "ui/src/main"))
if frozen:
    sys.exit(f"FAIL: PRODUCT_SCOPE frozen paths changed: {frozen}")
listed = set(re.findall(r"^\| `(ui/[^`]+)` \|", plan, re.M))
extra = sorted(changed("ui") - listed)
if extra:
    sys.exit(f"FAIL: ui changes outside the plan's Files Modified tables: {extra}")
print(f"PASS product scope: ui changes {sorted(changed('ui'))}")
PY
    bash "$0" ta-check || exit 1
    ;;
  handoff-ac)
    for n in 69 70; do
      run "s31-handoff-ac-$n" uv run python tools/validate_closeout_artifacts.py --plan "$PLAN/implementation-plan.md" \
        --handoff ".agent/context/handoffs/2026-10-10-gui-polish-residuals-MEU-$n-handoff.md" --ac-coverage-only
    done
    ;;
  windows-gate-check)
    python3 - <<'PY' || exit 1
import json, subprocess, sys
plan = "docs/execution/plans/2026-10-10-gui-polish-residuals"
p = f"{plan}/windows-gate-result.json"
try:
    r = json.load(open(p, encoding="utf-8-sig"))
except OSError as err:
    sys.exit(f"FAIL: {p} unreadable: {err}")
if r.get("schema") != "s31-windows-gate.v1":
    sys.exit(f"FAIL: schema {r.get('schema')}")
if r.get("clean_tree") is not True:
    sys.exit("FAIL: Windows run was not on a clean tree")
pre = r.get("preflight") or {}
if not pre.get("agentic_framework_head") or not pre.get("agent_registry_sha256") or pre.get("drift") is not False:
    sys.exit(f"FAIL: preflight missing or drifted: {pre}")
order = ["npm-ci", "mcp-npm-ci", "py-types", "py-lint", "ui-types", "ui-lint", "mcp-types", "py-tests", "ui-tests",
         "ui-build", "ui-harness-build", "mcp-build", "mcp-tests", "openapi", "state-render", "ui-electron", "source-audit"]
got = [s.get("id") for s in r.get("stages", [])]
if got != order:
    sys.exit(f"FAIL: stages {got} != {order}")
bad = [s["id"] for s in r["stages"] if s.get("exit") != 0]
if bad:
    sys.exit(f"FAIL: Windows stages failed: {bad}")
# RULE-3 (reflection 2026-10-01): every result reports the ui-electron duration.
electron_stage = next(s for s in r["stages"] if s["id"] == "ui-electron")
if not isinstance(electron_stage.get("seconds"), (int, float)):
    sys.exit("FAIL: ui-electron stage has no recorded duration (seconds)")
v, e, py = r.get("vitest") or {}, r.get("e2e") or {}, r.get("pytest") or {}
# COUNT_FLOORS (implementation-plan.md §Single-statement contracts).
if v.get("failed") != 0 or (v.get("total") or 0) < 748:
    sys.exit(f"FAIL: vitest {v}")
if e.get("unexpected") != 0 or e.get("flaky") not in (0, None) or (e.get("expected") or 0) < 127:
    sys.exit(f"FAIL: e2e {e}")
if py.get("failed") != 0 or not py.get("passed"):
    sys.exit(f"FAIL: pytest {py}")
floor = r.get("pytest_floor")
if floor is not None and py["passed"] < floor:
    sys.exit(f"FAIL: pytest passed {py['passed']} below the first-counted-attempt floor {floor}")
tested = r.get("tested_commit", "")
# GATED_PATHS (implementation-plan.md §Single-statement contracts); plan_checks.py asserts equality.
gated = ["ui", "packages", "mcp-server", "tests", "tools", "pyproject.toml", "uv.lock", "openapi.committed.json",
         "docs/build-plan/06-gui.md", "docs/build-plan/10-queue-card-ui.md",
         "docs/build-plan/11-page-layout.md", "docs/build-plan/build-priority-matrix.md",
         "docs/build-plan/gui-actions-index.md", "docs/proposals",
         "docs/execution/plans/2026-08-28-p10-queue-card-foundations",
         "docs/execution/plans/2026-09-02-p10-queue-card-migration",
         "docs/execution/plans/2026-09-03-p10-queue-card-dnd",
         "docs/execution/plans/2026-09-26-p11-layout-canon/implementation-plan.md",
         ".agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md",
         ".agent/model-registry.local.json", ".agent/model-registry.local.yaml",
         f"{plan}/validate-task.ps1"]
code = subprocess.run(["git", "diff", "--quiet", tested, "HEAD", "--", *gated]).returncode
if code != 0:
    sys.exit(f"FAIL: GATED_PATHS changed since Windows-tested commit {tested} (git diff exit {code})")
dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "--", *gated],
                       capture_output=True, text=True).stdout.strip()
if dirty:
    sys.exit(f"FAIL: uncommitted GATED_PATHS changes after the Windows-tested commit:\n{dirty}")
print(f"PASS windows gate @ {tested}: vitest {v} e2e {e} pytest {py}; ui-electron {electron_stage['seconds']} s")
PY
    ;;
  look-check)
    # CHROME_LOOK K1-K5 (local-requests.md §GATE): recorded with a result and provenance, all pass,
    # and bound to the same commit as the Windows gate.
    python3 - "$PLAN/walkthrough.md" "$PLAN/windows-gate-result.json" <<'PY' || exit 1
import json, re, sys
try:
    t = open(sys.argv[1], encoding="utf-8").read()
    g = json.load(open(sys.argv[2], encoding="utf-8-sig"))
except OSError as err:
    sys.exit(f"FAIL: {err}")
sec = re.split(r"^## CHROME_LOOK[ \t]*$", t, maxsplit=1, flags=re.M)
if len(sec) < 2:
    sys.exit("FAIL: walkthrough.md has no ## CHROME_LOOK section")
body = sec[1].split("\n## ", 1)[0]
for item in ("K1", "K2", "K3", "K4", "K5"):
    # An unfilled template line (literal 'pass|fail') never counts as a result (Session 29 Review R2-1).
    if re.search(rf"^\|?\s*{item}\b.*pass\|fail", body, re.M):
        sys.exit(f"FAIL: {item} still carries the template token 'pass|fail'")
    # The result is the first word after the item id (Session 29 Review R1 F3).
    m = re.search(rf"^\|?\s*{item}\b[^a-z]*(pass|fail)\b", body, re.M)
    if not m:
        sys.exit(f"FAIL: {item} has no recorded pass/fail")
    if m.group(1) != "pass":
        sys.exit(f"FAIL: {item} recorded fail (Decision Brief per cloud-local §3.5)")
if "USER_EXPLICIT" not in body and "relayed" not in body:
    sys.exit("FAIL: CHROME_LOOK results carry no provenance (USER_EXPLICIT or relayed quote)")
sha = (g.get("tested_commit") or "")[:7]
if not sha or sha not in body:
    sys.exit(f"FAIL: CHROME_LOOK does not name the gate's tested commit {sha!r}")
print(f"PASS CHROME_LOOK K1-K5 on {sha}")
PY
    ;;
  review-check)
    python3 - "$2" "$3" "$4" <<'PY' || exit 1
import re, sys
path, mode, cap = sys.argv[1], sys.argv[2], int(sys.argv[3])
try:
    t = open(path, encoding="utf-8").read()
except OSError as err:
    sys.exit(f"FAIL: review file unreadable: {err}")
fm = dict(re.findall(r'^(\w+):\s*"?([^"\n]*)"?$', t.split("---")[1], re.M))
target = "docs/execution/plans/2026-10-10-gui-polish-residuals/implementation-plan.md"
if fm.get("target_plan") != target: sys.exit(f"FAIL: target {fm.get('target_plan')}")
if fm.get("review_mode") != mode: sys.exit(f"FAIL: mode {fm.get('review_mode')}")
if int(fm.get("round", "0")) > cap: sys.exit(f"FAIL: round {fm.get('round')} over cap {cap}")
if fm.get("verdict") != "approved": sys.exit(f"FAIL: verdict {fm.get('verdict')}")
# The authorized route (human-review-decision.md): Codex on gpt-6.1-sol, never the author's vendor.
agent = fm.get("agent", "").lower()
if "gpt-6.1-sol" not in agent or any(v in agent for v in ("claude", "fable", "opus", "sonnet")):
    sys.exit(f"FAIL: agent {fm.get('agent')} is not the authorized route")
print(f"PASS {mode} review approved round {fm['round']} by {fm['agent']}")
PY
    ;;
  post-review-state)
    for n in 69 70; do
      run "s31-meu-$n-approved" uv run python tools/meu_status.py update "MEU-$n" approved --plan "$PLAN"
    done
    run s31-approved-render uv run python tools/meu_status.py render
    run s31-approved-check uv run python tools/meu_status.py render --check
    uv run python - <<'PY' || exit 1
import sys, yaml
rows = {r["id"]: r.get("status") for r in yaml.safe_load(open(".agent/context/meu-status.yaml", encoding="utf-8"))["meus"]}
bad = {k: rows.get(k) for k in ("MEU-69", "MEU-70") if rows.get(k) != "approved"}
if bad: sys.exit(f"FAIL: MEU state {bad}")
issues = {i["id"]: i for i in yaml.safe_load(open(".agent/context/known-issues.yaml", encoding="utf-8"))["issues"]}
for i in ("HEADER-CONSOLE-SETTINGS-BUTTON-STATE", "SETTINGS-ACTIVE-SECTION-HIGHLIGHT"):
    it = issues.get(i) or {}
    ev = ((it.get("verification") or {}).get("evidence_file") or "")
    if it.get("status") != "resolved" or not ev.startswith("docs/execution/plans/2026-10-10-gui-polish-residuals/"):
        sys.exit(f"FAIL: {i} status {it.get('status')} evidence {ev!r}")
g = open(".agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md", encoding="utf-8").read()
if "| 31 | `gui-polish-residuals` | MEU-69, MEU-70 | P4 | approved |" not in g: sys.exit("FAIL: grouping Session 31 not approved")
if "2026-10-10-gui-polish-residuals" not in open("docs/execution/metrics.md", encoding="utf-8").read(): sys.exit("FAIL: metrics row missing")
print("PASS POST_REVIEW_STATE")
PY
    run s31-issues-render-final uv run python tools/issue_triage.py render --check
    # Post-gate SSOT edits are doc-only (cloud-local §3.4) but gate stages read them: prove they stay green.
    vitest_env_ok s31-post-doc-tests tests/unit/layout-canon.test.ts tests/unit/queue-canon.test.ts tests/unit/gui-actions-audit.test.ts
    ;;
  *) echo "USAGE: validate-task.sh <check>"; exit 2 ;;
esac
