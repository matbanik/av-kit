#!/usr/bin/env bash
# Exact validation procedures for 2026-10-01-mcp-live-audit (Session 28, MEU-68).
# Kept in one script so task.md cells stay lintable (tools/lint_task_contract.py).
# Runs from the repo root; every procedure writes raw tool output under $RECEIPTS_DIR
# and exits nonzero on the first failed check. Executable only during the authorized
# execution session: it runs product tests/builds and spawns the backend.
# Stage list shared with validate-task.ps1 (WINDOWS_GATE): see STAGES_WINDOWS below.
set -uo pipefail

PLAN=docs/execution/plans/2026-10-01-mcp-live-audit
PLAN_BASE=175680c   # branch HEAD when this plan was written (Part A scope base)
RD="${RECEIPTS_DIR:?export RECEIPTS_DIR first}"
mkdir -p "$RD"
CHECK="${1:-}"
# The WINDOWS_GATE stage order, shared with validate-task.ps1 ($stages). packaged-probe is
# optional and non-blocking, so it is not part of the required order.
STAGES_WINDOWS=(preflight mcp-npm-ci uv-sync mcp-types mcp-build mcp-tests mcp-audit)
GATED_PATHS=(mcp-server packages pyproject.toml uv.lock "$PLAN/validate-task.ps1")
# |AUDIT_ACTION_SET| = rows of ACTION_INDEX (68 since MEU-62 added avkit_models.download_asset; A7).
export AUDIT_ACTION_COUNT=68
# TEST_SETS (plan §Single-statement contracts), paths relative to mcp-server/.
UNIT_TESTS=(tests/audit/classify.test.ts tests/audit/coverage.test.ts tests/audit/baseline.test.ts tests/audit/isolation.test.ts
            tests/audit/ledger.test.ts tests/audit/report.test.ts tests/audit/redact.test.ts)
RUNNER_TESTS=(tests/audit/run-cli.test.ts tests/audit/runner-fake-backend.test.ts)
DOC_TESTS=(tests/audit/docs.test.ts)
# STALE_SPEC_PATTERNS (plan): fixed strings that must not remain in 05 §MCP live audit.
# FILED_FINDINGS (plan amendment A2): discovery finding code -> filed known-issue id.
FILED_FINDINGS_JSON='{"schema_not_advertised": "MCP-TOOLS-LIST-EMPTY-INPUT-SCHEMA"}'
export FILED_FINDINGS_JSON
# FILED_STEP_FAILURES (A8): tool.action -> [required reason, filed known-issue id].
FILED_STEP_FAILURES_JSON='{"avkit_tts.cancel": ["confirmed_no_effect", "MCP-TTS-GENERATE-SYNCHRONOUS"]}'
export FILED_STEP_FAILURES_JSON
STALE_SPEC_PATTERNS=("status→pause" "get→set→reset" "health.liveness/dependencies/gpu" "GUI action index")

fail() { echo "FAIL: $*"; exit 1; }
# meu_status_is <MEU-id> <status>: JSON parse of `meu_status.py get` (prints JSON, tools/meu_status.py:98-108).
meu_status_is() {
  uv run python tools/meu_status.py get "$1" > "$RD/s28-meu-$1.json" 2> "$RD/s28-meu-$1.err" || { cat "$RD/s28-meu-$1.err"; fail "meu_status get $1"; }
  python3 -c 'import json,sys; s=json.load(open(sys.argv[1]))["status"]; print(sys.argv[2], "status", s); sys.exit(0 if s == sys.argv[3] else 1)' "$RD/s28-meu-$1.json" "$1" "$2"
}
run() { # run <receipt-id> <argv...>: raw invocation (container D-11), exit preserved
  local id="$1"; shift
  "$@" > "$RD/$id.txt" 2>&1
  local rc=$?
  tail -n 15 "$RD/$id.txt"
  echo "[$id] exit $rc"
  return $rc
}

# vitest_json <receipt-id> <vitest args...>: MCP Vitest with a JSON report; prints the path.
vitest_json() {
  local id="$1"; shift
  npm --prefix mcp-server run test -- "$@" --reporter=json --outputFile="$RD/$id.json" > "$RD/$id.txt" 2>&1
  echo $? > "$RD/$id.rc"
  [ -f "$RD/$id.json" ] || fail "$id: Vitest JSON missing (exit $(cat "$RD/$id.rc")); see $RD/$id.txt"
}

# vitest_assert <json> <mode>: mode green = zero failed/skipped/todo and no load errors;
# mode red = no load errors, >=1 failed assertion, no import/undefined failures, all
# VITEST_ACS (AC-68.1..68.14, 68.16) named in test titles.
vitest_assert() {
  python3 - "$1" "$2" <<'PY' || exit 1
import json, re, sys
path, mode = sys.argv[1], sys.argv[2]
j = json.load(open(path, encoding="utf-8"))
suites = j.get("testResults", [])
load = [s["name"] for s in suites if s.get("message")]
if load:
    sys.exit(f"FAIL: suite load errors (not an assertion Red/Green): {load}")
if j.get("numPendingTests", 0) or j.get("numTodoTests", 0):
    sys.exit("FAIL: skipped/todo tests present")
asserts = [a for s in suites for a in s.get("assertionResults", [])]
failed = [a for a in asserts if a.get("status") == "failed"]
if mode == "green":
    if failed or j.get("numFailedTests", 0):
        sys.exit(f"FAIL: {len(failed)} failed: {[a['fullName'][:80] for a in failed][:10]}")
    print(f"PASS green: {j.get('numPassedTests')} passed")
    sys.exit(0)
titles = " ".join(a.get("fullName", "") for a in asserts)
vitest_acs = [n for n in range(1, 17) if n != 15]  # VITEST_ACS: AC-68.1-68.14, 68.16
missing = [f"AC-68.{n}" for n in vitest_acs if not re.search(rf"AC-68\.{n}\b", titles)]
if missing:
    sys.exit(f"FAIL: ACs with no test: {missing}")
if not failed:
    sys.exit("FAIL: Red has no failing assertion")
bad = [a["fullName"] for a in failed
       if any(re.search(p, m) for m in a.get("failureMessages", [])
              for p in (r"Cannot find module", r"is not a function", r"is not defined", r"ERR_MODULE_NOT_FOUND",
                        r"^TypeError", r"ENOENT"))]
if bad:
    sys.exit(f"FAIL: Red failures are import/wiring errors, not assertions: {bad[:10]}")
print(f"PASS red: {len(failed)} failing assertions, {len(asserts) - len(failed)} passing, VITEST_ACS all named")
PY
}

# scope_check <base-ref> <a|b>: a = only PART_A_PATHS since PLAN_BASE; b = no product
# change on this branch relative to the merge-base with origin/main.
scope_check() {
  local base="$1" mode="$2"
  { git diff --name-only "$base" HEAD; git status --porcelain --untracked-files=all | sed 's/^...//'; } \
    | sort -u > "$RD/s28-scope-$mode-files.txt"
  python3 - "$RD/s28-scope-$mode-files.txt" "$mode" "$base" <<'PY' || exit 1
import fnmatch, json, subprocess, sys
files = [l.strip() for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
mode, base = sys.argv[2], sys.argv[3]
plan = "docs/execution/plans/2026-10-01-mcp-live-audit/"
part_a = ["mcp-server/scripts/*", "mcp-server/tests/audit/*", "mcp-server/package.json",
          "mcp-server/tsconfig.scripts.json", ".agent/workflows/mcp-audit.md", ".agent/workflows/README.md",
          ".agent/skills/mcp-tool-audit/*", ".agent/skills/README.md", ".agent/docs/commands.md",
          "docs/build-plan/05-mcp-server.md", "docs/BUILD_PLAN.md", plan + "*",
          ".agent/context/handoffs/2026-10-01-mcp-live-audit-*",
          ".agent/context/meu-status.yaml", ".agent/context/meu-registry.md",
          ".agent/context/known-issues.yaml", ".agent/context/known-issues.md",
          ".agent/context/current-focus.md"]
forbidden = ["packages/*", "ui/*", "mcp-server/src/*", "mcp-server/package-lock.json"]
bad = [f for f in files if any(fnmatch.fnmatch(f, p) for p in forbidden)]
if mode == "a":
    bad += [f for f in files if not any(fnmatch.fnmatch(f, p) for p in part_a)]
if bad:
    sys.exit(f"FAIL scope {mode}: out-of-scope changes {sorted(set(bad))}")
if "mcp-server/package.json" in files:
    old = json.loads(subprocess.run(["git", "show", f"{base}:mcp-server/package.json"], capture_output=True, text=True, check=True).stdout)
    new = json.load(open("mcp-server/package.json", encoding="utf-8"))
    old.pop("scripts", None); new.pop("scripts", None)
    if old != new:
        sys.exit("FAIL scope: mcp-server/package.json changed outside the scripts block")
print(f"PASS scope {mode}: {len(files)} changed paths, all allowed")
PY
  # AC-68.2: the runner never takes the in-process shortcut.
  if [ -d mcp-server/scripts ]; then
    rg -n -f mcp-server/tests/audit/forbidden-imports.txt mcp-server/scripts > "$RD/s28-scope-imports.txt" 2>&1
    case $? in 1) echo "PASS AC-68.2: no toolset import in mcp-server/scripts" ;; 0) cat "$RD/s28-scope-imports.txt"; fail "AC-68.2 runner imports toolsets" ;; *) fail "rg error" ;; esac
  fi
}

# audit_container_assert <out-dir> <runner-exit>: AC-68.12 container tolerance on a real run.
audit_container_assert() {
  local meu62_pending=1
  meu_status_is MEU-62 approved > /dev/null && meu62_pending=0
  python3 - "$1" "$2" "$meu62_pending" <<'PY' || exit 1
import json, os, re, sys
out, rc, meu62_pending = sys.argv[1], int(sys.argv[2]), sys.argv[3] == "1"
# MEU62_PENDING_TOLERANCE (plan): container-only, off once MEU-62 is approved.
MEU62_SET = {("avkit_tts", "generate"), ("avkit_tts", "get"), ("avkit_tts", "cancel"), ("avkit_models", "load")}
MEU62_SIGNATURE = re.compile(r"en_core_web_sm|spacy|vocab|config\.json|misaki", re.I)
p = os.path.join(out, "mcp-audit-summary.json")
if not os.path.exists(p):
    sys.exit(f"FAIL: no summary at {p} (runner exit {rc})")
s = json.load(open(p, encoding="utf-8"))
if s.get("schema") != "mcp-audit-summary.v1" or s.get("mode") != "container":
    sys.exit(f"FAIL: schema/mode {s.get('schema')}/{s.get('mode')}")
if rc not in (0, 1):
    sys.exit(f"FAIL: runner exit {rc} (2/3/4 = refused or errored)")
d = s.get("discovery", {})
n_actions = int(os.environ["AUDIT_ACTION_COUNT"])
if d.get("tools") != 8 or d.get("actions") != n_actions:
    sys.exit(f"FAIL: discovery surface {d.get('tools')} tools / {d.get('actions')} actions, expected 8 / {n_actions}")
filed = json.loads(os.environ["FILED_FINDINGS_JSON"])
issue_ids = set(re.findall(r"^- id: (\S+)", open(".agent/context/known-issues.yaml", encoding="utf-8").read(), re.M))
unfiled = [f for f in d.get("findings", []) if filed.get(f.get("code")) not in issue_ids]
if unfiled:
    sys.exit(f"FAIL: discovery findings without a filed issue (FILED_FINDINGS): {unfiled}")
if d.get("status") != "pass" and not d.get("findings"):
    sys.exit(f"FAIL: discovery {d.get('status')} with no findings recorded")
if not s.get("launch", {}).get("initialized"):
    sys.exit("FAIL: MCP initialize did not complete")
if not s.get("isolation", {}).get("ok"):
    sys.exit(f"FAIL: isolation {s.get('isolation')}")
c = s.get("cleanup", {})
if not (c.get("ok") and c.get("backend_exited") and c.get("root_removed") and not c.get("residuals")):
    sys.exit(f"FAIL: cleanup {c}")
steps = s.get("steps", [])
called = {(x["tool"], x["action"]) for x in steps}
if len(called) != n_actions:
    sys.exit(f"FAIL: {len(called)} distinct actions recorded, expected {n_actions}")
bad, tolerated_meu62, tolerated_filed = [], [], []
filed_steps = json.loads(os.environ["FILED_STEP_FAILURES_JSON"])
for x in steps:
    v = x.get("verdict")
    if v == "pass":
        if not x.get("observable"):
            bad.append((x["tool"], x["action"], "pass without observable"))
    elif v == "skip_env":
        e = x.get("env_bound") or {}
        if not (e.get("member") and e.get("signature_matched") and e.get("env_proof")):
            bad.append((x["tool"], x["action"], "skip_env without proven census membership"))
    elif v == "blocked":
        if not x.get("blocked_by"):
            bad.append((x["tool"], x["action"], "blocked without blocked_by"))
    elif v == "fail" and filed_steps.get(f'{x["tool"]}.{x["action"]}', [None, None])[0] == x.get("reason") \
            and filed_steps[f'{x["tool"]}.{x["action"]}'][1] in issue_ids:
        tolerated_filed.append((x["tool"], x["action"], x.get("reason")))
    elif v == "fail" and meu62_pending and (x["tool"], x["action"]) in MEU62_SET \
            and MEU62_SIGNATURE.search(x.get("error") or ""):
        tolerated_meu62.append((x["tool"], x["action"], (x.get("error") or "")[:80]))
    else:
        bad.append((x["tool"], x["action"], v))
if bad:
    sys.exit(f"FAIL: untolerated results {bad}")
if rc == 1 and not tolerated_meu62 and not tolerated_filed and not d.get("findings"):
    sys.exit("FAIL: runner exit 1 with no tolerated failure (MEU62_PENDING_TOLERANCE or FILED_FINDINGS)")
domains = {}
for x in steps:
    domains.setdefault(x["tool"], []).append(x.get("verdict"))
empty = [d for d, vs in domains.items() if "pass" not in vs]
if empty:
    sys.exit(f"FAIL: domains with zero pass: {empty} (each domain has entity-free steps: list/voices/available/sabr_get/gpu/settings/health)")
passes = sum(1 for x in steps if x.get("verdict") == "pass")
print(f"PASS audit-container: {passes} pass, {len(steps) - passes} tolerated; MEU62_PENDING_TOLERANCE {tolerated_meu62}; filed step failures {tolerated_filed}; filed findings {[f['code'] + ':' + f['tool'] for f in d.get('findings', [])]}; cleanup ok")
PY
}

# windows_gate_assert: cloud-local §3.3 minimum assertions + AUTHORITATIVE_ACCEPTANCE.
windows_gate_assert() {
  python3 - "$PLAN" "${GATED_PATHS[@]}" <<PY || exit 1
import hashlib, json, os, subprocess, sys
plan, gated = sys.argv[1], sys.argv[2:]
order = "${STAGES_WINDOWS[*]}".split()
def load(name):
    p = os.path.join(plan, name)
    try:
        return json.load(open(p, encoding="utf-8-sig"))
    except OSError as err:
        sys.exit(f"FAIL: {p} unreadable: {err}")
r = load("windows-gate-result.json")
if r.get("schema") != "s28-windows-gate.v1": sys.exit(f"FAIL: schema {r.get('schema')}")
if r.get("clean_tree") is not True: sys.exit("FAIL: Windows run was not on a clean tree")
pf = r.get("preflight") or {}
if pf.get("quiet_machine") is not True or not pf.get("rtk"): sys.exit(f"FAIL: preflight {pf}")
got = [s.get("id") for s in r.get("stages", []) if s.get("id") != "packaged-probe"]
if got != order: sys.exit(f"FAIL: stages {got} != {order}")
for s in r["stages"]:
    if s["id"] == "packaged-probe": continue
    if s["id"] == "mcp-audit":
        if s.get("exit") not in (0, 1): sys.exit(f"FAIL: mcp-audit exit {s.get('exit')} (2/3/4 = runner refused or errored)")
    elif s.get("exit") != 0:
        sys.exit(f"FAIL: stage {s['id']} exit {s.get('exit')}")
floor = load("mcp-test-floor.json")
t = r.get("mcp_tests") or {}
if t.get("failed") != 0 or (t.get("total") or 0) <= floor["total"]:
    sys.exit(f"FAIL: mcp_tests {t} vs floor {floor}")
s = load("mcp-audit-summary.json")
if s.get("mode") != "authoritative" or s.get("commit") != r.get("tested_commit"):
    sys.exit(f"FAIL: summary mode/commit {s.get('mode')}/{s.get('commit')} vs {r.get('tested_commit')}")
if not s.get("cleanup", {}).get("ok"): sys.exit(f"FAIL: cleanup {s.get('cleanup')}")
# Worst-of per action, the runner's own aggregate() order (run.ts WORST), so a later passing step
# of the same action never hides an earlier failure.
worst = ["fail", "blocked", "skip_env", "pass"]
v = {}
for x in s.get("steps", []):
    k, verdict = (x["tool"], x["action"]), x.get("verdict")
    rank = worst.index(verdict) if verdict in worst else -1
    if k not in v or rank < (worst.index(v[k]) if v[k] in worst else -1):
        v[k] = verdict
n_actions = int(os.environ["AUDIT_ACTION_COUNT"])
if len(v) != n_actions: sys.exit(f"FAIL: {len(v)} actions in authoritative summary, expected {n_actions}")
must = [("avkit_health", "liveness"), ("avkit_health", "dependencies"), ("avkit_tts", "generate")]
nm = [m for m in must if v.get(m) != "pass"]
if nm: sys.exit(f"FAIL: AUTHORITATIVE_ACCEPTANCE must-pass actions not pass: {nm}")
if any(x == "skip_env" for x in v.values()): sys.exit("FAIL: skip_env is not allowed in authoritative mode")
b = load("windows-gate-baseline.json")
if b.get("schema") != "mcp-audit-baseline.v1" or b.get("recorded_commit") != r.get("tested_commit") or b.get("mode") != "authoritative":
    sys.exit(f"FAIL: gate baseline header {b.get('schema')}/{b.get('recorded_commit')}/{b.get('mode')}")
committed = ".agent/skills/mcp-tool-audit/resources/baseline-snapshot.json"
if not os.path.exists(committed): sys.exit(f"FAIL: {committed} not committed")
if not os.path.exists(".agent/context/MCP/mcp-tool-audit-report.md"): sys.exit("FAIL: report not committed")
tested = r["tested_commit"]
rc = subprocess.run(["git", "diff", "--quiet", tested, "HEAD", "--", *gated]).returncode
if rc != 0: sys.exit(f"FAIL: GATED_PATHS changed since tested commit {tested} (git diff exit {rc})")
dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "--", *gated], capture_output=True, text=True).stdout.strip()
if dirty: sys.exit(f"FAIL: uncommitted changes under GATED_PATHS:\n{dirty}")
fails = sorted(f"{k[0]}.{k[1]}" for k, x in v.items() if x != "pass")
print(f"PASS windows gate @ {tested}: mcp_tests {t}; audit {n_actions} actions, non-pass {fails}")
PY
}

case "$CHECK" in
  prereq)
    for t in node npm uv rg git python3; do command -v "$t" > /dev/null || fail "missing $t"; done
    node -e 'process.exit(+process.versions.node.split(".")[0] >= 18 ? 0 : 1)' || fail "node < 18"
    # Context-tool decision re-check (create-plan §5f): absent graphs/headroom => not_applicable.
    { ls -d graphify-out graphify-out-research 2>&1; python3 -c 'import importlib.util,sys; sys.exit(0 if importlib.util.find_spec("headroom") else 3)'; echo "headroom-exit $?"; } > "$RD/s28-ctx-tools.txt" 2>&1
    grep -q "headroom-exit 3" "$RD/s28-ctx-tools.txt" || fail "headroom present: re-run the context-tool gate with the human"
    [ -d graphify-out ] && fail "graphify-out present: re-run the context-tool gate with the human"
    grep -q "H-4" "$PLAN/human-gate-decision.md" && ! grep -q "(PENDING)" "$PLAN/human-gate-decision.md" || fail "H-4 execution authorization not recorded"
    run s28-mcp-ci npm --prefix mcp-server ci || fail "mcp-server npm ci"
    run s28-uv-sync uv sync --frozen --all-packages || fail "uv sync"
    run s28-mcp-build0 npm --prefix mcp-server run build || fail "mcp build"
    vitest_json s28-mcp-floor-run
    python3 - "$RD/s28-mcp-floor-run.json" "$PLAN/mcp-test-floor.json" <<'PY' || exit 1
import json, sys
j = json.load(open(sys.argv[1], encoding="utf-8"))
if j.get("numFailedTests") != 0: sys.exit(f"FAIL: pre-edit MCP suite not green: {j.get('numFailedTests')} failed")
json.dump({"total": j["numTotalTests"], "passed": j["numPassedTests"], "recorded": "row 1 pre-edit"}, open(sys.argv[2], "w"), indent=2)
print(f"MCP_TEST_FLOOR {j['numTotalTests']}")
PY
    meu_status_is MEU-68 in_progress || fail "MEU-68 not set in_progress (meu_status.py update MEU-68 in_progress --plan $PLAN)"
    grep -q "MCP-PACKAGED-ENTRY-UNREACHABLE" .agent/context/known-issues.yaml || fail "D-6 hypothesis issue not filed"
    uv run python tools/issue_triage.py render --check > "$RD/s28-issues-render.txt" 2>&1 || fail "known-issues render drift"
    [ -f "$PLAN/walkthrough.md" ] && grep -q "MCP_TEST_FLOOR" "$PLAN/walkthrough.md" || fail "walkthrough prerequisites not recorded"
    echo "PASS prereq"
    ;;
  red)
    # The build compiles src/** only (tsconfig.json rootDir src); it refreshes dist for RUNNER_TESTS.
    run s28-red-build npm --prefix mcp-server run build || fail "mcp build"
    vitest_json s28-red "${UNIT_TESTS[@]}" "${RUNNER_TESTS[@]}" "${DOC_TESTS[@]}"
    vitest_assert "$RD/s28-red.json" red
    ;;
  green)
    vitest_json s28-green "${UNIT_TESTS[@]}"
    vitest_assert "$RD/s28-green.json" green
    ;;
  fake)
    run s28-fake-build npm --prefix mcp-server run build || fail "build"
    vitest_json s28-fake "${UNIT_TESTS[@]}" "${RUNNER_TESTS[@]}"
    vitest_assert "$RD/s28-fake.json" green
    ;;
  typecheck-red-green)
    f=mcp-server/scripts/audit/classify.ts
    [ -f mcp-server/tsconfig.scripts.json ] || fail "tsconfig.scripts.json missing"
    grep -q 'tsconfig.scripts.json' mcp-server/package.json || fail "typecheck script does not include tsconfig.scripts.json"
    grep -q '"audit": "tsx scripts/audit/run.ts' mcp-server/package.json || fail "audit script missing"
    cp "$f" "$RD/s28-classify.bak"
    trap 'cp "$RD/s28-classify.bak" "'"$f"'"' EXIT
    echo 'export const __s28TypeProbe: number = "not a number";' >> "$f"
    (cd mcp-server && npx tsc --noEmit -p tsconfig.json) > "$RD/s28-tc-red.txt" 2>&1
    [ $? -eq 0 ] || fail "Red: src-only tsc should not see scripts/ (got errors, see s28-tc-red.txt)"
    npm --prefix mcp-server run typecheck > "$RD/s28-tc-probe.txt" 2>&1
    [ $? -ne 0 ] && grep -Eq "scripts/audit/classify\.ts\([0-9]+,[0-9]+\): error TS2322" "$RD/s28-tc-probe.txt" || fail "new typecheck did not catch the probe in scripts/"
    cp "$RD/s28-classify.bak" "$f"; trap - EXIT
    run s28-tc-green npm --prefix mcp-server run typecheck || fail "typecheck after revert"
    grep -q '^| mcp-audit |' .agent/docs/commands.md || fail "D6 mcp-audit row missing in commands.md"
    git diff --quiet -- "$f" 2>/dev/null || git diff --stat -- "$f"
    echo "PASS AC-68.17 typecheck Red -> Green; D6 row registered"
    ;;
  audit-container)
    rm -rf "$RD/s28-audit-container"
    npm --prefix mcp-server run audit -- --mode container --no-baseline --out "$RD/s28-audit-container" --report "$RD/s28-audit-container/report.md" --agent claude-code-cloud > "$RD/s28-audit-container.run.txt" 2>&1
    rc=$?
    tail -n 25 "$RD/s28-audit-container.run.txt"
    audit_container_assert "$RD/s28-audit-container" "$rc"
    ;;
  docs)
    vitest_json s28-docs-test "${DOC_TESTS[@]}"
    vitest_assert "$RD/s28-docs-test.json" green
    for f in .agent/workflows/mcp-audit.md .agent/skills/mcp-tool-audit/SKILL.md; do
      head -n 1 "$f" | grep -q '^---$' || fail "$f has no frontmatter"
    done
    grep -q 'mcp-audit.md' .agent/workflows/README.md || fail "workflow not indexed"
    grep -q 'mcp-tool-audit' .agent/skills/README.md || fail "skill not indexed"
    # AC-68.18: the §MCP live audit section names no non-existent actions.
    awk '/^## MCP live audit \(residual\)/{on=1;next} /^## /{on=0} on' docs/build-plan/05-mcp-server.md > "$RD/s28-05-section.md"
    [ -s "$RD/s28-05-section.md" ] || fail "05 §MCP live audit section not found"
    pat_args=(); for s in "${STALE_SPEC_PATTERNS[@]}"; do pat_args+=(-e "$s"); done
    rg -n -F "${pat_args[@]}" "$RD/s28-05-section.md" > "$RD/s28-05-stale.txt" 2>&1
    case $? in 1) ;; 0) cat "$RD/s28-05-stale.txt"; fail "stale action names remain in 05 §MCP live audit" ;; *) fail "rg error" ;; esac
    rg -q 'baseline-snapshot.json' "$RD/s28-05-section.md" && rg -q -i 'isolated' "$RD/s28-05-section.md" || fail "05 section lacks baseline path or isolation rule"
    echo "PASS docs"
    ;;
  scope)
    case "${2:-}" in
      a) scope_check "$PLAN_BASE" a ;;
      b) git fetch -q origin main || fail "fetch origin main"; scope_check "$(git merge-base origin/main HEAD)" b ;;
      *) fail "scope needs a|b" ;;
    esac
    ;;
  gate-a)
    run s28-gate-a-types npm --prefix mcp-server run typecheck || fail "mcp-types"
    run s28-gate-a-build npm --prefix mcp-server run build || fail "mcp-build"
    vitest_json s28-gate-a-tests
    vitest_assert "$RD/s28-gate-a-tests.json" green
    python3 - "$RD/s28-gate-a-tests.json" "$PLAN/mcp-test-floor.json" <<'PY' || exit 1
import json, sys
j, f = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
if j["numTotalTests"] <= f["total"]: sys.exit(f"FAIL: mcp-tests {j['numTotalTests']} <= floor {f['total']}")
print(f"PASS mcp-tests {j['numTotalTests']} > floor {f['total']}")
PY
    scope_check "$PLAN_BASE" a
    run s28-gate-a-lint uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task "$PLAN/task.md" || fail "task-contract"
    grep -q "Part A checkpoint" "$PLAN/walkthrough.md" || fail "walkthrough §Part A checkpoint missing"
    echo "PASS gate-a"
    ;;
  seqgate)
    git fetch -q origin main || fail "fetch origin main"
    git merge-base --is-ancestor origin/main HEAD || fail "origin/main not merged into HEAD"
    meu_status_is MEU-62 approved || fail "SEQUENCING_GATE refused: MEU-62 not approved"
    # SSOT_MERGE_RULE: generated SSOT must be consistent after the merge.
    run s28-seq-render uv run python tools/meu_status.py render --check || fail "meu_status render --check after merge"
    run s28-seq-issues uv run python tools/issue_triage.py render --check || fail "issue_triage render --check after merge"
    scope_check "$(git merge-base origin/main HEAD)" b
    echo "PASS SEQUENCING_GATE"
    ;;
  pregate)
    run s28-pre-ci npm --prefix mcp-server ci || fail "mcp-npm-ci"
    run s28-pre-uv uv sync --frozen --all-packages || fail "uv-sync"
    run s28-pre-types npm --prefix mcp-server run typecheck || fail "mcp-types"
    run s28-pre-build npm --prefix mcp-server run build || fail "mcp-build"
    vitest_json s28-pre-tests
    vitest_assert "$RD/s28-pre-tests.json" green
    bash "$0" audit-container || fail "audit-container"
    echo "PASS pregate (non-authoritative)"
    ;;
  windows-gate-check)
    windows_gate_assert
    ;;
  findings-check)
    uv run python - "$PLAN" <<'PY' || exit 1
import json, os, sys, yaml
plan = sys.argv[1]
g = json.load(open(os.path.join(plan, "windows-gate-baseline.json"), encoding="utf-8-sig"))
c = json.load(open(".agent/skills/mcp-tool-audit/resources/baseline-snapshot.json", encoding="utf-8-sig"))
strip = lambda b: {**{k: v for k, v in b.items() if k not in ("entries", "findings")},
                   "entries": [{k: v for k, v in e.items() if k != "issue"} for e in b["entries"]],
                   "findings": [{k: v for k, v in f.items() if k != "issue"} for f in b.get("findings", [])]}
if strip(g) != strip(c):
    sys.exit("FAIL: BASELINE_ANNOTATION_RULE: committed baseline differs from the gate output beyond `issue`")
ids = {i["id"] for i in yaml.safe_load(open(".agent/context/known-issues.yaml", encoding="utf-8"))["issues"]}
missing = [f"{e['tool']}.{e['action']}" for e in c["entries"] if e["status"] != "pass" and e.get("issue") not in ids]
missing += [f"finding {f['code']}:{f['tool']}" for f in c.get("findings", []) if f.get("issue") not in ids]
if missing:
    sys.exit(f"FAIL: AUTHORITATIVE_ACCEPTANCE: non-pass entries without a filed issue {missing}")
print(f"PASS findings: {sum(e['status'] != 'pass' for e in c['entries'])} non-pass, all filed")
PY
    uv run python tools/issue_triage.py render --check > "$RD/s28-issues-render2.txt" 2>&1 || fail "known-issues render drift"
    ;;
  task-state|closeout)
    python3 - "$PLAN/task.md" "$CHECK" <<'PY' || exit 1
import re, sys
path, check = sys.argv[1], sys.argv[2]
pat = r"^\| [0-9]+ \|" if check == "task-state" else r"^\| ([0-9]+|H[12]-[0-9]+) \|"
rows = [l for l in open(path, encoding="utf-8") if re.match(pat, l)]
want = 12 if check == "task-state" else 21
if len(rows) != want: sys.exit(f"FAIL: expected {want} rows, got {len(rows)}")
for l in rows:
    s = l.rstrip().rstrip("|").split("|")[-1].strip().strip("`")
    if s == "[x]" or (s == "[B]" and "follow-up" in l and "B-" in l): continue
    sys.exit(f"FAIL: unfinished row: {l[:70]}")
print(f"PASS {check}: {len(rows)} rows done")
PY
    if [ "$CHECK" = closeout ]; then
      run s28-closeout-lint uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task "$PLAN/task.md" || fail "task-contract"
    fi
    ;;
  h1-verify)
    windows_gate_assert
    bash "$0" findings-check || fail "findings-check"
    bash "$0" scope b || fail "scope b"
    run s28-h1-types npm --prefix mcp-server run typecheck || fail "mcp-types"
    echo "PASS h1-verify"
    ;;
  ssot-review)
    run s28-render uv run python tools/meu_status.py render --check || fail "render --check"
    meu_status_is MEU-68 ready_for_review || fail "MEU-68 not ready_for_review"
    grep -E '^\| 28 \|' .agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md | grep -qi 'review' || fail "grouping Session 28 not marked in review"
    grep -q 'Session 28' .agent/context/current-focus.md || fail "focus not updated"
    echo "PASS ssot-review"
    ;;
  api-scope)
    git fetch -q origin main || fail "fetch origin main"
    mb=$(git merge-base origin/main HEAD)
    changed=$(git diff --name-only "$mb" HEAD -- packages/; git status --porcelain -- packages/)
    [ -z "$changed" ] || { echo "$changed"; fail "packages/ changed on this branch: G8 OpenAPI drift check required"; }
    echo "PASS api-scope: no packages/ change vs $mb; OpenAPI skip-with-basis (G8 not triggered)"
    ;;
  review-check)
    python3 - "$2" "$3" "$4" <<'PY' || exit 1
import re, sys
path, mode, cap = sys.argv[1], sys.argv[2], int(sys.argv[3])
t = open(path, encoding="utf-8").read()
fm = dict(re.findall(r'^(\w+):\s*"?([^"\n]*)"?$', t.split("---")[1], re.M))
target = "docs/execution/plans/2026-10-01-mcp-live-audit/implementation-plan.md"
if fm.get("target_plan") != target: sys.exit(f"FAIL: target {fm.get('target_plan')}")
if fm.get("review_mode") != mode: sys.exit(f"FAIL: mode {fm.get('review_mode')}")
if int(fm.get("round", "0")) > cap: sys.exit(f"FAIL: round {fm.get('round')} over cap {cap}")
if fm.get("verdict") != "approved": sys.exit(f"FAIL: verdict {fm.get('verdict')}")
if "fable" not in fm.get("agent", "").lower(): sys.exit(f"FAIL: agent {fm.get('agent')} is not the authorized route")
print(f"PASS {mode} review approved round {fm['round']} by {fm['agent']}")
PY
    ;;
  post-review-state)
    run s28-render2 uv run python tools/meu_status.py render --check || fail "render --check"
    meu_status_is MEU-68 approved || fail "MEU-68 not approved"
    uv run python - <<'PY' || exit 1
import sys, yaml
issues = {i["id"]: i for i in yaml.safe_load(open(".agent/context/known-issues.yaml", encoding="utf-8"))["issues"]}
if issues.get("MCP-LIVE-AUDIT-WORKFLOW", {}).get("status") != "resolved":
    sys.exit("FAIL: MCP-LIVE-AUDIT-WORKFLOW not resolved")
print("PASS issue resolved")
PY
    uv run python tools/issue_triage.py render --check > "$RD/s28-issues-render3.txt" 2>&1 || fail "known-issues render drift"
    grep -E '^\| 5 — MCP server' docs/BUILD_PLAN.md | grep -q 'MEU-68 approved' || fail "BUILD_PLAN Phase 5 row does not say MEU-68 approved"
    grep -E '^\| 28 \|' .agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md | grep -qi 'approved' || fail "grouping Session 28 not approved"
    grep -q '2026-10-01-mcp-live-audit' docs/execution/metrics.md || fail "metrics row missing"
    echo "PASS post-review-state"
    ;;
  *)
    fail "unknown check '$CHECK'"
    ;;
esac
