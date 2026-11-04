#!/usr/bin/env bash
# Exact validation procedures for 2026-09-30-tts-repair (Session 27). Helpers are adapted from
# Session 26 (docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh).
# Kept in one script so task.md cells stay lintable (tools/lint_task_contract.py).
# Runs from the repo root. Every procedure writes its raw tool output under $RECEIPTS_DIR and
# exits nonzero on the first failed check. It is executable only during the authorized
# execution session, because it runs product tests and builds.
# Stage ids match validate-task.ps1 exactly; windows-gate-check asserts that order.
set -uo pipefail

PLAN=docs/execution/plans/2026-09-30-tts-repair
RD="${RECEIPTS_DIR:-/tmp/av-kit}"
mkdir -p "$RD"
CHECK="${1:-}"

fail() { echo "FAIL: $*"; exit 1; }

# require_failed_title <json> <title-token> <expect-needle>: the named spec itself must have failed
# on an expect() whose message contains <expect-needle> (Review R1 F1: a sibling spec's failure
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
    sys.exit(f"FAIL: no spec titled {title} failed on an expect containing {needle!r} (Stop condition S8 if the layout does not overflow)")
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
  electron "$@" --repeat-each=20 --output="$RD/s27-repeat-$id" --reporter=json --outputFile="$RD/s27-repeat-$id.json" > "$RD/s27-repeat-$id.txt" 2>&1
  local rc=$?
  [ "$rc" -eq 0 ] || fail "repeat $id exit $rc (receipt $RD/s27-repeat-$id.txt)"
  echo "PASS repeat-each=20 $id"
}

# pytest_env_ok <receipt-id>: full Python suite; the failed set must be a subset of the
# baseline failed set captured by `baseline` before any product edit (ENV_BOUND_PY).
pytest_env_ok() {
  local id="$1"
  [ -f "$RD/s27-baseline-pytest.txt" ] || fail "baseline pytest receipt missing: run 'baseline' first"
  uv run pytest tests/ -q --tb=no -p no:cacheprovider -rfE > "$RD/$id.txt" 2>&1
  python3 - "$RD/s27-baseline-pytest.txt" "$RD/$id.txt" <<'PY' || exit 1
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
  [ -f "$RD/s27-baseline-pytest.txt" ] || fail "baseline pytest receipt missing: run 'baseline' first"
  uv run pytest "$@" -q --tb=short -p no:cacheprovider -rfE > "$RD/$id.txt" 2>&1
  python3 - "$RD/s27-baseline-pytest.txt" "$RD/$id.txt" "$id" <<'PY' || exit 1
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

# pytest_red <ac-token> <files...>: assertion-level Red. A failure or collection error is tolerated
# only when it is an ImportError/ModuleNotFoundError naming a not-yet-written MEU-62 symbol
# (MEU62_SYMBOLS); at least one decisive assertion failure in a test named <ac-token> is required.
MEU62_SYMBOLS="avkit_infra.tts.assets avkit_infra.model_manager.vocab TtsAsset AssetState required_tts_assets TtsAssetPort KOKORO_LANG_CODES SPACY_LANG_CODES TtsAssetOut resolve_vocab_path"
pytest_red() {
  local tag="$1"; shift
  local xml="$RD/s27-${tag}-red-pytest.xml"
  rm -f "$xml"
  uv run pytest "$@" -q --tb=short -p no:cacheprovider --junitxml="$xml" > "$RD/s27-${tag}-red-pytest.txt" 2>&1
  local rc=$?
  [ "$rc" -ne 0 ] || fail "$tag pytest Red expected a failing run, got exit 0"
  [ -f "$xml" ] || fail "$tag pytest Red junit XML missing (exit $rc)"
  python3 - "$tag" "$xml" "$MEU62_SYMBOLS" <<'PY' || exit 1
import re, sys, xml.etree.ElementTree as ET
tag, path, symbols = sys.argv[1], sys.argv[2], sys.argv[3].split()
decisive, tolerated, bad = [], [], []
for case in ET.parse(path).getroot().iter("testcase"):
    name = f"{case.get('classname')}::{case.get('name')}"
    for kind in ("failure", "error"):
        for el in case.findall(kind):
            msg = (el.get("message") or "") + (el.text or "")
            # "cannot import name 'x' from 'pkg.mod'" names the symbol as pkg.mod.x
            msg += " " + " ".join(f"{m}.{n}" for n, m in re.findall(r"cannot import name '(\w+)' from '([\w.]+)'", msg))
            if ("ModuleNotFoundError" in msg or "ImportError" in msg) and any(s in msg for s in symbols):
                tolerated.append(name)
            elif kind == "failure" and tag.lower() in name.lower() and (
                    "AssertionError" in msg or "assert " in msg or "DID NOT RAISE" in msg):
                decisive.append(name)
            else:
                bad.append(f"{kind}: {name}: {msg[:160]}")
if bad:
    sys.exit(f"FAIL: {tag} non-assertion failures/errors (setup/import?): {bad[:5]}")
if not decisive:
    sys.exit(f"FAIL: {tag} no failing {tag} assertion (tolerated missing-symbol: {len(tolerated)})")
print(f"PASS {tag} pytest RED: {len(decisive)} decisive, {len(tolerated)} missing-symbol")
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
PY62=(tests/unit/test_services.py tests/integration/test_tts_models.py tests/integration/test_tts_assets.py
      tests/e2e/test_api_tts_models.py tests/e2e/test_api_health_settings.py tests/integration/test_api_wiring.py)
PYREG62=(tests/e2e/test_api_openapi.py tests/unit/test_domain.py)
MCP62=(tests/models-assets.test.ts tests/tools-parity.test.ts tests/action-index.test.ts)
UNIT62=(tests/unit/settings-page.test.ts)
E2E62=(tests/e2e/settings.test.ts)
UNIT63=(tests/unit/tts-page.behavior.test.ts tests/unit/tts-page.test.ts tests/unit/tts-run-bar.test.ts)
UNIT64=(tests/unit/tts-page.behavior.test.ts tests/unit/tts-page.test.ts tests/unit/voice-combobox.test.tsx)
REGTTS=(tests/unit/layout-canon.test.ts tests/unit/e2e-wiring.test.ts tests/unit/gui-actions-audit.test.ts
        tests/unit/help-card.test.ts tests/unit/layout-primitives.test.ts tests/unit/settings-rail.test.tsx)
E2ETTS=(tests/e2e/tts-generate.test.ts)
AUDIT_SRC=(packages/infrastructure/src/avkit_infra/tts/assets.py packages/infrastructure/src/avkit_infra/tts/adapter.py
           packages/infrastructure/src/avkit_infra/model_manager/manager.py packages/core/src/avkit_core/services/models.py
           packages/core/src/avkit_core/services/tts.py packages/core/src/avkit_core/services/health.py
           ui/src/renderer/src/features/tts/TTSPage.tsx ui/src/renderer/src/features/tts/VoiceCombobox.tsx
           ui/src/renderer/src/features/tts/tts-controls.ts ui/src/renderer/src/features/tts/tts-run-bar.ts
           ui/src/renderer/src/features/settings/SettingsPage.tsx mcp-server/src/toolsets/models.ts)
PREFIX_AUDIT='TODO|FIXME|NotImplementedError|transition-all|bg-\[#|console\.log\(|except Exception:\s*pass|# type: ignore'

case "$CHECK" in
  prereq)
    [ ! -e graphify-out ] && [ ! -e graphify-out-research ] || fail "graph present: re-run the context-tool gate with the human (S1)"
    uv run python - <<'PY' || fail "MEU state (S1)"
import sys, yaml
rows = {r["id"]: r.get("status") for r in yaml.safe_load(open(".agent/context/meu-status.yaml", encoding="utf-8"))["meus"]}
want = {"MEU-16": "approved", "MEU-22": "approved", "MEU-56": "approved",
        "MEU-62": "pending", "MEU-63": "pending", "MEU-64": "pending"}
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
    # Pre-edit baseline: must run before any product edit. It records HEAD and the env-bound sets.
    [ -z "$(git status --porcelain -- ui packages mcp-server tests)" ] || fail "product tree already edited; baseline must precede row 3"
    git rev-parse HEAD > "$PLAN/baseline.sha"
    uv run pytest tests/ -q --tb=no -p no:cacheprovider -rfE > "$RD/s27-baseline-pytest.txt" 2>&1
    grep -qE "[0-9]+ (passed|failed)" "$RD/s27-baseline-pytest.txt" || fail "baseline pytest produced no summary"
    grep -E "^[0-9]+ (passed|failed)|passed|failed" "$RD/s27-baseline-pytest.txt" | tail -n 1
    vitest_env_ok s27-baseline-vitest
    run s27-baseline-build npm --prefix ui run build
    run s27-baseline-harness-build harness_build
    electron_env_ok s27-baseline-e2e
    echo "PASS baseline at $(cat "$PLAN/baseline.sha")"
    ;;
  repro-check)
    python3 - "$PLAN/walkthrough.md" <<'PY' || exit 1
import re, sys
try:
    t = open(sys.argv[1], encoding="utf-8").read()
except OSError:
    sys.exit("FAIL: walkthrough.md missing")
sec = re.split(r"^## LOCAL_REPRO[ \t]*$", t, maxsplit=1, flags=re.M)  # the heading line, not a prose mention
if len(sec) < 2:
    sys.exit("FAIL: walkthrough.md has no ## LOCAL_REPRO section")
body = sec[1].split("\n## ", 1)[0]
for r in ("R1", "R2", "R3", "R4", "R5"):
    if not re.search(rf"^\|?\s*{r}\b.*\b(reproduced|not-reproduced|different)\b", body, re.M):
        sys.exit(f"FAIL: {r} has no recorded result")
if "USER_EXPLICIT" not in body and "relayed" not in body:
    sys.exit("FAIL: LOCAL_REPRO results carry no provenance (USER_EXPLICIT or relayed quote)")
print("PASS LOCAL_REPRO recorded for R1-R5")
PY
    ;;
  census)
    rg -n -e preview-raw -e preview-cleaned -e preview-cleanup-btn -e language-select -e voice-grid -e voice-card \
      -e model-manage-toggle -e model-row -e model-get-btn -e model-load-btn -e unload-btn -e device-select \
      -e loaded-model -e download-progress -e error-banner -e resolveRunBarSlot -e dependencies-section \
      -e "'yt-dlp'" -e FFmpeg ui/tests > "$RD/s27-census.txt" 2>&1
    rc=$?; [ "$rc" -le 1 ] || fail "census rg (ui) exit $rc"
    rg -n -e DependenciesOut -e yt_dlp -e ModelDownloadRuntimeOut -e download-runtime -e ModelDownloadIn \
      -e "ROUTE_INDEX" -e "tts.generate" -e "_ring" -e MODEL_DOWNLOAD_RUNTIME_FIELDS -e 'ModelDownloadRuntime\b' \
      -e DependencyHealth -e 'HealthService\(' -e 'TTSService\(' -e 'ModelService\(' tests >> "$RD/s27-census.txt" 2>&1
    rc=$?; [ "$rc" -le 1 ] || fail "census rg (py) exit $rc"
    rg -n -e avkit_models -e download_runtime -e '"download"' -e ACTION_INDEX -e 'toHaveLength\(67\)' mcp-server/tests >> "$RD/s27-census.txt" 2>&1
    rc=$?; [ "$rc" -le 1 ] || fail "census rg (mcp) exit $rc"
    wc -l < "$RD/s27-census.txt"; echo "PASS census written: $RD/s27-census.txt (disposition every hit in walkthrough.md §Census)"
    ;;
  red62)
    pytest_red ac_62 "${PY62[@]}" || exit 1
    (cd mcp-server && npx vitest run tests/models-assets.test.ts --reporter=json --outputFile="$RD/s27-62-red-mcp.json") > "$RD/s27-62-red-mcp.txt" 2>&1
    rc=$?; [ "$rc" -ne 0 ] || fail "AC-62.13 MCP Red expected a failing run"
    python3 - "$RD/s27-62-red-mcp.json" <<'PY' || exit 1
import json, sys
j = json.load(open(sys.argv[1], encoding="utf-8"))
bad = [s["name"] for s in j.get("testResults", []) if s.get("message")]
if bad: sys.exit(f"FAIL: AC-62.13 MCP collection error {bad}")
d = [a for s in j["testResults"] for a in s["assertionResults"] if a["status"] == "failed" and "AC-62.13" in a["fullName"]]
if not d: sys.exit("FAIL: AC-62.13 no failing assertion")
print(f"PASS AC-62.13 MCP RED: {len(d)}")
PY
    vitest_red AC-62.15 "$RD/s27-62-red-vitest.json" - "${UNIT62[@]}" || exit 1
    electron_red AC-62.15 "$RD/s27-62-red-e2e.json" "${E2E62[@]}" || exit 1
    ;;
  green62-py)
    pytest_paths_ok s27-62-green-pytest "${PY62[@]}" "${PYREG62[@]}" || exit 1
    run s27-62-green-pyright uv run pyright packages/
    ;;
  green62)
    pytest_paths_ok s27-62-green-pytest-all "${PY62[@]}" "${PYREG62[@]}" || exit 1
    run s27-62-mcp-typecheck npm --prefix mcp-server run typecheck
    run s27-62-mcp-build npm --prefix mcp-server run build
    run s27-62-mcp-test npm --prefix mcp-server run test
    vitest_env_ok s27-62-green-vitest "${UNIT62[@]}" "${REGTTS[@]}"
    run s27-openapi-final uv run python tools/export_openapi.py --check openapi.committed.json
    ;;
  gate62)
    run s27-62-pyright uv run pyright packages/
    run s27-62-ruff uv run ruff check packages/ tests/
    pytest_paths_ok s27-62-pytest "${PY62[@]}" "${PYREG62[@]}" || exit 1
    run s27-62-mcp-typecheck-g npm --prefix mcp-server run typecheck
    run s27-62-mcp-build-g npm --prefix mcp-server run build
    run s27-62-mcp-test-g npm --prefix mcp-server run test
    run s27-62-typecheck npm --prefix ui run typecheck
    run s27-62-lint npm --prefix ui run lint
    vitest_env_ok s27-62-vitest "${UNIT62[@]}" "${REGTTS[@]}"
    run s27-62-openapi uv run python tools/export_openapi.py --check openapi.committed.json
    run s27-62-build npm --prefix ui run build
    electron_env_ok s27-62-e2e "${E2E62[@]}"
    electron_repeat 62-settings "${E2E62[@]}"
    ;;
  red63)
    vitest_red AC-63 "$RD/s27-63-red-vitest.json" tests/unit/tts-run-bar.test.ts "${UNIT63[@]}" || exit 1
    electron_red AC-63 "$RD/s27-63-red-e2e.json" "${E2ETTS[@]}" || exit 1
    ;;
  green63)
    vitest_env_ok s27-63-green "${UNIT63[@]}" "${REGTTS[@]}"
    ;;
  gate63)
    run s27-63-typecheck npm --prefix ui run typecheck
    run s27-63-lint npm --prefix ui run lint
    vitest_env_ok s27-63-vitest "${UNIT63[@]}" "${REGTTS[@]}"
    run s27-63-build npm --prefix ui run build
    electron_env_ok s27-63-e2e "${E2ETTS[@]}"
    electron_repeat 63-tts "${E2ETTS[@]}"
    ;;
  red64)
    vitest_red AC-64 "$RD/s27-64-red-vitest.json" tests/unit/voice-combobox.test.tsx "${UNIT64[@]}" || exit 1
    uv run pytest tests/unit/test_tts_voice_fixture.py -q -p no:cacheprovider > "$RD/s27-64-voice-fixture.txt" 2>&1 \
      || fail "VOICE_CATALOG_FIXTURE parity (write the fixture before the Red run)"
    electron_red AC-64 "$RD/s27-64-red-e2e.json" "${E2ETTS[@]}" || exit 1
    require_failed_title "$RD/s27-64-red-e2e.json" AC-64.6 toBeLessThanOrEqual || exit 1
    ;;
  green64)
    vitest_env_ok s27-64-green "${UNIT64[@]}" "${REGTTS[@]}"
    ;;
  gate64)
    run s27-64-typecheck npm --prefix ui run typecheck
    run s27-64-lint npm --prefix ui run lint
    vitest_env_ok s27-64-vitest "${UNIT64[@]}" tests/unit/tts-run-bar.test.ts "${REGTTS[@]}"
    run s27-64-build npm --prefix ui run build
    electron_env_ok s27-64-e2e "${E2ETTS[@]}"
    electron_repeat 64-tts "${E2ETTS[@]}"
    ;;
  hub)
    python3 - <<'PY' || exit 1
import re, sys
b03 = open("docs/build-plan/03-service-layer.md", encoding="utf-8").read()
sec = b03.split("## TTS runtime assets (residual)", 1)[1].split("\n## ", 1)[0]
need03 = ["D-8", "D-9", "D-10", "D-11", "D-12", "D-13", "D-14", "{asset}", "resolve_vocab_path", "any variant"]
miss = [n for n in need03 if n not in sec]
if miss: sys.exit(f"FAIL: 03 §TTS runtime assets lacks {miss}")
if "first PyTorch-variant load" in sec: sys.exit("FAIL: 03 still says 'first PyTorch-variant load' (D-10)")
b11 = open("docs/build-plan/11-page-layout.md", encoding="utf-8").read()
mm = b11.split("### TTS model manager (residual)", 1)[1].split("### TTS text panel", 1)[0]
tp = b11.split("### TTS text panel (residual)", 1)[1].split("### Settings section emphasis", 1)[0]
if "`get-btn`" in mm or "`model-get-btn`" not in mm: sys.exit("FAIL: 11 §TTS model manager test ids not the registry names (D-15)")
for name, sec in (("model manager", mm), ("text panel", tp)):
    if "2026-09-30-tts-repair/implementation-plan.md" not in sec: sys.exit(f"FAIL: 11 §TTS {name} lacks the migration pointer")
b07 = open("docs/build-plan/07-distribution.md", encoding="utf-8").read()
if "github.com/explosion" not in b07 or "TTS-PACKAGED-RUNTIME-EXCLUDED" not in b07:
    sys.exit("FAIL: 07-distribution lacks the spaCy wheel host or the packaged-runtime note")
ki = open(".agent/context/known-issues.yaml", encoding="utf-8").read()
for i in ("TTS-PACKAGED-RUNTIME-EXCLUDED", "TTS-VOICE-PACK-LAZY-FETCH", "TTS-NON-ENGLISH-G2P-DEPS"):
    if f"id: {i}" not in ki: sys.exit(f"FAIL: known issue {i} not filed")
print("PASS hub reconciliation + new issues")
PY
    run s27-issues-render-check uv run python tools/issue_triage.py render --check
    run s27-hub-render-check uv run python tools/meu_status.py render --check
    # The mockup-inventory TT rows stay untouched (AC-50.4 lock); prove the doc-reading suites still pass.
    vitest_env_ok s27-hub-doc-tests tests/unit/layout-canon.test.ts tests/unit/queue-canon.test.ts tests/unit/gui-actions-audit.test.ts
    ;;
  task-state)
    python3 - "$PLAN/task.md" <<'PY' || exit 1
import re, sys
rows = [l for l in open(sys.argv[1], encoding="utf-8") if re.match(r"^\| [0-9]+ \|", l)]
if len(rows) != 14:
    sys.exit(f"FAIL: expected 14 implementation rows (0-13), got {len(rows)}")
for l in rows:
    s = l.rstrip().rstrip("|").split("|")[-1].strip().strip("`")
    if s == "[x]" or (s == "[B]" and "follow-up" in l and "B-" in l):
        continue
    sys.exit(f"FAIL: unfinished row: {l[:60]}")
print("PASS implementation rows 0-13")
PY
    ;;
  pregate)
    echo "== input identity"; git rev-parse HEAD; git status --porcelain | sha256sum
    sha256sum ui/package-lock.json mcp-server/package-lock.json uv.lock; node --version; npm --prefix ui ls electron --depth=0 || true
    run s27-gate-py-types uv run pyright packages/
    run s27-gate-py-lint uv run ruff check packages/ tests/
    run s27-gate-ui-types npm --prefix ui run typecheck
    run s27-gate-ui-lint npm --prefix ui run lint
    run s27-gate-mcp-types npm --prefix mcp-server run typecheck
    run s27-gate-plan-static python3 "$PLAN/plan_checks.py" static
    run s27-gate-task-contract uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task "$PLAN/task.md"
    pytest_env_ok s27-gate-py-tests
    vitest_env_ok s27-gate-ui-tests
    run s27-gate-ui-build npm --prefix ui run build
    run s27-gate-ui-harness-build harness_build
    run s27-gate-mcp-build npm --prefix mcp-server run build
    run s27-gate-mcp-tests npm --prefix mcp-server run test
    run s27-gate-openapi uv run python tools/export_openapi.py --check openapi.committed.json
    run s27-gate-state-render uv run python tools/meu_status.py render --check
    electron_env_ok s27-gate-ui-electron
    bash "$0" tts-live-pre || exit 1
    for f in "${AUDIT_SRC[@]}"; do [ -f "$f" ] || fail "audited source missing: $f"; done
    if grep -nE "$PREFIX_AUDIT" "${AUDIT_SRC[@]}"; then fail "source audit hits"; fi
    echo "PASS container pre-gate (authoritative: windows-gate + tts-live)"
    ;;
  ssot-review)
    for n in 62 63 64; do
      run "s27-meu-$n-rfr" uv run python tools/meu_status.py update "MEU-$n" ready_for_review --plan "$PLAN"
    done
    run s27-render uv run python tools/meu_status.py render
    run s27-render-check uv run python tools/meu_status.py render --check
    grep -qE '^\| 27 \| `tts-repair` \| MEU-62, MEU-63, MEU-64 \| P2 \| in review \| `docs/execution/plans/2026-09-30-tts-repair/`' \
      .agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md || fail "grouping Session 27 not in review"
    grep -q 'tts-repair' .agent/context/current-focus.md && grep -q 'ready_for_review' .agent/context/current-focus.md \
      || fail "focus does not record Session 27 ready_for_review"
    echo "PASS SSOT review state"
    ;;
  api-scope)
    run s27-api-openapi uv run python tools/export_openapi.py --check openapi.committed.json
    run s27-api-route-index uv run pytest tests/e2e/test_api_openapi.py -q -p no:cacheprovider
    python3 - "$(cat "$PLAN/baseline.sha")" <<'PY' || exit 1
import subprocess, sys
base = sys.argv[1]
changed = set(subprocess.run(["git", "diff", "--name-only", base, "HEAD", "--", "packages/api/"],
                             capture_output=True, text=True, check=True).stdout.split())
changed |= {l[3:] for l in subprocess.run(["git", "status", "--porcelain", "--", "packages/api/"],
                                          capture_output=True, text=True, check=True).stdout.splitlines()}
allowed = {"packages/api/src/avkit_api/wiring.py", "packages/api/src/avkit_api/schemas/models.py",
           "packages/api/src/avkit_api/schemas/health.py", "packages/api/src/avkit_api/routes/models.py",
           "packages/api/src/avkit_api/routes/tts.py", "packages/api/src/avkit_api/routes/health.py"}
extra = sorted(changed - allowed)
if extra:
    sys.exit(f"FAIL: packages/api changes outside the plan's Files Modified: {extra}")
print(f"PASS api scope: {sorted(changed)}")
PY
    ;;
  handoff-ac)
    for n in 62 63 64; do
      run "s27-handoff-ac-$n" uv run python tools/validate_closeout_artifacts.py --plan "$PLAN/implementation-plan.md" \
        --handoff ".agent/context/handoffs/2026-09-30-tts-repair-MEU-$n-handoff.md" --ac-coverage-only
    done
    ;;
  windows-gate-check)
    python3 - <<'PY' || exit 1
import json, subprocess, sys
plan = "docs/execution/plans/2026-09-30-tts-repair"
p = f"{plan}/windows-gate-result.json"
try:
    r = json.load(open(p, encoding="utf-8-sig"))
except OSError as err:
    sys.exit(f"FAIL: {p} unreadable: {err}")
if r.get("schema") != "s27-windows-gate.v1":
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
if v.get("failed") != 0 or (v.get("total") or 0) < 675:
    sys.exit(f"FAIL: vitest {v}")
if e.get("unexpected") != 0 or e.get("flaky") not in (0, None) or (e.get("expected") or 0) < 110:
    sys.exit(f"FAIL: e2e {e}")
if py.get("failed") != 0 or not py.get("passed"):
    sys.exit(f"FAIL: pytest {py}")
floor = r.get("pytest_floor")
if floor is not None and py["passed"] < floor:
    sys.exit(f"FAIL: pytest passed {py['passed']} below the first-counted-attempt floor {floor}")
tested = r.get("tested_commit", "")
# GATED_PATHS (implementation-plan.md §Single-statement contracts); plan_checks.py asserts equality.
gated = ["ui", "packages", "mcp-server", "tests", "tools", "pyproject.toml", "uv.lock", "openapi.committed.json",
         "docs/build-plan/11-page-layout.md", "docs/build-plan/gui-actions-index.md",
         "docs/execution/plans/2026-09-26-p11-layout-canon/implementation-plan.md",
         ".agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md",
         ".agent/model-registry.local.json", ".agent/model-registry.local.yaml",
         f"{plan}/validate-task.ps1", f"{plan}/tts_live_check.py"]
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
  tts-live-check)
    python3 - <<'PY' || exit 1
import json, sys
plan = "docs/execution/plans/2026-09-30-tts-repair"
try:
    g = json.load(open(f"{plan}/windows-gate-result.json", encoding="utf-8-sig"))
    r = json.load(open(f"{plan}/tts-live-result.json", encoding="utf-8-sig"))
except OSError as err:
    sys.exit(f"FAIL: result unreadable: {err}")
if r.get("schema") != "s27-tts-live.v1":
    sys.exit(f"FAIL: schema {r.get('schema')}")
if r.get("tested_commit") != g.get("tested_commit"):
    sys.exit(f"FAIL: tts-live ran on {r.get('tested_commit')}, gate on {g.get('tested_commit')}")
if r.get("clean_tree") is not True or "C:/Temp/av-kit/s27-live" not in (r.get("models_directory") or "").replace("\\", "/"):
    sys.exit("FAIL: not a clean tree or not the throwaway models directory")
sys.path.insert(0, plan)
from tts_live_check import STEP_IDS  # TTS_LIVE_STEPS, defined once in tts_live_check.py
want = list(STEP_IDS)
got = [s.get("id") for s in r.get("steps", [])]
if got != want:
    sys.exit(f"FAIL: steps {got} != {want}")
bad = [s for s in r["steps"] if s.get("ok") is not True]
if bad:
    sys.exit(f"FAIL: tts-live steps failed: {bad}")
wav = r["steps"][STEP_IDS.index("generate-wav")].get("observed") or {}
if (wav.get("duration_s") or 0) <= 0.5 or (wav.get("rms") or 0) <= 0:
    sys.exit(f"FAIL: WAV not audible: {wav}")
print(f"PASS tts-live @ {r['tested_commit']}: {wav}")
PY
    ;;
  tts-live-pre)
    # Non-authoritative container run of tts_live_check.py (real HF + GitHub through the proxy),
    # so the Windows TTS_LIVE run is a confirmation, not the discovery (cloud-local §6).
    LIVE="$RD/s27-live"; rm -rf "$LIVE"; mkdir -p "$LIVE/models" "$LIVE/appdata"
    CLEAN=$([ -z "$(git status --porcelain)" ] && echo true || echo false)
    run s27-tts-live-pre uv run python "$PLAN/tts_live_check.py" --app-data "$LIVE/appdata" --models-dir "$LIVE/models" \
      --out "$RD/s27-tts-live-pre.json" --tested-commit "$(git rev-parse HEAD)" --clean-tree "$CLEAN"
    python3 - "$RD/s27-tts-live-pre.json" <<'PY' || exit 1
import json, sys
r = json.load(open(sys.argv[1], encoding="utf-8"))
ids = [s["id"] for s in r["steps"]]
sys.path.insert(0, "docs/execution/plans/2026-09-30-tts-repair")
from tts_live_check import STEP_IDS  # TTS_LIVE_STEPS, defined once in tts_live_check.py
if ids != list(STEP_IDS) or not all(s["ok"] for s in r["steps"]):
    sys.exit(f"FAIL: tts-live-pre {r['steps']}")
print(f"PASS tts-live-pre: {r['steps'][STEP_IDS.index('generate-wav')]['observed']}")
PY
    ;;
  review-check)
    python3 - "$2" "$3" "$4" <<'PY' || exit 1
import re, sys
path, mode, cap = sys.argv[1], sys.argv[2], int(sys.argv[3])
t = open(path, encoding="utf-8").read()
fm = dict(re.findall(r'^(\w+):\s*"?([^"\n]*)"?$', t.split("---")[1], re.M))
target = "docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md"
if fm.get("target_plan") != target: sys.exit(f"FAIL: target {fm.get('target_plan')}")
if fm.get("review_mode") != mode: sys.exit(f"FAIL: mode {fm.get('review_mode')}")
if int(fm.get("round", "0")) > cap: sys.exit(f"FAIL: round {fm.get('round')} over cap {cap}")
if fm.get("verdict") != "approved": sys.exit(f"FAIL: verdict {fm.get('verdict')}")
if "fable" not in fm.get("agent", "").lower(): sys.exit(f"FAIL: agent {fm.get('agent')} is not the authorized route")
print(f"PASS {mode} review approved round {fm['round']} by {fm['agent']}")
PY
    ;;
  post-review-state)
    for n in 62 63 64; do
      run "s27-meu-$n-approved" uv run python tools/meu_status.py update "MEU-$n" approved --plan "$PLAN"
    done
    run s27-approved-render uv run python tools/meu_status.py render
    run s27-approved-check uv run python tools/meu_status.py render --check
    uv run python - <<'PY' || exit 1
import sys, yaml
rows = {r["id"]: r.get("status") for r in yaml.safe_load(open(".agent/context/meu-status.yaml", encoding="utf-8"))["meus"]}
bad = {k: rows.get(k) for k in ("MEU-62", "MEU-63", "MEU-64") if rows.get(k) != "approved"}
if bad: sys.exit(f"FAIL: MEU state {bad}")
issues = {i["id"]: i for i in yaml.safe_load(open(".agent/context/known-issues.yaml", encoding="utf-8"))["issues"]}
five = ["TTS-GENERATE-FAILED-SILENT", "TTS-MODEL-MANAGE-AFFORDANCE", "TTS-CLEANUP-APPLY-MISSING",
        "TTS-CLEANUP-PREVIEW-REDUNDANT", "TTS-LANGUAGE-VOICE-PICKER-SPACE"]
for i in five:
    it = issues.get(i) or {}
    ev = ((it.get("verification") or {}).get("evidence_file") or "")
    if it.get("status") != "resolved" or not ev.startswith("docs/execution/plans/2026-09-30-tts-repair/"):
        sys.exit(f"FAIL: {i} status {it.get('status')} evidence {ev!r}")
g = open(".agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md", encoding="utf-8").read()
if "| 27 | `tts-repair` | MEU-62, MEU-63, MEU-64 | P2 | approved |" not in g: sys.exit("FAIL: grouping Session 27 not approved")
if "2026-09-30-tts-repair" not in open("docs/execution/metrics.md", encoding="utf-8").read(): sys.exit("FAIL: metrics row missing")
print("PASS POST_REVIEW_STATE")
PY
    run s27-issues-render-final uv run python tools/issue_triage.py render --check
    # Post-gate SSOT edits are doc-only (cloud-local §3.4) but gate stages read them: prove they stay green.
    vitest_env_ok s27-post-doc-tests tests/unit/layout-canon.test.ts tests/unit/queue-canon.test.ts tests/unit/gui-actions-audit.test.ts
    ;;
  *) echo "USAGE: validate-task.sh <check>"; exit 2 ;;
esac
