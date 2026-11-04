#!/usr/bin/env bash
# Exact validation procedures for 2026-09-28-p11-transcript-tts.
# Kept in one script so task.md cells stay lintable (tools/lint_task_contract.py).
# Runs from the repo root; every procedure writes its raw tool output under
# $RECEIPTS_DIR and exits nonzero on the first failed check. Executable only
# during the authorized execution session: it runs product tests/builds.
set -uo pipefail

PLAN=docs/execution/plans/2026-09-28-p11-transcript-tts
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

UNIT55=(tests/unit/queue-card-slots.test.tsx tests/unit/transcript-page.behavior.test.ts)
# REG55 covers every suite with a source pin on a file MEU-55 modifies (plan SOURCE_PINS).
REG55=(tests/unit/queue-header-row.test.tsx tests/unit/queue-card.test.ts tests/unit/queue-list.test.ts
       tests/unit/transcript-page.test.ts tests/unit/layout-primitives.test.ts tests/unit/queue-primitives.test.ts
       tests/unit/bulk-action-bar.test.ts tests/unit/convert-page.test.ts tests/unit/downloader-page.test.ts
       tests/unit/help-card.test.ts tests/unit/queue-canon.test.ts)
UNIT56=(tests/unit/tts-page.behavior.test.ts)
REG56=(tests/unit/tts-page.test.ts tests/unit/layout-primitives.test.ts tests/unit/queue-primitives.test.ts
       tests/unit/help-card.test.ts tests/unit/queue-canon.test.ts)
AMENDABLE=(ui/tests/unit/layout-primitives.test.ts ui/tests/unit/queue-primitives.test.ts
           ui/tests/e2e/transcript-queue.test.ts ui/tests/e2e/tts-generate.test.ts ui/tests/e2e/test-ids.ts)
FROZEN=(ui/tests/unit/queue-header-row.test.tsx ui/tests/unit/transcript-page.test.ts ui/tests/unit/tts-page.test.ts)

case "$CHECK" in
  prereq)
    [ ! -e graphify-out ] && [ ! -e graphify-out-research ] || fail "graph present: re-run context-tool gate with the human"
    python3 - <<'PY' || exit 1
import sys, yaml
d = yaml.safe_load(open(".agent/context/meu-status.yaml", encoding="utf-8"))
st = {m["id"]: m["status"] for m in d["meus"]}
need = {"MEU-49": "approved", "MEU-51": "approved", "MEU-52": "approved",
        "MEU-55": "pending", "MEU-56": "pending"}
bad = {k: st.get(k) for k, v in need.items() if st.get(k) != v}
if bad:
    sys.exit(f"FAIL: prerequisite SSOT mismatch {bad}")
print("PASS SSOT prerequisites", need)
PY
    [ -d ui/node_modules ] || fail "ui/node_modules missing: run 'npm --prefix ui ci' first"
    node --version; npm --prefix ui ls electron --depth=0 || true
    # Electron launchability decides whether an E2E failure can ever be [B]; probe it now.
    [ -x ui/node_modules/electron/dist/electron ] || fail "Electron binary missing (npm ci postinstall?)"
    unset ELECTRON_RUN_AS_NODE; sandbox_env
    xvfb-run -a ui/node_modules/electron/dist/electron --version || fail "Electron cannot start under xvfb: record exact error as B-evidence"
    echo "PASS prereq"
    ;;
  electron-setup)
    # ELECTRON_SETUP: npm's postinstall download dies through the container proxy (undici);
    # fetch the same release asset with curl, verify it against the package's own
    # checksums.json, and unpack it exactly as electron/install.js does.
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
  static)
    run s25-static-typecheck npm --prefix ui run typecheck
    run s25-static-lint npm --prefix ui run lint
    ;;
  handoff-census)
    python3 - <<'PY' || exit 1
import sys
base = ".agent/context/handoffs/2026-09-28-p11-transcript-tts-{}-handoff.md"
need = {"MEU-55": ["AC-55.1", "AC-55.7", "TA-3", "TA-5", "evidence.v1", "CACHE BOUNDARY"],
        "MEU-56": ["AC-56.1", "AC-56.6", "TA-6", "TA-7", "evidence.v1", "CACHE BOUNDARY"]}
for meu, markers in need.items():
    try:
        text = open(base.format(meu), encoding="utf-8").read()
    except OSError as err:
        sys.exit(f"FAIL: {meu} handoff unreadable: {err}")
    missing = [m for m in markers if m not in text]
    if missing:
        sys.exit(f"FAIL: {meu} handoff missing {missing}")
print("PASS handoff census")
PY
    ;;
  reflection)
    r=docs/execution/reflections/2026-09-28-p11-transcript-tts-reflection.md
    [ -f "$r" ] || fail "reflection missing"
    for m in '^## Next Session Design Rules' '^## Instruction Coverage' '^sections:' '^loaded:'; do
      grep -qE "$m" "$r" || fail "reflection missing marker $m"
    done
    echo "PASS reflection markers"
    ;;
  red-55)  vitest_red AC-55 "$RD/s25-55-red.json" "${UNIT55[@]}" ;;
  e2e-red-55) electron_red AC-55 "$RD/s25-55-e2e-red.json" tests/e2e/transcript-queue.test.ts ;;
  green-55) vitest_env_ok s25-55-green-vitest "${UNIT55[@]}" "${REG55[@]}" ;;
  e2e-55)
    run s25-55-build npm --prefix ui run build
    run s25-55-e2e electron tests/e2e/transcript-queue.test.ts tests/e2e/download-queue.test.ts tests/e2e/convert-queue.test.ts
    ;;
  red-56)  vitest_red AC-56 "$RD/s25-56-red.json" "${UNIT56[@]}" ;;
  e2e-red-56) electron_red AC-56 "$RD/s25-56-e2e-red.json" tests/e2e/tts-generate.test.ts ;;
  green-56) vitest_env_ok s25-56-green-vitest "${UNIT56[@]}" "${REG56[@]}" ;;
  e2e-56)
    run s25-56-build npm --prefix ui run build
    run s25-56-e2e electron tests/e2e/tts-generate.test.ts
    ;;
  amendments)
    # Compare against the pre-session baseline, not HEAD: once this plan's own new
    # test files are committed they must not start counting as pre-existing.
    BASE=0f51036
    changed=$(git diff --name-only "$BASE" -- ui/tests; git ls-files --others --exclude-standard -- ui/tests)
    echo "$changed"
    for f in "${FROZEN[@]}"; do
      echo "$changed" | grep -qx "$f" && fail "frozen test modified: $f"
    done
    while IFS= read -r f; do
      [ -z "$f" ] && continue
      git cat-file -e "$BASE:$f" 2>/dev/null || continue   # files absent at baseline are this plan's own tests
      printf '%s\n' "${AMENDABLE[@]}" | grep -qx "$f" || fail "pre-existing test outside TEST_AMENDMENTS modified: $f"
    done <<< "$changed"
    if grep -rnE '\b(it|test|describe)\.(skip|only|todo)\b' ui/tests; then fail "skip/only/todo present"; fi
    echo "PASS amendment guard"
    ;;
  pregate)
    echo "== input identity"; git rev-parse HEAD; git status --porcelain | sha256sum
    sha256sum ui/package-lock.json; node --version; npm --prefix ui ls electron --depth=0 || true
    echo "ELECTRON_RUN_AS_NODE=${ELECTRON_RUN_AS_NODE:-<unset>}"
    run s25-gate-typecheck npm --prefix ui run typecheck
    run s25-gate-lint npm --prefix ui run lint
    vitest_env_ok s25-gate-vitest
    run s25-gate-build npm --prefix ui run build
    run s25-gate-harness-build harness_build
    electron_env_ok s25-gate-e2e
    PAGES=(ui/src/renderer/src/features/transcript/TranscriptPage.tsx ui/src/renderer/src/features/tts/TTSPage.tsx)
    SRC=("${PAGES[@]}" ui/src/renderer/src/features/transcript/transcript-card.ts
         ui/src/renderer/src/features/transcript/TranscriptToolbar.tsx ui/src/renderer/src/features/tts/tts-run-bar.ts
         ui/src/renderer/src/components/queue/QueueCard.tsx ui/src/renderer/src/components/queue/QueueCardMenu.tsx
         ui/src/renderer/src/components/queue/QueueList.tsx ui/src/renderer/src/components/queue/QueueHeaderRow.tsx
         ui/src/renderer/src/components/ui/ProgressBar.tsx)
    for f in "${SRC[@]}"; do [ -f "$f" ] || fail "audited source missing: $f"; done
    if grep -nE 'TODO|FIXME|NotImplementedError|transition-all|bg-\[#' "${SRC[@]}"; then fail "source audit hits"; fi
    if grep -nE "width:|style=\{\{\s*width" "${PAGES[@]}"; then fail "inline width style in page (MEU-48 AC)"; fi
    echo "PASS container pre-gate (authoritative gate: windows-gate)"
    ;;
  windows-gate-check)
    python3 - <<'PY' || exit 1
import json, subprocess, sys
p = "docs/execution/plans/2026-09-28-p11-transcript-tts/windows-gate-result.json"
try:
    r = json.load(open(p, encoding="utf-8-sig"))
except OSError as err:
    sys.exit(f"FAIL: {p} unreadable: {err}")
if r.get("schema") != "s25-windows-gate.v1":
    sys.exit(f"FAIL: schema {r.get('schema')}")
if r.get("clean_tree") is not True:
    sys.exit("FAIL: Windows run was not on a clean tree")
order = ["npm-ci", "ui-types", "ui-lint", "ui-tests", "ui-build", "ui-harness-build", "ui-electron", "source-audit", "width-audit"]
got = [s.get("id") for s in r.get("stages", [])]
if got != order:
    sys.exit(f"FAIL: stages {got} != {order}")
bad = [s["id"] for s in r["stages"] if s.get("exit") != 0]
if bad:
    sys.exit(f"FAIL: Windows stages failed: {bad}")
if r.get("vitest", {}).get("failed") != 0 or r.get("e2e", {}).get("unexpected") != 0:
    sys.exit(f"FAIL: counts vitest={r.get('vitest')} e2e={r.get('e2e')}")
tested = r.get("tested_commit", "")
code = subprocess.run(["git", "diff", "--quiet", tested, "HEAD", "--", "ui", "packages", "mcp-server"]).returncode
if code != 0:
    sys.exit(f"FAIL: code changed since Windows-tested commit {tested} (git diff exit {code})")
dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "--", "ui", "packages", "mcp-server"],
                       capture_output=True, text=True).stdout.strip()
if dirty:
    sys.exit(f"FAIL: uncommitted code changes after the Windows-tested commit:\n{dirty}")
print(f"PASS windows gate @ {tested}: vitest {r['vitest']} e2e {r['e2e']}")
PY
    ;;
  task-state)
    python3 - "$PLAN/task.md" <<'PY' || exit 1
import re, sys
rows = [l for l in open(sys.argv[1], encoding="utf-8") if re.match(r"^\| [0-9]+ \|", l)]
if len(rows) != 9:
    sys.exit(f"FAIL: expected 9 implementation rows, got {len(rows)}")
for l in rows:
    s = l.rstrip().rstrip("|").split("|")[-1].strip().strip("`")
    if s == "[x]" or (s == "[B]" and "follow-up" in l and "B-" in l):
        continue
    sys.exit(f"FAIL: unfinished row: {l[:60]}")
print("PASS implementation rows 1-9")
PY
    ;;
  ssot-review)
    for n in 55 56; do
      run "s25-meu-$n-rfr" uv run python tools/meu_status.py update "MEU-$n" ready_for_review --plan "$PLAN"
    done
    run s25-render uv run python tools/meu_status.py render
    run s25-render-check uv run python tools/meu_status.py render --check
    grep -qE '^\| 25 \| `p11-transcript-tts` \| in review \| `docs/execution/plans/2026-09-28-p11-transcript-tts/`' \
      .agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md || fail "grouping Session 25 not in review"
    grep -q 'ready_for_review' .agent/context/current-focus.md || fail "focus does not record Session 25 ready_for_review"
    grep -q 'Next: Phase 11 page layout (MEU-55)' docs/BUILD_PLAN.md || fail "hub Next changed before approval"
    echo "PASS SSOT review state"
    ;;
  review-check)
    python3 - "$2" "$3" "$4" <<'PY' || exit 1
import re, sys
path, mode, cap = sys.argv[1], sys.argv[2], int(sys.argv[3])
t = open(path, encoding="utf-8").read()
fm = dict(re.findall(r'^(\w+):\s*"?([^"\n]*)"?$', t.split("---")[1], re.M))
target = "docs/execution/plans/2026-09-28-p11-transcript-tts/implementation-plan.md"
if fm.get("target_plan") != target: sys.exit(f"FAIL: target {fm.get('target_plan')}")
if fm.get("review_mode") != mode: sys.exit(f"FAIL: mode {fm.get('review_mode')}")
if int(fm.get("round", "0")) > cap: sys.exit(f"FAIL: round {fm.get('round')} over cap {cap}")
if fm.get("verdict") != "approved": sys.exit(f"FAIL: verdict {fm.get('verdict')}")
if "fable" not in fm.get("agent", "").lower(): sys.exit(f"FAIL: agent {fm.get('agent')} is not the authorized route")
print(f"PASS {mode} review approved round {fm['round']} by {fm['agent']}")
PY
    ;;
  post-review-state)
    for n in 55 56; do
      run "s25-meu-$n-approved" uv run python tools/meu_status.py update "MEU-$n" approved --plan "$PLAN"
    done
    run s25-approved-render uv run python tools/meu_status.py render
    run s25-approved-check uv run python tools/meu_status.py render --check
    "$0" post-review-assert
    ;;
  post-review-assert)
    python3 - <<'PY' || exit 1
import sys, yaml
plan = "docs/execution/plans/2026-09-28-p11-transcript-tts"
d = yaml.safe_load(open(".agent/context/meu-status.yaml", encoding="utf-8"))
for m in d["meus"]:
    if m["id"] in ("MEU-55", "MEU-56"):
        if m["status"] != "approved" or plan not in str(m.get("execution_plan", "")):
            sys.exit(f"FAIL: {m['id']} not approved/bound: {m['status']} {m.get('execution_plan')}")
print("PASS MEU-55/56 approved and bound")
PY
    grep -qE '^\| 25 \| `p11-transcript-tts` \| approved \| `docs/execution/plans/2026-09-28-p11-transcript-tts/`' \
      .agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md || fail "grouping Session 25 not approved"
    grep -q 'Next: Phase 11 page layout (MEU-57)' docs/BUILD_PLAN.md || fail "hub Next not advanced to MEU-57"
    grep -q 'Session 26' .agent/context/current-focus.md || fail "focus not advanced to Session 26"
    [ "$(grep -cE '^\| [0-9-]+ \| p11-transcript-tts \|' docs/execution/metrics.md)" -eq 1 ] || fail "missing/duplicate metrics row"
    echo "PASS POST_REVIEW_STATE and metrics"
    ;;
  final)
    python3 - "$PLAN/task.md" <<'PY' || exit 1
import re, sys
rows = [l for l in open(sys.argv[1], encoding="utf-8") if re.match(r"^\| (?:[0-9]+|H[12]-[0-9]+) \|", l)]
if len(rows) != 19:
    sys.exit(f"FAIL: expected 19 rows, got {len(rows)}")
for l in rows:
    s = l.rstrip().rstrip("|").split("|")[-1].strip().strip("`")
    if s == "[x]" or (s == "[B]" and "follow-up" in l and "B-" in l):
        continue
    sys.exit(f"FAIL: unfinished row: {l[:60]}")
print("PASS 19 rows")
PY
    "$0" review-check .agent/context/handoffs/2026-09-28-p11-transcript-tts-implementation-critical-review.md execution 6 || exit 1
    "$0" post-review-assert || exit 1
    echo "PASS final completion gate"
    ;;
  *) echo "USAGE: validate-task.sh <check>"; exit 2 ;;
esac
