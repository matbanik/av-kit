"""Session 72 OpenAPI delta (AC-106.5's OpenAPI block; implementation-plan.md §Plan-local scripts).

AC-106.5 says that against the base snapshot the only changes are ``ArrowAnnotationIn.head``,
``RectAnnotationIn.shape``, the new ``StepAnnotationIn``, its member and discriminator mapping
in each union that lists the marks, and ``SettingsPutIn.step_color`` and ``.step_size``. This
checks that structurally, so a change the AC doesn't name can't hide in a regenerated file.

It reads the base from ``git show 5db3623:openapi.committed.json`` and the new document from
``openapi.committed.json`` in the work tree (or ``--new PATH``), then:

1. requires the base to hold none of the additions (otherwise it is the wrong base);
2. requires each addition in the new document: the four properties, none of them in a
   ``required`` list, ``head`` with default ``"end"`` and ``shape`` with default ``"rect"``,
   and ``StepAnnotationIn`` with ``type`` const ``"step"`` and ``additionalProperties: false``;
3. requires ``StepAnnotationIn`` to be referenced exactly in the two mark unions
   (``AnnotateIn`` and ``CaptureShotDetailOut``), once in each ``oneOf`` and as each mapping's
   ``step`` value, and nowhere else;
4. removes every addition and requires what is left to equal the base exactly.

Two later changes are set back before step 4: the release ``info.version`` (rc4 row 7) and
Session 104's cookie test shapes (``COOKIE_TEST_SHAPES``, D-1600), which must be exactly the
base's or exactly that session's committed shapes.

A pydantic split into ``-Input`` and ``-Output`` names fails step 4, and is a departure (S7).
``--selftest`` builds the expected document from the base and checks that it passes, and that
the base itself, an extra property, a missing addition, a renamed schema, a changed
``required`` list and a stray reference are each refused. The last line is
``openapi-delta: pass`` or ``openapi-delta: fail`` (``openapi-delta selftest: ...`` under
``--selftest``). Run from the repository root.
"""

from __future__ import annotations

import copy
import json
import pathlib
import subprocess
import sys
from typing import Any

BASE_SHA = "5db3623"
SNAPSHOT = "openapi.committed.json"
STEP = "StepAnnotationIn"
STEP_REF = f"#/components/schemas/{STEP}"
UNIONS = ("AnnotateIn", "CaptureShotDetailOut")
#: (schema, property, required default or None)
ADDED_PROPERTIES = (
    ("ArrowAnnotationIn", "head", "end"),
    ("RectAnnotationIn", "shape", "rect"),
    ("SettingsPutIn", "step_color", None),
    ("SettingsPutIn", "step_size", None),
)
#: Session 104 (MEU-169, AC-169.5 and AC-169.6, 2026-11-27, D-1600): the cookie test reply gains
#: ``outcome`` and ``error_message``, and the ``CookieTestOutcome`` enum is new. Like the release
#: bump below, it is outside the capture shapes this AC pins. The two schemas must be either both
#: the base's or both exactly these shapes; they are then set back to the base's before the
#: compare, so any other change to them is still refused.
COOKIE_TEST_SHAPES: dict[str, dict[str, Any]] = {
    "CookieTestOut": {
        "additionalProperties": False,
        "description": "Cookie probe result without cookie bytes (`COOKIE_TEST_WIRE`).",
        "properties": {
            "error_message": {"anyOf": [{"type": "string"}, {"type": "null"}], "title": "Error Message"},
            "ok": {"title": "Ok", "type": "boolean"},
            "outcome": {"anyOf": [{"$ref": "#/components/schemas/CookieTestOutcome"}, {"type": "null"}]},
        },
        "required": ["ok", "outcome", "error_message"],
        "title": "CookieTestOut",
        "type": "object",
    },
    "CookieTestOutcome": {
        "description": "Where a cookie test stopped (`COOKIE_TEST_OUTCOME`, MEU-169). Wire values are lowercase.",
        "enum": ["ok", "unreadable", "check_failed"],
        "title": "CookieTestOutcome",
        "type": "string",
    },
}


def union_items(doc: dict[str, Any], name: str) -> dict[str, Any]:
    return doc["components"]["schemas"][name]["properties"]["annotations"]["items"]


def refs_to_step(node: Any, path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if value == STEP_REF:
                found.append(f"{path}/{key}")
            else:
                found.extend(refs_to_step(value, f"{path}/{key}"))
    elif isinstance(node, list):
        for i, value in enumerate(node):
            found.extend(refs_to_step(value, f"{path}/{i}"))
    return found


def first_difference(a: Any, b: Any, path: str = "") -> str | None:
    if type(a) is not type(b):
        return f"{path or '/'}: {type(a).__name__} != {type(b).__name__}"
    if isinstance(a, dict):
        for key in sorted(set(a) | set(b)):
            # a is the stripped new document and b the base.
            if key not in a:
                return f"{path}/{key}: only in the base"
            if key not in b:
                return f"{path}/{key}: only in the new document"
            diff = first_difference(a[key], b[key], f"{path}/{key}")
            if diff:
                return diff
        return None
    if isinstance(a, list):
        if len(a) != len(b):
            return f"{path}: list length {len(a)} != {len(b)}"
        for i, (x, y) in enumerate(zip(a, b, strict=True)):
            diff = first_difference(x, y, f"{path}/{i}")
            if diff:
                return diff
        return None
    return None if a == b else f"{path}: {a!r} != {b!r}"


def check(base: dict[str, Any], new: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    schemas = new.get("components", {}).get("schemas", {})
    base_schemas = base["components"]["schemas"]
    if STEP in base_schemas or refs_to_step(base):
        problems.append(f"the base already holds {STEP}")
    for schema, prop, default in ADDED_PROPERTIES:
        if prop in base_schemas.get(schema, {}).get("properties", {}):
            problems.append(f"the base already holds {schema}.{prop}")
        node = schemas.get(schema, {})
        if prop not in node.get("properties", {}):
            problems.append(f"missing {schema}.{prop}")
            continue
        if prop in node.get("required", []):
            problems.append(f"{schema}.{prop} is required")
        if default is not None and node["properties"][prop].get("default") != default:
            problems.append(f"{schema}.{prop} default is {node['properties'][prop].get('default')!r}, not {default!r}")
    step = schemas.get(STEP)
    if step is None:
        problems.append(f"missing {STEP}")
    else:
        if step.get("properties", {}).get("type", {}).get("const") != "step":
            problems.append(f"{STEP}.type is not const 'step'")
        if step.get("additionalProperties") is not False:
            problems.append(f"{STEP} allows additional properties")
    expected_refs = []
    for name in UNIONS:
        try:
            items = union_items(new, name)
        except KeyError:
            problems.append(f"{name} has no annotations union")
            continue
        members = [m for m in items.get("oneOf", []) if m == {"$ref": STEP_REF}]
        if len(members) != 1:
            problems.append(f"{name}'s oneOf lists {STEP} {len(members)} time(s), not once")
        if items.get("discriminator", {}).get("mapping", {}).get("step") != STEP_REF:
            problems.append(f"{name}'s mapping has no step -> {STEP}")
        prefix = f"/components/schemas/{name}/properties/annotations/items"
        expected_refs.append(f"{prefix}/discriminator/mapping/step")
        expected_refs.extend(f"{prefix}/oneOf/{i}/$ref" for i, m in enumerate(items.get("oneOf", [])) if m == {"$ref": STEP_REF})
    stray = sorted(set(refs_to_step(new)) - set(expected_refs))
    for path in stray:
        problems.append(f"a reference to {STEP} outside the mark unions: {path}")
    cookie_now = tuple(schemas.get(name) for name in COOKIE_TEST_SHAPES)
    cookie_base = tuple(base_schemas.get(name) for name in COOKIE_TEST_SHAPES)
    if cookie_now not in (cookie_base, tuple(COOKIE_TEST_SHAPES.values())):
        problems.append("CookieTestOut and CookieTestOutcome are neither the base's nor Session 104's shapes")
    if problems:
        return problems
    stripped = copy.deepcopy(new)
    stripped_schemas = stripped["components"]["schemas"]
    del stripped_schemas[STEP]
    for schema, prop, _ in ADDED_PROPERTIES:
        del stripped_schemas[schema]["properties"][prop]
    for name in UNIONS:
        items = union_items(stripped, name)
        items["oneOf"] = [m for m in items["oneOf"] if m != {"$ref": STEP_REF}]
        del items["discriminator"]["mapping"]["step"]
    # A release bump changes info.version (0.1.0-rc.4, 2026-11-21); it is release metadata, not
    # the API shape this AC pins, so it is set back to the base's value before the compare.
    stripped["info"]["version"] = base["info"]["version"]
    for name in COOKIE_TEST_SHAPES:
        if name in base_schemas:
            stripped_schemas[name] = copy.deepcopy(base_schemas[name])
        else:
            stripped_schemas.pop(name, None)
    diff = first_difference(stripped, base)
    if diff:
        problems.append(f"a change AC-106.5 doesn't name: {diff}")
    return problems


def expected_from(base: dict[str, Any]) -> dict[str, Any]:
    """The base plus the additions, as the selftest's passing fixture."""
    doc = copy.deepcopy(base)
    schemas = doc["components"]["schemas"]
    schemas["ArrowAnnotationIn"]["properties"]["head"] = {"default": "end", "enum": ["end", "none", "both"], "title": "Head", "type": "string"}
    schemas["RectAnnotationIn"]["properties"]["shape"] = {"default": "rect", "enum": ["rect", "ellipse"], "title": "Shape", "type": "string"}
    schemas["SettingsPutIn"]["properties"]["step_color"] = {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None, "title": "Step Color"}
    schemas["SettingsPutIn"]["properties"]["step_size"] = {"anyOf": [{"type": "integer"}, {"type": "null"}], "default": None, "title": "Step Size"}
    schemas[STEP] = {
        "additionalProperties": False,
        "properties": {"type": {"const": "step", "title": "Type", "type": "string"}, "x": {"type": "integer"}},
        "required": ["type", "x"],
        "title": STEP,
        "type": "object",
    }
    for name in UNIONS:
        items = union_items(doc, name)
        items["oneOf"].append({"$ref": STEP_REF})
        items["discriminator"]["mapping"]["step"] = STEP_REF
    return doc


def load_base() -> dict[str, Any]:
    text = subprocess.run(["git", "show", f"{BASE_SHA}:{SNAPSHOT}"], capture_output=True, check=True).stdout
    return json.loads(text.decode("utf-8"))


def selftest() -> int:
    base = load_base()
    good = expected_from(base)

    def extra(doc: dict[str, Any]) -> None:
        doc["components"]["schemas"]["TextAnnotationIn"]["properties"]["glow"] = {"type": "boolean"}

    def missing(doc: dict[str, Any]) -> None:
        del doc["components"]["schemas"]["SettingsPutIn"]["properties"]["step_size"]

    def renamed(doc: dict[str, Any]) -> None:
        schemas = doc["components"]["schemas"]
        schemas["ArrowAnnotationIn-Input"] = schemas["ArrowAnnotationIn"]

    def required(doc: dict[str, Any]) -> None:
        doc["components"]["schemas"]["ArrowAnnotationIn"]["required"].append("head")

    def stray(doc: dict[str, Any]) -> None:
        doc["components"]["schemas"]["TextAnnotationIn"]["properties"]["x_step"] = {"$ref": STEP_REF}

    def default(doc: dict[str, Any]) -> None:
        doc["components"]["schemas"]["RectAnnotationIn"]["properties"]["shape"]["default"] = "ellipse"

    bumped = copy.deepcopy(good)
    bumped["info"]["version"] = "0.0.0-selftest"
    cookie = copy.deepcopy(good)
    cookie["components"]["schemas"].update(copy.deepcopy(COOKIE_TEST_SHAPES))
    other_cookie = copy.deepcopy(cookie)
    other_cookie["components"]["schemas"]["CookieTestOutcome"]["enum"].append("expired")
    cases: list[tuple[str, dict[str, Any], bool]] = [
        ("expected", good, True),
        ("version bump only", bumped, True),
        ("Session 104 cookie shape", cookie, True),
        ("other cookie shape", other_cookie, False),
        ("base itself", copy.deepcopy(base), False),
    ]
    for label, mutate in (("extra property", extra), ("missing addition", missing), ("renamed schema", renamed),
                          ("changed required", required), ("stray reference", stray), ("wrong default", default)):
        doc = copy.deepcopy(good)
        mutate(doc)
        cases.append((label, doc, False))
    wrong = []
    for label, doc, want in cases:
        problems = check(base, doc)
        got = not problems
        print(f"selftest {label}: {'pass' if got else 'refused'} (expected {'pass' if want else 'refused'})")
        for p in problems:
            print("   ", p)
        if got != want:
            wrong.append(label)
    print(f"openapi-delta selftest: {len(cases)} case(s), {len(wrong)} wrong: {wrong}")
    return 1 if wrong else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if argv and (len(argv) != 2 or argv[0] != "--new"):
        print("usage: openapi-delta.py [--new PATH] | --selftest  (run from the repository root)")
        return 2
    new_path = pathlib.Path(argv[1] if argv else SNAPSHOT)
    problems = check(load_base(), json.loads(new_path.read_bytes().decode("utf-8")))
    for p in problems:
        print("problem:", p)
    print(f"openapi-delta: {'fail' if problems else 'pass'}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
