"""Session 76 fixture check (AC-1; implementation-plan.md §The registry fixture, §Plan-local checkers).

Usage: ``python fixture-check.py`` from the repository root, or ``python fixture-check.py --selftest``.

It checks ``FIXTURE`` (``tests/tooling/fixtures/registry-home/model-registry.json``):

* the file is LF with a trailing newline and equals ``json.dumps(…, indent=2, sort_keys=True)``
  of itself plus ``"\\n"``;
* the top-level keys are exactly ``schema_version`` (1), ``updated`` (``2026-11-15``),
  ``bump_gate`` (``human``), ``catalog`` and ``classes``;
* the slug set equals ``OVERLAY``'s bound plus forbidden slugs; each entry holds only the six
  keys; each capability token is one of ``OVERLAY``'s contract tokens, the global
  ``coordinator`` contract's tokens, or ``agentic_exec``;
* ``classes`` is only ``coordinator``, whose one binding names a catalog slug;
* no string (key or value) holds ``http``, ``/``, ``\\``, ``@``, ``$`` or ``P:``;
* ``resolve_model.py validate --registry <temp copy> --strict`` exits 0 from a temp copy of the
  machine tool files, with ``AGENT_MODEL_REGISTRY`` at the copy, and leaves the copy unchanged.
  Nothing under ``P:/.agent`` is written;
* ``make_fixture.py --out <temp>`` writes bytes equal to ``FIXTURE``, its overlay reader returns
  what ``yaml.safe_load`` returns for ``OVERLAY``, and an independent build in this script (from
  the same registry and ``yaml.safe_load``) gives the same data.

``--selftest`` builds its own fixture with the independent build (from the machine registry,
read only, and ``OVERLAY``), then must accept it and refuse copies with ``price_per_mtok``, a
``sources`` key, an unknown slug, a URL string, CRLF line endings, and a catalog entry without
``vendor`` (only the strict validate refuses that one).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path.cwd()
FIXTURE = ROOT / "tests/tooling/fixtures/registry-home/model-registry.json"
MAKE = ROOT / "tests/tooling/fixtures/registry-home/make_fixture.py"
OVERLAY = ROOT / ".agent/model-registry.local.yaml"
MACHINE_TOOLS = Path("P:/.agent")
LIVE_REGISTRY = MACHINE_TOOLS / "model-registry.json"
TOOL_FILES = ("tools/resolve_model.py", "tools/ModelRegistry.psm1", "schema/model-registry.v1.schema.json")
KEEP = ("vendor", "harness_ids", "price_band", "capabilities", "efforts", "auth")
TOP = {"schema_version": 1, "updated": "2026-11-15", "bump_gate": "human"}
BANNED = ("http", "/", "\\", "@", "$", "P:")


def independent_build(registry: dict, overlay: dict) -> dict:
    """A second implementation of §The registry fixture, kept apart from make_fixture.py."""
    need: dict[str, set[str]] = {}
    forbid: set[str] = set()
    for cls in overlay["classes"].values():
        caps = set(cls["contract"].get("capabilities", []))
        forbid |= set(cls["contract"].get("forbid", []))
        for binding in cls.get("bindings", {}).values():
            need.setdefault(binding["slug"], set()).update(caps)
    coord = overlay["classes"]["avkit_coordinator"]["bindings"]["cursor-task"]
    contract = registry["classes"]["coordinator"]["contract"]
    catalog = {}
    for slug in sorted(set(need) | forbid):
        live = registry["catalog"][slug]
        entry = {k: live[k] for k in KEEP if k in live}
        entry["capabilities"] = sorted(need.get(slug, set())) or ["agentic_exec"]
        catalog[slug] = entry
    catalog[coord["slug"]]["capabilities"] = sorted(set(catalog[coord["slug"]]["capabilities"]) | set(contract["capabilities"]))
    return {
        **TOP,
        "catalog": catalog,
        "classes": {"coordinator": {"contract": contract, "bindings": {"cursor-task": {"slug": coord["slug"], "effort": coord["effort"]}}}},
    }


def dump(data: dict) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _strings(node: object, out: list[str]) -> None:
    if isinstance(node, dict):
        for k, v in node.items():
            out.append(str(k))
            _strings(v, out)
    elif isinstance(node, list):
        for v in node:
            _strings(v, out)
    elif isinstance(node, str):
        out.append(node)


def strict_validate(data: bytes) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="tth-fixture-") as tmp:
        home = Path(tmp) / "home"
        for rel in TOOL_FILES:
            (home / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(MACHINE_TOOLS / rel, home / rel)
        copy = home / "model-registry.json"
        copy.write_bytes(data)
        before = hashlib.sha256(data).hexdigest()
        env = {k: v for k, v in os.environ.items() if k != "AGENT_MODEL_REGISTRY"}
        env.update(AGENT_MODEL_REGISTRY=str(copy), PYTHONIOENCODING="utf-8")
        r = subprocess.run(
            [sys.executable, str(home / "tools/resolve_model.py"), "validate", "--registry", str(copy), "--strict"],
            capture_output=True, text=True, encoding="utf-8", env=env, cwd=tmp, check=False,
        )
        print(f"   strict validate: exit {r.returncode}; {(r.stdout + r.stderr).strip().splitlines()[0] if (r.stdout + r.stderr).strip() else ''}")
        problems = []
        if r.returncode != 0:
            problems.append(f"strict validate exit {r.returncode}: {(r.stdout + r.stderr).strip()[-300:]}")
        if hashlib.sha256(copy.read_bytes()).hexdigest() != before:
            problems.append("strict validate changed the copy")
        return problems


def check(data: bytes, overlay: dict, registry: dict, strict: bool = True) -> list[str]:
    problems: list[str] = []
    if b"\r" in data or not data.endswith(b"\n"):
        problems.append("not LF with a trailing newline")
    try:
        doc = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return problems + [f"not JSON: {exc}"]
    if dump(doc) != data.replace(b"\r\n", b"\n") or (b"\r" in data):
        problems.append("not equal to json.dumps(indent=2, sort_keys=True) of itself")
    if set(doc) != set(TOP) | {"catalog", "classes"}:
        problems.append(f"top-level keys {sorted(doc)}")
    for k, v in TOP.items():
        if doc.get(k) != v:
            problems.append(f"{k} is {doc.get(k)!r}, want {v!r}")
    bound, forbid, tokens = set(), set(), {"agentic_exec"}
    for cls in overlay["classes"].values():
        tokens |= set(cls["contract"].get("capabilities", []))
        forbid |= set(cls["contract"].get("forbid", []))
        bound |= {b["slug"] for b in cls.get("bindings", {}).values()}
    tokens |= set(registry["classes"]["coordinator"]["contract"]["capabilities"])
    catalog = doc.get("catalog", {})
    if set(catalog) != bound | forbid:
        problems.append(f"slugs {sorted(set(catalog) ^ (bound | forbid))} differ from the overlay's bound plus forbidden")
    for slug, entry in catalog.items():
        extra = set(entry) - set(KEEP)
        if extra:
            problems.append(f"{slug}: keys outside the six: {sorted(extra)}")
        bad = set(entry.get("capabilities", [])) - tokens
        if bad:
            problems.append(f"{slug}: capability tokens outside the contracts: {sorted(bad)}")
    classes = doc.get("classes", {})
    if set(classes) != {"coordinator"}:
        problems.append(f"classes {sorted(classes)}, want only coordinator")
    else:
        bindings = classes["coordinator"].get("bindings", {})
        if list(bindings) != ["cursor-task"] or bindings["cursor-task"].get("slug") not in catalog:
            problems.append(f"coordinator bindings {bindings}")
    strings: list[str] = []
    _strings(doc, strings)
    for s in strings:
        hit = [b for b in BANNED if b in s]
        if hit:
            problems.append(f"string {s!r} holds {hit}")
    if strict:
        problems += strict_validate(data)
    return problems


def load_make():
    spec = importlib.util.spec_from_file_location("make_fixture", MAKE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    overlay = yaml.safe_load(OVERLAY.read_text(encoding="utf-8"))
    registry = json.loads(LIVE_REGISTRY.read_text(encoding="utf-8"))
    data = FIXTURE.read_bytes()
    print(f"FIXTURE: {len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()}")
    problems = check(data, overlay, registry)
    doc = json.loads(data)
    print(f"   catalog {sorted(doc['catalog'])}")
    with tempfile.TemporaryDirectory(prefix="tth-make-") as tmp:
        out = Path(tmp) / "model-registry.json"
        r = subprocess.run([sys.executable, str(MAKE), "--out", str(out)], capture_output=True, text=True,
                           encoding="utf-8", check=False)
        same = r.returncode == 0 and out.is_file() and out.read_bytes() == data
        print(f"   make_fixture.py --out <temp>: exit {r.returncode}; bytes equal to FIXTURE: {same}")
        if not same:
            problems.append(f"make_fixture.py does not regenerate FIXTURE: {(r.stdout + r.stderr).strip()[-300:]}")
    parsed = load_make().load_overlay(OVERLAY)
    print(f"   make_fixture.load_overlay equals yaml.safe_load: {parsed == overlay}")
    if parsed != overlay:
        problems.append("make_fixture.load_overlay differs from yaml.safe_load")
    indep = dump(independent_build(registry, overlay))
    print(f"   independent build equals FIXTURE: {indep == data}")
    if indep != data:
        problems.append("the independent build differs from FIXTURE")
    for p in problems:
        print("FAIL", p)
    print(f"fixture-check: {len(problems)} problem(s)")
    return 1 if problems else 0


def selftest() -> int:
    overlay = yaml.safe_load(OVERLAY.read_text(encoding="utf-8"))
    registry = json.loads(LIVE_REGISTRY.read_text(encoding="utf-8"))
    good_doc = independent_build(registry, overlay)
    good = dump(good_doc)

    def mutate(fn) -> bytes:
        d = json.loads(good)
        fn(d)
        return dump(d)

    first = sorted(good_doc["catalog"])[0]
    cases = (
        ("control: the independent build", good, True),
        ("a price_per_mtok key", mutate(lambda d: d["catalog"][first].update(price_per_mtok={"in": 1})), False),
        ("a sources key", mutate(lambda d: d["catalog"][first].update(sources=["x"])), False),
        ("an unknown slug", mutate(lambda d: d["catalog"].update({"invented-model": dict(d["catalog"][first])})), False),
        ("a URL string", mutate(lambda d: d["catalog"][first].update(auth="https" + "://example.invalid")), False),
        ("CRLF line endings", good.replace(b"\n", b"\r\n"), False),
        ("an entry without vendor", mutate(lambda d: d["catalog"]["gpt-6.1-sol"].pop("vendor")), False),
    )
    failures = []
    for name, data, accept in cases:
        problems = check(data, overlay, registry)
        ok = not problems
        print(f"{'ok  ' if ok == accept else 'BAD '} {name}: {'accepted' if ok else problems[:3]}")
        if ok != accept:
            failures.append(name)
    vendorless = cases[-1][1]
    only_strict = check(vendorless, overlay, registry, strict=False)
    print(f"{'ok  ' if not only_strict else 'BAD '} the vendorless entry passes every check but the strict validate: {only_strict or 'yes'}")
    if only_strict:
        failures.append("vendorless without strict")
    for f in failures:
        print("SELFTEST FAIL:", f)
    print(f"fixture-check selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv else main())
