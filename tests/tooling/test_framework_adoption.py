"""Exercise the adoption's real boundaries, including refusal and freshness paths."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PLAN = Path("docs/execution/plans/2026-09-26-framework-update-adoption")
RULE_MAP = PLAN / "rule-preservation.md"
INSTRUCTIONS = ("AGENTS.md", "GUARDRAILS.md")
HELPER = ROOT / PLAN / "checks/verify_adoption.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_dir(root: Path) -> Path:
    """The throwaway framework source repo that sits beside a fixture root."""
    return root.parent / "source"


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return result.stdout.strip()


def commit_source(root: Path, files: dict[str, bytes]) -> str:
    """Commit files to a clean single-commit source repo for root; return its HEAD."""
    repo = source_dir(root)
    for name, data in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    git(repo, "init", "-q")
    for key, value in [
        ("user.name", "fixture"),
        ("user.email", "fixture@example.invalid"),
        ("core.autocrlf", "false"),
        ("commit.gpgsign", "false"),
    ]:
        git(repo, "config", key, value)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--no-verify", "-m", "fixture source")
    return git(repo, "rev-parse", "HEAD")


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def run(script: Path, *args: object, env: dict[str, str] | None = None):
    assert script.is_file(), f"required implementation missing: {script.name}"
    return subprocess.run(
        [sys.executable, str(script), *map(str, args)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=ROOT,
        env=os.environ | {"RECEIPTS_DIR": "C:/Temp/av-kit"} | (env or {}),
        check=False,
    )


def verify(root: Path, mode: str, *args: object):
    return run(
        HELPER,
        mode,
        "--root",
        root,
        "--source",
        source_dir(root),
        "--manifest",
        root / "manifest.json",
        *args,
    )


MACHINE_TOOLS = Path("P:/.agent")
TOOL_FILES = (
    "tools/resolve_model.py",
    "tools/ModelRegistry.psm1",
    "schema/model-registry.v1.schema.json",
)
FIXTURE = ROOT / "tests/tooling/fixtures/registry-home/model-registry.json"
OVERLAY = Path(".agent/model-registry.local.yaml")


def build_registry_home(dest: Path) -> dict:
    """A temp registry home: the machine resolver's code, the tracked fixture, a compiled overlay.

    Only the tool files come from MACHINE_TOOLS. The registry is FIXTURE, strictly validated
    here, and the project overlay is compiled against it in a temp project, so no test reads
    or writes the machine registry or the tracked compiled overlay.
    """
    home = dest / "home"
    for rel in TOOL_FILES:
        assert (MACHINE_TOOLS / rel).is_file(), f"machine resolver file missing: {rel}"
        (home / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(MACHINE_TOOLS / rel, home / rel)
    registry = home / "model-registry.json"
    shutil.copyfile(FIXTURE, registry)
    resolver = home / "tools/resolve_model.py"
    env = {"AGENT_MODEL_REGISTRY": str(registry)}
    checked = run(resolver, "validate", "--registry", registry, "--strict", env=env)
    assert checked.returncode == 0, checked.stdout + checked.stderr
    project = dest / "project"
    overlay = project / OVERLAY
    overlay.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / OVERLAY, overlay)
    compiled = run(resolver, "validate", "--overlay", overlay, "--write-compiled", env=env)
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    return {"resolver": resolver, "project": project, "env": env}


def test_ac_2_fixture_registry_home_compiles(tmp_path):
    import yaml

    assert FIXTURE.is_file(), "registry fixture missing: run make_fixture.py beside it"
    home = build_registry_home(tmp_path)
    compiled = home["project"] / ".agent/model-registry.local.json"
    stamp = json.loads(compiled.read_text(encoding="utf-8"))["validated_against"]
    assert stamp == sha(FIXTURE)
    data = yaml.safe_load((ROOT / OVERLAY).read_text(encoding="utf-8"))
    data["classes"]["avkit_coordinator"]["bindings"]["cursor-task"]["slug"] = "invented"
    bad = tmp_path / "invented.yaml"
    bad.write_text(yaml.safe_dump(data), encoding="utf-8")
    result = run(home["resolver"], "validate", "--overlay", bad, env=home["env"])
    assert result.returncode != 0, result.stdout + result.stderr
    assert "unknown_slug" in result.stderr, result.stdout + result.stderr


@pytest.fixture(scope="module")
def registry_home(tmp_path_factory):
    return build_registry_home(tmp_path_factory.mktemp("registry-home"))


def fixture_wrapper(dest: Path, project: Path) -> Path:
    """A byte copy of the dispatch wrapper whose project root is the fixture project."""
    data = (ROOT / "tools/Invoke-CodexDispatch.ps1").read_bytes()
    needle = b"$dispatchProjectRoot = 'P:/av-kit'"
    assert data.count(needle) == 1, "the wrapper's project-root line is not unique"
    root_line = f"$dispatchProjectRoot = '{project.as_posix()}'".encode()
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / "Invoke-CodexDispatch.ps1"
    target.write_bytes(data.replace(needle, root_line))
    return target


@pytest.fixture
def baseline(tmp_path: Path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "product.txt").write_text("user-owned bytes", encoding="utf-8")
    (root / "allowed.txt").write_text("before", encoding="utf-8")
    data = {
        "schema_version": "avkit-adoption.v1",
        "source_sha": commit_source(root, {"README.md": b"fixture source\n"}),
        "files": [
            {
                "path": "allowed.txt",
                "preimage_sha256": sha(root / "allowed.txt"),
                "absent_at_start": False,
                "source_path": None,
                "source_sha256": None,
                "postimage_sha256": None,
            }
        ],
        "protected_files": [{"path": "product.txt", "preimage_sha256": sha(root / "product.txt")}],
        "bootstrap_paths": [],
        "initial_paths": ["allowed.txt", "product.txt", "manifest.json"],
    }
    write_json(root / "manifest.json", data)
    return root, data


def test_verifier_bootstrap_accepts_captured_bytes(baseline):
    root, _ = baseline
    result = verify(root, "baseline")
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("path", ["product.txt", "allowed.txt"])
def test_verifier_bootstrap_refuses_drift_without_restoring(baseline, path):
    root, _ = baseline
    (root / path).write_text("concurrent edit", encoding="utf-8")
    result = verify(root, "baseline")
    assert result.returncode == 1 and "drift" in result.stdout.lower()
    assert (root / path).read_text() == "concurrent edit"


def test_verifier_bootstrap_refuses_source_revision_change(baseline):
    root, data = baseline
    data["source_sha"] = "0" * 40
    write_json(root / "manifest.json", data)
    result = verify(root, "baseline")
    assert result.returncode == 1 and "source" in result.stdout.lower()


@pytest.mark.parametrize("path", ["../outside.txt", "P:/outside.txt"])
def test_verifier_bootstrap_rejects_path_escape(baseline, path):
    root, data = baseline
    data["files"][0]["path"] = path
    write_json(root / "manifest.json", data)
    result = verify(root, "baseline")
    assert result.returncode == 1 and "path" in result.stdout.lower()


def test_verifier_bootstrap_new_unlisted_file_refused(baseline):
    root, _ = baseline
    (root / "intruder.txt").write_text("unexpected", encoding="utf-8")
    result = verify(root, "baseline")
    assert result.returncode == 1 and "allow" in result.stdout.lower()


def test_verifier_bootstrap_declared_bootstrap_exception(baseline):
    root, data = baseline
    data["bootstrap_paths"] = ["allowed.txt"]
    write_json(root / "manifest.json", data)
    (root / "allowed.txt").write_text("implemented helper", encoding="utf-8")
    result = verify(root, "baseline")
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("tool", ["lint_task_contract.py", "validate_closeout_artifacts.py"])
def test_evidence_contract_real_cli_selftests(tool):
    result = run(ROOT / "tools" / tool, "--selftest")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "0 failure" in result.stdout


def test_evidence_contract_missing_ac_rejected(tmp_path):
    plan, handoff = tmp_path / "plan.md", tmp_path / "handoff.md"
    plan.write_text("| AC-1 | one |\n| AC-2 | two |\n", encoding="utf-8")
    handoff.write_text("| AC-1 | done |\n", encoding="utf-8")
    result = run(
        ROOT / "tools/validate_closeout_artifacts.py",
        "--handoff",
        handoff,
        "--plan",
        plan,
        "--ac-coverage-only",
    )
    assert result.returncode == 1 and "AC-2" in result.stdout


def test_legacy_review_checker_remains_compatible():
    result = run(ROOT / "tools/check_exec_review.py", "--self-test")
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "verdict,target,round_number,expected",
    [
        ("approved", "plan.md", 1, 0),
        ("changes_required", "plan.md", 1, 1),
        ("approved", "other.md", 1, 1),
        ("approved", "plan.md", 7, 1),
    ],
)
def test_review_pipeline_target_bound_approval(tmp_path, verdict, target, round_number, expected):
    report, state = tmp_path / "review.md", tmp_path / "state.json"
    report.write_text(
        f"---\nreview_mode: execution\ntarget_plan: {target}\nround: {round_number}\n"
        f"verdict: {verdict}\nfindings_count: 0\n---\n\nOld body: approved\n",
        encoding="utf-8",
    )
    tool = ROOT / "tools/validate_closeout_artifacts.py"
    common = [
        "--review",
        report,
        "--expected-review-mode",
        "execution",
        "--expected-target-plan",
        "plan.md",
        "--max-review-rounds",
        "6",
    ]
    first = run(tool, *common, "--review-state-only", "--output", state)
    if first.returncode:
        assert expected == 1
    else:
        second = run(tool, *common, "--review-state-receipt", state, "--approved-state-only")
        assert second.returncode == expected, second.stdout + second.stderr


def test_review_pipeline_raw_bytes_and_null_semantics(tmp_path):
    document, backup, schema = [tmp_path / p for p in ("output.json", "raw.json", "schema.json")]
    raw = '{\r\n"manual": null, "optional": null, "unknown": null, "text": "café"\r\n}'
    document.write_bytes(raw.encode("utf-8"))
    write_json(
        schema,
        {
            "type": "object",
            "properties": {
                "manual": {"type": ["string", "null"]},
                "optional": {"type": "string"},
                "text": {"type": "string"},
            },
            "required": ["manual"],
            "additionalProperties": False,
        },
    )
    result = run(
        ROOT / "tools/adapt_output_schema.py",
        "strip-nulls",
        document,
        "--schema",
        schema,
        "--raw-copy",
        backup,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert backup.read_bytes() == raw.encode("utf-8")
    assert json.loads(document.read_text(encoding="utf-8")) == {
        "manual": None,
        "unknown": None,
        "text": "café",
    }


def test_review_pipeline_ledger_adversarial_selftest(tmp_path):
    result = run(ROOT / "tools/review_ledger.py", "selftest", env={"RECEIPTS_DIR": str(tmp_path)})
    assert result.returncode == 0, result.stdout + result.stderr
    assert "0 failure" in result.stdout


@pytest.mark.parametrize("fail_static", [False, True])
def test_validation_stages_stop_and_bind_inputs(tmp_path, fail_static):
    inputs = tmp_path / "input.py"
    inputs.write_text("original", encoding="utf-8")
    config, output = tmp_path / "stages.json", tmp_path / "results.json"
    write_json(
        config,
        {
            "inputs": [str(inputs)],
            "stages": [
                {
                    "phase": phase,
                    "argv": [sys.executable, "-c", f"raise SystemExit({code})"],
                    "cwd": str(tmp_path),
                }
                for phase, code in [("static", int(fail_static)), ("targeted", 0), ("full", 0)]
            ],
        },
    )
    result = run(HELPER, "stages", "--stage-config", config, "--output", output)
    assert result.returncode == int(fail_static), result.stdout + result.stderr
    records = json.loads(output.read_text())
    assert [r["result"] for r in records["stages"]] == (
        ["fail", "not_run", "not_run"] if fail_static else ["pass", "pass", "pass"]
    )
    if not fail_static:
        valid = run(HELPER, "stage-state", "--stage-config", config, "--output", output)
        assert valid.returncode == 0
        inputs.write_text("mutated", encoding="utf-8")
        stale = run(HELPER, "stage-state", "--stage-config", config, "--output", output)
        assert stale.returncode == 1 and "stale" in stale.stdout.lower()


@pytest.mark.parametrize(
    "class_name,harness,expected",
    [
        ("avkit_coordinator", "cursor-task", "cursor-grok-4.6-xhigh"),
        ("avkit_coordinator", "claude-p", "claude-opus-5"),
        ("avkit_builder", "cursor-task", "cursor-grok-4.6-xhigh"),
        ("avkit_builder", "claude-code-agents", "sonnet"),
        ("avkit_verifier", "cursor-task", "composer-2.5-fast"),
        ("avkit_verifier", "claude-code-agents", "sonnet"),
        ("avkit_router", "claude-code-agents", "haiku"),
    ],
)
def test_registry_contract_preserves_bindings(class_name, harness, expected, registry_home):
    result = run(
        registry_home["resolver"],
        "resolve",
        class_name,
        "--harness",
        harness,
        "--project",
        registry_home["project"],
        "--format",
        "json",
        env=registry_home["env"],
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert expected in result.stdout


@pytest.mark.parametrize("author,expected", [("openai", 1), ("anthropic", 0)])
def test_registry_contract_vendor_independence(author, expected, registry_home):
    result = run(
        registry_home["resolver"],
        "resolve",
        "avkit_independent_reviewer",
        "--harness",
        "codex-cli",
        "--project",
        registry_home["project"],
        "--author-vendor",
        author,
        "--format",
        "json",
        env=registry_home["env"],
    )
    assert (result.returncode != 0) == bool(expected), result.stdout + result.stderr
    assert ("vendor_diversity_violation" if expected else "gpt-6.1-sol") in (
        result.stderr if expected else result.stdout
    )


def test_registry_contract_unsupported_harness_refused(registry_home):
    result = run(
        registry_home["resolver"],
        "resolve",
        "avkit_coordinator",
        "--harness",
        "claude-code-agents",
        "--project",
        registry_home["project"],
        "--format",
        "json",
        env=registry_home["env"],
    )
    assert result.returncode != 0 and "unresolvable_on_harness" in result.stderr


def build_migrated_tree(dest: Path, overrides: dict[str, bytes] | None = None) -> Path:
    """Copy actual adopted bytes; each negative case mutates its own isolated tree.

    The source repo holds a file at each source_path with its recorded digest, so
    the source checks pass on their own and each case reaches its static oracle.
    An override (POSIX relative path -> bytes) stands in for that path's live bytes;
    an override for a path outside the manifest is not copied.
    """
    overrides = overrides or {}
    root = dest / "root"
    data = json.loads((ROOT / PLAN / "adoption-manifest.json").read_text(encoding="utf-8"))
    for entry in data["files"] + data["protected_files"]:
        path = Path(entry["path"])
        source, target = ROOT / path, root / path
        if path.as_posix() in overrides:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(overrides[path.as_posix()])
        elif source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    copy_backlink_targets(root, overrides)
    rebind_instruction_pins(root)
    sources: dict[str, bytes] = {}
    for entry in data["files"]:
        if entry.get("source_path"):
            sources[entry["source_path"]] = entry["source_path"].encode("utf-8")
            entry["source_sha256"] = hashlib.sha256(sources[entry["source_path"]]).hexdigest()
    data["source_sha"] = commit_source(root, sources)
    write_json(root / "manifest.json", data)
    return root


def instruction_links(text: str) -> list[str]:
    """Relative link targets, by the verifier's own regex, skip rule and `#` split."""
    links = []
    for link in re.findall(r"\]\(([^)]+)\)", text):
        if re.match(r"(?:https?:|#|mailto:)", link):
            continue
        links.append(link.split("#", 1)[0])
    return links


def copy_backlink_targets(root: Path, overrides: dict[str, bytes]) -> None:
    """Copy in each instruction link target the tree lacks; one level, each file once.

    A target that neither the overrides nor ROOT holds stays missing, so the verifier
    still refuses a broken link.
    """
    for name in INSTRUCTIONS:
        copied = root / name
        if not copied.is_file():
            continue
        for link in instruction_links(copied.read_text(encoding="utf-8")):
            rel = Path(link)
            if not link or rel.is_absolute() or rel.drive or ".." in rel.parts:
                continue  # the verifier refuses these itself
            target = root / rel
            if target.exists():
                continue
            if rel.as_posix() in overrides:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(overrides[rel.as_posix()])
            elif (ROOT / rel).is_file():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, target)


def rule_map_counts(path: Path) -> dict:
    """The rule map's `counts`, from its one JSON block, by the verifier's regex."""
    blocks = re.findall(r"```json\s*\n(.*?)\n```", path.read_text(encoding="utf-8"), re.S)
    assert len(blocks) == 1, f"the rule map has {len(blocks)} JSON blocks: {path}"
    return json.loads(blocks[0])["counts"]


def rebind_instruction_pins(root: Path) -> None:
    """Pin the copied rule map to the copied instruction files, bytewise (CRLF kept)."""
    rule_map = root / RULE_MAP
    counts = rule_map_counts(rule_map)
    data = rule_map.read_bytes()
    for name in INSTRUCTIONS:
        old = counts[name]["postimage_sha256"].encode()
        assert data.count(old) == 1, f"the rule map pin for {name} is not unique"
        data = data.replace(old, sha(root / name).encode())
    rule_map.write_bytes(data)


def tracked_pin_mismatches(root: Path) -> list[str]:
    """One message per instruction file whose rule-map pin no longer matches it."""
    counts = rule_map_counts(root / RULE_MAP)
    messages = []
    for name in INSTRUCTIONS:
        old, new = counts[name]["postimage_sha256"], sha(root / name)
        if old == new:
            continue
        command = (
            'uv run python -c "import pathlib; '
            f"p=pathlib.Path('{RULE_MAP.as_posix()}'); b=p.read_bytes(); "
            f"assert b.count(b'{old}')==1; "
            f"p.write_bytes(b.replace(b'{old}', b'{new}'))\""
        )
        messages.append(
            f"{name}: the rule map pins {old} but the file hashes to {new}. "
            "Check that the rule map still covers the edited file's blocks first, "
            "then commit the rebind alone (D-132, c34866b). "
            f"Rebind: {command}"
        )
    return messages


@pytest.fixture
def migrated_tree(tmp_path):
    return build_migrated_tree(tmp_path)


@pytest.mark.parametrize("mutation", ["none", "youtube", "template", "backlink", "routing"])
def test_review_pipeline_governance_static_oracles(migrated_tree, mutation):
    root = migrated_tree
    if mutation == "youtube":
        p = root / "AGENTS.md"
        p.write_text(
            p.read_text(encoding="utf-8").replace("YouTube", "OtherService"), encoding="utf-8"
        )
    elif mutation == "template":
        with (root / ".agent/templates/TASK-TEMPLATE.md").open("a", encoding="utf-8") as f:
            f.write("\nUnsynchronized content\n")
    elif mutation == "backlink":
        with (root / "AGENTS.md").open("a", encoding="utf-8") as f:
            f.write("\n[mandatory](.agent/docs/missing-required-policy.md)\n")
    elif mutation == "routing":
        with (root / ".agent/docs/model-routing.md").open("a", encoding="utf-8") as f:
            f.write("\nDefault reviewer: GPT-4.1. Fallback: Gemini.\n")
    result = verify(root, "static")
    assert result.returncode == (0 if mutation == "none" else 1), result.stdout + result.stderr


@pytest.mark.parametrize("mutation", ["registry", "rule-map", "fallback", "pin", "history"])
def test_governance_preservation_and_routing_inventory(migrated_tree, mutation):
    root = migrated_tree
    if mutation == "registry":
        p = root / ".agent/schemas/registry.yaml"
        p.write_text(
            p.read_text(encoding="utf-8").replace(
                'heading: "Project Context"', 'heading: "Missing section"'
            ),
            encoding="utf-8",
        )
    elif mutation == "rule-map":
        (root / PLAN / "rule-preservation.md").write_text("No mapping\n", encoding="utf-8")
    else:
        p = root / ".agent/roles/researcher.md"
        text = {
            "fallback": "Fallback: Gemini.\n",
            "pin": "Default model: GPT-4.1.\n",
            "history": "Historical observation (2026-01-01): GPT-4.1 was measured.\n",
        }[mutation]
        with p.open("a", encoding="utf-8") as stream:
            stream.write("\n" + text)
    result = verify(root, "static")
    assert result.returncode == (0 if mutation == "history" else 1), result.stdout + result.stderr


def test_ac_6_pin_follows_the_copied_instructions(tmp_path):
    agents = (ROOT / "AGENTS.md").read_bytes() + b"Fixture note appended after adoption.\r\n"
    root = build_migrated_tree(tmp_path, {"AGENTS.md": agents})
    result = verify(root, "static")
    assert result.returncode == 0, result.stdout + result.stderr


def test_ac_7_backlink_closure_copies_new_targets(tmp_path):
    link = b"[fixture policy](.agent/docs/fixture-new-policy.md)\r\n"
    overrides = {
        "AGENTS.md": (ROOT / "AGENTS.md").read_bytes() + link,
        ".agent/docs/fixture-new-policy.md": b"# Fixture policy\r\n",
    }
    root = build_migrated_tree(tmp_path, overrides)
    result = verify(root, "static")
    assert result.returncode == 0, result.stdout + result.stderr


def test_ac_8_pin_oracle_still_refuses(tmp_path):
    root = build_migrated_tree(tmp_path)
    rule_map = root / PLAN / "rule-preservation.md"
    data = rule_map.read_bytes()
    pin = sha(root / "AGENTS.md").encode()
    assert data.count(pin) == 1, "the copied rule map does not pin the copied AGENTS.md once"
    rule_map.write_bytes(data.replace(pin, b"0" * 64))
    result = verify(root, "static")
    assert result.returncode == 1, result.stdout + result.stderr
    assert "rule map identity mismatch" in result.stdout, result.stdout + result.stderr


def test_ac_14_tracked_rule_map_pin_matches_live_instructions(tmp_path):
    mismatches = tracked_pin_mismatches(ROOT)
    assert mismatches == [], "\n".join(mismatches)
    (tmp_path / RULE_MAP).parent.mkdir(parents=True)
    shutil.copyfile(ROOT / RULE_MAP, tmp_path / RULE_MAP)
    (tmp_path / "AGENTS.md").write_bytes((ROOT / "AGENTS.md").read_bytes() + b"\n")
    shutil.copyfile(ROOT / "GUARDRAILS.md", tmp_path / "GUARDRAILS.md")
    mismatches = tracked_pin_mismatches(tmp_path)
    assert len(mismatches) == 1, mismatches
    assert "AGENTS.md" in mismatches[0] and "p.write_bytes(" in mismatches[0], mismatches


@pytest.mark.parametrize("mutation", ["missing", "wrong-target", "unapproved", "forged-status"])
def test_review_pipeline_approval_rejects_uncorrelated_claims(baseline, mutation):
    root, _ = baseline
    binding = {
        "loop_id": "fixture",
        "target_plan": "wrong.md"
        if mutation == "wrong-target"
        else str(PLAN / "implementation-plan.md"),
        "verdict": "approved",
        "round": 1,
        "dispatch_exit_code": 0,
    }
    if mutation != "missing":
        if mutation == "unapproved":
            binding["verdict"] = "changes_required"
        write_json(root / PLAN / "review-binding.json", binding)
    result = verify(root, "approval", "--loop-id", "fixture")
    assert result.returncode == 1, result.stdout + result.stderr


def test_review_pipeline_closeout_requires_real_completion(baseline):
    root, _ = baseline
    result = verify(root, "closeout")
    assert result.returncode == 1, result.stdout + result.stderr


@pytest.mark.parametrize("fault", ["global-redefinition", "unknown-binding", "bad-explicit"])
def test_registry_contract_bad_configuration_refused(tmp_path, fault, registry_home):
    import yaml

    overlay = ROOT / ".agent/model-registry.local.yaml"
    assert overlay.is_file(), "project overlay missing"
    data = yaml.safe_load(overlay.read_text(encoding="utf-8"))
    if fault == "global-redefinition":
        data["classes"]["coordinator"] = data["classes"]["avkit_coordinator"]
    elif fault == "unknown-binding":
        data["classes"]["avkit_coordinator"]["bindings"]["cursor-task"]["slug"] = "invented"
    target = tmp_path / "overlay.yaml"
    target.write_text(yaml.safe_dump(data), encoding="utf-8")
    env = dict(registry_home["env"])
    if fault == "bad-explicit":
        env["AGENT_MODEL_REGISTRY"] = str(tmp_path / "absent.json")
        result = run(
            registry_home["resolver"],
            "resolve",
            "avkit_coordinator",
            "--harness",
            "cursor-task",
            "--project",
            registry_home["project"],
            "--format",
            "json",
            env=env,
        )
    else:
        result = run(registry_home["resolver"], "validate", "--overlay", target, env=env)
    assert result.returncode != 0, result.stdout + result.stderr


@pytest.mark.parametrize("route", ["machine", "human"])
def test_review_pipeline_correlated_approval_positive(tmp_path, route):
    """Fixture approval verifies structure only and never authorizes live work."""
    for name in ["review_ledger.py", "validate_closeout_artifacts.py", "durable_evidence.py"]:
        source = ROOT / "tools" / name
        assert source.is_file(), f"required implementation missing: {name}"
        dest = tmp_path / "tools" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
    for name in [
        ".agent/schemas/review-verdict.schema.v2.json",
        ".agent/context/review-vocabulary.yaml",
    ]:
        dest = tmp_path / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dest)
    plan = tmp_path / PLAN / "implementation-plan.md"
    plan.parent.mkdir(parents=True, exist_ok=True)
    plan.write_text("| AC-1 | Fixture acceptance |\n", encoding="utf-8")
    report = tmp_path / (
        ".agent/context/handoffs/2026-09-26-framework-update-ado"
        "ption-implementation-critical-review.md"
    )
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        f"---\nreview_mode: execution\ntarget_plan: {PLAN.as_posix()}/implementation-plan.md\n"
        "round: 1\nverdict: approved\nfindings_count: 0\n---\n",
        encoding="utf-8",
    )
    goal = "Verify the fixture implementation against the declared acceptance contract."
    reviewer = "Mat" if route == "human" else "fixture-independent-anthropic"
    verdict = {
        "schema_version": "review-verdict.v2",
        "date": "2026-09-26",
        "review_mode": "execution",
        "loop_id": "fixture",
        "round": 1,
        "target_plan": (PLAN / "implementation-plan.md").as_posix(),
        "agent": reviewer,
        "requested_verbosity": "standard",
        "verdict": "approved",
        "summary": "Fixture approved",
        "intent_anchor": goal,
        "intent_achieved": "yes",
        "findings": [],
        "checklist_results": [
            {
                "check": "fixture inspection",
                "result": "pass",
                "procedure": "Inspect fixture contract",
                "observer": reviewer,
                "exit_code": None,
                "evidence": "Fixture acceptance holds",
            }
        ],
    }
    raw = tmp_path / "raw.json"
    write_json(raw, verdict)
    env = {"RECEIPTS_DIR": str(tmp_path / "receipts")}
    ledger = tmp_path / "tools/review_ledger.py"
    opened = run(
        ledger,
        "begin",
        "--loop-id",
        "fixture",
        "--review-mode",
        "execution",
        "--producer",
        "fixture-coder-openai",
        "--goal-anchor",
        goal,
        "--ac-file",
        plan,
        "--vocabulary",
        tmp_path / ".agent/context/review-vocabulary.yaml",
        env=env,
    )
    assert opened.returncode == 0, opened.stdout + opened.stderr
    recorded = run(ledger, "record", "--loop-id", "fixture", "--verdict-file", raw, env=env)
    assert recorded.returncode == 0, recorded.stdout + recorded.stderr
    status = tmp_path / "status.json"
    write_json(
        status,
        {
            "schema_version": "dispatch-status.v1",
            "dispatch_id": "fixture",
            "exit_code": 0,
            "child_exit_code": 0,
            "author_vendor": "openai",
            "reviewer_vendor": "anthropic",
            "output_paths": {"final_output": str(raw)},
        },
    )
    decision = tmp_path / PLAN / "human-review-decision.md"
    decision.write_text(
        "Fixture only: USER_EXPLICIT Mat reviewed the fixture and approved.\n"
        "Chat reference: fixture-chat-message-1\n",
        encoding="utf-8",
    )
    binding = {
        "route": route,
        "loop_id": "fixture",
        "producer": "fixture-coder-openai",
        "target_plan": (PLAN / "implementation-plan.md").as_posix(),
        "round": 1,
        "plan_sha256": sha(plan),
        "report_path": str(report.relative_to(tmp_path)),
        "report_sha256": sha(report),
        "raw_verdict_path": str(raw),
        "raw_verdict_sha256": sha(raw),
        "status_path": str(status),
        "status_sha256": sha(status),
        "effective_cap": 6,
        "author_vendor": "openai",
        "reviewer_vendor": "anthropic",
        "goal_anchor": goal,
        "human_decision_path": str(decision.relative_to(tmp_path)),
        "human_decision_sha256": sha(decision),
        "human_observer": "Mat",
        "trusted_user_message_reference": "fixture-chat-message-1",
    }
    write_json(tmp_path / PLAN / "review-binding.json", binding)
    # Approval mode never reads the source repo, so a placeholder revision suffices.
    write_json(tmp_path / "manifest.json", {"source_sha": "f" * 40})
    result = run(
        HELPER,
        "approval",
        "--root",
        tmp_path,
        "--manifest",
        tmp_path / "manifest.json",
        "--loop-id",
        "fixture",
        env=env,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_review_pipeline_valid_continuation_preserves_approval(tmp_path):
    test_review_pipeline_correlated_approval_positive(tmp_path, "human")
    env = {"RECEIPTS_DIR": str(tmp_path / "receipts")}
    ledger = tmp_path / "tools/review_ledger.py"
    continued = run(
        ledger,
        "continue",
        "--loop-id",
        "fixture",
        "--rounds",
        "1",
        "--by",
        "Mat",
        "--at",
        "2026-09-26T12:00:00-04:00",
        "--said",
        "Fixture only: allow one further round while preserving all prior review history.",
        env=env,
    )
    assert continued.returncode == 0, continued.stdout + continued.stderr
    path = tmp_path / PLAN / "review-binding.json"
    binding = json.loads(path.read_text(encoding="utf-8"))
    binding["effective_cap"] = 7
    write_json(path, binding)
    state = json.loads((tmp_path / "receipts/review-ledger/fixture.json").read_text())
    assert len(state["rounds"]) == 1 and state["grants"][-1]["owner"] == "Mat"
    result = run(HELPER, "approval", "--root", tmp_path, "--loop-id", "fixture", env=env)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("wrong_target", [False, True])
def test_review_pipeline_ledger_binds_exact_plan(tmp_path, wrong_target):
    plan = tmp_path / "plan.md"
    plan.write_text("| AC-1 | Preserve exact review target |\n", encoding="utf-8")
    goal = "Verify that only this exact plan can satisfy the review loop."
    env = {"RECEIPTS_DIR": str(tmp_path / "receipts")}
    ledger = ROOT / "tools/review_ledger.py"
    opened = run(
        ledger,
        "begin",
        "--loop-id",
        "target-fixture",
        "--review-mode",
        "execution",
        "--producer",
        "fixture-author",
        "--goal-anchor",
        goal,
        "--ac-file",
        plan,
        env=env,
    )
    assert opened.returncode == 0, opened.stdout + opened.stderr
    verdict = {
        "schema_version": "review-verdict.v2",
        "date": "2026-09-26",
        "review_mode": "execution",
        "loop_id": "target-fixture",
        "round": 1,
        "target_plan": str(tmp_path / "plan.md.bak" if wrong_target else plan),
        "agent": "independent-fixture",
        "requested_verbosity": "standard",
        "verdict": "approved",
        "summary": "Fixture approval",
        "intent_anchor": goal,
        "intent_achieved": "yes",
        "findings": [],
        "checklist_results": [
            {
                "check": "fixture",
                "command": "fixture-check",
                "exit_code": 0,
                "result": "pass",
                "evidence": "Matched",
            }
        ],
    }
    raw = tmp_path / "verdict.json"
    write_json(raw, verdict)
    recorded = run(ledger, "record", "--loop-id", "target-fixture", "--verdict-file", raw, env=env)
    assert recorded.returncode == int(wrong_target), recorded.stdout + recorded.stderr
    if wrong_target:
        assert "target-plan-mismatch" in recorded.stdout
        state = json.loads((tmp_path / "receipts/review-ledger/target-fixture.json").read_text())
        assert state["rounds"] == []


@pytest.mark.parametrize(
    "fault",
    [
        "report-verdict",
        "raw-target",
        "status-exit",
        "status-output",
        "loop-intent",
        "loop-target",
        "continuation",
        "human-decision",
    ],
)
def test_review_pipeline_complete_approval_tampering(tmp_path, fault):
    route = "human" if fault == "human-decision" else "machine"
    test_review_pipeline_correlated_approval_positive(tmp_path, route)
    path = tmp_path / PLAN / "review-binding.json"
    binding = json.loads(path.read_text(encoding="utf-8"))
    if fault == "report-verdict":
        report = tmp_path / binding["report_path"]
        report.write_text(
            report.read_text().replace("verdict: approved", "verdict: changes_required")
        )
        binding["report_sha256"] = sha(report)
    elif fault == "raw-target":
        raw = Path(binding["raw_verdict_path"])
        value = json.loads(raw.read_text())
        value["target_plan"] = "other-plan.md"
        write_json(raw, value)
        binding["raw_verdict_sha256"] = sha(raw)
    elif fault.startswith("status-"):
        status = Path(binding["status_path"])
        value = json.loads(status.read_text())
        if fault == "status-exit":
            value["child_exit_code"] = 1
        else:
            value["output_paths"]["final_output"] = str(tmp_path / "unrelated.json")
        write_json(status, value)
        binding["status_sha256"] = sha(status)
    elif fault in ("loop-intent", "loop-target", "continuation"):
        ledger = tmp_path / "receipts/review-ledger/fixture.json"
        value = json.loads(ledger.read_text())
        if fault == "loop-intent":
            value["goal_anchor"] = "Review a completely different implementation instead."
        elif fault == "loop-target":
            value["target_plan"] = str(tmp_path / "other-plan.md")
        else:
            value["grants"] = [{"round": 1, "owner": "", "said": "", "granted": "", "rounds": 1}]
            binding["effective_cap"] = 7
        write_json(ledger, value)
    else:
        (tmp_path / binding["human_decision_path"]).unlink()
    write_json(path, binding)
    result = run(
        HELPER,
        "approval",
        "--root",
        tmp_path,
        "--manifest",
        tmp_path / "manifest.json",
        "--loop-id",
        "fixture",
        env={"RECEIPTS_DIR": str(tmp_path / "receipts")},
    )
    assert result.returncode == 1, result.stdout + result.stderr


@pytest.mark.parametrize("fault", ["same-vendor", "unknown-class", "bad-registry"])
def test_review_pipeline_wrapper_refuses_before_provider(tmp_path, fault, registry_home):
    marker = tmp_path / "provider-called.txt"
    provider = tmp_path / "fake-provider.cmd"
    provider.write_text(f'@echo off\necho called > "{marker}"\nexit /b 88\n')
    env = os.environ | {"RECEIPTS_DIR": "C:/Temp/av-kit"} | registry_home["env"]
    extra = []
    if fault == "unknown-class":
        extra = ["-ModelClass", "no_such_local_class"]
    if fault == "bad-registry":
        env["AGENT_MODEL_REGISTRY"] = str(tmp_path / "absent.json")
    result = subprocess.run(
        [
            "pwsh",
            "-NoProfile",
            "-File",
            str(fixture_wrapper(tmp_path / "wrapper", registry_home["project"])),
            "-NonReviewDispatch",
            "-AuthorVendor",
            "openai" if fault == "same-vendor" else "anthropic",
            "-PromptText",
            "fixture only",
            "-CodexExecutable",
            str(provider),
            *extra,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        cwd=ROOT,
        check=False,
    )
    assert result.returncode != 0, result.stdout + result.stderr
    assert not marker.exists(), result.stdout + result.stderr
    expected = {
        "same-vendor": "vendor_diversity_violation",
        "unknown-class": "unknown_class",
        "bad-registry": "registry_not_found",
    }[fault]
    assert expected in result.stdout + result.stderr


@pytest.mark.parametrize("mutation", ["environment", "registry", "task-validation", "task-status"])
def test_validation_stages_live_runtime_inputs(tmp_path, mutation):
    input_file = tmp_path / "input.py"
    input_file.write_text("stable input", encoding="utf-8")
    task = tmp_path / "task.md"
    task.write_text(
        "| 1 | Work | coder | result | check-a | — | shared | evidence | `[ ]` |\n",
        encoding="utf-8",
    )
    config, output = tmp_path / "stages.json", tmp_path / "result.json"
    write_json(
        config,
        {
            "inputs": [str(input_file)],
            "task_path": str(task),
            "stages": [
                {"phase": phase, "argv": [sys.executable, "-c", "pass"], "cwd": str(tmp_path)}
                for phase in ["static", "targeted", "full"]
            ],
        },
    )
    result = run(HELPER, "stages", "--stage-config", config, "--output", output)
    assert result.returncode == 0, result.stdout + result.stderr
    unchanged = run(HELPER, "stage-state", "--stage-config", config, "--output", output)
    assert unchanged.returncode == 0, unchanged.stdout + unchanged.stderr
    env = {}
    if mutation == "environment":
        env["ELECTRON_RUN_AS_NODE"] = "unexpected-runtime-mode"
    elif mutation == "registry":
        env["AGENT_MODEL_REGISTRY"] = str(tmp_path / "missing-registry.json")
    elif mutation == "task-validation":
        task.write_text(
            task.read_text(encoding="utf-8").replace("check-a", "check-b"), encoding="utf-8"
        )
    else:
        task.write_text(task.read_text(encoding="utf-8").replace("[ ]", "[x]"), encoding="utf-8")
    checked = run(HELPER, "stage-state", "--stage-config", config, "--output", output, env=env)
    assert checked.returncode == (0 if mutation == "task-status" else 1), (
        checked.stdout + checked.stderr
    )


@pytest.mark.parametrize(
    "class_name,expected",
    [
        ("avkit_builder", 0),
        ("avkit_coordinator", 0),
        ("avkit_verifier", 0),
        ("builder", 1),
        ("coordinator", 1),
        ("unregistered_avkit_builder", 1),
    ],
)
def test_registry_contract_registered_task_command(tmp_path, class_name, expected):
    import re
    import shlex

    doc = (ROOT / ".agent/docs/commands.md").read_text(encoding="utf-8")
    row = next(line for line in doc.splitlines() if line.startswith("| task-contract |"))
    match = re.search(r"`([^`]+)`", row)
    if match is None:
        raise ValueError("Registered task command is missing")
    command_text = match.group(1)
    argv = shlex.split(command_text)
    assert argv[:3] == ["uv", "run", "python"]
    template = (ROOT / "docs/execution/plans/TASK-TEMPLATE.md").read_text(encoding="utf-8")
    header = next(
        line for line in template.splitlines() if "| # |" in line and "builder_model" in line
    )
    path = tmp_path / "task.md"
    validation = (
        "rtk proxy uv run python tools/meu_status.py render --check "
        "*> C:/Temp/av-kit/fixture.txt; $code=$LASTEXITCODE; "
        "Get-Content C:/Temp/av-kit/fixture.txt; exit $code"
    )
    path.write_text(
        "## Task Table\n\n"
        + header
        + "\n|---|---|---|---|---|---|---|---|---|---|\n"
        + f"| 1 | Validate state | tester | State | `{validation}` | — | shared | "
        + f"docs/execution/metrics.md | `{class_name}` | `[ ]` |\n",
        encoding="utf-8",
    )
    argv = [str(path) if arg == "TASK" else arg for arg in argv[3:]]
    checked = run(ROOT / argv[0], *argv[1:])
    assert checked.returncode == expected, checked.stdout + checked.stderr


@pytest.mark.parametrize("wrong_count", [False, True])
def test_review_pipeline_approval_with_nonblocking_findings(tmp_path, wrong_count):
    test_review_pipeline_correlated_approval_positive(tmp_path, "human")
    raw = tmp_path / "raw.json"
    verdict = json.loads(raw.read_text(encoding="utf-8"))
    verdict["round"] = 2
    verdict["findings"] = [
        {
            "id": "OBS1",
            "severity": "Low",
            "confidence": "High",
            "blocking": False,
            "subject": "deliverable",
            "finding_kind": "clerical",
            "finding": "A minor explanatory label can be clearer.",
            "file_line": "fixture.md:1",
            "recommendation": "Clarify the label.",
            "status": "open",
        }
    ]
    write_json(raw, verdict)
    env = {"RECEIPTS_DIR": str(tmp_path / "receipts")}
    recorded = run(
        tmp_path / "tools/review_ledger.py",
        "record",
        "--loop-id",
        "fixture",
        "--verdict-file",
        raw,
        env=env,
    )
    assert recorded.returncode == 0, recorded.stdout + recorded.stderr
    binding_path = tmp_path / PLAN / "review-binding.json"
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    report = tmp_path / binding["report_path"]
    report.write_text(
        report.read_text(encoding="utf-8")
        .replace("round: 1", "round: 2")
        .replace("findings_count: 0", f"findings_count: {0 if wrong_count else 1}"),
        encoding="utf-8",
    )
    binding.update(round=2, report_sha256=sha(report), raw_verdict_sha256=sha(raw))
    write_json(binding_path, binding)
    checked = run(HELPER, "approval", "--root", tmp_path, "--loop-id", "fixture", env=env)
    assert checked.returncode == int(wrong_count), checked.stdout + checked.stderr


@pytest.mark.parametrize(
    "fault",
    [
        None,
        "missing",
        "source",
        "decision-drift",
        "reference",
        "target",
        "loop",
        "model",
        "effort",
        "author",
        "reviewer",
        "dispatch-model",
        "dispatch-loop",
    ],
)
def test_review_pipeline_explicit_vendor_exception(tmp_path, fault):
    """A real user exception is scoped; fixtures never authorize live reviews."""
    test_review_pipeline_correlated_approval_positive(tmp_path, "machine")
    binding_path = tmp_path / PLAN / "review-binding.json"
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    decision = tmp_path / PLAN / "human-review-decision.md"
    reference = "I approve dispetching to review to codex cli gpt-6-astra xhigh"
    decision.write_text(f"Fixture only: USER_EXPLICIT\n{reference}\n", encoding="utf-8")
    exception = {
        "source": "USER_EXPLICIT",
        "decision_path": decision.relative_to(tmp_path).as_posix(),
        "decision_sha256": sha(decision),
        "trusted_user_message_reference": reference,
        "target_plan": binding["target_plan"],
        "loop_id": binding["loop_id"],
        "model": "gpt-6-astra",
        "effort": "xhigh",
        "author_vendor": "openai",
        "reviewer_vendor": "openai",
    }
    binding["reviewer_vendor"] = "openai"
    binding["vendor_exception"] = exception
    status_path = Path(binding["status_path"])
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update(
        model="gpt-6-astra",
        reasoning_effort="xhigh",
        loop_id="fixture",
        model_class="avkit_independent_reviewer",
        author_vendor="openai",
    )
    if fault == "missing":
        del binding["vendor_exception"]
    elif fault == "source":
        exception["source"] = "SYSTEM_INJECTED"
    elif fault == "decision-drift":
        decision.write_text("No authorization", encoding="utf-8")
    elif fault == "reference":
        exception["trusted_user_message_reference"] = "Different request"
    elif fault in ("target", "loop", "model", "effort", "author", "reviewer"):
        key = {
            "target": "target_plan",
            "loop": "loop_id",
            "author": "author_vendor",
            "reviewer": "reviewer_vendor",
        }.get(fault, fault)
        exception[key] = "unrelated"
    elif fault == "dispatch-model":
        status["model"] = "different-model"
    elif fault == "dispatch-loop":
        status["loop_id"] = "another-loop"
    write_json(status_path, status)
    binding["status_sha256"] = sha(status_path)
    write_json(binding_path, binding)
    result = run(
        HELPER,
        "approval",
        "--root",
        tmp_path,
        "--manifest",
        tmp_path / "manifest.json",
        "--loop-id",
        "fixture",
        env={"RECEIPTS_DIR": str(tmp_path / "receipts")},
    )
    assert result.returncode == int(fault is not None), result.stdout + result.stderr


@pytest.mark.parametrize(
    "caller",
    [
        "Resolve-AgentModel -Class builder -Harness cursor-task",
        "builder_model column with class pins {builder|coordinator}",
    ],
)
def test_registry_contract_generic_class_census(migrated_tree, caller):
    path = migrated_tree / ".agent/roles/researcher.md"
    with path.open("a", encoding="utf-8") as stream:
        stream.write("\n" + caller + "\n")
    result = verify(migrated_tree, "static")
    assert result.returncode == 1, result.stdout + result.stderr
    assert "global routing class" in result.stdout
