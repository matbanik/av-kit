#!/usr/bin/env bash
# Exact validation procedures for 2026-10-02-capture-flatten-backup (Session 30). Helpers are copied from
# Session 29 (docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh) and Session 27
# (pytest_red), plus mcp_env_ok for the BASELINE_PENDING census member.
# Kept in one script so task.md cells stay lintable (tools/lint_task_contract.py).
# Runs from the repo root. Every procedure writes its raw tool output under $RECEIPTS_DIR and
# exits nonzero on the first failed check. It is executable only during the authorized
# execution session, because it runs product tests and builds.
# Stage ids match validate-task.ps1 exactly; windows-gate-check asserts that order.
set -uo pipefail

PLAN=docs/execution/plans/2026-10-02-capture-flatten-backup
RD="${RECEIPTS_DIR:-/tmp/av-kit}"
mkdir -p "$RD"
CHECK="${1:-}"

fail() { echo "FAIL: $*"; exit 1; }

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
  electron "$@" --repeat-each=20 --output="$RD/s30-repeat-$id" --reporter=json --outputFile="$RD/s30-repeat-$id.json" > "$RD/s30-repeat-$id.txt" 2>&1
  local rc=$?
  [ "$rc" -eq 0 ] || fail "repeat $id exit $rc (receipt $RD/s30-repeat-$id.txt)"
  echo "PASS repeat-each=20 $id"
}

# pytest_env_ok <receipt-id>: full Python suite; the failed set must be a subset of the
# baseline failed set captured by `baseline` before any product edit (ENV_BOUND_PY).
pytest_env_ok() {
  local id="$1"
  [ -f "$RD/s30-baseline-pytest.txt" ] || fail "baseline pytest receipt missing: run 'baseline' first"
  uv run pytest tests/ -q --tb=no -p no:cacheprovider -rfE > "$RD/$id.txt" 2>&1
  python3 - "$RD/s30-baseline-pytest.txt" "$RD/$id.txt" <<'PY' || exit 1
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
  [ -f "$RD/s30-baseline-pytest.txt" ] || fail "baseline pytest receipt missing: run 'baseline' first"
  uv run pytest "$@" -q --tb=short -p no:cacheprovider -rfE > "$RD/$id.txt" 2>&1
  python3 - "$RD/s30-baseline-pytest.txt" "$RD/$id.txt" "$id" <<'PY' || exit 1
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

# mcp_env_ok <receipt-id> [vitest args...]: full or targeted MCP Vitest. The only tolerated failure is the
# BASELINE_PENDING census member, re-proven from the sources: the committed baseline is unchanged since
# baseline.sha and lacks exactly the two MCP_ACTIONS keys (implementation-plan.md §Environment-bound census).
mcp_env_ok() {
  local id="$1"; shift
  local json="$RD/$id.json"
  rm -f "$json"
  npm --prefix mcp-server run test -- "$@" --reporter=json --outputFile="$json" > "$RD/$id.txt" 2>&1
  local rc=$?
  [ -f "$json" ] || fail "$id: MCP Vitest JSON missing (exit $rc)"
  python3 - "$id" "$json" "$rc" "$(cat "$PLAN/baseline.sha" 2>/dev/null)" <<'PY' || exit 1
import json, re, subprocess, sys
rid, path, rc, base = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
j = json.load(open(path, encoding="utf-8"))
suites = j.get("testResults", [])
load = [s["name"] for s in suites if s.get("message")]
if load:
    sys.exit(f"FAIL: {rid} suite load errors {load}")
if j.get("numPendingTests", 0) or j.get("numTodoTests", 0):
    sys.exit(f"FAIL: {rid} pending/todo present")
PENDING = "AC-68.5 the committed baseline's entries equal AUDIT_ACTION_SET and every non-pass carries an issue"
BASE = ".agent/skills/mcp-tool-audit/resources/baseline-snapshot.json"
def baseline_pending_proof():
    if not base or subprocess.run(["git", "diff", "--quiet", base, "--", BASE]).returncode != 0:
        return False
    reg = open("mcp-server/src/toolsets/registry.ts", encoding="utf-8").read()
    served = {f"{t}.{a}" for t, a in re.findall(r'\{ tool: "(\w+)", action: "(\w+)", method:', reg)}
    entries = {f"{e['tool']}.{e['action']}" for e in json.load(open(BASE, encoding="utf-8"))["entries"]}
    return served - entries == {"avkit_capture.flatten", "avkit_capture.revert"} and not (entries - served)
failed = [a for s in suites for a in s.get("assertionResults", []) if a.get("status") == "failed"]
real = [a["fullName"] for a in failed if not (a["fullName"].endswith(PENDING) and baseline_pending_proof())]
if real:
    sys.exit(f"FAIL: {rid} real MCP failures: {real}")
if rc != 0 and not failed:
    sys.exit(f"FAIL: {rid} exit {rc} with no failed assertion (runner error)")
print(f"PASS {rid}: {j.get('numPassedTests')} passed of {j.get('numTotalTests')}, BASELINE_PENDING tolerated: {len(failed)}")
PY
}

# pytest_red <tag> <paths...>: assertion-level Red; an import error is tolerated only when it names one of
# PY_SYMBOLS (the declared new symbols). Copied from Session 27.
PY_SYMBOLS="CaptureFlattenConflictError flatten revert latest_backup resolve_backup_dir ANNOTATED_FORMATS ANNOTATED_EXT ANNOTATED_SUFFIXES output_format"
pytest_red() {
  local tag="$1"; shift
  local xml="$RD/s30-red-py-pytest.xml"
  rm -f "$xml"
  uv run pytest "$@" -q --tb=short -p no:cacheprovider --junitxml="$xml" > "$RD/s30-red-py-pytest.txt" 2>&1
  local rc=$?
  [ "$rc" -ne 0 ] || fail "$tag pytest Red expected a failing run, got exit 0"
  [ -f "$xml" ] || fail "$tag pytest Red junit XML missing (exit $rc)"
  python3 - "$tag" "$xml" "$PY_SYMBOLS" <<'PY' || exit 1
import re, sys, xml.etree.ElementTree as ET
tag, path, symbols = sys.argv[1], sys.argv[2], sys.argv[3].split()
decisive, tolerated, bad, other = [], [], [], []
for case in ET.parse(path).getroot().iter("testcase"):
    name = f"{case.get('classname')}::{case.get('name')}"
    for kind in ("failure", "error"):
        for el in case.findall(kind):
            msg = (el.get("message") or "") + (el.text or "")
            if ("ModuleNotFoundError" in msg or "ImportError" in msg or "AttributeError" in msg) and any(s in msg for s in symbols):
                tolerated.append(name)
            elif kind == "failure" and ("AssertionError" in msg or "assert " in msg or "DID NOT RAISE" in msg):
                (decisive if tag.lower() in name.lower() else other).append(name)
            else:
                bad.append(f"{kind}: {name}: {msg[:160]}")
if bad:
    sys.exit(f"FAIL: {tag} non-assertion failures/errors (setup/import?): {bad[:5]}")
if not decisive:
    sys.exit(f"FAIL: {tag} no failing {tag} assertion (tolerated missing-symbol: {len(tolerated)})")
print(f"PASS {tag} pytest RED: {len(decisive)} decisive, {len(tolerated)} missing-symbol; "
      f"other failing (must be TA-4 pins, dispositioned in walkthrough §Census): {other}")
PY
}

# vitest_red <ui|mcp-server> <ac-tag> <json> <new-file|-> <files...>: assertion-level Red; a declared new
# file may fail only with a missing-module message (Session 29 helper, with the package prefix as a parameter).
vitest_red() {
  local pkg="$1" tag="$2" json="$3" newf="$4"; shift 4
  rm -f "$json"
  npm --prefix "$pkg" run test -- "$@" --reporter=json --outputFile="$json" > "$RD/$(basename "$json" .json).txt" 2>&1
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
other = [a["fullName"][:70] for a in failed if a not in decisive]
if not decisive:
    sys.exit(f"FAIL: {tag} no failed {tag} assertion (only setup/import errors?)")
print(f"PASS {tag} RED: {len(decisive)} failing {tag} assertions, {j.get('numPassedTests')} passing; "
      f"other failing (must be TA-n amended pins, dispositioned in walkthrough §Census): {other}")
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

# Test sets. Paths for npm --prefix runs are relative to that package.
PYT=(tests/e2e/test_api_capture_flatten.py tests/unit/test_capture_service.py tests/unit/test_capture_adapter.py)
REGPY=(tests/e2e/test_api_captures.py tests/unit/test_domain_capture.py tests/unit/test_capture_adapter.py tests/e2e/test_api_openapi.py
       tests/e2e/test_api_downloads.py tests/unit/test_domain.py)
MCPT=(tests/capture.test.ts tests/user-confirm.test.ts tests/action-index.test.ts tests/convert.test.ts
      tests/m7-resource.test.ts tests/strict-confirm.test.ts tests/tools-parity.test.ts tests/audit/coverage.test.ts
      tests/audit/classify.test.ts tests/audit/isolation.test.ts tests/audit/runner-fake-backend.test.ts)
UNIT67=(tests/unit/capture-flatten.test.ts tests/unit/capture-page.behavior.test.ts tests/unit/capture-page.test.ts
        tests/unit/capture-main.behavior.test.ts tests/unit/capture-help-content.test.ts)
# REGCAP: every existing capture unit suite plus the doc/registry suites and the Settings page suite.
REGCAP=(tests/unit/capture-page.test.ts tests/unit/capture-page.behavior.test.ts tests/unit/capture-fit-map.test.ts
        tests/unit/capture-hit-test.test.ts tests/unit/capture-annotate.test.ts tests/unit/capture-arrow-head.test.ts
        tests/unit/capture-color.test.ts tests/unit/capture-sample.test.ts tests/unit/capture-text-metrics.test.ts
        tests/unit/capture-help-content.test.ts tests/unit/capture-filmstrip-label.test.ts tests/unit/capture-toolbar.test.ts
        tests/unit/capture-zoom.test.ts tests/unit/capture-main.behavior.test.ts tests/unit/settings-page.test.ts
        tests/unit/layout-primitives.test.ts tests/unit/layout-canon.test.ts tests/unit/gui-actions-audit.test.ts
        tests/unit/e2e-wiring.test.ts)
E2ECAP=(tests/e2e/capture-inbox.test.ts tests/e2e/settings.test.ts)
REPEAT_GREP="AC-67|AC-57.10"
AUDIT_SRC=(packages/core/src/avkit_core/services/capture.py packages/api/src/avkit_api/routes/captures.py
           packages/infrastructure/src/avkit_infra/capture/adapter.py
           mcp-server/src/toolsets/capture.ts mcp-server/src/toolsets/registry.ts mcp-server/scripts/audit/plan.ts
           mcp-server/scripts/audit/client.ts mcp-server/scripts/audit/classify.ts
           ui/src/renderer/src/features/capture/CapturePage.tsx ui/src/renderer/src/features/capture/capture-flatten.ts
           ui/src/renderer/src/features/capture/capture-commands.ts ui/src/renderer/src/features/capture/CaptureFilmstrip.tsx
           ui/src/renderer/src/features/settings/SettingsPage.tsx)
PREFIX_AUDIT='TODO|FIXME|transition-all|bg-\[#|console\.log\(|@ts-ignore|@ts-expect-error|: any\b'
OPENAPI_NEW=("/api/v1/captures/{id}/flatten" "/api/v1/captures/{id}/revert")

# audit_container: non-authoritative live audit against a real spawned backend (container mode). Exit 1 is
# expected from the standing MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA findings; the check is on the two new steps.
audit_container() {
  local out="$RD/s30-audit-container"
  rm -rf "$out"
  npm --prefix mcp-server run build > "$RD/s30-audit-build.txt" 2>&1 || fail "mcp build for audit"
  npm --prefix mcp-server run audit -- --mode container --no-baseline --out "$out" --agent cloud-s30 > "$RD/s30-audit-container.txt" 2>&1
  local rc=$?
  [ "$rc" -le 1 ] || fail "container audit exit $rc (2 baseline / 3 isolation / 4 runner): $RD/s30-audit-container.txt"
  python3 - "$out/mcp-audit-summary.json" <<'PY' || exit 1
import json, sys
s = json.load(open(sys.argv[1], encoding="utf-8"))
steps = {x["id"]: x for x in s["steps"]}
for sid in ("capture.flatten", "capture.revert", "capture.remove"):
    st = steps.get(sid)
    if not st or st.get("verdict") != "pass":
        sys.exit(f"FAIL: container audit {sid}: {st and (st.get('verdict'), st.get('reason'), st.get('observable'))}")
    ref = (st.get("refusal") or {}).get("refusal_declined") or {}
    if not ref.get("isError") or ref.get("changed"):
        sys.exit(f"FAIL: container audit {sid}: declined user confirmation not refused cleanly: {ref}")
if not (s.get("cleanup") or {}).get("ok"):
    sys.exit(f"FAIL: container audit cleanup {s.get('cleanup')}")
print(f"PASS audit-container: capture.flatten, capture.revert and capture.remove pass with declined refusals; counts {s.get('counts')}")
PY
}

case "$CHECK" in
  prereq)
    [ ! -e graphify-out ] && [ ! -e graphify-out-research ] || fail "graph present: re-run the context-tool gate with the human (S1)"
    uv run python - <<'PY' || fail "MEU state (S1)"
import sys, yaml
rows = {r["id"]: r.get("status") for r in yaml.safe_load(open(".agent/context/meu-status.yaml", encoding="utf-8"))["meus"]}
want = {"MEU-38": "approved", "MEU-60": "approved", "MEU-67": "pending"}
bad = {k: rows.get(k) for k, v in want.items() if rows.get(k) != v}
if bad:
    sys.exit(f"REFUSED: {bad}")
print("PASS MEU state", want)
PY
    grep -q "^Source: \`USER_EXPLICIT\`" "$PLAN/human-gate-decision.md" || fail "gate decision record missing"
    ! grep -q "^Pending\. Execution starts only" "$PLAN/human-gate-decision.md" || fail "execution message not recorded (plan_to_exec_gate: human)"
    [ -d .venv ] || fail ".venv missing: run 'uv sync' first"
    [ -d ui/node_modules ] || fail "ui/node_modules missing: run 'npm --prefix ui ci' first"
    [ -d mcp-server/node_modules ] || fail "mcp-server/node_modules missing: run 'npm --prefix mcp-server ci'"
    [ -x ui/node_modules/electron/dist/electron ] || fail "Electron binary missing: run electron-setup"
    uv run python -c "import PIL" || fail "Pillow not importable (contract tests need the real adapter)"
    unset ELECTRON_RUN_AS_NODE; sandbox_env
    xvfb-run -a ui/node_modules/electron/dist/electron --version || fail "Electron cannot start under xvfb"
    echo "PASS prereq"
    ;;
  electron-setup)
    [ -d ui/node_modules/electron ] || fail "run 'npm --prefix ui ci' first"
    # Session 29 A-2 / Session 27 A-5: the package's own checksum-pinned installer, run once and serially.
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
    [ -z "$(git status --porcelain -- ui packages mcp-server tests openapi.committed.json)" ] || fail "product tree already edited; baseline must precede row 2"
    git rev-parse HEAD > "$PLAN/baseline.sha"
    uv run pytest tests/ -q --tb=no -p no:cacheprovider -rfE > "$RD/s30-baseline-pytest.txt" 2>&1
    grep -qE "[0-9]+ (passed|failed)" "$RD/s30-baseline-pytest.txt" || fail "baseline pytest produced no summary"
    grep -E "[0-9]+ (passed|failed)" "$RD/s30-baseline-pytest.txt" | tail -n 1
    vitest_env_ok s30-baseline-vitest
    run s30-baseline-mcp-build npm --prefix mcp-server run build
    mcp_env_ok s30-baseline-mcp
    run s30-baseline-build npm --prefix ui run build
    run s30-baseline-harness-build harness_build
    electron_env_ok s30-baseline-e2e
    echo "PASS baseline at $(cat "$PLAN/baseline.sha")"
    ;;
  census)
    # Every test that pins something this plan touches. Each hit gets TA-n, fixture, unaffected or new-contradiction.
    rg -n -e 'toHaveLength\(68\)' -e 'toBe\(68\)' -e ACTION_INDEX -e ACTION_SET -e CAPTURE_ACTION_INDEX -e CAPTURE_ACTIONS \
      -e DESTRUCTIVE -e 'confirm_required' -e CAPTURE_KEYS -e close_to_tray -e isolationKeys -e 'MAPPING' -e 'six output' \
      -e SERVER_INSTRUCTIONS -e 'Files on disk' -e CaptureShotDetailOut -e CaptureShotOut -e annotate_and_save -e 'def remove' \
      -e '/annotate' -e 'capture-confirm-strip' -e 'capture-delete-confirm' -e 'capture-dirty-confirm' -e 'capture-status' \
      -e 'original-annotated' -e 'settings-leaf-' -e capturePutSchema -e parseSettingsPut -e 'discovery.actions' \
      -e 'baseline-snapshot' -e 'flatten' -e 'revert' -e 'backup' -e 'SETTINGS_KEY_TABLE' -e 'shouldNotifyInboxChange' \
      -e "'/captures/'" -e 'capture-save' -e ROUTE_COUNT -e DOMAIN_ERROR_TYPE -e 'openapi.committed' \
      -e test_api_downloads -e 'annotated\.png' -e ANNOTATED_SUFFIX -e 'bake\(' -e ToolRuntime -e registerMcpSurface \
      -e confirmWithUser -e RefusalRecord -e refusalVerdict -e 'elicit' \
      tests ui/tests mcp-server/tests > "$RD/s30-census.txt" 2>&1
    rc=$?; [ "$rc" -le 1 ] || fail "census rg exit $rc"
    wc -l < "$RD/s30-census.txt"; echo "PASS census written: $RD/s30-census.txt (disposition every hit in walkthrough.md §Census)"
    ;;
  red-py)
    pytest_red ac_67 "${PYT[@]}"
    ;;
  green-py)
    pytest_paths_ok s30-green-py "${PYT[@]}" "${REGPY[@]}"
    ;;
  red-mcp)
    # The runner suite drives dist/index.js, so build first (Round 1 F4).
    run s30-red-mcp-build npm --prefix mcp-server run build
    vitest_red mcp-server AC-67 "$RD/s30-red-mcp-vitest.json" tests/user-confirm.test.ts "${MCPT[@]}"
    ;;
  green-mcp)
    run s30-green-mcp-build npm --prefix mcp-server run build
    mcp_env_ok s30-green-mcp "${MCPT[@]}"
    ;;
  gate-cycle1)
    run s30-c1-py-types uv run pyright packages/
    run s30-c1-py-lint uv run ruff check packages/ tests/
    pytest_paths_ok s30-c1-pytest "${PYT[@]}" "${REGPY[@]}"
    run s30-c1-mcp-types npm --prefix mcp-server run typecheck
    run s30-c1-mcp-build npm --prefix mcp-server run build
    mcp_env_ok s30-c1-mcp-tests
    # G8 two-step: --check first; regenerate only on drift; then --check must pass (AC-67.15).
    if uv run python tools/export_openapi.py --check openapi.committed.json > "$RD/s30-openapi-check-1.txt" 2>&1; then
      echo "openapi: no drift on this run (regenerated earlier; the first drift receipt is in walkthrough §Cycle 1 gate)"
    else
      echo "openapi: drift detected (expected once the routes exist)"; tail -n 5 "$RD/s30-openapi-check-1.txt"
      run s30-openapi-regen uv run python tools/export_openapi.py -o openapi.committed.json
    fi
    run s30-openapi-check-2 uv run python tools/export_openapi.py --check openapi.committed.json
    python3 - "$(cat "$PLAN/baseline.sha")" "${OPENAPI_NEW[@]}" <<'PY' || exit 1
import json, subprocess, sys
base, new_paths = sys.argv[1], set(sys.argv[2:])
old = json.loads(subprocess.run(["git", "show", f"{base}:openapi.committed.json"], capture_output=True, text=True, check=True).stdout)
cur = json.load(open("openapi.committed.json", encoding="utf-8"))
added, removed = set(cur["paths"]) - set(old["paths"]), set(old["paths"]) - set(cur["paths"])
if added != new_paths or removed:
    sys.exit(f"FAIL: openapi paths added {sorted(added)} removed {sorted(removed)}")
changed = [p for p in old["paths"] if cur["paths"][p] != old["paths"][p]]
if changed:
    sys.exit(f"FAIL: existing openapi paths changed: {changed}")
os_, cs = old["components"]["schemas"], cur["components"]["schemas"]
diff = sorted(k for k in set(os_) | set(cs) if os_.get(k) != cs.get(k))
if not set(diff) <= {"CaptureShotDetailOut", "SettingsPutIn"}:
    sys.exit(f"FAIL: unexpected schema changes {diff}")
if "backup_path" not in cs["CaptureShotDetailOut"].get("properties", {}):
    sys.exit("FAIL: CaptureShotDetailOut lacks backup_path")
print(f"PASS openapi diff: +{sorted(added)}; schemas changed {diff}")
PY
    audit_container
    ;;
  audit-container)
    audit_container
    ;;
  red-ui)
    vitest_red ui AC-67 "$RD/s30-red-ui-vitest.json" tests/unit/capture-flatten.test.ts "${UNIT67[@]}" || exit 1
    electron_red AC-67 "$RD/s30-red-ui-e2e.json" "${E2ECAP[@]}" || exit 1
    ;;
  green-ui)
    vitest_env_ok s30-green-ui "${UNIT67[@]}" "${REGCAP[@]}"
    run s30-green-ui-build npm --prefix ui run build
    electron_env_ok s30-green-ui-e2e "${E2ECAP[@]}" -g "AC-67"
    ;;
  gate67)
    run s30-67-typecheck npm --prefix ui run typecheck
    run s30-67-lint npm --prefix ui run lint
    vitest_env_ok s30-67-vitest "${UNIT67[@]}" "${REGCAP[@]}"
    run s30-67-build npm --prefix ui run build
    run s30-67-harness-build harness_build
    electron_env_ok s30-67-e2e "${E2ECAP[@]}"
    electron_repeat 67-capture "${E2ECAP[@]}" -g "$REPEAT_GREP"
    ;;
  hub)
    python3 - <<'PY' || exit 1
import sys
b09 = open("docs/build-plan/09-screenshot-capture.md", encoding="utf-8").read()
flat = b09.split("### Flatten with backup", 1)[1].split("## Named deferrals", 1)[0]
for need in ("Session 30 plan D-9", "Session 30 plan D-10", "Session 30 plan D-11", "Session 30 plan D-13",
             "Session 30 plan D-14", "Session 30 plan D-22", "Session 30 plan D-23", "Session 30 plan D-24"):
    if need not in flat:
        sys.exit(f"FAIL: 09 §Flatten with backup lacks {need!r}")
mcp = b09.split("\n## MCP\n", 1)[1].split("\n## ", 1)[0]
for row in ("| `flatten` | `POST /captures/{id}/flatten` |", "| `revert` | `POST /captures/{id}/revert` |"):
    if row not in mcp:
        sys.exit(f"FAIL: 09 §MCP lacks {row}")
# Round 1 F5: test the line that carries the Destructive sentence itself, not a neighbouring paragraph.
dline = [l for l in mcp.splitlines() if "Destructive `remove`" in l]
if not dline or not all(w in dline[0] for w in ("flatten", "revert", "elicitation")):
    sys.exit("FAIL: 09 §MCP Destructive sentence does not name flatten, revert and the elicitation confirmation")
card = [l for l in b09.splitlines() if l.startswith("Settings page: new **Capture** card")]
if not card or not all(k in card[0] for k in ("flatten_backup", "backup_dir", "annotated_format")):
    sys.exit("FAIL: 09 Settings page sentence lacks the three leaves")
b05 = open("docs/build-plan/05-mcp-server.md", encoding="utf-8").read()
if "Files on disk are not deleted" in b05 or "Capture remove deletes the shot's files" not in b05:
    sys.exit("FAIL: 05 instruction line not updated to INSTRUCTION_TEXT")
gate = b05.split("### Destructive gate", 1)[1].split("\n### ", 1)[0]
if "elicitation" not in gate:
    sys.exit("FAIL: 05 §Destructive gate lacks the USER_CONFIRM (elicitation) sentence")
if "annotate→flatten→revert" not in b05:
    sys.exit("FAIL: 05 audit lifecycle row lacks annotate→flatten→revert")
if not any("avkit_capture" in l and "flatten" in l and "revert" in l for l in b05.splitlines()[85:105]):
    sys.exit("FAIL: 05 capture destructive list lacks flatten/revert")
b11 = open("docs/build-plan/11-page-layout.md", encoding="utf-8").read()
cap = b11.split("## Capture page layout", 1)[1].split("\n## ", 1)[0]
if "Apply to image" not in cap or "MEU-67" not in cap:
    sys.exit("FAIL: 11 §Capture page layout lacks the Apply to image (MEU-67) sentence")
idx = open("docs/build-plan/gui-actions-index.md", encoding="utf-8").read()
for a in ("capture:apply_image", "capture:revert_image", "settings:browse_capture_backup_dir"):
    if f"| `{a}` |" not in idx:
        sys.exit(f"FAIL: gui-actions-index lacks {a}")
print("PASS hub reconciliation")
PY
    run s30-hub-render-check uv run python tools/meu_status.py render --check
    vitest_env_ok s30-hub-doc-tests tests/unit/layout-canon.test.ts tests/unit/queue-canon.test.ts tests/unit/gui-actions-audit.test.ts
    ;;
  task-state)
    python3 - "$PLAN/task.md" <<'PY' || exit 1
import re, sys
rows = [l for l in open(sys.argv[1], encoding="utf-8") if re.match(r"^\| [0-9]+ \|", l)]
if len(rows) != 11:
    sys.exit(f"FAIL: expected 11 implementation rows (0-10), got {len(rows)}")
for l in rows:
    s = l.rstrip().rstrip("|").split("|")[-1].strip().strip("`")
    if s == "[x]" or (s == "[B]" and "follow-up" in l and "B-" in l):
        continue
    sys.exit(f"FAIL: unfinished row: {l[:60]}")
print("PASS implementation rows 0-10")
PY
    ;;
  pregate)
    echo "== input identity"; git rev-parse HEAD; git status --porcelain | sha256sum
    sha256sum ui/package-lock.json mcp-server/package-lock.json uv.lock; node --version; npm --prefix ui ls electron --depth=0 || true
    run s30-gate-py-types uv run pyright packages/
    run s30-gate-py-lint uv run ruff check packages/ tests/
    run s30-gate-ui-types npm --prefix ui run typecheck
    run s30-gate-ui-lint npm --prefix ui run lint
    run s30-gate-mcp-types npm --prefix mcp-server run typecheck
    run s30-gate-plan-static python3 "$PLAN/plan_checks.py" static
    run s30-gate-task-contract uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task "$PLAN/task.md"
    pytest_env_ok s30-gate-py-tests
    vitest_env_ok s30-gate-ui-tests
    run s30-gate-ui-build npm --prefix ui run build
    run s30-gate-ui-harness-build harness_build
    run s30-gate-mcp-build npm --prefix mcp-server run build
    mcp_env_ok s30-gate-mcp-tests
    run s30-gate-openapi uv run python tools/export_openapi.py --check openapi.committed.json
    run s30-gate-state-render uv run python tools/meu_status.py render --check
    electron_env_ok s30-gate-ui-electron
    for f in "${AUDIT_SRC[@]}"; do [ -f "$f" ] || fail "audited source missing: $f"; done
    if grep -nE "$PREFIX_AUDIT" "${AUDIT_SRC[@]}"; then fail "source audit hits"; fi
    echo "PASS container pre-gate (authoritative: LOCAL_SEQUENCE)"
    ;;
  ssot-review)
    run s30-meu-67-rfr uv run python tools/meu_status.py update MEU-67 ready_for_review --plan "$PLAN"
    run s30-render uv run python tools/meu_status.py render
    run s30-render-check uv run python tools/meu_status.py render --check
    grep -qE '^\| 30 \| `capture-flatten-backup` \| MEU-67 \| P3 \| in review \| `docs/execution/plans/2026-10-02-capture-flatten-backup/`' \
      .agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md || fail "grouping Session 30 not in review"
    grep -q 'capture-flatten-backup' .agent/context/current-focus.md && grep -q 'ready_for_review' .agent/context/current-focus.md \
      || fail "focus does not record Session 30 ready_for_review"
    echo "PASS SSOT review state"
    ;;
  api-scope)
    # PRODUCT_SCOPE (implementation-plan.md §Single-statement contracts).
    run s30-api-openapi uv run python tools/export_openapi.py --check openapi.committed.json
    python3 - "$(cat "$PLAN/baseline.sha")" "$PLAN/implementation-plan.md" <<'PY' || exit 1
import re, subprocess, sys
base, plan = sys.argv[1], open(sys.argv[2], encoding="utf-8").read()
def changed(*paths):
    out = set(subprocess.run(["git", "diff", "--name-only", base, "HEAD", "--", *paths],
                             capture_output=True, text=True, check=True).stdout.split())
    out |= {l[3:] for l in subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "--", *paths],
                                          capture_output=True, text=True, check=True).stdout.splitlines()}
    return out
frozen = sorted(changed("ui/src/main", "tools"))
if frozen:
    sys.exit(f"FAIL: PRODUCT_SCOPE frozen paths changed: {frozen}")
listed = set(re.findall(r"^\| `((?:ui|packages|mcp-server|tests)/[^`]+|openapi\.committed\.json)` \|", plan, re.M))
product = changed("ui", "packages", "mcp-server", "tests", "openapi.committed.json")
extra = sorted(product - listed)
if extra:
    sys.exit(f"FAIL: product changes outside the plan's Files Modified table: {extra}")
# PRODUCT_SCOPE: the adapter's drawing functions keep their AST (AC-67.29).
import ast
ADAPTER = "packages/infrastructure/src/avkit_infra/capture/adapter.py"
def drawing(src):
    out = {}
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
                node.name in ("arrowhead_vertices", "text_plate_box", "_color_rgb", "_load_font") or node.name.startswith("_apply")):
            out[node.name] = ast.dump(node)
    return out
old = drawing(subprocess.run(["git", "show", f"{base}:{ADAPTER}"], capture_output=True, text=True, check=True).stdout)
new = drawing(open(ADAPTER, encoding="utf-8").read())
if not old or old != new:
    sys.exit(f"FAIL: adapter drawing functions changed: {sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))}")
print(f"PASS product scope: {len(product)} changed product files, all listed; adapter drawing unchanged ({len(old)} functions)")
PY
    ;;
  handoff-ac)
    run s30-handoff-ac-67 uv run python tools/validate_closeout_artifacts.py --plan "$PLAN/implementation-plan.md" \
      --handoff .agent/context/handoffs/2026-10-02-capture-flatten-backup-MEU-67-handoff.md --ac-coverage-only
    ;;
  audit-check)
    # LOCAL_SEQUENCE step 1: the authoritative audit summary, the rewritten baseline and the issue carry-over.
    python3 - "$PLAN/mcp-audit-summary.json" "$PLAN/windows-gate-result.json" <<'PY' || exit 1
import json, re, subprocess, sys
try:
    s = json.load(open(sys.argv[1], encoding="utf-8-sig"))
except OSError as err:
    sys.exit(f"FAIL: {err}")
if s.get("schema") != "mcp-audit-summary.v1" or s.get("mode") != "authoritative":
    sys.exit(f"FAIL: summary schema/mode {s.get('schema')} {s.get('mode')}")
steps = {x["id"]: x for x in s["steps"]}
for sid in ("capture.flatten", "capture.revert", "capture.remove"):
    st = steps.get(sid) or {}
    if st.get("verdict") != "pass":
        sys.exit(f"FAIL: {sid} not pass: {st}")
    ref = (st.get("refusal") or {}).get("refusal_declined") or {}
    if not ref.get("isError") or ref.get("changed"):
        sys.exit(f"FAIL: {sid} declined user confirmation not refused cleanly: {ref}")
deltas = {d["key"]: d for d in s.get("deltas", [])}
for k in ("avkit_capture.flatten", "avkit_capture.revert"):
    if (deltas.get(k) or {}).get("delta") not in ("NEW", "UNCHANGED"):
        sys.exit(f"FAIL: delta {k} {deltas.get(k)}")
bad = [k for k, d in deltas.items() if d["delta"] in ("REGRESSION", "REMOVED")]
if bad:
    sys.exit(f"FAIL: audit REGRESSION/REMOVED {bad} (Stop condition S5)")
if not (s.get("cleanup") or {}).get("ok"):
    sys.exit(f"FAIL: cleanup {s.get('cleanup')}")
BASE = ".agent/skills/mcp-tool-audit/resources/baseline-snapshot.json"
b = json.load(open(BASE, encoding="utf-8"))
reg = open("mcp-server/src/toolsets/registry.ts", encoding="utf-8").read()
served = {f"{t}.{a}" for t, a in re.findall(r'\{ tool: "(\w+)", action: "(\w+)", method:', reg)}
entries = {f"{e['tool']}.{e['action']}" for e in b["entries"]}
if entries != served:
    sys.exit(f"FAIL: baseline coverage missing {sorted(served - entries)} extra {sorted(entries - served)}")
untagged = [f"{e['tool']}.{e['action']}" for e in b["entries"] if e["status"] != "pass" and not e.get("issue")]
untagged += [f"{f['code']}:{f['tool']}" for f in b["findings"] if not f.get("issue")]
if untagged:
    sys.exit(f"FAIL: non-pass baseline items without an issue: {untagged}")
if b.get("recorded_commit") != s.get("commit"):
    sys.exit(f"FAIL: baseline recorded_commit {b.get('recorded_commit')} != audit commit {s.get('commit')}")
try:
    tested = json.load(open(sys.argv[2], encoding="utf-8-sig")).get("tested_commit")
except OSError:
    tested = None
if tested:
    # The audit and the gate must have run on the same code: only the baseline, the report and this plan
    # folder may differ between them (LOCAL_SEQUENCE code identity).
    rc = subprocess.run(["git", "diff", "--quiet", s["commit"], tested, "--", "ui", "packages", "mcp-server", "tests",
                         "tools", "pyproject.toml", "uv.lock", "openapi.committed.json"]).returncode
    if rc != 0:
        sys.exit(f"FAIL: audit commit {s['commit']} and gate commit {tested} differ in code")
print(f"PASS audit-check: flatten/revert pass, {len(entries)} baseline entries, counts {s.get('counts')}")
PY
    ;;
  windows-gate-check)
    python3 - <<'PY' || exit 1
import json, re, subprocess, sys
plan = "docs/execution/plans/2026-10-02-capture-flatten-backup"
p = f"{plan}/windows-gate-result.json"
try:
    r = json.load(open(p, encoding="utf-8-sig"))
except OSError as err:
    sys.exit(f"FAIL: {p} unreadable: {err}")
if r.get("schema") != "s30-windows-gate.v1":
    sys.exit(f"FAIL: schema {r.get('schema')}")
if r.get("clean_tree") is not True:
    sys.exit("FAIL: Windows run was not on a clean tree")
pre = r.get("preflight") or {}
if not pre.get("agentic_framework_head") or not pre.get("agent_registry_sha256"):
    sys.exit(f"FAIL: preflight missing: {pre}")
if pre.get("drift") is not False:
    # A-8: a drift passes only when it names a recorded human A-decision and keeps the previous hashes.
    acc = pre.get("drift_accepted") or ""
    hgd = open(f"{plan}/human-gate-decision.md", encoding="utf-8").read()
    if not re.fullmatch(r"A-\d+", acc) or not re.search(rf"^## .*\b{re.escape(acc)}\b", hgd, re.M) or not pre.get("previous"):
        sys.exit(f"FAIL: preflight drifted without a recorded A-decision: {pre}")
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
if v.get("failed") != 0 or (v.get("total") or 0) < 748:
    sys.exit(f"FAIL: vitest {v}")
if e.get("unexpected") != 0 or e.get("flaky") not in (0, None) or (e.get("expected") or 0) < 127:
    sys.exit(f"FAIL: e2e {e}")
if py.get("failed") != 0 or (py.get("passed") or 0) < 629:
    sys.exit(f"FAIL: pytest {py}")
floor = r.get("pytest_floor")
if floor is not None and py["passed"] < floor:
    sys.exit(f"FAIL: pytest passed {py['passed']} below the carried floor {floor}")
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
         ".agent/skills/mcp-tool-audit", ".agent/workflows/mcp-audit.md", ".agent/workflows/README.md",
         ".agent/skills/README.md", ".agent/docs", ".agent/schemas", ".agent/roles", ".agent/templates",
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
    # FLATTEN_LOOK F1-F8 (local-requests.md §GATE): recorded with a result and provenance, all pass,
    # and bound to the same commit as the Windows gate.
    python3 - "$PLAN/walkthrough.md" "$PLAN/windows-gate-result.json" <<'PY' || exit 1
import json, re, sys
try:
    t = open(sys.argv[1], encoding="utf-8").read()
    g = json.load(open(sys.argv[2], encoding="utf-8-sig"))
except OSError as err:
    sys.exit(f"FAIL: {err}")
sec = re.split(r"^## FLATTEN_LOOK[ \t]*$", t, maxsplit=1, flags=re.M)
if len(sec) < 2:
    sys.exit("FAIL: walkthrough.md has no ## FLATTEN_LOOK section")
body = sec[1].split("\n## ", 1)[0]
for item in ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"):
    if re.search(rf"^\|?\s*{item}\b.*pass\|fail", body, re.M):
        sys.exit(f"FAIL: {item} still carries the template token 'pass|fail'")
    m = re.search(rf"^\|?\s*{item}\b[^a-z]*(pass|fail)\b", body, re.M)
    if not m:
        sys.exit(f"FAIL: {item} has no recorded pass/fail")
    if m.group(1) != "pass":
        sys.exit(f"FAIL: {item} recorded fail (Decision Brief per cloud-local §3.5)")
if "USER_EXPLICIT" not in body and "relayed" not in body:
    sys.exit("FAIL: FLATTEN_LOOK results carry no provenance (USER_EXPLICIT or relayed quote)")
sha = (g.get("tested_commit") or "")[:7]
if not sha or sha not in body:
    sys.exit(f"FAIL: FLATTEN_LOOK does not name the gate's tested commit {sha!r}")
print(f"PASS FLATTEN_LOOK F1-F8 on {sha}")
PY
    ;;
  review-check)
    python3 - "$2" "$3" "$4" <<'PY' || exit 1
import re, sys
path, mode, cap = sys.argv[1], sys.argv[2], int(sys.argv[3])
t = open(path, encoding="utf-8").read()
fm = dict(re.findall(r'^(\w+):\s*"?([^"\n]*)"?$', t.split("---")[1], re.M))
target = "docs/execution/plans/2026-10-02-capture-flatten-backup/implementation-plan.md"
if fm.get("target_plan") != target: sys.exit(f"FAIL: target {fm.get('target_plan')}")
if fm.get("review_mode") != mode: sys.exit(f"FAIL: mode {fm.get('review_mode')}")
if int(fm.get("round", "0")) > cap: sys.exit(f"FAIL: round {fm.get('round')} over cap {cap}")
if fm.get("verdict") != "approved": sys.exit(f"FAIL: verdict {fm.get('verdict')}")
# Authorized routes (human-review-decision.md): Fable 5.1 subagent (Round 1), then Codex CLI gpt-6.1-sol
# dispatched by the local agent (from Round 2, 2026-10-10). The Opus 5.5 route was superseded before any round ran.
if fm.get("agent", "").lower() not in ("claude-fable-5-1-subagent", "codex-cli-gpt-6.1-sol"):
    sys.exit(f"FAIL: agent {fm.get('agent')} is not an authorized route")
print(f"PASS {mode} review approved round {fm['round']} by {fm['agent']}")
PY
    ;;
  post-review-state)
    run s30-meu-67-approved uv run python tools/meu_status.py update MEU-67 approved --plan "$PLAN"
    run s30-approved-render uv run python tools/meu_status.py render
    run s30-approved-check uv run python tools/meu_status.py render --check
    uv run python - <<'PY' || exit 1
import sys, yaml
rows = {r["id"]: r.get("status") for r in yaml.safe_load(open(".agent/context/meu-status.yaml", encoding="utf-8"))["meus"]}
if rows.get("MEU-67") != "approved": sys.exit(f"FAIL: MEU-67 {rows.get('MEU-67')}")
issues = {i["id"]: i for i in yaml.safe_load(open(".agent/context/known-issues.yaml", encoding="utf-8"))["issues"]}
for i in ("CAPTURE-FLATTEN-WITH-BACKUP", "MCP-INSTRUCTIONS-CAPTURE-REMOVE-FILES", "MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA"):
    it = issues.get(i) or {}
    ev = ((it.get("verification") or {}).get("evidence_file") or "")
    if it.get("status") != "resolved" or not ev.startswith("docs/execution/plans/2026-10-02-capture-flatten-backup/"):
        sys.exit(f"FAIL: {i} status {it.get('status')} evidence {ev!r}")
g = open(".agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md", encoding="utf-8").read()
if "| 30 | `capture-flatten-backup` | MEU-67 | P3 | approved |" not in g: sys.exit("FAIL: grouping Session 30 not approved")
if "2026-10-02-capture-flatten-backup" not in open("docs/execution/metrics.md", encoding="utf-8").read(): sys.exit("FAIL: metrics row missing")
print("PASS POST_REVIEW_STATE")
PY
    run s30-issues-render-final uv run python tools/issue_triage.py render --check
    vitest_env_ok s30-post-doc-tests tests/unit/layout-canon.test.ts tests/unit/queue-canon.test.ts tests/unit/gui-actions-audit.test.ts
    ;;
  *) echo "USAGE: validate-task.sh <check>"; exit 2 ;;
esac
