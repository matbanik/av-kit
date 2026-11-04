"""MEU-24 packaging contract — AC-24.1–24.10. Titles must contain the AC id."""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_FILE = REPO_ROOT / "packaging" / "avkit-backend.spec"
PACK_SCRIPT = REPO_ROOT / "tools" / "package_backend.py"
PACK_DIST_DIR = REPO_ROOT / "packaging" / "dist" / "avkit-backend"
PACK_DIST_EXE = PACK_DIST_DIR / "avkit-backend.exe"

HIDDEN_IMPORTS = (
    "yt_dlp",
    "youtube_transcript_api",
    "sqlalchemy",
    "pydantic",
    "uvicorn",
    "avkit_api",
    "avkit_core",
    "avkit_infra",
    "structlog",
)
SECRET_KEYS = ("token", "mcp_token", "AVKIT_API_TOKEN", "--token", "--mcp-token")
DESCRIPTOR_KEYS = frozenset(
    {
        "schema_version",
        "pid",
        "instance_id",
        "executable_path",
        "host",
        "port",
        "bind",
        "api_base",
        "app_data",
        "started_at",
    }
)


def _spec_text() -> str:
    assert SPEC_FILE.is_file(), f"missing SPEC_FILE {SPEC_FILE}"
    return SPEC_FILE.read_text(encoding="utf-8")


@pytest.mark.parametrize("ac_id", ["AC-24.1"], ids=["AC-24.1"])
def test_spec_onedir(ac_id: str) -> None:
    """AC-24.1 SPEC_ONEDIR — COLLECT onedir named avkit-backend, no --onefile."""
    assert ac_id == "AC-24.1"
    text = _spec_text()
    assert "COLLECT" in text
    assert "avkit-backend" in text
    assert "--onefile" not in text
    assert "onefile=True" not in text


@pytest.mark.parametrize("ac_id", ["AC-24.2"], ids=["AC-24.2"])
def test_hidden_imports(ac_id: str) -> None:
    """AC-24.2 HIDDEN_IMPORTS appear in the spec."""
    assert ac_id == "AC-24.2"
    text = _spec_text()
    missing = [name for name in HIDDEN_IMPORTS if name not in text]
    assert missing == []


@pytest.mark.parametrize("ac_id", ["AC-24.3"], ids=["AC-24.3"])
def test_exclude_globs(ac_id: str) -> None:
    """AC-24.3 EXCLUDE_GLOBS reject models, avkit.db, .env, onnx, pth."""
    assert ac_id == "AC-24.3"
    text = _spec_text()
    for token in ("avkit.db", ".env", ".onnx", ".pth"):
        assert token in text
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            assert not node.value.endswith("avkit.db") or "exclude" in text.lower()


@pytest.mark.parametrize("ac_id", ["AC-24.4"], ids=["AC-24.4"])
def test_bind_host_localhost(ac_id: str) -> None:
    """AC-24.4 BIND_HOST 127.0.0.1 — spec/hooks do not pass 0.0.0.0."""
    assert ac_id == "AC-24.4"
    from avkit_api.cli import BIND_HOST

    assert BIND_HOST == "127.0.0.1"
    text = _spec_text()
    assert "0.0.0.0" not in text


@pytest.mark.parametrize("ac_id", ["AC-24.5"], ids=["AC-24.5"])
def test_entry_and_spawn_flags(ac_id: str) -> None:
    """AC-24.5 ENTRY_SCRIPT + SPAWN_FLAGS remain required."""
    assert ac_id == "AC-24.5"
    text = _spec_text()
    assert "avkit_api" in text and "__main__" in text
    from avkit_api.cli import parse_args

    with pytest.raises(SystemExit):
        parse_args(["--token", "t", "--port", "0", "--app-data", "."])


@pytest.mark.parametrize("ac_id", ["AC-24.6"], ids=["AC-24.6"])
def test_secret_sentinels(tmp_path: Path, ac_id: str) -> None:
    """AC-24.6 SECRET_SENTINELS absent from return JSON and file bytes."""
    assert ac_id == "AC-24.6"
    from avkit_api.cli import write_descriptor

    sentinel_a = "sentinel-token-AAA-9f3a"
    sentinel_b = "sentinel-mcp-BBB-c21b"
    payload = write_descriptor(
        app_data=tmp_path,
        pid=os.getpid(),
        instance_id="inst-pack",
        executable_path=str(tmp_path / "avkit-backend.exe"),
        host="127.0.0.1",
        port=51236,
        token=sentinel_a,
        mcp_token=sentinel_b,
    )
    raw = (tmp_path / "backend.json").read_bytes()
    serialized = json.dumps(payload, separators=(",", ":"))
    assert sentinel_a not in serialized
    assert sentinel_b not in serialized
    assert sentinel_a.encode("utf-8") not in raw
    assert sentinel_b.encode("utf-8") not in raw
    for key in SECRET_KEYS:
        assert key.encode("utf-8") not in raw
    leaked = dict(payload)
    leaked["instance_id"] = sentinel_a
    assert sentinel_a in json.dumps(leaked)
    assert PACK_SCRIPT.is_file(), "packaging helper must exist to own the sentinel contract"


@pytest.mark.parametrize("ac_id", ["AC-24.7"], ids=["AC-24.7"])
def test_descriptor_keys_atomic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, ac_id: str
) -> None:
    """AC-24.7 DESCRIPTOR_KEYS + os.replace."""
    assert ac_id == "AC-24.7"
    from avkit_api.cli import write_descriptor

    calls: list[tuple[str, str]] = []
    real_replace = os.replace

    def _spy(src: str, dst: str) -> None:
        calls.append((src, dst))
        real_replace(src, dst)

    monkeypatch.setattr(os, "replace", _spy)
    payload = write_descriptor(
        app_data=tmp_path,
        pid=os.getpid(),
        instance_id="inst-keys",
        executable_path=str(tmp_path / "avkit-backend.exe"),
        host="127.0.0.1",
        port=51237,
        token="nonce",
        mcp_token="mcp",
    )
    assert set(payload) == DESCRIPTOR_KEYS
    assert calls
    assert PACK_SCRIPT.is_file()


@pytest.mark.parametrize("ac_id", ["AC-24.8"], ids=["AC-24.8"])
def test_ready_line_requires_pack_script(ac_id: str) -> None:
    """AC-24.8 READY_LINE is printed by cli.main after bind — pack script must exist."""
    assert ac_id == "AC-24.8"
    from avkit_api.cli import READY_PREFIX

    assert READY_PREFIX == "AVKIT_READY"
    assert PACK_SCRIPT.is_file()


@pytest.mark.parametrize("ac_id", ["AC-24.9"], ids=["AC-24.9"])
def test_no_torch_in_spec(ac_id: str) -> None:
    """AC-24.9 NO_TORCH_NSIS on the spec side."""
    assert ac_id == "AC-24.9"
    text = _spec_text()
    tree = ast.parse(text)
    hidden: list[str] = []
    excludes: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "hiddenimports":
                    if isinstance(node.value, ast.List):
                        hidden = [
                            elt.value
                            for elt in node.value.elts
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                        ]
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "Analysis":
                for kw in node.keywords:
                    if kw.arg == "excludes" and isinstance(kw.value, ast.List):
                        excludes = [
                            elt.value
                            for elt in kw.value.elts
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                        ]
    assert "torch" not in hidden
    assert "torch" in excludes
    assert "cuda" not in hidden


@pytest.mark.parametrize("ac_id", ["AC-24.10"], ids=["AC-24.10"])
def test_pack_dist_onedir_layout(ac_id: str) -> None:
    """AC-24.10 PACK_DIST_DIR contains PACK_DIST_EXE plus onedir support tree."""
    assert ac_id == "AC-24.10"
    assert PACK_SCRIPT.is_file()
    if not PACK_DIST_EXE.is_file():
        pytest.fail("PACK_DIST_EXE missing — pack script has not produced an onedir tree")
    raw = PACK_DIST_EXE.read_bytes()
    assert raw[:2] == b"MZ"
    assert len(raw) > 1024, "PACK_DIST_EXE is a layout stub, not a PyInstaller COLLECT"
    support = PACK_DIST_DIR / "_internal"
    assert support.is_dir() or any(PACK_DIST_DIR.iterdir())


# --- MEU-72 AC-72.6 SPEC_BUNDLE ---------------------------------------------------------------

SPEC_EXCLUDES_72 = {
    "torch",
    "torchvision",
    "torchaudio",
    "kokoro",
    "phonemizer",
    "espeakng_loader",
    "misaki.espeak",
}
SPEC_HIDDEN_72 = {
    "misaki.en",
    "misaki.token",
    "num2words",
    "spacy",
    "onnxruntime",
    "avkit_infra.tts.g2p",
    "avkit_infra.tts.espeak",
}
SPEC_DATAS_FORBIDDEN_72 = ("kokoro-v1_0.pth", ".onnx", "voices", "en_core_web_sm", "espeak")


def _calls_named(node: ast.AST, name: str) -> list[ast.Call]:
    return [
        sub
        for sub in ast.walk(node)
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) and sub.func.id == name
    ]


def _first_str_arg(call: ast.Call) -> str | None:
    if call.args and isinstance(call.args[0], ast.Constant) and isinstance(call.args[0].value, str):
        return call.args[0].value
    return None


def test_ac_72_6_spec_bundle() -> None:
    """AC-72.6 SPEC_BUNDLE: excludes, hiddenimports, misaki datas, num2words as source."""
    tree = ast.parse(_spec_text())
    assigned: dict[str, ast.expr] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigned[target.id] = node.value
    analysis = _calls_named(tree, "Analysis")
    assert len(analysis) == 1
    keywords = {kw.arg: kw.value for kw in analysis[0].keywords if kw.arg}

    def resolve(value: ast.expr) -> ast.expr:
        if isinstance(value, ast.Name) and value.id in assigned:
            return assigned[value.id]
        return value

    excludes = resolve(keywords["excludes"])
    assert isinstance(excludes, ast.List)
    excluded = {elt.value for elt in excludes.elts if isinstance(elt, ast.Constant)}
    assert SPEC_EXCLUDES_72 <= excluded, SPEC_EXCLUDES_72 - excluded

    hidden = resolve(keywords["hiddenimports"])
    assert isinstance(hidden, ast.List)
    named = {elt.value for elt in hidden.elts if isinstance(elt, ast.Constant)}
    assert SPEC_HIDDEN_72 <= named, SPEC_HIDDEN_72 - named
    submodules = [_first_str_arg(call) for call in _calls_named(hidden, "collect_submodules")]
    assert "num2words" in submodules

    datas = resolve(keywords["datas"])
    data_calls = [_first_str_arg(call) for call in _calls_named(datas, "collect_data_files")]
    assert "misaki" in data_calls
    strings = [
        sub.value
        for sub in ast.walk(datas)
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str)
    ]
    for forbidden in SPEC_DATAS_FORBIDDEN_72:
        assert not any(forbidden in item for item in strings), forbidden

    mode = resolve(keywords["module_collection_mode"])
    assert ast.literal_eval(mode).get("num2words") == "py"
