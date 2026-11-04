#!/usr/bin/env bash
# Exact validation procedures for 2026-10-01-capture-viewport-chrome (Session 29). Helpers are copied from
# Session 27 (docs/execution/plans/2026-09-30-tts-repair/validate-task.sh), minus the Python-only Red helper.
# Kept in one script so task.md cells stay lintable (tools/lint_task_contract.py).
# Runs from the repo root. Every procedure writes its raw tool output under $RECEIPTS_DIR and
# exits nonzero on the first failed check. It is executable only during the authorized
# execution session, because it runs product tests and builds.
# Stage ids match validate-task.ps1 exactly; windows-gate-check asserts that order.
set -uo pipefail

PLAN=docs/execution/plans/2026-10-01-capture-viewport-chrome
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
    sys.exit(f"FAIL: no spec titled {title} failed on an expect containing {needle!r} (Stop condition S4 if the toolbar does not overflow)")
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
  electron "$@" --repeat-each=20 --output="$RD/s29-repeat-$id" --reporter=json --outputFile="$RD/s29-repeat-$id.json" > "$RD/s29-repeat-$id.txt" 2>&1
  local rc=$?
  [ "$rc" -eq 0 ] || fail "repeat $id exit $rc (receipt $RD/s29-repeat-$id.txt)"
  echo "PASS repeat-each=20 $id"
}

# pytest_env_ok <receipt-id>: full Python suite; the failed set must be a subset of the
# baseline failed set captured by `baseline` before any product edit (ENV_BOUND_PY).
pytest_env_ok() {
  local id="$1"
  [ -f "$RD/s29-baseline-pytest.txt" ] || fail "baseline pytest receipt missing: run 'baseline' first"
  uv run pytest tests/ -q --tb=no -p no:cacheprovider -rfE > "$RD/$id.txt" 2>&1
  python3 - "$RD/s29-baseline-pytest.txt" "$RD/$id.txt" <<'PY' || exit 1
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
  [ -f "$RD/s29-baseline-pytest.txt" ] || fail "baseline pytest receipt missing: run 'baseline' first"
  uv run pytest "$@" -q --tb=short -p no:cacheprovider -rfE > "$RD/$id.txt" 2>&1
  python3 - "$RD/s29-baseline-pytest.txt" "$RD/$id.txt" "$id" <<'PY' || exit 1
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
UNIT65=(tests/unit/capture-toolbar.test.ts tests/unit/capture-page.behavior.test.ts tests/unit/layout-primitives.test.ts)
UNIT66=(tests/unit/capture-zoom.test.ts tests/unit/capture-fit-map.test.ts tests/unit/capture-hit-test.test.ts
        tests/unit/capture-page.behavior.test.ts tests/unit/capture-help-content.test.ts)
# REGCAP: every existing capture unit suite plus the doc/registry suites and the shared-Disclosure neighbours.
REGCAP=(tests/unit/capture-page.test.ts tests/unit/capture-page.behavior.test.ts tests/unit/capture-fit-map.test.ts
        tests/unit/capture-hit-test.test.ts tests/unit/capture-annotate.test.ts tests/unit/capture-arrow-head.test.ts
        tests/unit/capture-color.test.ts tests/unit/capture-sample.test.ts tests/unit/capture-text-metrics.test.ts
        tests/unit/capture-help-content.test.ts tests/unit/capture-filmstrip-label.test.ts
        tests/unit/layout-primitives.test.ts tests/unit/layout-canon.test.ts tests/unit/gui-actions-audit.test.ts
        tests/unit/e2e-wiring.test.ts tests/unit/tts-page.behavior.test.ts)
E2ECAP=(tests/e2e/capture-inbox.test.ts)
# Neighbours of the shared Disclosure primitive under real Electron.
E2EDISC=(tests/e2e/layout-primitives.test.ts tests/e2e/tts-generate.test.ts)
REPEAT_GREP="AC-65|AC-66|AC-59.12|AC-60.12|AC-57.10"
AUDIT_SRC=(ui/src/renderer/src/features/capture/CaptureViewport.tsx ui/src/renderer/src/features/capture/CapturePage.tsx
           ui/src/renderer/src/features/capture/capture-toolbar.ts ui/src/renderer/src/features/capture/capture-zoom.ts
           ui/src/renderer/src/features/capture/capture-fit-map.ts ui/src/renderer/src/features/capture/capture-help-content.ts
           ui/src/renderer/src/components/ui/Disclosure.tsx)
PREFIX_AUDIT='TODO|FIXME|transition-all|bg-\[#|console\.log\(|@ts-ignore|@ts-expect-error|: any\b'

case "$CHECK" in
  prereq)
    [ ! -e graphify-out ] && [ ! -e graphify-out-research ] || fail "graph present: re-run the context-tool gate with the human (S1)"
    uv run python - <<'PY' || fail "MEU state (S1)"
import sys, yaml
rows = {r["id"]: r.get("status") for r in yaml.safe_load(open(".agent/context/meu-status.yaml", encoding="utf-8"))["meus"]}
want = {"MEU-57": "approved", "MEU-59": "approved", "MEU-60": "approved", "MEU-65": "pending", "MEU-66": "pending"}
bad = {k: rows.get(k) for k, v in want.items() if rows.get(k) != v}
if bad:
    sys.exit(f"REFUSED: {bad}")
print("PASS MEU state", want)
PY
    grep -q "^Source: \`USER_EXPLICIT\`" "$PLAN/human-gate-decision.md" || fail "gate decision record missing"
    ! grep -q "^Pending\. Record the user's exact execution message" "$PLAN/human-gate-decision.md" || fail "execution message not recorded (plan_to_exec_gate: human)"
    [ -d .venv ] || fail ".venv missing: run 'uv sync' first"
    [ -d ui/node_modules ] || fail "ui/node_modules missing: run 'npm --prefix ui ci' first"
    [ -d mcp-server/node_modules ] || fail "mcp-server/node_modules missing: run 'npm --prefix mcp-server ci'"
    [ -x ui/node_modules/electron/dist/electron ] || fail "Electron binary missing: run electron-setup"
    node -e "const l=require('./ui/node_modules/lucide-react');for(const n of ['MousePointer2','MoveUpRight','Square','Highlighter','Type','Undo2','Redo2','Image','Layers','ZoomIn','ZoomOut','Maximize','SlidersHorizontal','ChevronDown','ChevronUp'])if(!l[n]){console.error('missing icon '+n);process.exit(1)}" \
      || fail "a TOOLBAR_BUTTONS / OPTIONS_TOGGLE icon is missing from the installed lucide-react"
    unset ELECTRON_RUN_AS_NODE; sandbox_env
    xvfb-run -a ui/node_modules/electron/dist/electron --version || fail "Electron cannot start under xvfb"
    echo "PASS prereq"
    ;;
  electron-setup)
    [ -d ui/node_modules/electron ] || fail "run 'npm --prefix ui ci' first"
    # A-2: the package's own installer, run once and serially before any test. This is the same
    # method as the .ps1 npm-ci stage (Session 27 A-5). It is checksum-pinned to the package's
    # checksums.json and exits 0 when the binary is already installed.
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
    uv run pytest tests/ -q --tb=no -p no:cacheprovider -rfE > "$RD/s29-baseline-pytest.txt" 2>&1
    grep -qE "[0-9]+ (passed|failed)" "$RD/s29-baseline-pytest.txt" || fail "baseline pytest produced no summary"
    grep -E "^[0-9]+ (passed|failed)|passed|failed" "$RD/s29-baseline-pytest.txt" | tail -n 1
    vitest_env_ok s29-baseline-vitest
    run s29-baseline-build npm --prefix ui run build
    run s29-baseline-harness-build harness_build
    electron_env_ok s29-baseline-e2e
    echo "PASS baseline at $(cat "$PLAN/baseline.sha")"
    ;;
  census)
    # Every test that pins something this plan touches (TEST_AMENDMENTS is empty: each hit must be 'unaffected').
    rg -n -e 'capture-tool-' -e capture-undo -e capture-redo -e capture-view- -e 'capture-color' -e capture-named-color \
      -e capture-stroke -e capture-font-size -e capture-text-bg -e capture-chrome -e capture-settings -e capture-draw-surface \
      -e capture-viewport-image -e capture-handle- -e capture-text-draft -e fitScaleOrigin -e mapPointerToImage -e mapImageToPointer \
      -e clampImagePoint -e hitTestMarks -e 'h-7' -e flex-nowrap -e overflow-x -e "name: 'Advanced'" -e 'Cleanup ·' \
      -e 'Disclosure' -e 'viewBox' -e preserveAspectRatio -e object-contain -e 'Select a shot' -e "'Settings'" \
      -e wheel -e 'Control+' -e getZoomFactor -e 'Sample original' -e 'four-tools' -e sampleShot \
      ui/tests > "$RD/s29-census.txt" 2>&1
    rc=$?; [ "$rc" -le 1 ] || fail "census rg exit $rc"
    wc -l < "$RD/s29-census.txt"; echo "PASS census written: $RD/s29-census.txt (disposition every hit in walkthrough.md §Census)"
    ;;
  red65)
    vitest_red AC-65 "$RD/s29-65-red-vitest.json" tests/unit/capture-toolbar.test.ts "${UNIT65[@]}" || exit 1
    electron_red AC-65 "$RD/s29-65-red-e2e.json" "${E2ECAP[@]}" || exit 1
    require_failed_title "$RD/s29-65-red-e2e.json" AC-65.4 toBeLessThanOrEqual || exit 1
    ;;
  green65)
    vitest_env_ok s29-65-green "${UNIT65[@]}" "${REGCAP[@]}"
    ;;
  gate65)
    run s29-65-typecheck npm --prefix ui run typecheck
    run s29-65-lint npm --prefix ui run lint
    vitest_env_ok s29-65-vitest "${UNIT65[@]}" "${REGCAP[@]}"
    run s29-65-build npm --prefix ui run build
    run s29-65-harness-build harness_build
    electron_env_ok s29-65-e2e "${E2ECAP[@]}"
    electron_env_ok s29-65-e2e-disclosure "${E2EDISC[@]}"
    electron_repeat 65-capture "${E2ECAP[@]}" -g "$REPEAT_GREP"
    ;;
  red66)
    vitest_red AC-66 "$RD/s29-66-red-vitest.json" tests/unit/capture-zoom.test.ts "${UNIT66[@]}" || exit 1
    electron_red AC-66 "$RD/s29-66-red-e2e.json" "${E2ECAP[@]}" || exit 1
    ;;
  green66-unit)
    vitest_env_ok s29-66-green-unit tests/unit/capture-zoom.test.ts tests/unit/capture-fit-map.test.ts tests/unit/capture-hit-test.test.ts
    ;;
  green66)
    vitest_env_ok s29-66-green "${UNIT65[@]}" "${UNIT66[@]}" "${REGCAP[@]}"
    run s29-66-green-build npm --prefix ui run build
    electron_env_ok s29-66-green-e2e "${E2ECAP[@]}" -g "AC-66"
    ;;
  gate66)
    run s29-66-typecheck npm --prefix ui run typecheck
    run s29-66-lint npm --prefix ui run lint
    vitest_env_ok s29-66-vitest "${UNIT65[@]}" "${UNIT66[@]}" "${REGCAP[@]}"
    run s29-66-build npm --prefix ui run build
    run s29-66-harness-build harness_build
    electron_env_ok s29-66-e2e "${E2ECAP[@]}"
    electron_env_ok s29-66-e2e-disclosure "${E2EDISC[@]}"
    electron_repeat 66-capture "${E2ECAP[@]}" -g "$REPEAT_GREP"
    ;;
  hub)
    python3 - <<'PY' || exit 1
import re, sys
b09 = open("docs/build-plan/09-screenshot-capture.md", encoding="utf-8").read()
tools = b09.split("### Viewport tools", 1)[1].split("### Destructive Delete", 1)[0]
if "#viewport-zoom" not in tools or "MEU-66" not in tools:
    sys.exit("FAIL: 09 §Viewport tools zoom sentence lacks the §Viewport zoom (MEU-66) pointer")
zoom = b09.split("### Viewport zoom", 1)[1].split("### Flatten with backup", 1)[0]
for need in ("0.25", "1/3", "2/3", "5", "page_zoom.cc", "Session 29 plan D-14", "Session 29 plan D-15",
             "Session 29 plan D-17", "Session 29 plan D-18"):
    if need not in zoom:
        sys.exit(f"FAIL: 09 §Viewport zoom lacks {need!r}")
if "the exact bounds are fixed at plan time" in zoom:
    sys.exit("FAIL: 09 §Viewport zoom Levels row still unresolved")
icons = b09.split("### Viewport toolbar icons and Options", 1)[1].split("### Viewport zoom", 1)[0]
for need in ("Session 29 plan D-9", "Session 29 plan D-12"):
    if need not in icons:
        sys.exit(f"FAIL: 09 §Viewport toolbar icons and Options lacks {need}")
meus = b09.split("## MEUs", 1)[1].split("## Exit criteria", 1)[0]
for m in ("MEU-65", "MEU-66", "MEU-67"):
    if f"| {m} |" not in meus:
        sys.exit(f"FAIL: 09 §MEUs lacks {m}")
b11 = open("docs/build-plan/11-page-layout.md", encoding="utf-8").read()
cap = b11.split("## Capture page layout", 1)[1].split("\n## ", 1)[0]
if "Options" not in cap or "MEU-65" not in cap:
    sys.exit("FAIL: 11 §Capture page layout lacks the Options (MEU-65) sentence")
idx = open("docs/build-plan/gui-actions-index.md", encoding="utf-8").read()
for a in ("capture:zoom_in", "capture:zoom_out", "capture:zoom_fit"):
    if f"| `{a}` |" not in idx:
        sys.exit(f"FAIL: gui-actions-index lacks {a}")
print("PASS hub reconciliation")
PY
    run s29-hub-render-check uv run python tools/meu_status.py render --check
    # The CP rows stay untouched (AC-50.1/50.4 lock); prove the doc-reading suites still pass.
    vitest_env_ok s29-hub-doc-tests tests/unit/layout-canon.test.ts tests/unit/queue-canon.test.ts tests/unit/gui-actions-audit.test.ts
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
    run s29-gate-py-types uv run pyright packages/
    run s29-gate-py-lint uv run ruff check packages/ tests/
    run s29-gate-ui-types npm --prefix ui run typecheck
    run s29-gate-ui-lint npm --prefix ui run lint
    run s29-gate-mcp-types npm --prefix mcp-server run typecheck
    run s29-gate-plan-static python3 "$PLAN/plan_checks.py" static
    run s29-gate-task-contract uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task "$PLAN/task.md"
    pytest_env_ok s29-gate-py-tests
    vitest_env_ok s29-gate-ui-tests
    run s29-gate-ui-build npm --prefix ui run build
    run s29-gate-ui-harness-build harness_build
    run s29-gate-mcp-build npm --prefix mcp-server run build
    run s29-gate-mcp-tests npm --prefix mcp-server run test
    run s29-gate-openapi uv run python tools/export_openapi.py --check openapi.committed.json
    run s29-gate-state-render uv run python tools/meu_status.py render --check
    electron_env_ok s29-gate-ui-electron
    for f in "${AUDIT_SRC[@]}"; do [ -f "$f" ] || fail "audited source missing: $f"; done
    if grep -nE "$PREFIX_AUDIT" "${AUDIT_SRC[@]}"; then fail "source audit hits"; fi
    echo "PASS container pre-gate (authoritative: windows-gate + CAPTURE_LOOK)"
    ;;
  ssot-review)
    for n in 65 66; do
      run "s29-meu-$n-rfr" uv run python tools/meu_status.py update "MEU-$n" ready_for_review --plan "$PLAN"
    done
    run s29-render uv run python tools/meu_status.py render
    run s29-render-check uv run python tools/meu_status.py render --check
    grep -qE '^\| 29 \| `capture-viewport-chrome` \| MEU-65, MEU-66 \| P3 \| in review \| `docs/execution/plans/2026-10-01-capture-viewport-chrome/`' \
      .agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md || fail "grouping Session 29 not in review"
    grep -q 'capture-viewport-chrome' .agent/context/current-focus.md && grep -q 'ready_for_review' .agent/context/current-focus.md \
      || fail "focus does not record Session 29 ready_for_review"
    echo "PASS SSOT review state"
    ;;
  api-scope)
    # PRODUCT_SCOPE (implementation-plan.md §Single-statement contracts).
    run s29-api-openapi uv run python tools/export_openapi.py --check openapi.committed.json
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
    ;;
  handoff-ac)
    for n in 65 66; do
      run "s29-handoff-ac-$n" uv run python tools/validate_closeout_artifacts.py --plan "$PLAN/implementation-plan.md" \
        --handoff ".agent/context/handoffs/2026-10-01-capture-viewport-chrome-MEU-$n-handoff.md" --ac-coverage-only
    done
    ;;
  windows-gate-check)
    python3 - <<'PY' || exit 1
import json, subprocess, sys
plan = "docs/execution/plans/2026-10-01-capture-viewport-chrome"
p = f"{plan}/windows-gate-result.json"
try:
    r = json.load(open(p, encoding="utf-8-sig"))
except OSError as err:
    sys.exit(f"FAIL: {p} unreadable: {err}")
if r.get("schema") != "s29-windows-gate.v1":
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
v, e, py = r.get("vitest") or {}, r.get("e2e") or {}, r.get("pytest") or {}
# COUNT_FLOORS (implementation-plan.md §Single-statement contracts).
if v.get("failed") != 0 or (v.get("total") or 0) < 702:
    sys.exit(f"FAIL: vitest {v}")
if e.get("unexpected") != 0 or e.get("flaky") not in (0, None) or (e.get("expected") or 0) < 118:
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
print(f"PASS windows gate @ {tested}: vitest {v} e2e {e} pytest {py}")
PY
    ;;
  look-check)
    # CAPTURE_LOOK L1-L6 (local-requests.md §GATE): recorded with a result and provenance, all pass,
    # and bound to the same commit as the Windows gate.
    python3 - "$PLAN/walkthrough.md" "$PLAN/windows-gate-result.json" <<'PY' || exit 1
import json, re, sys
try:
    t = open(sys.argv[1], encoding="utf-8").read()
    g = json.load(open(sys.argv[2], encoding="utf-8-sig"))
except OSError as err:
    sys.exit(f"FAIL: {err}")
sec = re.split(r"^## CAPTURE_LOOK[ \t]*$", t, maxsplit=1, flags=re.M)
if len(sec) < 2:
    sys.exit("FAIL: walkthrough.md has no ## CAPTURE_LOOK section")
body = sec[1].split("\n## ", 1)[0]
for item in ("L1", "L2", "L3", "L4", "L5", "L6"):
    # An unfilled template line (literal 'pass|fail') never counts as a result (Review R2-1).
    if re.search(rf"^\|?\s*{item}\b.*pass\|fail", body, re.M):
        sys.exit(f"FAIL: {item} still carries the template token 'pass|fail'")
    # The result is the first word after the item id (Review R1 F3), never a later "pass|fail" template token.
    m = re.search(rf"^\|?\s*{item}\b[^a-z]*(pass|fail)\b", body, re.M)
    if not m:
        sys.exit(f"FAIL: {item} has no recorded pass/fail")
    if m.group(1) != "pass":
        sys.exit(f"FAIL: {item} recorded fail (Decision Brief per cloud-local §3.5)")
if "USER_EXPLICIT" not in body and "relayed" not in body:
    sys.exit("FAIL: CAPTURE_LOOK results carry no provenance (USER_EXPLICIT or relayed quote)")
sha = (g.get("tested_commit") or "")[:7]
if not sha or sha not in body:
    sys.exit(f"FAIL: CAPTURE_LOOK does not name the gate's tested commit {sha!r}")
print(f"PASS CAPTURE_LOOK L1-L6 on {sha}")
PY
    ;;
  review-check)
    python3 - "$2" "$3" "$4" <<'PY' || exit 1
import re, sys
path, mode, cap = sys.argv[1], sys.argv[2], int(sys.argv[3])
t = open(path, encoding="utf-8").read()
fm = dict(re.findall(r'^(\w+):\s*"?([^"\n]*)"?$', t.split("---")[1], re.M))
target = "docs/execution/plans/2026-10-01-capture-viewport-chrome/implementation-plan.md"
if fm.get("target_plan") != target: sys.exit(f"FAIL: target {fm.get('target_plan')}")
if fm.get("review_mode") != mode: sys.exit(f"FAIL: mode {fm.get('review_mode')}")
if int(fm.get("round", "0")) > cap: sys.exit(f"FAIL: round {fm.get('round')} over cap {cap}")
if fm.get("verdict") != "approved": sys.exit(f"FAIL: verdict {fm.get('verdict')}")
if "fable" not in fm.get("agent", "").lower(): sys.exit(f"FAIL: agent {fm.get('agent')} is not the authorized route")
print(f"PASS {mode} review approved round {fm['round']} by {fm['agent']}")
PY
    ;;
  post-review-state)
    for n in 65 66; do
      run "s29-meu-$n-approved" uv run python tools/meu_status.py update "MEU-$n" approved --plan "$PLAN"
    done
    run s29-approved-render uv run python tools/meu_status.py render
    run s29-approved-check uv run python tools/meu_status.py render --check
    uv run python - <<'PY' || exit 1
import sys, yaml
rows = {r["id"]: r.get("status") for r in yaml.safe_load(open(".agent/context/meu-status.yaml", encoding="utf-8"))["meus"]}
bad = {k: rows.get(k) for k in ("MEU-65", "MEU-66") if rows.get(k) != "approved"}
if bad: sys.exit(f"FAIL: MEU state {bad}")
issues = {i["id"]: i for i in yaml.safe_load(open(".agent/context/known-issues.yaml", encoding="utf-8"))["issues"]}
for i in ("CAPTURE-TOOLBAR-ICONS", "CAPTURE-SETTINGS-BUTTON-LABEL", "CAPTURE-VIEWPORT-ZOOM"):
    it = issues.get(i) or {}
    ev = ((it.get("verification") or {}).get("evidence_file") or "")
    if it.get("status") != "resolved" or not ev.startswith("docs/execution/plans/2026-10-01-capture-viewport-chrome/"):
        sys.exit(f"FAIL: {i} status {it.get('status')} evidence {ev!r}")
g = open(".agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md", encoding="utf-8").read()
if "| 29 | `capture-viewport-chrome` | MEU-65, MEU-66 | P3 | approved |" not in g: sys.exit("FAIL: grouping Session 29 not approved")
if "2026-10-01-capture-viewport-chrome" not in open("docs/execution/metrics.md", encoding="utf-8").read(): sys.exit("FAIL: metrics row missing")
print("PASS POST_REVIEW_STATE")
PY
    run s29-issues-render-final uv run python tools/issue_triage.py render --check
    # Post-gate SSOT edits are doc-only (cloud-local §3.4) but gate stages read them: prove they stay green.
    vitest_env_ok s29-post-doc-tests tests/unit/layout-canon.test.ts tests/unit/queue-canon.test.ts tests/unit/gui-actions-audit.test.ts
    ;;
  *) echo "USAGE: validate-task.sh <check>"; exit 2 ;;
esac
