"""eSpeak NG CLI adapter: detection (`ESPEAK_DETECT`) and G2P (`ESPEAK_G2P`) (MEU-74, D-71).

`EspeakCliAdapter` implements `avkit_core.ports.tts.EspeakPort`. It runs the user-installed
``espeak-ng`` executable as a subprocess, with the text on stdin and never in argv. av-kit
never ships, links or installs espeak-ng; ``phonemizer``, ``espeakng_loader`` and
``misaki.espeak`` are never imported.

`MULTI_E2M`, `EN_E2M` and the post-processing in `_multi_map` and `_en_map` are ported from
misaki 0.9.4 ``misaki/espeak.py`` (``EspeakG2P`` and ``EspeakFallback``), Copyright hexgrad,
licensed under the Apache License, Version 2.0 (https://github.com/hexgrad/misaki). They keep
the upstream behaviour at misaki's ``version=None``, which is what kokoro 0.9.4 passes.
`tests/unit/test_espeak_adapter.py` checks both tables against the installed misaki source.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, Protocol

from avkit_core.domain.errors import DomainError, ValidationError
from avkit_core.domain.tts import ESPEAK_LANG_CODES, ESPEAK_UNAVAILABLE, EspeakStatus

ESPEAK_EXE = "espeak-ng"
# `%ProgramFiles%\eSpeak NG\espeak-ng.exe`, then the x86 tree: the eSpeak NG MSI's install dirs.
ESPEAK_INSTALL_DIRS: tuple[str, ...] = ("ProgramFiles", "ProgramFiles(x86)")
ESPEAK_INSTALL_EXE = Path("eSpeak NG") / "espeak-ng.exe"
ESPEAK_VERSION_TIMEOUT_S = 5
ESPEAK_G2P_TIMEOUT_S = 30
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

# `ESPEAK_VOICE`: the espeak-ng voice per Kokoro lang code (kokoro 0.9.4 `pipeline.py`).
ESPEAK_VOICE: dict[str, str] = {
    "e": "es",
    "f": "fr-fr",
    "h": "hi",
    "i": "it",
    "p": "pt-br",
    "a": "en-us",
    "b": "en-gb",
}

# Ported from misaki 0.9.4 `EspeakG2P.__init__` `self.e2m` (Apache-2.0), for e/f/h/i/p.
MULTI_E2M: dict[str, str] = {
    "a^ɪ": "I",
    "a^ʊ": "W",
    "d^z": "ʣ",
    "d^ʒ": "ʤ",
    "e^ɪ": "A",
    "o^ʊ": "O",
    "ə^ʊ": "Q",
    "s^s": "S",
    "t^s": "ʦ",
    "t^ʃ": "ʧ",
    "ɔ^ɪ": "Y",
}

# Ported from misaki 0.9.4 `EspeakFallback.E2M` (Apache-2.0), for the English fallback only.
EN_E2M: dict[str, str] = {
    "ʔˌn̩": "ʔn",
    "ʔn̩": "ʔn",
    "a^ɪ": "I",
    "a^ʊ": "W",
    "d^ʒ": "ʤ",
    "e^ɪ": "A",
    "e": "A",
    "t^ʃ": "ʧ",
    "ɔ^ɪ": "Y",
    "ə^l": "ᵊl",
    "ʲo": "jo",
    "ʲə": "jə",
    "ʲ": "",
    "ɚ": "əɹ",
    "r": "ɹ",
    "x": "k",
    "ç": "k",
    "ɐ": "ə",
    "ɬ": "l",
    "̃": "",
}

# Upstream orders: `EspeakG2P` sorts by key, `EspeakFallback` by key length, longest first
# (a stable sort, so equal lengths keep the dict order above).
_MULTI_ORDER = sorted(MULTI_E2M.items())
_EN_ORDER = sorted(EN_E2M.items(), key=lambda kv: -len(kv[0]))
# Text is split at this punctuation; each separator is kept verbatim (angles become curly).
_SEPARATORS = re.compile(r'([;:,.!?¡¿—…"«»“”()])')
_CURLY = {"«": "“", "»": "”"}
# espeak-ng marks a language switch inside a clause as `(en)` ... `(es)`.
_SWITCH_FLAG = re.compile(r"\([a-z]{2,3}(?:-[a-z0-9]+)*\)")
_SYLLABIC = re.compile(r"(\S)̩")

Runner = Callable[..., subprocess.CompletedProcess[str]]


class TtsRuntimeError(DomainError):
    """The eSpeak NG subprocess is missing, exited nonzero or timed out (D-97)."""


class _Token(Protocol):
    text: str


def _multi_map(ps: str) -> str:
    """`MULTI_E2M` in sorted key order, then `^` and `-` removed (misaki `espeak.py:96-104`)."""
    for old, new in _MULTI_ORDER:
        ps = ps.replace(old, new)
    return ps.replace("^", "").replace("-", "")


def _en_map(ps: str, british: bool) -> str:
    """`EN_E2M` longest key first, then the `EspeakFallback.__call__` steps (`espeak.py:49-58`)."""
    for old, new in _EN_ORDER:
        ps = ps.replace(old, new)
    ps = _SYLLABIC.sub(r"ᵊ\1", ps).replace(chr(809), "")
    if british:
        ps = ps.replace("e^ə", "ɛː").replace("iə", "ɪə").replace("ə^ʊ", "Q")
    else:
        ps = ps.replace("o^ʊ", "O").replace("ɜːɹ", "ɜɹ").replace("ɜː", "ɜɹ")
        ps = ps.replace("ɪə", "iə").replace("ː", "")
    ps = ps.replace("o", "ɔ")
    ps = ps.replace("ɾ", "T").replace("ʔ", "t")
    return ps.replace("^", "")


class EspeakCliAdapter:
    """`EspeakPort` over the espeak-ng CLI. `which`, `environ` and `run` are injectable."""

    def __init__(
        self,
        *,
        which: Callable[[str], str | None] = shutil.which,
        environ: Mapping[str, str] | None = None,
        run: Runner = subprocess.run,
    ) -> None:
        self._which = which
        self._environ = os.environ if environ is None else environ
        self._run = run
        # Version per `(path, mtime_ns)`. Only successful probes are stored (no latch).
        self._versions: dict[tuple[str, int], str] = {}

    def _locate(self) -> Path | None:
        found = self._which(ESPEAK_EXE)
        if found:
            return Path(found)
        for variable in ESPEAK_INSTALL_DIRS:
            root = self._environ.get(variable)
            if not root:
                continue
            candidate = Path(root) / ESPEAK_INSTALL_EXE
            if candidate.is_file():
                return candidate
        return None

    def status(self) -> EspeakStatus:
        """`ESPEAK_DETECT`: re-resolve the executable now; `--version` only on a new file."""
        path = self._locate()
        if path is None:
            return ESPEAK_UNAVAILABLE
        try:
            key = (str(path), path.stat().st_mtime_ns)
        except OSError:
            return ESPEAK_UNAVAILABLE
        version = self._versions.get(key)
        if version is None:
            version = self._probe_version(path)
            if version is None:
                return ESPEAK_UNAVAILABLE
            self._versions[key] = version
        return EspeakStatus(available=True, version=version, path=path)

    def _probe_version(self, path: Path) -> str | None:
        try:
            done = self._run(
                [str(path), "--version"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=ESPEAK_VERSION_TIMEOUT_S,
                creationflags=CREATE_NO_WINDOW,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if done.returncode != 0:
            return None
        lines = (done.stdout or "").splitlines()
        first = lines[0].strip() if lines else ""
        return first or None

    def phonemize(self, text: str, lang_code: str) -> str:
        """`ESPEAK_G2P` for e/f/h/i/p: IPA through `MULTI_E2M`, punctuation kept in place."""
        if lang_code not in ESPEAK_LANG_CODES:
            raise ValidationError(f"espeak-ng G2P does not serve lang_code {lang_code!r}")
        return self._phonemize(text, ESPEAK_VOICE[lang_code], _multi_map)

    def en_fallback(self, british: bool) -> Callable[[_Token], tuple[str | None, int | None]]:
        """`ESPEAK_EN_FALLBACK`: the callable `misaki.en.G2P(fallback=...)` gets for a/b."""
        voice = ESPEAK_VOICE["b" if british else "a"]

        def fallback(token: _Token) -> tuple[str | None, int | None]:
            raw = self._phonemize(token.text, voice, lambda ps: ps)
            if not raw.strip():
                return None, None
            return _en_map(raw.strip(), british), 2

        return fallback

    def _phonemize(self, text: str, voice: str, mapping: Callable[[str], str]) -> str:
        status = self.status()
        if not status.available or status.path is None:
            raise TtsRuntimeError("espeak-ng failed: espeak-ng is not installed")
        parts: list[str] = []
        for index, piece in enumerate(_SEPARATORS.split(text)):
            if index % 2 == 1:
                parts.append(_CURLY.get(piece, piece))
                continue
            core = piece.strip()
            if not core:
                parts.append(piece)
                continue
            lead = piece[: len(piece) - len(piece.lstrip())]
            trail = piece[len(piece.rstrip()) :]
            parts.append(lead + mapping(self._ipa(status.path, voice, core)) + trail)
        return "".join(parts)

    def _ipa(self, exe: Path, voice: str, text: str) -> str:
        """One espeak-ng run: IPA with `^` ties, language-switch flags removed."""
        argv = [str(exe), "-q", "--ipa", "--tie=^", "-v", voice, "--stdin"]
        kwargs: dict[str, Any] = {
            "input": text,
            "capture_output": True,
            "text": True,
            "encoding": "utf-8",
            "errors": "replace",
            "timeout": ESPEAK_G2P_TIMEOUT_S,
            "creationflags": CREATE_NO_WINDOW,
            "check": False,
        }
        try:
            done = self._run(argv, **kwargs)
        except subprocess.TimeoutExpired as exc:
            raise TtsRuntimeError(
                f"espeak-ng failed: timed out after {ESPEAK_G2P_TIMEOUT_S} s"
            ) from exc
        except OSError as exc:
            raise TtsRuntimeError(f"espeak-ng failed: {exc}") from exc
        if done.returncode != 0:
            detail = (done.stderr or "").strip()
            suffix = f": {detail}" if detail else ""
            raise TtsRuntimeError(f"espeak-ng failed: exit {done.returncode}{suffix}")
        lines = [line.strip() for line in (done.stdout or "").splitlines() if line.strip()]
        return _SWITCH_FLAG.sub("", " ".join(lines)).strip()
