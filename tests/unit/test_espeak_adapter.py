"""MEU-74 eSpeak NG adapter: `ESPEAK_DETECT` (AC-74.2) and `ESPEAK_G2P` / `ESPEAK_MAP` (AC-74.6).

Every case runs against a fake `which`, environment and process runner. Executables are
real tmp files so the `(path, mtime_ns)` version cache sees real stat results.
"""

from __future__ import annotations

import ast
import importlib.util
import os
import subprocess
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from avkit_core.domain.errors import ValidationError

VERSION_LINE = (
    "eSpeak NG text-to-speech: 1.52.0  Data at: C:\\Program Files\\eSpeak NG\\espeak-ng-data"
)
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)


class FakeRunner:
    """Records every call. `--version` answers `version_rc`; `--stdin` answers `outputs[stdin]`."""

    def __init__(self) -> None:
        self.calls: list[tuple[list[str], dict[str, Any]]] = []
        self.version_rc = 0
        self.version_raise: BaseException | None = None
        self.outputs: dict[str, str] = {}
        self.default_output = ""
        self.g2p_rc = 0
        self.g2p_raise: BaseException | None = None

    def __call__(self, argv: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        self.calls.append((list(argv), kwargs))
        if "--version" in argv:
            if self.version_raise is not None:
                raise self.version_raise
            return subprocess.CompletedProcess(
                argv, self.version_rc, f"{VERSION_LINE}\nsecond line\n", ""
            )
        if self.g2p_raise is not None:
            raise self.g2p_raise
        text = str(kwargs.get("input", "")).strip()
        out = self.outputs.get(text, self.default_output)
        return subprocess.CompletedProcess(
            argv, self.g2p_rc, f" {out}\n", "boom" if self.g2p_rc else ""
        )

    def version_calls(self) -> int:
        return sum(1 for argv, _ in self.calls if "--version" in argv)

    def g2p_calls(self) -> list[tuple[list[str], dict[str, Any]]]:
        return [(argv, kw) for argv, kw in self.calls if "--stdin" in argv]


def _exe(root: Path) -> Path:
    exe = root / "eSpeak NG" / "espeak-ng.exe"
    exe.parent.mkdir(parents=True, exist_ok=True)
    exe.write_bytes(b"MZ")
    return exe


def _adapter(
    runner: FakeRunner,
    *,
    which: Callable[[str], str | None] = lambda _name: None,
    environ: dict[str, str] | None = None,
) -> Any:
    from avkit_infra.tts.espeak import EspeakCliAdapter

    return EspeakCliAdapter(which=which, environ=environ or {}, run=runner)


def _on_path(exe: Path) -> Callable[[str], str | None]:
    return lambda name: str(exe) if name == "espeak-ng" else None


def _g2p_adapter(tmp_path: Path) -> tuple[Any, FakeRunner, Path]:
    runner = FakeRunner()
    exe = _exe(tmp_path / "bin")
    return _adapter(runner, which=_on_path(exe)), runner, exe


# --- AC-74.2 ESPEAK_DETECT ---------------------------------------------------------------


def test_ac_74_2_found_on_path(tmp_path: Path) -> None:
    from avkit_core.domain.tts import EspeakStatus

    runner = FakeRunner()
    exe = _exe(tmp_path / "onpath")
    pf = _exe(tmp_path / "pf")
    adapter = _adapter(runner, which=_on_path(exe), environ={"ProgramFiles": str(pf.parents[1])})
    assert adapter.status() == EspeakStatus(available=True, version=VERSION_LINE, path=exe)
    argv, kwargs = runner.calls[0]
    assert argv == [str(exe), "--version"]
    assert kwargs["timeout"] == 5


def test_ac_74_2_found_only_under_program_files(tmp_path: Path) -> None:
    from avkit_core.domain.tts import EspeakStatus

    runner = FakeRunner()
    exe = _exe(tmp_path / "pf")
    _exe(tmp_path / "pf86")
    environ = {"ProgramFiles": str(tmp_path / "pf"), "ProgramFiles(x86)": str(tmp_path / "pf86")}
    adapter = _adapter(runner, environ=environ)
    assert adapter.status() == EspeakStatus(available=True, version=VERSION_LINE, path=exe)


def test_ac_74_2_found_only_under_program_files_x86(tmp_path: Path) -> None:
    from avkit_core.domain.tts import EspeakStatus

    runner = FakeRunner()
    exe = _exe(tmp_path / "pf86")
    environ = {"ProgramFiles": str(tmp_path / "pf"), "ProgramFiles(x86)": str(tmp_path / "pf86")}
    adapter = _adapter(runner, environ=environ)
    assert adapter.status() == EspeakStatus(available=True, version=VERSION_LINE, path=exe)


@pytest.mark.parametrize(
    "environ",
    [{}, {"ProgramFiles": "{tmp}/pf", "ProgramFiles(x86)": "{tmp}/pf86"}],
    ids=["no-env", "empty-dirs"],
)
def test_ac_74_2_found_nowhere(tmp_path: Path, environ: dict[str, str]) -> None:
    from avkit_core.domain.tts import EspeakStatus

    runner = FakeRunner()
    env = {key: value.format(tmp=tmp_path) for key, value in environ.items()}
    adapter = _adapter(runner, environ=env)
    assert adapter.status() == EspeakStatus(available=False, version=None, path=None)
    assert runner.calls == []


@pytest.mark.parametrize(
    "failure",
    ["nonzero", "timeout", "oserror"],
)
def test_ac_74_2_failing_version_probe_is_unavailable(tmp_path: Path, failure: str) -> None:
    runner = FakeRunner()
    exe = _exe(tmp_path / "bin")
    if failure == "nonzero":
        runner.version_rc = 1
    elif failure == "timeout":
        runner.version_raise = subprocess.TimeoutExpired([str(exe), "--version"], 5)
    else:
        runner.version_raise = OSError("bad exe")
    status = _adapter(runner, which=_on_path(exe)).status()
    assert status.available is False
    assert status.version is None


def test_ac_74_2_version_is_cached_per_path_and_mtime(tmp_path: Path) -> None:
    runner = FakeRunner()
    exe = _exe(tmp_path / "bin")
    adapter = _adapter(runner, which=_on_path(exe))
    assert adapter.status().available is True
    assert adapter.status().available is True
    assert runner.version_calls() == 1
    mtime = exe.stat().st_mtime_ns
    os.utime(exe, ns=(mtime + 2_000_000_000, mtime + 2_000_000_000))
    assert adapter.status().version == VERSION_LINE
    assert runner.version_calls() == 2


def test_ac_74_2_a_fresh_install_is_seen_on_the_next_call(tmp_path: Path) -> None:
    runner = FakeRunner()
    environ = {"ProgramFiles": str(tmp_path / "pf")}
    adapter = _adapter(runner, environ=environ)
    assert adapter.status().available is False
    exe = _exe(tmp_path / "pf")
    status = adapter.status()
    assert status.available is True
    assert status.path == exe


def test_ac_74_2_a_failed_probe_is_not_latched(tmp_path: Path) -> None:
    runner = FakeRunner()
    exe = _exe(tmp_path / "bin")
    adapter = _adapter(runner, which=_on_path(exe))
    runner.version_rc = 1
    assert adapter.status().available is False
    runner.version_rc = 0
    assert adapter.status().available is True


# --- AC-74.6 ESPEAK_G2P ------------------------------------------------------------------


def test_ac_74_6_argv_is_exact_and_text_goes_on_stdin(tmp_path: Path) -> None:
    adapter, runner, exe = _g2p_adapter(tmp_path)
    runner.outputs = {"este texto": "ˈeste tˈeksto"}
    assert adapter.phonemize("este texto", "e") == "ˈeste tˈeksto"
    calls = runner.g2p_calls()
    assert len(calls) == 1
    argv, kwargs = calls[0]
    assert argv == [str(exe), "-q", "--ipa", "--tie=^", "-v", "es", "--stdin"]
    assert all("este" not in part for part in argv)
    assert kwargs["input"].strip() == "este texto"
    assert kwargs["timeout"] == 30
    assert kwargs["encoding"] == "utf-8"
    assert kwargs["creationflags"] & CREATE_NO_WINDOW == CREATE_NO_WINDOW


def test_ac_74_6_voice_per_lang_code() -> None:
    from avkit_infra.tts.espeak import ESPEAK_VOICE

    assert ESPEAK_VOICE == {
        "e": "es",
        "f": "fr-fr",
        "h": "hi",
        "i": "it",
        "p": "pt-br",
        "a": "en-us",
        "b": "en-gb",
    }


@pytest.mark.parametrize(
    ("lang_code", "voice"), [("f", "fr-fr"), ("h", "hi"), ("i", "it"), ("p", "pt-br")]
)
def test_ac_74_6_multilingual_codes_use_their_voice(
    tmp_path: Path, lang_code: str, voice: str
) -> None:
    adapter, runner, _exe_path = _g2p_adapter(tmp_path)
    runner.default_output = "bɔ̃"
    adapter.phonemize("bon", lang_code)
    argv, _kwargs = runner.g2p_calls()[0]
    assert argv[argv.index("-v") + 1] == voice


def test_ac_74_6_punctuation_is_preserved_and_angles_become_curly(tmp_path: Path) -> None:
    adapter, runner, _exe_path = _g2p_adapter(tmp_path)
    runner.outputs = {"Hola": "ˈola", "mundo": "mˈundo", "bien": "bjˈen"}
    assert adapter.phonemize("Hola, «mundo» (bien).", "e") == "ˈola, “mˈundo” (bjˈen)."
    stdin = [kwargs["input"].strip() for _argv, kwargs in runner.g2p_calls()]
    assert stdin == ["Hola", "mundo", "bien"]


def test_ac_74_6_every_separator_survives_in_order(tmp_path: Path) -> None:
    adapter, runner, _exe_path = _g2p_adapter(tmp_path)
    runner.default_output = "a"
    text = 'x;x:x,x.x!x?¡x¿x—x…x"x“x”x'
    assert adapter.phonemize(text, "e") == 'a;a:a,a.a!a?¡a¿a—a…a"a“a”a'


def test_ac_74_6_language_switch_flags_are_stripped(tmp_path: Path) -> None:
    adapter, runner, _exe_path = _g2p_adapter(tmp_path)
    runner.outputs = {"hola weekend": "ˈola (en)wˈiːkɛnd(es)"}
    assert adapter.phonemize("hola weekend", "e") == "ˈola wˈiːkɛnd"


@pytest.mark.parametrize("failure", ["nonzero", "timeout"])
def test_ac_74_6_failure_raises_tts_runtime_error(tmp_path: Path, failure: str) -> None:
    from avkit_infra.tts.espeak import TtsRuntimeError

    adapter, runner, exe = _g2p_adapter(tmp_path)
    if failure == "nonzero":
        runner.g2p_rc = 1
    else:
        runner.g2p_raise = subprocess.TimeoutExpired([str(exe)], 30)
    with pytest.raises(TtsRuntimeError, match="^espeak-ng failed: "):
        adapter.phonemize("hola", "e")


def test_ac_74_6_phonemize_without_espeak_raises_tts_runtime_error() -> None:
    from avkit_infra.tts.espeak import TtsRuntimeError

    runner = FakeRunner()
    with pytest.raises(TtsRuntimeError, match="^espeak-ng failed: "):
        _adapter(runner).phonemize("hola", "e")
    assert runner.g2p_calls() == []


@pytest.mark.parametrize("lang_code", ["j", "z", "x"])
def test_ac_74_6_unsupported_lang_code_raises_validation_error(
    tmp_path: Path, lang_code: str
) -> None:
    adapter, runner, _exe_path = _g2p_adapter(tmp_path)
    with pytest.raises(ValidationError):
        adapter.phonemize("text", lang_code)
    assert runner.g2p_calls() == []


# --- AC-74.6 ESPEAK_MAP: MULTI_E2M (e/f/h/i/p) --------------------------------------------

MULTI_SAMPLES: list[tuple[str, str]] = [
    ("ka^ɪ", "kI"),
    ("ka^ʊ", "kW"),
    ("d^zeta", "ʣeta"),
    ("d^ʒiro", "ʤiro"),
    ("le^ɪ", "lA"),
    ("so^ʊ", "sO"),
    ("ɡə^ʊ", "ɡQ"),
    ("mas^s", "maS"),
    ("pit^sa", "piʦa"),
    ("t^ʃao", "ʧao"),
    ("bɔ^ɪ", "bY"),
]


@pytest.mark.parametrize(("raw", "mapped"), MULTI_SAMPLES)
def test_ac_74_6_multi_e2m_one_sample_per_rule(tmp_path: Path, raw: str, mapped: str) -> None:
    adapter, runner, _exe_path = _g2p_adapter(tmp_path)
    runner.default_output = raw
    assert adapter.phonemize("w", "i") == mapped


def test_ac_74_6_multi_samples_cover_every_rule() -> None:
    from avkit_infra.tts.espeak import MULTI_E2M

    assert isinstance(MULTI_E2M, dict)
    assert len(MULTI_SAMPLES) == len(MULTI_E2M)


def test_ac_74_6_spanish_e_stays_e(tmp_path: Path) -> None:
    adapter, runner, _exe_path = _g2p_adapter(tmp_path)
    runner.outputs = {"este": "ˈeste"}
    assert adapter.phonemize("este", "e") == "ˈeste"


def test_ac_74_6_french_keeps_the_nasal_tilde_and_drops_hyphens(tmp_path: Path) -> None:
    adapter, runner, _exe_path = _g2p_adapter(tmp_path)
    runner.outputs = {"bonjour": "bɔ̃-ʒˈuʁ"}
    out = adapter.phonemize("bonjour", "f")
    assert out == "bɔ̃ʒˈuʁ"
    assert "\u0303" in out


def test_ac_74_6_multilingual_applies_no_english_only_rule(tmp_path: Path) -> None:
    adapter, runner, _exe_path = _g2p_adapter(tmp_path)
    runner.default_output = "e r x ã ɚ ɐ"
    assert adapter.phonemize("w", "p") == "e r x ã ɚ ɐ"


# --- AC-74.6 ESPEAK_MAP: EN_E2M and ESPEAK_EN_FALLBACK -------------------------------------

# One sample per EspeakFallback.E2M rule, US (british=False), with the final value after
# every post-step (`o`→`ɔ`, `ɾ`→`T`, `ʔ`→`t`, `ː` removed, `^` removed).
EN_SAMPLES: list[tuple[str, str]] = [
    ("bʌʔˌn\u0329", "bʌtn"),
    ("bʌʔn\u0329", "bʌtn"),
    ("ma^ɪ", "mI"),
    ("na^ʊ", "nW"),
    ("d^ʒʌmp", "ʤʌmp"),
    ("de^ɪ", "dA"),
    ("bed", "bAd"),
    ("t^ʃɪp", "ʧɪp"),
    ("bɔ^ɪ", "bY"),
    ("lə^l", "lᵊl"),
    ("tʲo", "tjɔ"),
    ("tʲə", "tjə"),
    ("tʲa", "ta"),
    ("fɚ", "fəɹ"),
    ("red", "ɹAd"),
    ("lɔx", "lɔk"),
    ("içt", "ikt"),
    ("sɐk", "sək"),
    ("ɬan", "lan"),
    ("bã", "ba"),
]


@pytest.mark.parametrize(("raw", "mapped"), EN_SAMPLES)
def test_ac_74_6_en_e2m_one_sample_per_rule(tmp_path: Path, raw: str, mapped: str) -> None:
    adapter, runner, _exe_path = _g2p_adapter(tmp_path)
    runner.default_output = raw
    fallback = adapter.en_fallback(False)
    assert fallback(SimpleNamespace(text="word")) == (mapped, 2)


def test_ac_74_6_en_samples_cover_every_rule() -> None:
    from avkit_infra.tts.espeak import EN_E2M

    assert isinstance(EN_E2M, dict)
    assert len(EN_SAMPLES) == len(EN_E2M)


@pytest.mark.parametrize(
    ("british", "raw", "mapped"),
    [
        (False, "ɡo^ʊ", "ɡO"),
        (False, "wɔːɾɚ", "wɔTəɹ"),
        (False, "bɜːɹd", "bɜɹd"),
        (False, "bɜːd", "bɜɹd"),
        (False, "nɪə", "niə"),
        (False, "bʌtn\u0329", "bʌtᵊn"),
        (True, "ɡə^ʊ", "ɡQ"),
        (True, "niə", "nɪə"),
        (True, "kɑːt", "kɑːt"),
        # Upstream order: E2M `e`→`A` runs first, so `e^ə` never reaches the British step.
        (True, "ðe^ə", "ðAə"),
    ],
)
def test_ac_74_6_en_fallback_post_steps(
    tmp_path: Path, british: bool, raw: str, mapped: str
) -> None:
    adapter, runner, _exe_path = _g2p_adapter(tmp_path)
    runner.default_output = raw
    assert adapter.en_fallback(british)(SimpleNamespace(text="word")) == (mapped, 2)
    argv, kwargs = runner.g2p_calls()[0]
    assert argv[argv.index("-v") + 1] == ("en-gb" if british else "en-us")
    assert kwargs["input"].strip() == "word"


def test_ac_74_6_en_fallback_empty_output_is_none(tmp_path: Path) -> None:
    adapter, runner, _exe_path = _g2p_adapter(tmp_path)
    runner.default_output = ""
    assert adapter.en_fallback(False)(SimpleNamespace(text="zzz")) == (None, None)


# --- AC-74.6 ESPEAK_MAP_PARITY ------------------------------------------------------------


def _misaki_espeak_tree() -> ast.Module:
    spec = importlib.util.find_spec("misaki")
    assert spec is not None and spec.submodule_search_locations
    source = Path(next(iter(spec.submodule_search_locations))) / "espeak.py"
    return ast.parse(source.read_text(encoding="utf-8"))


def _class(tree: ast.Module, name: str) -> ast.ClassDef:
    return next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == name)


def _upstream_multi(tree: ast.Module) -> dict[str, str]:
    init = next(
        node
        for node in _class(tree, "EspeakG2P").body
        if isinstance(node, ast.FunctionDef) and node.name == "__init__"
    )
    for node in init.body:
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Attribute)
            and node.targets[0].attr == "e2m"
            and isinstance(node.value, ast.Dict)
        ):
            return ast.literal_eval(node.value)
    raise AssertionError("EspeakG2P.__init__ has no self.e2m dict literal")


def _upstream_en(tree: ast.Module) -> dict[str, str]:
    for node in _class(tree, "EspeakFallback").body:
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "E2M"
        ):
            for inner in ast.walk(node.value):
                if isinstance(inner, ast.Dict):
                    return ast.literal_eval(inner)
    raise AssertionError("EspeakFallback has no E2M dict literal")


def test_ac_74_6_espeak_map_parity_with_installed_misaki() -> None:
    from avkit_infra.tts.espeak import EN_E2M, MULTI_E2M

    tree = _misaki_espeak_tree()
    assert dict(MULTI_E2M) == _upstream_multi(tree)
    assert dict(EN_E2M) == _upstream_en(tree)
    # D-98: espeak.py never imports the upstream G2P stack. `sys.modules` cannot show this here,
    # because the `avkit_infra.tts` package init imports kokoro, which imports misaki.espeak.
    spec = importlib.util.find_spec("avkit_infra.tts.espeak")
    assert spec is not None and spec.origin is not None
    imported: set[str] = set()
    for node in ast.walk(ast.parse(Path(spec.origin).read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not imported & {"misaki", "phonemizer", "espeakng_loader"}
