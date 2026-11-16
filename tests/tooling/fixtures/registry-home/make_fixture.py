"""Write the synthetic model registry that the adoption tests resolve against (Session 76, D-911).

Usage, from anywhere::

    uv run python tests/tooling/fixtures/registry-home/make_fixture.py [--registry P] [--out P]

It reads the project overlay (``.agent/model-registry.local.yaml``) and a model registry
(``--registry``, default ``P:/.agent/model-registry.json``, read only) and writes
``model-registry.json`` beside this file, or ``--out``. Nothing else is written.

The output holds:

* ``schema_version``, ``updated`` and ``bump_gate``;
* a ``catalog`` of exactly the model ids the overlay binds or forbids, each with only
  ``vendor``, ``harness_ids``, ``price_band``, ``capabilities``, ``efforts`` and ``auth`` copied
  from the registry. Each bound id's ``capabilities`` are cut to the tokens that the overlay's
  contracts for it require; an id that is only forbidden carries ``["agentic_exec"]``;
* one global class, ``coordinator``: the registry's contract, with one synthetic binding, the
  overlay coordinator's ``cursor-task`` binding. The overlay's ``global-redefinition`` fault needs
  a global class to collide with. The coordinator's binding also carries the global contract's
  tokens.

Upkeep: when an overlay binding or contract changes, re-run this script and commit the new
fixture in the same edit. A stale fixture fails loudly: the strict validate or the resolve in
``build_registry_home`` refuses it.

The overlay is read with a small YAML-subset reader (block mappings, flow lists and flow
mappings of plain scalars), so the script needs only the standard library. Anything outside that
subset is refused.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]
OVERLAY = ROOT / ".agent" / "model-registry.local.yaml"
DEFAULT_REGISTRY = Path("P:/.agent/model-registry.json")
FIXTURE = HERE / "model-registry.json"
KEEP = ("vendor", "harness_ids", "price_band", "capabilities", "efforts", "auth")
TOP = {"schema_version": 1, "updated": "2026-11-15", "bump_gate": "human"}
COORDINATOR = ("avkit_coordinator", "cursor-task")

_KEY = re.compile(r"^(?P<indent> *)(?P<key>[A-Za-z0-9_.-]+):(?: (?P<value>.*))?$")
_PLAIN = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]*$")
_YAML11_WORDS = {"yes", "no", "on", "off", "y", "n", "null", "~"}


class SubsetError(ValueError):
    """The overlay uses YAML outside the subset this reader accepts."""


def _scalar(text: str, where: str) -> object:
    text = text.strip()
    if text == "true":
        return True
    if text == "false":
        return False
    if re.fullmatch(r"-?[0-9]+", text):
        return int(text)
    numeric = re.fullmatch(r"[0-9.]+", text)
    if text.lower() in _YAML11_WORDS or not _PLAIN.fullmatch(text) or numeric:
        raise SubsetError(f"{where}: unsupported scalar {text!r}")
    return text


def _value(text: str, where: str) -> object:
    text = text.strip()
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        return [_scalar(item, where) for item in inner.split(",")] if inner else []
    if text.startswith("{") and text.endswith("}"):
        out: dict[str, object] = {}
        inner = text[1:-1].strip()
        for item in inner.split(",") if inner else []:
            key, sep, val = item.partition(":")
            if not sep or not _PLAIN.fullmatch(key.strip()) or key.strip() in out:
                raise SubsetError(f"{where}: unsupported flow mapping item {item!r}")
            out[key.strip()] = _scalar(val, where)
        return out
    return _scalar(text, where)


def load_overlay(path: Path) -> dict:
    """Read the overlay's YAML subset into the same data ``yaml.safe_load`` returns."""
    root: dict[str, object] = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    pending: tuple[int, dict, str] | None = None
    text = path.read_bytes().decode("utf-8").replace("\r\n", "\n")
    for number, line in enumerate(text.split("\n"), 1):
        where = f"{path.name}:{number}"
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = _KEY.match(line)
        if match is None or "\t" in line or " #" in line:
            raise SubsetError(f"{where}: unsupported line {line!r}")
        indent = len(match["indent"])
        if pending is not None:
            parent_indent, parent, key = pending
            if indent <= parent_indent:
                raise SubsetError(f"{where}: {key!r} has no value")
            child: dict[str, object] = {}
            parent[key] = child
            stack.append((indent, child))
            pending = None
        while stack and indent < stack[-1][0]:
            stack.pop()
        if not stack or indent != stack[-1][0] and stack[-1][0] != -1:
            raise SubsetError(f"{where}: inconsistent indentation")
        if stack[-1][0] == -1:
            if indent != 0:
                raise SubsetError(f"{where}: the first level must not be indented")
            stack[-1] = (0, root)
        current = stack[-1][1]
        key = match["key"]
        if key in current:
            raise SubsetError(f"{where}: duplicate key {key!r}")
        if match["value"] is None or not match["value"].strip():
            pending = (indent, current, key)
        else:
            current[key] = _value(match["value"], where)
    if pending is not None:
        raise SubsetError(f"{path.name}: {pending[2]!r} has no value")
    return root


def build(registry: dict, overlay: dict) -> dict:
    """The fixture's data, from a registry and the overlay."""
    required: dict[str, set[str]] = {}
    forbidden: set[str] = set()
    for spec in overlay["classes"].values():
        contract = spec["contract"]
        forbidden.update(contract.get("forbid", []))
        for binding in spec.get("bindings", {}).values():
            required.setdefault(binding["slug"], set()).update(contract.get("capabilities", []))
    global_contract = registry["classes"]["coordinator"]["contract"]
    binding = overlay["classes"][COORDINATOR[0]]["bindings"][COORDINATOR[1]]
    synthetic = {"slug": binding["slug"], "effort": binding["effort"]}
    required.setdefault(binding["slug"], set()).update(global_contract["capabilities"])
    catalog = {}
    for slug in sorted(set(required) | forbidden):
        entry = registry["catalog"][slug]
        catalog[slug] = {key: entry[key] for key in KEEP if key in entry}
        catalog[slug]["capabilities"] = sorted(required.get(slug, set())) or ["agentic_exec"]
    return {
        **TOP,
        "catalog": catalog,
        "classes": {
            "coordinator": {
                "contract": global_contract,
                "bindings": {COORDINATOR[1]: synthetic},
            }
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--out", type=Path, default=FIXTURE)
    args = parser.parse_args(argv)
    registry = json.loads(args.registry.read_bytes().decode("utf-8"))
    data = build(registry, load_overlay(OVERLAY))
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(text.encode("utf-8"))
    size, entries = len(text.encode("utf-8")), len(data["catalog"])
    print(f"wrote {args.out.name}: {size} bytes, {entries} catalog entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
