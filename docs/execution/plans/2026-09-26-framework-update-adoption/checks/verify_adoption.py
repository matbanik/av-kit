"""Fail-closed adoption checks; observations never restore or overwrite user files."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

PLAN = Path("docs/execution/plans/2026-09-26-framework-update-adoption")
TOOLS = (
    "durable_evidence.py",
    "lint_task_contract.py",
    "validate_closeout_artifacts.py",
    "validate_json_schema.py",
    "adapt_output_schema.py",
    "review_ledger.py",
)
TEMPLATES = {
    "PLAN": "docs/execution/plans/PLAN-TEMPLATE.md",
    "TASK": "docs/execution/plans/TASK-TEMPLATE.md",
    "HANDOFF": ".agent/context/handoffs/TEMPLATE.md",
    "REVIEW": ".agent/context/handoffs/REVIEW-TEMPLATE.md",
    "REFLECTION": "docs/execution/reflections/TEMPLATE.md",
}


class Refuse(ValueError):
    """A required contract or evidence is absent, invalid or stale."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise Refuse(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def document(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"expected object: {path}")
    return value


def inside(root: Path, name: str) -> Path:
    require(
        not Path(name).is_absolute() and not re.match(r"^[A-Za-z]:", name),
        f"absolute path is not allowed: {name}",
    )
    target = (root / name).resolve()
    require(target.is_relative_to(root.resolve()), f"path escapes root: {name}")
    return target


def command(argv: list[str], cwd: Path, env: dict | None = None):
    return subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def git(root: Path, *args: str) -> str:
    result = command(["rtk", "proxy", "git", "-C", str(root), *args], root)
    require(result.returncode == 0, f"git evidence unavailable: {result.stderr}")
    return result.stdout.strip()


def source_state(source: Path, data: dict) -> None:
    require(git(source, "rev-parse", "HEAD") == data["source_sha"], "source revision drift")
    require(not git(source, "status", "--porcelain"), "source working-tree drift")
    for entry in data.get("files", []):
        if entry.get("source_path"):
            p = inside(source, entry["source_path"])
            require(
                p.is_file() and digest(p) == entry["source_sha256"],
                f"source file drift: {entry['source_path']}",
            )


def file_state(root: Path, data: dict, *, baseline: bool) -> None:
    entries = data["files"] + data["protected_files"]
    require(entries, "empty file manifest")
    names = [entry["path"] for entry in entries]
    require(len(names) == len(set(names)), "duplicate manifest path")
    bootstrap = set(data.get("bootstrap_paths", []))
    for name in bootstrap:
        inside(root, name)
        require(name in {e["path"] for e in data["files"]}, "undeclared bootstrap path")
    for entry in entries:
        p = inside(root, entry["path"])
        protected = entry in data["protected_files"]
        if baseline and entry["path"] in bootstrap and not protected:
            continue
        if entry["path"] == (PLAN / "adoption-manifest.json").as_posix():
            continue  # A manifest cannot contain its own final digest.
        expected = entry.get("preimage_sha256")
        if not protected and entry.get("postimage_sha256"):
            expected = entry["postimage_sha256"]
        require((digest(p) if p.is_file() else None) == expected, f"file drift: {entry['path']}")
    allowed = set(names) | set(data.get("initial_paths", []))
    if (root / ".git").exists():
        actual = set(
            git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split("\0")
        ) - {""}
    else:
        actual = {
            p.relative_to(root).as_posix()
            for p in root.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts
        }
    require(
        not actual - allowed - {"manifest.json"},
        f"files outside allowlist: {sorted(actual - allowed - {'manifest.json'})}",
    )


def task_rows(path: Path) -> dict[str, list[str]]:
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("|"):
            cells = [c.strip().strip("`") for c in re.split(r"(?<!\\)\|", line.strip("|"))]
            if cells and re.fullmatch(r"(?:[0-6]|1[ab]|H[12]-[1-7])", cells[0]):
                require(len(cells) == 9, f"invalid task columns: {cells[0]}")
                require(
                    cells[5] == "—" or cells[5] in rows,
                    f"missing or cyclic task dependency: {cells[0]}",
                )
                rows[cells[0]] = cells
    require(len(rows) == 21, "incomplete task contract")
    return rows


def static(root: Path) -> None:
    for name in TOOLS:
        require((root / "tools" / name).is_file(), f"missing selected dependency: {name}")
    for name, target in TEMPLATES.items():
        require(
            (root / target).read_bytes()
            == (root / f".agent/templates/{name}-TEMPLATE.md").read_bytes(),
            f"template copies differ: {name}",
        )
    for name, line_cap, byte_cap in [("AGENTS.md", 170, 20000), ("GUARDRAILS.md", 90, 8000)]:
        p = root / name
        text = p.read_text(encoding="utf-8")
        require(
            len(text.splitlines()) <= line_cap and p.stat().st_size <= byte_cap,
            f"instruction size exceeds bound: {name}",
        )
        for link in re.findall(r"\]\(([^)]+)\)", text):
            if re.match(r"(?:https?:|#|mailto:)", link):
                continue
            link_path = link.split("#", 1)[0]
            require(inside(root, link_path).exists(), f"broken instruction backlink: {link}")
    agents = (root / "AGENTS.md").read_text(encoding="utf-8")
    for pattern in [
        r"YouTube",
        r"(?i)never.*(?:upload|publish)",
        r"(?i)independent.*review",
        r"(?i)human.*(?:approval|authorization)",
        r"(?i)Electron",
        r"(?i)FIC",
    ]:
        require(re.search(pattern, agents), f"lost local rule: {pattern}")
    require((root / PLAN / "rule-preservation.md").is_file(), "rule map missing")
    routing = (root / ".agent/docs/model-routing.md").read_text(encoding="utf-8")
    require(
        "avkit_independent_reviewer" in routing and "Mat" in routing, "routing contract missing"
    )
    require(
        not re.search(r"(?im)^.*(?:default reviewer|fallback)\s*:\s*(?:GPT-|Gemini)", routing),
        "stale or unconfigured live routing",
    )
    task_rows(root / PLAN / "task.md")
    governance_inventory(root)


def embedded_json(path: Path) -> dict:
    blocks = re.findall(r"```json\s*\n(.*?)\n```", path.read_text(encoding="utf-8"), re.S)
    require(len(blocks) == 1, f"missing unique machine inventory: {path}")
    value = json.loads(blocks[0])
    require(isinstance(value, dict), f"inventory must be an object: {path}")
    return value


def heading_anchor(heading: str) -> str:
    return re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")


def governance_inventory(root: Path) -> None:
    """Check rule coverage, historical registry IDs and line-specific routing exceptions."""
    import base64

    manifest = document(root / PLAN / "adoption-manifest.json")
    mapping = embedded_json(root / PLAN / "rule-preservation.md")
    require(mapping["schema_version"] == "rule-map.v1", "unsupported rule map")
    for name in ["AGENTS.md", "GUARDRAILS.md"]:
        entry = next(e for e in manifest["files"] if e["path"] == name)
        before = base64.b64decode(entry["preimage_base64"]).decode("utf-8")
        count = mapping["counts"][name]
        require(
            count["preimage_sha256"] == entry["preimage_sha256"]
            and count["postimage_sha256"] == digest(root / name),
            f"rule map identity mismatch: {name}",
        )
        require(count["after_blocks"] <= count["before_blocks"], "instruction rule growth")
        covered = set()
        for item in mapping["blocks"]:
            if item["file"] != name:
                continue
            require(item["action"] and item["reason"], "unexplained rule removal")
            covered.update(range(item["start"], item["end"] + 1))
            path, anchor = item["successor"].split("#", 1)
            text = inside(root, path).read_text(encoding="utf-8")
            anchors = {heading_anchor(h) for h in re.findall(r"^#+ (.+)$", text, re.M)}
            anchors.update(re.findall(r'<a id="([^"]+)"', text))
            require(anchor in anchors, f"missing rule successor: {item['successor']}")
        needed = {i for i, line in enumerate(before.splitlines(), 1) if line.strip()}
        require(needed <= covered, f"unmapped source rules: {name}")

    registry = yaml.safe_load((root / ".agent/schemas/registry.yaml").read_text(encoding="utf-8"))
    old_entry = next(e for e in manifest["files"] if e["path"] == ".agent/schemas/registry.yaml")
    old_registry = yaml.safe_load(base64.b64decode(old_entry["preimage_base64"]))
    old_ids = {s["section_id"] for s in old_registry["sections"]}
    new_ids = [s["section_id"] for s in registry["sections"]]
    require(old_ids <= set(new_ids) and len(new_ids) == len(set(new_ids)), "registry ID drift")
    headings = set(re.findall(r"^## (.+)$", (root / "AGENTS.md").read_text(encoding="utf-8"), re.M))
    require(
        all(s["heading"] in headings for s in registry["sections"]),
        "registry heading has no live owner",
    )
    census = embedded_json(root / PLAN / "routing-census.md")
    require(census["schema_version"] == "routing-census.v1", "unsupported routing census")
    known = {(m["path"], m["text_sha256"]) for m in census["matches"] if m["reason"]}
    numeric = re.compile(
        r"gpt[- ]?\d|opus[- ]?\d|sonnet[- ]?\d|haiku[- ]?\d|grok[- ]?\d|"
        r"composer[- ]?\d|gemini[- ]?\d",
        re.I,
    )
    paths = {inside(root, f["path"]) for f in census["files"]}
    for prefix in [
        ".agent/docs",
        ".agent/roles",
        ".agent/skills",
        ".agent/workflows",
        ".agent/templates",
        ".cursor/agents",
        ".claude/agents",
    ]:
        paths.update(
            p
            for p in (root / prefix).rglob("*")
            if p.is_file() and p.suffix in [".md", ".ps1", ".sh", ".svg"]
        )
    for path in paths:
        name = path.relative_to(root).as_posix()
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            require(
                not re.search(
                    r"(?i)(?:--?(?:model)?class[ =]+|resolve\s+)[`'\"]?"
                    r"(?:builder|coordinator|verifier)\b|"
                    r"class pins[^\{]*\{[^}]*\b(?:builder|coordinator|verifier)\b",
                    line,
                ),
                f"global routing class on active caller: {name}",
            )
            signature = hashlib.sha256(line.encode()).hexdigest()
            if (name, signature) in known:
                continue  # Individually classified dated observations and loader data.
            require(
                not re.search(
                    r"(?i)(?:default (?:reviewer|model)|fallback)\s*:\s*"
                    r"(?:GPT|Gemini|Claude|Opus|Sonnet|Grok)",
                    line,
                ),
                f"unconfigured live routing: {name}",
            )
            if numeric.search(line):
                require(
                    re.match(
                        r"Historical observation \(\d{4}-\d{2}-\d{2}\): .+ was measured\.$", line
                    ),
                    f"uncensused model pin: {name}",
                )


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Refuse(f"module unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    sys.path.insert(0, str(path.parent))
    spec.loader.exec_module(module)
    return module


def explicit_vendor_exception(root: Path, binding: dict, status: dict) -> None:
    """Validate this project's user-authorized CLI exception, never infer consent."""
    exception = binding.get("vendor_exception")
    if not isinstance(exception, dict):
        raise Refuse("same-vendor reviewer requires explicit authorization")
    require(exception["source"] == "USER_EXPLICIT", "authorization is not from the user")
    require(
        exception["target_plan"] == binding["target_plan"]
        and exception["loop_id"] == binding["loop_id"],
        "authorization target or loop mismatch",
    )
    require(
        exception["model"] == status["model"] == "gpt-6-astra"
        and exception["effort"] == status["reasoning_effort"] == "xhigh"
        and exception["author_vendor"]
        == binding["author_vendor"]
        == status["author_vendor"]
        == "openai"
        and exception["reviewer_vendor"] == binding["reviewer_vendor"] == "openai"
        and status["model_class"] == "avkit_independent_reviewer"
        and status["loop_id"] == binding["loop_id"],
        "dispatch does not match the authorized reviewer",
    )
    decision = inside(root, exception["decision_path"])
    require(digest(decision) == exception["decision_sha256"], "authorization record drift")
    reference = exception["trusted_user_message_reference"]
    text = decision.read_text(encoding="utf-8")
    require(
        reference == "I approve dispetching to review to codex cli gpt-6-astra xhigh"
        and reference in text
        and "USER_EXPLICIT" in text,
        "missing trusted user authorization reference",
    )
    # The receiving orchestrator attests the actual chat provenance. A file alone
    # cannot authorize a dispatch; approval still requires the independent verdict.


def approval(root: Path, loop_id: str) -> None:
    binding = document(root / PLAN / "review-binding.json")
    plan = root / PLAN / "implementation-plan.md"
    target = (PLAN / "implementation-plan.md").as_posix()
    require(
        binding["loop_id"] == loop_id and binding["target_plan"] == target,
        "approval target or loop mismatch",
    )
    require(binding["plan_sha256"] == digest(plan), "stale approval plan identity")
    report = inside(root, binding["report_path"])
    require(digest(report) == binding["report_sha256"], "stale review report")
    meta = yaml.safe_load(report.read_text(encoding="utf-8").split("---", 2)[1])
    require(
        meta["review_mode"] == "execution" and meta["target_plan"] == target,
        "wrong review mode or target",
    )
    require(meta["verdict"] == "approved", "review is not approved")
    raw = Path(binding["raw_verdict_path"])
    require(digest(raw) == binding["raw_verdict_sha256"], "raw verdict drift")
    ledger_tool = load_module(root / "tools/review_ledger.py", "adoption_review_ledger")
    try:
        ledger = ledger_tool.load_ledger(loop_id)
        verdict = ledger_tool.load_verdict(raw)
    except (ledger_tool.Refuse, ledger_tool.FailClosed) as exc:
        raise Refuse(str(exc)) from exc
    require(
        ledger["review_mode"] == "execution" and ledger["producer"] == binding["producer"],
        "ledger kind or producer mismatch",
    )
    require(
        Path(ledger["target_plan"]).resolve() == plan.resolve(),
        "ledger target mismatch",
    )
    require(ledger["instrument_digest"] == ledger_tool.instrument_digest(), "review schema drift")
    require(ledger["ac_ids"] == ledger_tool.load_ac_ids(plan), "review AC identity drift")
    require(ledger["goal_anchor"] == binding["goal_anchor"], "loop intent mismatch")
    require(
        ledger_tool.normalize_anchor(ledger["goal_anchor"])
        in ledger_tool.normalize_anchor(verdict["intent_anchor"]),
        "verdict intent mismatch",
    )
    cap = ledger_tool.rounds_allowed(ledger)
    require(cap == binding["effective_cap"], "unmatched continuation cap")
    for grant in ledger.get("grants", []):
        require(
            isinstance(grant.get("owner"), str)
            and grant["owner"].strip()
            and isinstance(grant.get("said"), str)
            and len("".join(grant["said"].split())) >= ledger_tool.MIN_RATIONALE,
            "invalid human continuation",
        )
        ledger_tool.datetime.datetime.fromisoformat(grant["granted"])
    final = ledger["rounds"][-1]
    require(
        meta["findings_count"] == len(verdict["findings"]) == len(final["findings"]),
        "review findings count mismatch",
    )
    require(
        meta["round"]
        == binding["round"]
        == verdict["round"]
        == final["round"]
        == len(ledger["rounds"])
        <= cap,
        "review round mismatch or cap exceeded",
    )
    require(
        verdict["loop_id"] == loop_id
        and verdict["target_plan"] == target
        and verdict["review_mode"] == "execution",
        "verdict target mismatch",
    )
    require(
        verdict["agent"] == final["agent"] != ledger["producer"], "self review or agent mismatch"
    )
    require(
        final["verdict"] == verdict["verdict"] == "approved"
        and final["blocking"] == 0
        and verdict["intent_achieved"] == "yes"
        and not any(f["blocking"] for f in verdict["findings"]),
        "unresolved review findings",
    )
    if binding["route"] == "machine":
        status_path = Path(binding["status_path"])
        require(digest(status_path) == binding["status_sha256"], "dispatch status drift")
        status = document(status_path)
        if binding["author_vendor"] == binding["reviewer_vendor"]:
            explicit_vendor_exception(root, binding, status)
        require(
            status["schema_version"] == "dispatch-status.v1"
            and status["exit_code"] == 0
            and status["child_exit_code"] == 0,
            "unsuccessful dispatch",
        )
        require(
            Path(status["output_paths"]["final_output"]).resolve() == raw.resolve(),
            "dispatch output mismatch",
        )
    elif binding["route"] == "human":
        decision = inside(root, binding["human_decision_path"])
        require(binding["human_observer"] == verdict["agent"] == "Mat", "unknown human reviewer")
        require(digest(decision) == binding["human_decision_sha256"], "human decision drift")
        text = decision.read_text(encoding="utf-8")
        reference = binding["trusted_user_message_reference"]
        require(
            isinstance(reference, str)
            and bool(reference.strip())
            and reference in text
            and "USER_EXPLICIT" in text,
            "missing trusted user decision reference",
        )
        # Provenance is attested by the receiving orchestrator. A file alone never
        # grants permission to create this binding; the real chat decision is required.
    else:
        raise Refuse("unknown review route")


def metrics(root: Path, data: dict) -> None:
    p = root / "docs/execution/metrics.md"
    text = p.read_text(encoding="utf-8")
    import base64

    original = next(e for e in data["files"] if e["path"] == "docs/execution/metrics.md")
    before = base64.b64decode(original["preimage_base64"]).decode("utf-8")
    require(text.startswith(before), "historical metrics changed")
    additions = text[len(before) :]
    rows = [line for line in additions.splitlines() if "framework-update-adoption" in line]
    require(len(rows) == 1 and "2026-09-26" in rows[0], "missing unique metrics row")
    require(all(cell.strip() for cell in rows[0].strip("|").split("|")), "empty metrics cell")


def final(root: Path, data: dict, *, closeout: bool) -> None:
    static(root)
    rows = task_rows(root / PLAN / "task.md")
    required = [
        key
        for key in rows
        if (
            key in ["0", "1", "1a", "1b", "2", "3", "4", "5", "6"]
            or (closeout and key not in ["H2-4", "H2-5"])
        )
    ]
    require(all(rows[key][-1] in ["[x]", "[B]"] for key in required), "incomplete task rows")
    for key in required:
        if rows[key][-1] == "[B]":
            tool = load_module(root / "tools/durable_evidence.py", "adoption_durable_evidence")
            task = root / PLAN / "task.md"
            require(
                not tool.blocked_evidence_problems(
                    " | ".join(rows[key]), key, task.read_text(encoding="utf-8"), task
                ),
                f"invalid blocker: {key}",
            )
    if closeout:
        approval(root, "framework-update-adoption-execution")
        metrics(root, data)
        for name in [
            ".agent/context/handoffs/2026-09-26-framework-update-adoption-handoff.md",
            "docs/execution/reflections/2026-09-26-framework-update-adoption-reflection.md",
        ]:
            require((root / name).is_file(), f"missing closeout artifact: {name}")


def live_runtime_identity() -> dict:
    """Observe runtime inputs now; a saved description is not a live observation."""
    variables = [
        "RECEIPTS_DIR",
        "AGENT_MODEL_REGISTRY_HOME",
        "AGENT_MODEL_REGISTRY",
        "PYTHONPATH",
        "PYRIGHT_PYTHON_FORCE_VERSION",
        "PYTHONIOENCODING",
        "ELECTRON_RUN_AS_NODE",
        "VIRTUAL_ENV",
        "PATH",
    ]
    registry = os.environ.get("AGENT_MODEL_REGISTRY")
    if not registry and os.environ.get("AGENT_MODEL_REGISTRY_HOME"):
        registry = str(Path(os.environ["AGENT_MODEL_REGISTRY_HOME"]) / "model-registry.json")
    selected = None
    if registry:
        path = Path(registry).resolve()
        require(path.is_file(), f"selected registry unavailable: {path}")
        selected = {"path": str(path), "sha256": digest(path)}
    executables = {}
    for name in ["rtk", "uv", "pwsh", "git"]:
        resolved = shutil.which(name)
        require(resolved, f"runtime executable unavailable: {name}")
        path = Path(str(resolved)).resolve()
        executables[name] = {"path": str(path), "sha256": digest(path)}
    return {
        "platform": sys.platform,
        "python": sys.version,
        "python_executable": str(Path(sys.executable).resolve()),
        "python_sha256": digest(Path(sys.executable)),
        "variables": {key: os.environ.get(key) for key in variables},
        "distributions": sorted(
            (d.metadata["Name"], d.version) for d in importlib.metadata.distributions()
        ),
        "executables": executables,
        "selected_registry": selected,
    }


def stage_identity(config: Path, spec: dict) -> str:
    material = {
        "config": digest(config),
        "inputs": {str(p): digest(Path(p)) for p in spec["inputs"]},
        "live_runtime": live_runtime_identity(),
    }
    if spec.get("task_path"):
        text = Path(spec["task_path"]).read_text(encoding="utf-8")
        material["live_task_contract"] = [
            "|".join(line.split("|")[:-2])
            for line in text.splitlines()
            if re.match(r"^\| (?:[0-6]|1[ab]|H[12]-[1-7]) \|", line)
        ]
    return hashlib.sha256(json.dumps(material, sort_keys=True).encode()).hexdigest()


def stages(config: Path, output: Path, *, verify_only: bool) -> bool:
    spec = document(config)
    identity = stage_identity(config, spec)
    require(
        [s["phase"] for s in spec["stages"]] == ["static", "targeted", "full"],
        "invalid validation stage order",
    )
    if verify_only:
        evidence = document(output)
        require(evidence["tested_state"] == identity, "stale validation inputs")
        require(
            len(evidence["stages"]) == 3
            and all(r["result"] == "pass" and r["exit_code"] == 0 for r in evidence["stages"]),
            "incomplete successful stage evidence",
        )
        return True
    records = []
    passing = True
    for stage in spec["stages"]:
        argv = stage["argv"]
        require(
            isinstance(argv, list) and argv and all(isinstance(x, str) for x in argv),
            "invalid stage argv",
        )
        if passing:
            result = command(argv, Path(stage["cwd"]))
            passing = result.returncode == 0
            record = dict(
                stage,
                result="pass" if passing else "fail",
                exit_code=result.returncode,
                output=result.stdout + result.stderr,
            )
        else:
            record = dict(
                stage, result="not_run", exit_code=None, output="Earlier blocking stage failed"
            )
        records.append(record)
    require(stage_identity(config, spec) == identity, "validation inputs changed during run")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"tested_state": identity, "stages": records}, indent=2), encoding="utf-8"
    )
    return passing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "mode",
        choices=[
            "baseline",
            "static",
            "final",
            "approval",
            "metrics",
            "closeout",
            "stages",
            "stage-state",
        ],
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--source", type=Path, default=Path("P:/agentic-framework"))
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--loop-id", default="framework-update-adoption-execution")
    parser.add_argument("--stage-config", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.mode in ["stages", "stage-state"]:
            require(args.stage_config and args.output, "stage config and output required")
            require(
                stages(args.stage_config, args.output, verify_only=args.mode == "stage-state"),
                "blocking validation stage failed",
            )
        elif args.mode == "approval":
            approval(args.root, args.loop_id)
        else:
            require(args.manifest, "manifest required")
            data = document(args.manifest)
            source_state(args.source, data)
            if args.mode in ["baseline", "final", "closeout"]:
                file_state(args.root, data, baseline=args.mode == "baseline")
            if args.mode == "static":
                static(args.root)
            elif args.mode in ["final", "closeout"]:
                final(args.root, data, closeout=args.mode == "closeout")
            elif args.mode == "metrics":
                metrics(args.root, data)
    except (OSError, ValueError, KeyError, TypeError, IndexError, ImportError) as exc:
        print(f"REFUSE: {exc}")
        return 1
    print(f"OK: {args.mode} contract satisfied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
