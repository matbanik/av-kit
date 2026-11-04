# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller onedir spec for avkit-backend.

EXCLUDE_GLOBS (must not be collected): avkit.db, .env, *.onnx, *.pth,
**/.avkit/models/**, **/cuda/**, **/cudnn/**.

SPEC_BUNDLE (MEU-72): the ONNX runtime ships without torch or kokoro. English G2P is
misaki.en (Apache-2.0) plus its data; num2words (LGPL-2.1) is collected as replaceable .py
source. phonemizer, espeakng_loader and misaki.espeak (the in-process espeak-ng binding) are
excluded; eSpeak NG is a user-installed CLI. Kokoro weights, voice packs and the spaCy model
are downloaded at runtime and never bundled. See THIRD_PARTY_NOTICES.md.
"""

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

SPEC_DIR = Path(SPECPATH)  # noqa: F821 — injected by PyInstaller
REPO_ROOT = SPEC_DIR.parent
ENTRY = str(REPO_ROOT / "packages" / "api" / "src" / "avkit_api" / "__main__.py")

hiddenimports = [
    "yt_dlp",
    "youtube_transcript_api",
    "sqlalchemy",
    "pydantic",
    "uvicorn",
    "avkit_api",
    "avkit_core",
    "avkit_infra",
    "structlog",
    "onnxruntime",
    "spacy",
    "misaki",
    "misaki.data",
    "misaki.en",
    "misaki.token",
    "num2words",
    *collect_submodules("num2words"),
    "avkit_infra.tts.g2p",
    "avkit_infra.tts.espeak",
]

datas = [*collect_data_files("misaki")]

a = Analysis(  # noqa: F821
    [ENTRY],
    pathex=[str(REPO_ROOT / "packages" / "api" / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "torch",
        "torchvision",
        "torchaudio",
        "kokoro",
        "phonemizer",
        "espeakng_loader",
        "misaki.espeak",
    ],
    # LGPL-2.1: keep num2words as plain .py files a user can replace (THIRD_PARTY_NOTICES.md).
    module_collection_mode={"num2words": "py"},
    noarchive=False,
)
pyz = PYZ(a.pure)  # noqa: F821
exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="avkit-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)
coll = COLLECT(  # noqa: F821
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="avkit-backend",
)
