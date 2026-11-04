"""Carry known-issue ids onto a freshly written MCP audit baseline (Session 30, LOCAL_SEQUENCE step 1).

``npm --prefix mcp-server run audit -- --update-baseline`` rewrites
``.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json`` without the ``issue`` ids that
``mcp-server/tests/audit/coverage.test.ts`` requires on every non-pass entry and finding
(``scripts/audit/run.ts:584-594``). ``BASELINE_ANNOTATION_RULE`` (``.agent/skills/mcp-tool-audit/SKILL.md``)
allows exactly one edit after an authoritative run: setting ``issue`` on non-pass entries and findings.

This script does only that, mechanically:

- an entry with ``status != "pass"`` gets the ``issue`` of the prior entry with the same tool, action and
  status;
- a finding gets the ``issue`` of the prior finding with the same code and tool;
- anything non-pass without such a prior issue is a new failure: the script changes nothing and exits 1,
  so the human files it first (``/mcp-audit`` step 5). It never invents an id.

Stdlib only. Usage::

    python baseline_carry.py --prior <copy of the committed baseline> --baseline <rewritten baseline>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def carry(prior: dict, new: dict) -> tuple[dict, list[str]]:
    """Return the new baseline with prior issue ids copied on, and the keys that have none."""
    by_entry = {
        (e["tool"], e["action"], e["status"]): e.get("issue")
        for e in prior.get("entries", [])
        if e.get("issue")
    }
    by_finding = {(f["code"], f["tool"]): f.get("issue") for f in prior.get("findings", []) if f.get("issue")}
    missing: list[str] = []
    for entry in new.get("entries", []):
        if entry["status"] == "pass":
            continue
        issue = by_entry.get((entry["tool"], entry["action"], entry["status"]))
        if issue:
            entry["issue"] = issue
        else:
            missing.append(f"entry {entry['tool']}.{entry['action']} ({entry['status']})")
    for finding in new.get("findings", []):
        issue = by_finding.get((finding["code"], finding["tool"]))
        if issue:
            finding["issue"] = issue
        else:
            missing.append(f"finding {finding['code']}:{finding['tool']}")
    return new, missing


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--prior", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    args = parser.parse_args()
    prior = json.loads(args.prior.read_text(encoding="utf-8"))
    new = json.loads(args.baseline.read_text(encoding="utf-8"))
    if new.get("schema") != "mcp-audit-baseline.v1" or new.get("mode") != "authoritative":
        print(f"FAIL: {args.baseline} is not an authoritative mcp-audit-baseline.v1")
        return 1
    if new.get("recorded_commit") == prior.get("recorded_commit"):
        print("FAIL: the baseline was not rewritten by this run (recorded_commit unchanged)")
        return 1
    updated, missing = carry(prior, new)
    if missing:
        print("FAIL: non-pass items with no prior issue (file them first; baseline left unchanged):")
        for item in missing:
            print(f"  {item}")
        return 1
    # Same serialization as writeBaselineIfAllowed (scripts/audit/classify.ts): 2-space JSON plus newline.
    args.baseline.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tagged = sum(1 for e in updated["entries"] if e.get("issue")) + sum(1 for f in updated["findings"] if f.get("issue"))
    print(f"PASS baseline_carry: {tagged} issue ids carried; {len(updated['entries'])} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
