"""Session 39 ``SCOPE_CHECK`` scope-ast step (implementation-plan.md Verification Plan §5, ``PRODUCT_SCOPE``).

Usage, from the worktree root: ``uv run python docs/execution/plans/2026-10-16-capture-new-marks/scope-ast.py``
compares ``adapter.py`` at ``baseline.sha`` with the working tree; ``--base REF`` uses another
baseline; ``--selftest`` runs the synthetic fixtures below. Read-only. Exit 0 when in scope.

The whole adapter module is frozen except what ``PRODUCT_SCOPE`` lets change (round 1 F4):

* ``CaptureAdapter.bake`` and ``CaptureAdapter._apply`` may change (``REGION_PASS``);
* the new region names ``region_clip``, ``apply_region_pass``, ``eraser_fill``,
  ``_apply_pixelate`` and ``_apply_eraser`` may be added, at module or class level;
* import statements are compared as bindings: every baseline binding (local name -> module,
  imported name, level) stays exactly as it was, and a new binding may not rebind a name the
  baseline module binds at top level.

Every other top-level statement, and every other ``CaptureAdapter`` body statement, must
have the same ``ast.dump`` in the same order -- module constants (``SUPERSAMPLE``,
``ARROWHEAD_LENGTH_FACTOR``, ``FONT_CANDIDATES``, ``NAMED_RGB``, ...), the docstring, the
logger, every drawn-mark painter and helper, and every other method.
"""

from __future__ import annotations

import ast
import pathlib
import subprocess
import sys

ADAPTER = "packages/infrastructure/src/avkit_infra/capture/adapter.py"
PLAN = pathlib.Path(__file__).resolve().parent
CLASS = "CaptureAdapter"
CHANGEABLE_METHODS = frozenset({"bake", "_apply"})
NEW_NAMES = frozenset({"region_clip", "apply_region_pass", "eraser_fill", "_apply_pixelate", "_apply_eraser"})

Binding = tuple[str | None, str, int]


def _bindings(stmts: list[ast.stmt]) -> dict[str, Binding]:
    out: dict[str, Binding] = {}
    for stmt in stmts:
        if isinstance(stmt, ast.Import):
            for a in stmt.names:
                out[a.asname or a.name.split(".")[0]] = (None, a.name, 0)
        elif isinstance(stmt, ast.ImportFrom):
            for a in stmt.names:
                out[a.asname or a.name] = (stmt.module, a.name, stmt.level)
    return out


def _bound_names(stmt: ast.stmt) -> set[str]:
    if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return {stmt.name}
    targets: list[ast.expr] = []
    if isinstance(stmt, ast.Assign):
        targets = list(stmt.targets)
    elif isinstance(stmt, (ast.AnnAssign, ast.AugAssign)):
        targets = [stmt.target]
    return {n.id for t in targets for n in ast.walk(t) if isinstance(n, ast.Name)}


def _is_new(stmt: ast.stmt) -> bool:
    names = _bound_names(stmt)
    return bool(names) and names <= NEW_NAMES


def _frozen(stmts: list[ast.stmt], *, in_class: bool) -> list[str]:
    kept = []
    for stmt in stmts:
        if isinstance(stmt, (ast.Import, ast.ImportFrom)) or _is_new(stmt):
            continue
        if in_class and isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)) and stmt.name in CHANGEABLE_METHODS:
            continue
        if not in_class and isinstance(stmt, ast.ClassDef) and stmt.name == CLASS:
            # the class header (bases, decorators, keywords) is frozen; its body is compared below
            kept.append(repr((CLASS, *(ast.dump(n) for n in (*stmt.bases, *stmt.keywords, *stmt.decorator_list)))))
            continue
        kept.append(ast.dump(stmt))
    return kept


def _class_body(tree: ast.Module) -> list[ast.stmt] | None:
    found = [s for s in tree.body if isinstance(s, ast.ClassDef) and s.name == CLASS]
    return found[0].body if len(found) == 1 else None


def _first_diff(old: list[str], new: list[str]) -> str:
    for i, (a, b) in enumerate(zip(old, new)):
        if a != b:
            return f"statement {i}: {a[:110]} -> {b[:110]}"
    return f"statement count {len(old)} -> {len(new)}"


def compare(old_src: str, new_src: str) -> list[str]:
    old, new = ast.parse(old_src), ast.parse(new_src)
    problems = []
    old_b, new_b = _bindings(old.body), _bindings(new.body)
    lost = sorted(k for k, v in old_b.items() if new_b.get(k) != v)
    if lost:
        problems.append(f"baseline import bindings removed or changed: {lost}")
    baseline_names = set(old_b) | {n for s in old.body for n in _bound_names(s)}
    rebound = sorted(k for k in set(new_b) - set(old_b) if k in baseline_names)
    if rebound:
        problems.append(f"new imports rebind baseline names: {rebound}")
    if _frozen(old.body, in_class=False) != _frozen(new.body, in_class=False):
        problems.append("module-level change outside PRODUCT_SCOPE: " + _first_diff(_frozen(old.body, in_class=False), _frozen(new.body, in_class=False)))
    old_c, new_c = _class_body(old), _class_body(new)
    if old_c is None or new_c is None:
        problems.append(f"expected exactly one class {CLASS} in both versions")
    else:
        if _frozen(old_c, in_class=True) != _frozen(new_c, in_class=True):
            problems.append(f"{CLASS} change outside PRODUCT_SCOPE: " + _first_diff(_frozen(old_c, in_class=True), _frozen(new_c, in_class=True)))
        for name in sorted(CHANGEABLE_METHODS):
            if not any(isinstance(s, ast.FunctionDef) and s.name == name for s in new_c):
                problems.append(f"{CLASS}.{name} is missing")
    return problems


BASE_SRC = '''"""Adapter."""
from __future__ import annotations
import math
from PIL import Image, ImageDraw
from avkit_core.domain.capture import ArrowAnnotation, RectAnnotation

SUPERSAMPLE = 4
FONT_CANDIDATES = ("segoeui.ttf", "arial.ttf")


def _color_rgb(color):
    return (0, 0, 0)


class CaptureAdapter:
    KIND = "capture"

    def bake(self, src, marks):
        for m in marks:
            self._apply(src, m)

    def _apply(self, img, m):
        self._apply_rect(img, m)

    def _apply_rect(self, img, m):
        ImageDraw.Draw(img).rectangle((0, 0, SUPERSAMPLE, 1))
'''

IN_SCOPE_SRC = '''"""Adapter."""
from __future__ import annotations
import math
from collections import Counter
from PIL import Image, ImageDraw
from avkit_core.domain.capture import ArrowAnnotation, EraserAnnotation, PixelateAnnotation, RectAnnotation

SUPERSAMPLE = 4
FONT_CANDIDATES = ("segoeui.ttf", "arial.ttf")


def _color_rgb(color):
    return (0, 0, 0)


def region_clip(m, w, h):
    return None


def apply_region_pass(canvas, marks):
    return canvas


class CaptureAdapter:
    KIND = "capture"

    def bake(self, src, marks):
        src = apply_region_pass(src, marks)
        for m in marks:
            self._apply(src, m)

    def _apply(self, img, m):
        if isinstance(m, PixelateAnnotation):
            return
        self._apply_rect(img, m)

    def _apply_rect(self, img, m):
        ImageDraw.Draw(img).rectangle((0, 0, SUPERSAMPLE, 1))

    def _apply_pixelate(self, canvas, m):
        return Counter()
'''


def _variant(old: str, new: str) -> str:
    assert BASE_SRC.count(old) == 1, old
    return BASE_SRC.replace(old, new)


#: (name, new source, expected in scope)
SELFTEST = (
    ("identical", BASE_SRC, True),
    ("permitted-changes", IN_SCOPE_SRC, True),
    ("supersample-changed", _variant("SUPERSAMPLE = 4", "SUPERSAMPLE = 2"), False),
    ("font-candidates-changed", _variant('("segoeui.ttf", "arial.ttf")', '("arial.ttf",)'), False),
    ("frozen-method-changed", _variant("rectangle((0, 0, SUPERSAMPLE, 1))", "rectangle((0, 0, SUPERSAMPLE, 2))"), False),
    ("frozen-helper-changed", _variant("return (0, 0, 0)", "return (1, 0, 0)"), False),
    ("class-attribute-changed", _variant('KIND = "capture"', 'KIND = "shot"'), False),
    ("new-unpermitted-constant", _variant("SUPERSAMPLE = 4\n", "SUPERSAMPLE = 4\nBLOCK = 8\n"), False),
    ("new-unpermitted-method", _variant("    def _apply_rect(", "    def _apply_blur(self, img, m):\n        pass\n\n    def _apply_rect("), False),
    ("import-rebinds-baseline-name", _variant("import math\n", "import math\nfrom fastmath import SUPERSAMPLE\n"), False),
    ("baseline-import-removed", _variant("import math\n", ""), False),
    ("baseline-import-retargeted", _variant("from PIL import Image, ImageDraw", "from PIL import Image\nfrom fakepil import ImageDraw"), False),
    ("permitted-name-reassigns-constant", _variant("def _color_rgb(", "region_clip = SUPERSAMPLE = 9\n\n\ndef _color_rgb("), False),
    ("docstring-changed", _variant('"""Adapter."""', '"""Adapter v2."""'), False),
    ("class-base-changed", _variant("class CaptureAdapter:", "class CaptureAdapter(object):"), False),
    ("bake-removed", _variant("    def bake(self, src, marks):\n        for m in marks:\n            self._apply(src, m)\n\n", ""), False),
)


def selftest() -> int:
    wrong = []
    for name, src, want in SELFTEST:
        problems = compare(BASE_SRC, src)
        got = not problems
        print(f"{name}: {'in scope' if got else 'refused'} (expected {'in scope' if want else 'refused'}){'' if got else ' -- ' + problems[0][:120]}")
        if got != want:
            wrong.append(name)
    print(f"scope-ast selftest: {len(SELFTEST)} fixture(s), {len(wrong)} wrong: {wrong}")
    return 1 if wrong else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if argv and (len(argv) != 2 or argv[0] != "--base"):
        print("usage: scope-ast.py [--base REF] | --selftest")
        return 2
    base = argv[1] if argv else (PLAN / "baseline.sha").read_text(encoding="utf-8").strip()
    old = subprocess.run(["git", "show", f"{base}:{ADAPTER}"], capture_output=True, text=True, encoding="utf-8", check=True).stdout
    new = pathlib.Path(ADAPTER).read_text(encoding="utf-8")
    problems = compare(old, new)
    for p in problems:
        print("SCOPE-AST:", p)
    print(f"scope-ast: adapter outside PRODUCT_SCOPE: {len(problems)} problem(s) (base {base})")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
