#!/usr/bin/env bash
# Exact validation procedures for 2026-09-28-p11-capture-settings (helpers adapted from Session 25).
# Kept in one script so task.md cells stay lintable (tools/lint_task_contract.py).
# Runs from the repo root; every procedure writes its raw tool output under
# $RECEIPTS_DIR and exits nonzero on the first failed check. Executable only
# during the authorized execution session: it runs product tests/builds.
set -uo pipefail

PLAN=docs/execution/plans/2026-09-28-p11-capture-settings
RD="${RECEIPTS_DIR:-/tmp/av-kit}"
mkdir -p "$RD"
CHECK="${1:-}"

fail() { echo "FAIL: $*"; exit 1; }

# sandbox_env: Chromium refuses to run as root with its sandbox on (container runs as root).
sandbox_env() {
  if [ "$(id -u)" = "0" ]; then export ELECTRON_DISABLE_SANDBOX=1; fi
}

# ENV_BOUND_TESTS: the only Vitest failures tolerated in the Linux container, each with a
# signature proving the environment cause. The Windows gate (WINDOWS_GATE) tolerates none.
#   AC-51.6: expected hash is of the CRLF checkout (.gitattributes text=auto); proven by
#            recomputing the CRLF hash of the test-ids.ts prefix here.
#   AC-41.3: reads the Windows-only path P:/zorivest/...; proven by its absence here.
vitest_env_ok() { # vitest_env_ok <receipt-id> <vitest args...>
  local id="$1"; shift
  local json="$RD/$id.json"
  npm --prefix ui run test -- "$@" --reporter=json --outputFile="$json" > "$RD/$id.txt" 2>&1
  local rc=$?
  [ -f "$json" ] || fail "$id: Vitest JSON missing (exit $rc)"
  python3 - "$id" "$json" "$rc" <<'PY' || exit 1
import hashlib, json, os, subprocess, sys
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
    prefix = t.split(b"// MEU-51 primitive harness IDs.")[0]
    if b"\r" in t:
        return False
    h = hashlib.sha256(prefix.replace(b"\n", b"\r\n")).hexdigest().upper()
    if h != "819760B9840EE4BF38633B3628DC2E7820D4B87E05A0EC720B75B61C89D28A73":
        return False
    # Replicate the rest of AC-51.6 (layout-primitives.test.ts:190-196), which the
    # failed hash assertion prevents from running in this container.
    import re as _re
    text = t.decode("utf-8")
    head, tail = text.split("// MEU-51 primitive harness IDs.")
    prior = _re.findall(r"^export const \w+ = '([^']+)'", head, _re.M)
    new = _re.findall(r"^export const \w+ = '([^']+)'", tail, _re.M)
    if len(set(new)) != len(new) or any(v in prior for v in new):
        return False
    return all(i in new for i in ("primitive-disclosure", "primitive-segment", "primitive-chip",
                                  "primitive-form", "primitive-path"))
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
receipt = open(path[:-5] + ".txt", encoding="utf-8", errors="replace").read()
if "Unhandled Error" in receipt or "Unhandled Rejection" in receipt or j.get("success") is False and not failed:
    sys.exit(f"FAIL: {rid} unhandled error reported by Vitest (see receipt)")
print(f"PASS {rid}: {j.get('numPassedTests')} passed, env-bound tolerated: {[a['fullName'][:40] for a in failed]}")
PY
}

# electron_env_ok <receipt-id> [args...]: full Electron run tolerating only ENV_BOUND_E2E —
# the capture-picker specs that need the Windows-only win-x64 sidecar stub
# (native/region-picker-stub, built by `build:picker-stub` with dotnet -r win-x64).
# Tolerated only off Windows, only while the stub is absent, and only when the
# failure is exactly the stub-missing assertion. WINDOWS_GATE tolerates none.
electron_env_ok() {
  local id="$1"; shift
  local json="$RD/$id.json"
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
real, tolerated, passed = [], [], 0
for top in j.get("suites", []):
    for file, spec in specs(top):
        for test in spec.get("tests", []):
            results = test.get("results", [])
            status = results[-1].get("status") if results else "missing"
            if status in ("passed", "skipped") and test.get("status") != "unexpected":
                passed += status == "passed"
                continue
            msgs = " ".join(e.get("message", "") for r in results for e in r.get("errors", []))
            # Either the spec's own stub-present guard, or its direct spawn of that same absent stub.
            stub_error = ("the deterministic sidecar stub is missing" in msgs
                          or ("ENOENT" in msgs and "avkit-region-picker-stub.exe" in msgs))
            env = (file.endswith("capture-picker.test.ts") and os.name != "nt"
                   and not os.path.exists(stub) and stub_error)
            (tolerated if env else real).append(f"{file}: {spec.get('title')}")
if real:
    sys.exit(f"FAIL: {rid} real Electron failures: {real}")
if rc != 0 and not tolerated:
    sys.exit(f"FAIL: {rid} exit {rc} with no failed spec (runner error)")
print(f"PASS {rid}: {passed} passed, env-bound tolerated: {tolerated}")
PY
}

# harness_build: the isolated MEU-51 primitive harness (E2E_HARNESS) into ui/out-e2e.
harness_build() {
  AVKIT_PRIMITIVE_HARNESS_BUILD=1 npm --prefix ui run build -- --outDir "$(pwd)/ui/out-e2e"
}

# electron: run Playwright against real Electron, headless display when none exists.
electron() {
  unset ELECTRON_RUN_AS_NODE AVKIT_E2E_OUT_DIR
  sandbox_env
  if [ -z "${DISPLAY:-}" ]; then
    xvfb-run -a npm --prefix ui run test:e2e -- "$@"
  else
    npm --prefix ui run test:e2e -- "$@"
  fi
}

# vitest_red <ac-tag> <json> <files...>: assertion-level Red, never a collection error.
vitest_red() {
  local tag="$1" json="$2"; shift 2
  npm --prefix ui run test -- "$@" --reporter=json --outputFile="$json" > "$RD/$(basename "$json" .json).txt" 2>&1
  local rc=$?
  [ "$rc" -ne 0 ] || fail "$tag Red expected a failing run, got exit 0"
  [ -f "$json" ] || fail "$tag Red JSON report missing"
  python3 - "$tag" "$json" "$#" <<'PY' || exit 1
import json, sys
tag, path, nfiles = sys.argv[1], sys.argv[2], int(sys.argv[3])
j = json.load(open(path, encoding="utf-8"))
suites = j.get("testResults", [])
if len(suites) != nfiles:
    sys.exit(f"FAIL: {tag} expected {nfiles} collected files, got {len(suites)}")
load_errors = [s["name"] for s in suites if s.get("message")]
if load_errors:
    sys.exit(f"FAIL: {tag} suite load/collection error in {load_errors}")
if j.get("numPendingTests", 0) or j.get("numTodoTests", 0):
    sys.exit(f"FAIL: {tag} pending/todo tests present")
failed = [a for s in suites for a in s.get("assertionResults", [])
          if a.get("status") == "failed" and tag in a.get("fullName", "")]
decisive = [a for a in failed if any("expected" in m.lower() or "assert" in m.lower()
                                     for m in a.get("failureMessages", []))]
if not decisive:
    sys.exit(f"FAIL: {tag} no failed {tag} assertion (only setup/import errors?)")
print(f"PASS {tag} RED: {len(decisive)} failing {tag} assertions, {j.get('numPassedTests')} passing")
PY
}

# electron_red <ac-tag> <json> <files...>: fresh build, then at least one AC expect() failure.
electron_red() {
  local tag="$1" json="$2"; shift 2
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
    for s in suite.get("specs", []):
        yield s
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

run() { # run <receipt-id> <cmd...>: exact receipt, propagate exit
  local id="$1"; shift
  "$@" > "$RD/$id.txt" 2>&1
  local rc=$?
  tail -n 25 "$RD/$id.txt"
  [ "$rc" -eq 0 ] || fail "$id exit $rc (receipt $RD/$id.txt)"
  echo "PASS $id"
}

PC="$PLAN/plan_checks.py"

# vitest_red_new <tag> <json> <new-file|-> <files...>: RED_ORACLE via plan_checks.py.
# Declared new test files may fail only with a missing-module message; every other
# failure must be an assertion titled with <tag>.
vitest_red_new() {
  local tag="$1" json="$2" newf="$3"; shift 3
  npm --prefix ui run test -- "$@" --reporter=json --outputFile="$json" > "$RD/$(basename "$json" .json).txt" 2>&1
  local rc=$?
  [ "$rc" -ne 0 ] || fail "$tag Red expected a failing run, got exit 0"
  if [ "$newf" = "-" ]; then
    uv run python "$PC" red --kind vitest --json "$json" --ac "$tag"
  else
    uv run python "$PC" red --kind vitest --json "$json" --ac "$tag" --new-file "$newf"
  fi
}

UNIT57=(tests/unit/capture-page.behavior.test.ts tests/unit/capture-filmstrip-label.test.ts)
# REG57: suites with source pins or layout contracts on files MEU-57 modifies.
REG57=(tests/unit/capture-page.test.ts tests/unit/layout-primitives.test.ts tests/unit/gui-actions-audit.test.ts
       tests/unit/help-card.test.ts tests/unit/layout-canon.test.ts tests/unit/capture-interactive.test.ts
       tests/unit/capture-lifecycle.test.ts)
E2E57=(tests/e2e/capture-inbox.test.ts tests/e2e/capture-picker.test.ts)
UNIT58=(tests/unit/settings-page.test.ts tests/unit/settings-rail.test.tsx tests/unit/layout-primitives.test.ts)
REG58=(tests/unit/convert-page.test.ts tests/unit/convert-page.behavior.test.ts tests/unit/capture-page.test.ts
       tests/unit/gui-actions-audit.test.ts tests/unit/help-card.test.ts tests/unit/chrome-zorivest.test.ts
       tests/unit/layout-canon.test.ts)
E2E58=(tests/e2e/settings.test.ts tests/e2e/convert-queue.test.ts tests/e2e/capture-inbox.test.ts tests/e2e/help-search.spec.ts)
DOC_READING_TESTS=(tests/unit/layout-canon.test.ts tests/unit/queue-canon.test.ts)
AUDIT_SRC=(ui/src/renderer/src/features/capture/CapturePage.tsx ui/src/renderer/src/features/capture/CaptureViewport.tsx
           ui/src/renderer/src/features/capture/CaptureFilmstrip.tsx ui/src/renderer/src/features/capture/capture-filmstrip-label.ts
           ui/src/renderer/src/features/settings/SettingsPage.tsx ui/src/renderer/src/features/settings/SettingsRail.tsx
           ui/src/renderer/src/features/settings/settings-sections.ts ui/src/renderer/src/features/settings/StartAtSignInControl.tsx
           ui/src/renderer/src/components/ui/PathRow.tsx)

case "$CHECK" in
  prereq)
    [ ! -e graphify-out ] && [ ! -e graphify-out-research ] || fail "graph present: re-run context-tool gate with the human"
    uv run python "$PC" self-test || fail "plan_checks self-test"
    uv run python "$PC" meu-state --expect MEU-50..56=approved --expect MEU-57..58=pending || fail "SEQUENCING_GATE"
    [ -d ui/node_modules ] || fail "ui/node_modules missing: run 'npm --prefix ui ci' first"
    [ -d mcp-server/node_modules ] || fail "mcp-server/node_modules missing"
    node --version; npm --prefix ui ls electron --depth=0 || true
    [ -x ui/node_modules/electron/dist/electron ] || fail "Electron binary missing: run electron-setup"
    unset ELECTRON_RUN_AS_NODE; sandbox_env
    xvfb-run -a ui/node_modules/electron/dist/electron --version || fail "Electron cannot start under xvfb"
    echo "PASS prereq"
    ;;
  electron-setup)
    [ -d ui/node_modules/electron ] || fail "run 'npm --prefix ui ci' first"
    if [ -x ui/node_modules/electron/dist/electron ] && [ -f ui/node_modules/electron/path.txt ]; then
      echo "Electron already installed: $(cat ui/node_modules/electron/dist/version)"
    else
      V=$(node -p "require('./ui/node_modules/electron/package.json').version")
      Z="electron-v$V-linux-x64.zip"; T="$RD/$Z"
      curl -sSL --retry 3 --max-time 600 -o "$T" "https://github.com/electron/electron/releases/download/v$V/$Z" || fail "curl download failed"
      EXP=$(node -p "require('./ui/node_modules/electron/checksums.json')['$Z']")
      ACT=$(sha256sum "$T" | cut -d' ' -f1)
      [ "$EXP" = "$ACT" ] || fail "checksum mismatch: expected $EXP got $ACT"
      (cd ui/node_modules/electron && node -e "
const {extract}=require('@electron-internal/extract-zip');const fs=require('fs'),path=require('path');const d=process.cwd();
extract(process.argv[1],{dir:path.join(d,'dist')}).then(()=>fs.writeFileSync(path.join(d,'path.txt'),'electron')).catch(e=>{console.error(e);process.exit(1)})" "$T") || fail "extract failed"
      echo "installed Electron $V (sha256 $ACT)"
    fi
    unset ELECTRON_RUN_AS_NODE; sandbox_env
    xvfb-run -a ui/node_modules/electron/dist/electron --version || fail "Electron cannot start under xvfb"
    echo "PASS electron-setup"
    ;;
  baseline)
    # Pre-edit baseline: the untouched tree passes everything except ENV_BOUND.
    vitest_env_ok s26-baseline-vitest
    run s26-baseline-build npm --prefix ui run build
    run s26-baseline-harness-build harness_build
    electron_env_ok s26-baseline-e2e
    ;;
  census)
    rg -n -e capture-save -e capture-tool- -e capture-inbox-path -e capture-hotkey -e capture-page-save \
      -e capture-filmstrip -e capture-empty -e capture-status -e capture-chrome -e createPortal -e display_name \
      -e mcp-token-present -e settings-page -e max-w-3xl -e readiness- -e settings-leaf-cookie_mode \
      -e apply-defaults-btn -e theme- -e settings-log-file-path -e components/ui/ ui/tests > "$RD/s26-census.txt" 2>&1
    rc=$?; [ "$rc" -le 1 ] || fail "census rg exit $rc"
    wc -l < "$RD/s26-census.txt"; echo "PASS census written: $RD/s26-census.txt"
    ;;
  red57)
    vitest_red_new AC-57 "$RD/s26-57-red-vitest.json" tests/unit/capture-filmstrip-label.test.ts "${UNIT57[@]}" || exit 1
    electron_red AC-57 "$RD/s26-57-red-e2e.json" tests/e2e/capture-inbox.test.ts || exit 1
    ;;
  green57)
    vitest_env_ok s26-57-green "${UNIT57[@]}" "${REG57[@]}"
    ;;
  gate57)
    run s26-57-typecheck npm --prefix ui run typecheck
    run s26-57-lint npm --prefix ui run lint
    vitest_env_ok s26-57-vitest "${UNIT57[@]}" "${REG57[@]}"
    run s26-57-build npm --prefix ui run build
    electron_env_ok s26-57-e2e "${E2E57[@]}"
    ;;
  red58)
    vitest_red_new AC-58 "$RD/s26-58-red-vitest.json" tests/unit/settings-rail.test.tsx "${UNIT58[@]}" || exit 1
    electron_red AC-58 "$RD/s26-58-red-e2e.json" tests/e2e/settings.test.ts || exit 1
    ;;
  green58)
    vitest_env_ok s26-58-green "${UNIT58[@]}" "${REG58[@]}"
    ;;
  gate58)
    run s26-58-typecheck npm --prefix ui run typecheck
    run s26-58-lint npm --prefix ui run lint
    vitest_env_ok s26-58-vitest "${UNIT58[@]}" "${REG58[@]}"
    run s26-58-build npm --prefix ui run build
    run s26-58-harness-build harness_build
    electron_env_ok s26-58-e2e "${E2E58[@]}"
    ;;
  pregate)
    echo "== input identity"; git rev-parse HEAD; git status --porcelain | sha256sum
    sha256sum ui/package-lock.json mcp-server/package-lock.json; node --version; npm --prefix ui ls electron --depth=0 || true
    run s26-gate-py-types uv run pyright packages/
    run s26-gate-py-lint uv run ruff check packages/ tests/
    run s26-gate-typecheck npm --prefix ui run typecheck
    run s26-gate-lint npm --prefix ui run lint
    run s26-gate-mcp-types npm --prefix mcp-server run typecheck
    run s26-gate-task-contract uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task "$PLAN/task.md"
    # py-tests is authoritative in WINDOWS_GATE only: this container fails 61 Windows-bound tests
    # (C:/ fixture paths, NSIS/PowerShell packaging, framework tooling) with packages/ unchanged
    # (walkthrough H1-2; plan amendment A9).
    vitest_env_ok s26-gate-vitest
    run s26-gate-build npm --prefix ui run build
    run s26-gate-harness-build harness_build
    # The MCP suite asserts the built dist exists (AC-32.8, AC-38.8), so build first (A9).
    run s26-gate-mcp-build npm --prefix mcp-server run build
    run s26-gate-mcp-tests npm --prefix mcp-server run test
    run s26-gate-openapi uv run python tools/export_openapi.py --check openapi.committed.json
    run s26-gate-render uv run python tools/meu_status.py render --check
    electron_env_ok s26-gate-e2e
    for f in "${AUDIT_SRC[@]}"; do [ -f "$f" ] || fail "audited source missing: $f"; done
    if grep -nE 'TODO|FIXME|NotImplementedError|transition-all|bg-\[#' "${AUDIT_SRC[@]}"; then fail "source audit hits"; fi
    echo "PASS container pre-gate (authoritative gate: windows-gate)"
    ;;
  windows-gate-check)
    python3 - <<'PY' || exit 1
import json, subprocess, sys
p = "docs/execution/plans/2026-09-28-p11-capture-settings/windows-gate-result.json"
try:
    r = json.load(open(p, encoding="utf-8-sig"))
except OSError as err:
    sys.exit(f"FAIL: {p} unreadable: {err}")
if r.get("schema") != "s26-windows-gate.v1":
    sys.exit(f"FAIL: schema {r.get('schema')}")
if r.get("clean_tree") is not True:
    sys.exit("FAIL: Windows run was not on a clean tree")
order = ["npm-ci", "mcp-npm-ci", "py-types", "py-lint", "ui-types", "ui-lint", "mcp-types", "py-tests", "ui-tests",
         "ui-build", "ui-harness-build", "mcp-build", "mcp-tests", "openapi", "state-render", "ui-electron", "source-audit"]
got = [s.get("id") for s in r.get("stages", [])]
if got != order:
    sys.exit(f"FAIL: stages {got} != {order}")
bad = [s["id"] for s in r["stages"] if s.get("exit") != 0]
if bad:
    sys.exit(f"FAIL: Windows stages failed: {bad}")
v, e = r.get("vitest") or {}, r.get("e2e") or {}
# COUNT_FLOORS (amended 2026-09-29 to the Session 25 final gate): Vitest >= 631, Electron >= 103.
if v.get("failed") != 0 or (v.get("total") or 0) < 631:
    sys.exit(f"FAIL: vitest {v}")
if e.get("unexpected") != 0 or e.get("flaky") not in (0, None) or (e.get("expected") or 0) < 103:
    sys.exit(f"FAIL: e2e {e}")
tested = r.get("tested_commit", "")
code = subprocess.run(["git", "diff", "--quiet", tested, "HEAD", "--", "ui", "packages", "mcp-server"]).returncode
if code != 0:
    sys.exit(f"FAIL: code changed since Windows-tested commit {tested} (git diff exit {code})")
dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "--", "ui", "packages", "mcp-server"],
                       capture_output=True, text=True).stdout.strip()
if dirty:
    sys.exit(f"FAIL: uncommitted code changes after the Windows-tested commit:\n{dirty}")
print(f"PASS windows gate @ {tested}: vitest {v} e2e {e}")
PY
    ;;
  doc-tests)
    vitest_env_ok s26-doc-tests "${DOC_READING_TESTS[@]}" || exit 1
    # test_framework_adoption.py is Windows-bound (RTK, pwsh, P:/.agent registry); the container
    # cannot pass it. Here it must add no NEW failure versus 7613beb, the A11 commit that
    # WINDOWS_GATE attempt 2 ran at 91/91 with zero tolerance (plan amendments A10, A11).
    WT="$RD/wt-doc-base"; rm -rf "$WT"; git worktree add -q "$WT" 7613beb || fail "worktree"
    (cd "$WT" && "$OLDPWD/.venv/bin/python" -m pytest tests/tooling/test_framework_adoption.py -q --tb=no -p no:cacheprovider > "$RD/s26-doc-pytest-base.txt" 2>&1)
    .venv/bin/python -m pytest tests/tooling/test_framework_adoption.py -q --tb=no -p no:cacheprovider > "$RD/s26-doc-pytest.txt" 2>&1
    git worktree remove --force "$WT"
    python3 - "$RD/s26-doc-pytest-base.txt" "$RD/s26-doc-pytest.txt" <<'PY' || exit 1
import re, sys
def failed(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    if not re.search(r"\d+ (passed|failed)", text):
        sys.exit(f"FAIL: {path} has no pytest summary (collection/runner error)")
    return {line.split(" - ")[0] for line in text.splitlines() if line.startswith("FAILED ")}
base, head = failed(sys.argv[1]), failed(sys.argv[2])
new = sorted(head - base)
if new:
    sys.exit(f"FAIL: s26-doc-pytest new failures versus 7613beb: {new}")
print(f"PASS s26-doc-pytest: no new failures (container-bound baseline {len(base)}, head {len(head)})")
PY
    ;;
  ssot-review)
    for n in 57 58; do
      run "s26-meu-$n-rfr" uv run python tools/meu_status.py update "MEU-$n" ready_for_review --plan "$PLAN"
    done
    run s26-render uv run python tools/meu_status.py render
    run s26-render-check uv run python tools/meu_status.py render --check
    grep -qE '^\| 26 \| `p11-capture-settings` \| in review \| `docs/execution/plans/2026-09-28-p11-capture-settings/`' \
      .agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md || fail "grouping Session 26 not in review"
    grep -q 'ready_for_review' .agent/context/current-focus.md || fail "focus does not record Session 26 ready_for_review"
    bash "$0" doc-tests || exit 1
    echo "PASS SSOT review state"
    ;;
  review-check)
    python3 - "$2" "$3" "$4" <<'PY' || exit 1
import re, sys
path, mode, cap = sys.argv[1], sys.argv[2], int(sys.argv[3])
t = open(path, encoding="utf-8").read()
fm = dict(re.findall(r'^(\w+):\s*"?([^"\n]*)"?$', t.split("---")[1], re.M))
target = "docs/execution/plans/2026-09-28-p11-capture-settings/implementation-plan.md"
if fm.get("target_plan") != target: sys.exit(f"FAIL: target {fm.get('target_plan')}")
if fm.get("review_mode") != mode: sys.exit(f"FAIL: mode {fm.get('review_mode')}")
if int(fm.get("round", "0")) > cap: sys.exit(f"FAIL: round {fm.get('round')} over cap {cap}")
if fm.get("verdict") != "approved": sys.exit(f"FAIL: verdict {fm.get('verdict')}")
if "fable" not in fm.get("agent", "").lower(): sys.exit(f"FAIL: agent {fm.get('agent')} is not the authorized route")
print(f"PASS {mode} review approved round {fm['round']} by {fm['agent']}")
PY
    ;;
  task-state)
    uv run python - "$PLAN/task.md" <<'PY' || exit 1
import re, sys
rows = [l for l in open(sys.argv[1], encoding="utf-8") if re.match(r"^\| [0-9]+ \|", l)]
if len(rows) != 8:
    sys.exit(f"FAIL: expected 8 implementation rows, got {len(rows)}")
for l in rows:
    s = l.rstrip().rstrip("|").split("|")[-1].strip().strip("`")
    if s == "[x]" or (s == "[B]" and "follow-up" in l and "B-" in l):
        continue
    sys.exit(f"FAIL: unfinished row: {l[:60]}")
print("PASS implementation rows 1-8")
PY
    ;;
  post-review-state)
    for n in 57 58; do
      run "s26-meu-$n-approved" uv run python tools/meu_status.py update "MEU-$n" approved --plan "$PLAN"
    done
    run s26-approved-render uv run python tools/meu_status.py render
    run s26-approved-check uv run python tools/meu_status.py render --check
    bash "$0" post-review-assert
    ;;
  post-review-assert)
    uv run python "$PC" meu-state --expect MEU-50..58=approved --plan "$PLAN" || fail "PHASE11 MEU state"
    uv run python "$PC" post-review --plan "$PLAN" || fail "POST_REVIEW_STATE"
    bash "$0" doc-tests || exit 1
    echo "PASS POST_REVIEW_STATE, DOC_READING_TESTS and PHASE11_EXIT_PREDICATE (with windows-gate-check)"
    ;;
  *) echo "USAGE: validate-task.sh <check>"; exit 2 ;;
esac
