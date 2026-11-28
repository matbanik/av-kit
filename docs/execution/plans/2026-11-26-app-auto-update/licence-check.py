"""Session 106 dependency and licence check (task row 13; implementation-plan.md S7).

Compares ``ui/package-lock.json`` with its row-0 copy in ``R/baseline-copies``. It passes when:

* ``ui/package.json`` holds ``"electron-updater": "6.8.11"`` (exact) under ``dependencies``;
* every package entry added to the lock is ``node_modules/electron-updater`` or in its dependency
  closure as the lock resolves it (nested ``node_modules`` first, then up the tree);
* no existing entry changed its version or was removed;
* each added package has a licence from the plan's list and a licence file in ``ui/``'s tree;
* each package the lock moved from a development to a production package (its ``dev`` flag
  dropped) has a licence file or a reviewed
  ``packaging/licence-overrides/npm-<name>.txt`` (D-1577: lazy-val 1.0.5 ships none).

Anything else is S7. ``--selftest`` runs the fixtures.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
COPIES = pathlib.Path("C:/Temp/av-kit/2026-11-26-app-auto-update/baseline-copies")
LOCK = "ui/package-lock.json"
PKG = "ui/package.json"
LIB, VERSION = "electron-updater", "6.8.11"
LICENCES = {"MIT", "ISC", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0", "0BSD", "BlueOak-1.0.0"}
LICENCE_FILES = ("license", "licence", "copying")


def _resolve(packages: dict, from_key: str, name: str) -> str | None:
    base = from_key
    while True:
        cand = f"{base}/node_modules/{name}" if base else f"node_modules/{name}"
        if cand in packages:
            return cand
        if not base:
            return None
        i = base.rfind("/node_modules/")
        base = base[:i] if i >= 0 else ""


def closure(packages: dict, start: str) -> set[str]:
    seen: set[str] = set()
    todo = [start]
    while todo:
        key = todo.pop()
        if key in seen or key not in packages:
            continue
        seen.add(key)
        info = packages[key]
        for dep in {**info.get("dependencies", {}), **info.get("optionalDependencies", {})}:
            got = _resolve(packages, key, dep)
            if got:
                todo.append(got)
    return seen


def _has_licence_file(folder: pathlib.Path) -> bool:
    return folder.is_dir() and any(
        p.is_file() and p.name.lower().startswith(LICENCE_FILES) for p in folder.iterdir()
    )


def check(root: pathlib.Path = ROOT, copies: pathlib.Path = COPIES) -> list[str]:
    problems: list[str] = []
    pkg = json.loads((root / PKG).read_text(encoding="utf-8"))
    want = pkg.get("dependencies", {}).get(LIB)
    if want != VERSION:
        problems.append(f"licence-check: {PKG} dependencies.{LIB} is {want!r}, not {VERSION!r}")
    before = json.loads((copies / LOCK).read_text(encoding="utf-8"))["packages"]
    after = json.loads((root / LOCK).read_text(encoding="utf-8"))["packages"]
    lib_key = f"node_modules/{LIB}"
    if after.get(lib_key, {}).get("version") != VERSION:
        problems.append(f"licence-check: lock {lib_key} is {after.get(lib_key, {}).get('version')}")
    allowed = closure(after, lib_key)
    added = sorted(k for k in after if k not in before)
    for k in sorted(before):
        if k not in after:
            problems.append(f"licence-check: {k} removed")
        elif k and before[k].get("version") != after[k].get("version"):
            was, now = before[k].get("version"), after[k].get("version")
            problems.append(f"licence-check: {k} changed {was} -> {now}")
    for k in added:
        info = after[k]
        lic = info.get("license")
        folder = root / "ui" / k
        file_ok = _has_licence_file(folder)
        print(
            f"licence-check added {k} {info.get('version')} {lic} "
            f"licence-file={'yes' if file_ok else 'NO'}"
        )
        if k not in allowed:
            problems.append(f"licence-check: {k} is not {LIB} or its dependency")
        if lic not in LICENCES:
            problems.append(f"licence-check: {k} licence {lic!r} is not on the list")
        if not file_ok:
            problems.append(f"licence-check: {k} has no licence file in {folder}")
    promoted = sorted(
        k for k in before if k in after and before[k].get("dev") and not after[k].get("dev")
    )
    for k in promoted:
        info = after[k]
        lic = info.get("license")
        name = k.rsplit("node_modules/", 1)[-1]
        override = root / "packaging" / "licence-overrides" / f"npm-{name.replace('/', '-')}.txt"
        file_ok = _has_licence_file(root / "ui" / k) or override.is_file()
        print(
            f"licence-check promoted {k} {info.get('version')} {lic} "
            f"licence-file={'yes' if file_ok else 'NO'}"
        )
        if lic not in LICENCES:
            # The list binds added packages (S7); a promoted one was already in the lock, and the
            # generator's own rules (GPL class, a licence text) decide whether it ships (D-1577).
            print(f"licence-check note: promoted {k} licence {lic!r} is outside the added list")
        if not file_ok:
            problems.append(f"licence-check: promoted {k} has no licence file and no override")
    print(f"licence-check: {len(added)} added, {len(promoted)} promoted, closure {len(allowed)}")
    if not added:
        problems.append("licence-check: nothing added to the lock")
    return problems


def selftest() -> int:
    base_lock = {
        "packages": {
            "": {"dependencies": {"zod": "1"}},
            "node_modules/zod": {"version": "1.0.0", "license": "MIT"},
            "node_modules/semver": {"version": "7.0.0", "license": "ISC"},
        }
    }

    def after_lock(extra: dict, change: dict | None = None) -> dict:
        pk = dict(base_lock["packages"])
        pk[""] = {"dependencies": {"zod": "1", LIB: VERSION}}
        pk[f"node_modules/{LIB}"] = {
            "version": VERSION,
            "license": "MIT",
            "dependencies": {"semver": "7", "lazy-val": "1"},
        }
        pk.update(extra)
        pk.update(change or {})
        return {"packages": pk}

    lazy = {"node_modules/lazy-val": {"version": "1.0.5", "license": "MIT"}}
    cases = [
        ("library and its dependency pass", after_lock(lazy), VERSION, True, True),
        (
            "a foreign added package fails",
            after_lock({**lazy, "node_modules/left-pad": {"version": "1.0.0", "license": "MIT"}}),
            VERSION,
            True,
            False,
        ),
        (
            "a bad licence fails",
            after_lock({"node_modules/lazy-val": {"version": "1.0.5", "license": "GPL-3.0"}}),
            VERSION,
            True,
            False,
        ),
        (
            "a changed version fails",
            after_lock(lazy, {"node_modules/zod": {"version": "2.0.0", "license": "MIT"}}),
            VERSION,
            True,
            False,
        ),
        ("a range in package.json fails", after_lock(lazy), "^6.8.11", True, False),
        ("a missing licence file fails", after_lock(lazy), VERSION, False, False),
    ]
    bad = 0
    with tempfile.TemporaryDirectory() as d:
        for n, (name, lock, pin, files, want) in enumerate(cases):
            root, copies = pathlib.Path(d) / f"r{n}", pathlib.Path(d) / f"c{n}"
            (copies / "ui").mkdir(parents=True)
            (root / "ui").mkdir(parents=True)
            (copies / LOCK).write_text(json.dumps(base_lock), encoding="utf-8")
            (root / LOCK).write_text(json.dumps(lock), encoding="utf-8")
            (root / PKG).write_text(json.dumps({"dependencies": {LIB: pin}}), encoding="utf-8")
            for k in lock["packages"]:
                if k and k not in base_lock["packages"]:
                    (root / "ui" / k).mkdir(parents=True, exist_ok=True)
                    if files:
                        (root / "ui" / k / "LICENSE").write_text("x", encoding="utf-8")
            got = check(root, copies)
            ok = (not got) == want
            bad += 0 if ok else 1
            print(f"selftest {'ok ' if ok else 'BAD'} {name}: {got}")
    # A development package the lock makes a production one (D-1577).
    dev_lock = {
        "packages": {
            **base_lock["packages"],
            "node_modules/ms": {"version": "2.1.3", "license": "MIT", "dev": True},
        }
    }
    promo = after_lock(lazy, {"node_modules/ms": {"version": "2.1.3", "license": "MIT"}})
    for n, (name, override, want) in enumerate(
        [
            ("a promoted package with no licence file fails", False, False),
            ("a promoted package with a reviewed override passes", True, True),
        ]
    ):
        with tempfile.TemporaryDirectory() as d:
            root, copies = pathlib.Path(d) / "r", pathlib.Path(d) / "c"
            (copies / "ui").mkdir(parents=True)
            (root / "ui" / "node_modules/lazy-val").mkdir(parents=True)
            (root / "ui" / "node_modules/lazy-val/LICENSE").write_text("x", encoding="utf-8")
            (root / "ui" / "node_modules" / LIB).mkdir(parents=True)
            (root / "ui" / "node_modules" / LIB / "LICENSE").write_text("x", encoding="utf-8")
            (copies / LOCK).write_text(json.dumps(dev_lock), encoding="utf-8")
            (root / LOCK).write_text(json.dumps(promo), encoding="utf-8")
            (root / PKG).write_text(json.dumps({"dependencies": {LIB: VERSION}}), encoding="utf-8")
            if override:
                o = root / "packaging" / "licence-overrides" / "npm-ms.txt"
                o.parent.mkdir(parents=True)
                o.write_text("x", encoding="utf-8")
            got = check(root, copies)
            ok = (not got) == want
            bad += 0 if ok else 1
            print(f"selftest {'ok ' if ok else 'BAD'} {name}: {got}")
    total = len(cases) + 2
    print(f"licence-check selftest: {total - bad}/{total} ok")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if argv:
        print(__doc__)
        return 2
    problems = check()
    for p in problems:
        print("PROBLEM:", p)
    print(f"licence-check: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
