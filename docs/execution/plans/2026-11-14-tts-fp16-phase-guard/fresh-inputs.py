"""Session 73 fresh inputs (plan FRESH_INPUTS and INSTALLED_READ; D-790, D-791, D-798).

``run`` downloads the spike's seven inputs from Hugging Face at the app's own pins into a new
folder under ``C:/Temp/av-kit/s73``, hashes the installed copies of the same seven files under
``<HOME>/.avkit/models`` (read only: no listing, no copy, no other file), and compares both with
Session 52's cached copies. It exits 0 only when every downloaded file equals its cached copy and
every installed file that exists equals it too. The receipt writes ``<HOME>`` for the home folder.

Before the Hugging Face client is imported, ``run`` drops every inherited ``HF_*`` and
``HUGGINGFACE_*`` variable from its own process and points every client cache into its private
``HF_HOME``. Each file is fetched with ``force_download``, so no inherited cache, and no file
already in the destination, can stand in for a fresh body download.

``selftest`` proves the refusals, the read and the comparison on its own fixtures, offline. It
also starts this script's ``client-check`` in a child process: the real client, an inherited
cache that already holds the file, and a stale local copy, with the network forbidden and only
the body transfer stubbed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable

S73 = pathlib.Path("C:/Temp/av-kit/s73")
CACHED = pathlib.Path("C:/Temp/av-kit/s52/smoke-models")
HF_HOME = S73 / "hf-home"
VOICES = ("af_heart", "am_michael", "af_bella", "bf_emma")
EXPECT = {
    "kokoro-v1.0-onnx/onnx/model_fp16.onnx": (
        "ba4527a874b42b21e35f468c10d326fdff3c7fc8cac1f85e9eb6c0dfc35c334a"
    ),
    "kokoro-v1.0-onnx/onnx/model_quantized.onnx": (
        "fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478"
    ),
}
#: Variables that would send the download elsewhere, or stop it, if set.
REFUSED_ENV = (
    "HF_ENDPOINT",
    "HF_HUB_OFFLINE",
    "TRANSFORMERS_OFFLINE",
    "HUGGINGFACE_CO_STAGING",
    "HF_HUB_ENABLE_HF_TRANSFER",
)
#: Inherited variables with these prefixes are dropped from this process before the client loads.
SCRUB_PREFIXES = ("HF_", "HUGGINGFACE_")
HF_DEFAULT_ENDPOINT = "https://huggingface.co"

Fetch = Callable[[str, str, "str | None", pathlib.Path], pathlib.Path]


class InputError(Exception):
    """A refusal: the run writes nothing and reads no installed file."""


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inputs() -> list[dict[str, str | None]]:
    """The seven files, with the repository, file name and revision the app itself uses."""
    from avkit_infra.tts.assets import ONNX_VOCAB_FILE, ONNX_VOCAB_REPO
    from avkit_infra.tts.voices import HF_FILE_MAP, ONNX_LOCAL_DIR, ONNX_REPO, ONNX_REVISION

    rows: list[dict[str, str | None]] = []
    for variant in ("kokoro-onnx-fp16", "kokoro-onnx-int8"):
        repo, filename = HF_FILE_MAP[variant]
        rows.append(
            {
                "rel": f"{ONNX_LOCAL_DIR}/{filename}",
                "repo": repo,
                "filename": filename,
                "revision": ONNX_REVISION,
                "subdir": ONNX_LOCAL_DIR,
            }
        )
    for voice in VOICES:
        filename = f"voices/{voice}.bin"
        rows.append(
            {
                "rel": f"{ONNX_LOCAL_DIR}/{filename}",
                "repo": ONNX_REPO,
                "filename": filename,
                "revision": ONNX_REVISION,
                "subdir": ONNX_LOCAL_DIR,
            }
        )
    # vocab.py fetches config.json with no revision, so neither does this.
    rows.append(
        {
            "rel": ONNX_VOCAB_FILE,
            "repo": ONNX_VOCAB_REPO,
            "filename": ONNX_VOCAB_FILE,
            "revision": None,
            "subdir": "",
        }
    )
    return rows


def check_dest(dest: pathlib.Path, root: pathlib.Path) -> None:
    resolved = dest.resolve()
    if resolved == root.resolve() or root.resolve() not in resolved.parents:
        raise InputError(f"destination must lie inside {root}")
    if dest.exists():
        raise InputError("destination already exists (S17); it is never deleted")


def check_env(env: dict[str, str]) -> None:
    hits = [name for name in REFUSED_ENV if env.get(name)]
    if hits:
        raise InputError("refused environment: " + ", ".join(hits))


def confine_env(hf_home: pathlib.Path) -> list[str]:
    """Drop inherited HF variables and point every client cache into ``hf_home``.

    Returns the dropped names (names only). Must run before ``huggingface_hub`` is imported,
    because the client reads its cache paths once, at import.
    """
    if "huggingface_hub" in sys.modules:
        raise InputError("huggingface_hub was imported before its environment was confined")
    dropped = sorted(k for k in os.environ if k.upper().startswith(SCRUB_PREFIXES))
    for name in dropped:
        del os.environ[name]
    os.environ["HF_HOME"] = str(hf_home)
    os.environ["HF_HUB_CACHE"] = str(hf_home / "hub")
    os.environ["HF_XET_CACHE"] = str(hf_home / "xet")
    os.environ["HF_ASSETS_CACHE"] = str(hf_home / "assets")
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    return dropped


def _inside(path: str, root: pathlib.Path) -> bool:
    p, r = pathlib.Path(path).resolve(), root.resolve()
    return p == r or r in p.parents


def verify_client(hf_home: pathlib.Path) -> list[str]:
    """Refuse a loaded client whose caches lie outside ``hf_home`` or whose source moved."""
    from huggingface_hub import constants as c

    paths = {
        "HF_HOME": c.HF_HOME,
        "HF_HUB_CACHE": c.HF_HUB_CACHE,
        "HUGGINGFACE_HUB_CACHE": c.HUGGINGFACE_HUB_CACHE,
        "HF_XET_CACHE": c.HF_XET_CACHE,
        "HF_ASSETS_CACHE": c.HF_ASSETS_CACHE,
    }
    bad = [name for name, value in paths.items() if not _inside(value, hf_home)]
    if c.ENDPOINT != HF_DEFAULT_ENDPOINT:
        bad.append("ENDPOINT")
    if c.HF_HUB_OFFLINE:
        bad.append("HF_HUB_OFFLINE")
    if bad:
        raise InputError("the client is not confined: " + ", ".join(bad))
    return sorted(paths)


def hf_fetch(
    repo: str, filename: str, revision: str | None, local_dir: pathlib.Path
) -> pathlib.Path:
    from huggingface_hub import hf_hub_download

    cache = os.environ.get("HF_HUB_CACHE")
    if not cache:
        raise InputError("the client's cache was not confined")
    return pathlib.Path(
        hf_hub_download(
            repo_id=repo,
            filename=filename,
            revision=revision,
            local_dir=str(local_dir),
            cache_dir=cache,
            force_download=True,
            token=False,
        )
    )


def metadata_commit(local_dir: pathlib.Path, filename: str) -> str | None:
    meta = local_dir / ".cache" / "huggingface" / "download" / f"{filename}.metadata"
    if not meta.is_file():
        return None
    lines = meta.read_text(encoding="utf-8").splitlines()
    return lines[0].strip() if lines else None


def download(
    rows: list[dict[str, str | None]], dest: pathlib.Path, fetch: Fetch
) -> dict[str, dict[str, object]]:
    out: dict[str, dict[str, object]] = {}
    for row in rows:
        rel, sub = str(row["rel"]), str(row["subdir"] or "")
        local_dir = dest / sub if sub else dest
        got = fetch(str(row["repo"]), str(row["filename"]), row["revision"], local_dir)
        want = dest / rel
        if got.resolve() != want.resolve() or not want.is_file():
            raise InputError(f"{rel} did not land at its planned path")
        out[rel] = {
            "sha256": sha256(want),
            "bytes": want.stat().st_size,
            "commit": metadata_commit(local_dir, str(row["filename"])),
        }
    return out


def installed(rows: list[dict[str, str | None]], models: pathlib.Path) -> dict[str, str]:
    """SHA-256 of each named file under ``models``, or ``absent``. Nothing else is opened."""
    return {
        str(r["rel"]): (
            sha256(models / str(r["rel"])) if (models / str(r["rel"])).is_file() else "absent"
        )
        for r in rows
    }


def compare(
    rows: list[dict[str, str | None]],
    cached: pathlib.Path,
    got: dict[str, dict[str, object]],
    have: dict[str, str],
    expect: dict[str, str],
) -> tuple[list[dict[str, object]], list[str]]:
    files: list[dict[str, object]] = []
    problems: list[str] = []
    for row in rows:
        rel = str(row["rel"])
        c = sha256(cached / rel) if (cached / rel).is_file() else "absent"
        d = got[rel]
        i = have[rel]
        down_eq = d["sha256"] == c
        inst_eq = None if i == "absent" else i == c
        files.append(
            {
                **row,
                "cached_sha256": c,
                "downloaded_sha256": d["sha256"],
                "downloaded_bytes": d["bytes"],
                "commit": d["commit"],
                "installed_sha256": i,
                "download_equals_cached": down_eq,
                "installed_equals_cached": inst_eq,
            }
        )
        if rel in expect and c != expect[rel]:
            problems.append(f"S10: the cached {rel} is not the planned file")
        if not down_eq:
            problems.append(f"S18: the downloaded {rel} differs from Session 52's copy")
        if row["revision"] is not None and d["commit"] != row["revision"]:
            problems.append(f"S18: {rel} came from commit {d['commit']}, not the pinned revision")
        if inst_eq is False:
            problems.append(f"S18: the installed {rel} differs from Session 52's copy")
    return files, problems


def _fold(text: str) -> str:
    return text.lower().replace("\\\\", "/").replace("\\", "/")


def redact(text: str, home: pathlib.Path) -> str:
    """Write ``<HOME>`` for the home folder, plain or JSON-escaped; refuse any form left over."""
    raw = str(home)
    for form in (raw.replace("\\", "\\\\"), raw, home.as_posix()):
        text = text.replace(form, "<HOME>")
    if _fold(raw) in _fold(text):
        raise InputError("S6: a raw home path is still in the receipt")
    return text


def run(dest: pathlib.Path, out: pathlib.Path) -> int:
    check_env(dict(os.environ))
    check_dest(dest, S73)
    if HF_HOME.exists():
        raise InputError("the private HF_HOME already exists (S17); it is never deleted")
    dropped = confine_env(HF_HOME)
    rows = inputs()
    confined = verify_client(HF_HOME)
    got = download(rows, dest, hf_fetch)
    home = pathlib.Path.home()
    have = installed(rows, home / ".avkit" / "models")
    files, problems = compare(rows, CACHED, got, have, EXPECT)
    report = {
        "dest": str(dest),
        "hf_home": str(HF_HOME),
        "scrubbed_env": dropped,
        "client_confined": confined,
        "force_download": True,
        "installed_root": "<HOME>/.avkit/models",
        "installed_present": sum(1 for v in have.values() if v != "absent"),
        "files": files,
        "problems": problems,
    }
    text = redact(json.dumps(report, indent=2), home)
    out.write_text(text + "\n", encoding="utf-8", newline="")
    for f in files:
        print(
            f["rel"],
            "download_equals_cached",
            f["download_equals_cached"],
            "installed",
            "absent" if f["installed_sha256"] == "absent" else f["installed_equals_cached"],
        )
    for p in problems:
        print(p)
    print(f"fresh-inputs: {len(problems)} problem(s)")
    return 1 if problems else 0


def selftest() -> int:
    checks: dict[str, bool] = {}
    base = pathlib.Path(tempfile.mkdtemp(prefix="s73-fresh-selftest-"))
    try:
        root = base / "s73"
        root.mkdir()
        rows = inputs()
        from avkit_infra.tts.voices import ONNX_REVISION

        by_rel = {str(r["rel"]): r for r in rows}
        checks["seven_rows"] = len(rows) == 7
        checks["fp16_pin"] = (
            by_rel.get("kokoro-v1.0-onnx/onnx/model_fp16.onnx", {}).get("revision") == ONNX_REVISION
        )
        checks["int8_pin"] = (
            by_rel.get("kokoro-v1.0-onnx/onnx/model_quantized.onnx", {}).get("revision")
            == ONNX_REVISION
        )
        checks["config_unpinned"] = by_rel.get("config.json", {}).get("revision", "x") is None

        def refused(fn: Callable[[], object]) -> bool:
            try:
                fn()
            except InputError:
                return True
            return False

        checks["refuse_outside"] = refused(lambda: check_dest(base / "elsewhere", root))
        checks["refuse_root_itself"] = refused(lambda: check_dest(root, root))
        (root / "taken").mkdir()
        checks["refuse_existing"] = refused(lambda: check_dest(root / "taken", root))
        checks["accept_new"] = not refused(lambda: check_dest(root / "new", root))
        checks["refuse_endpoint"] = refused(
            lambda: check_env({"HF_ENDPOINT": "https://example.invalid"})
        )
        checks["refuse_offline"] = refused(lambda: check_env({"HF_HUB_OFFLINE": "1"}))
        checks["refuse_offline_alias"] = refused(lambda: check_env({"TRANSFORMERS_OFFLINE": "1"}))
        checks["refuse_staging"] = refused(lambda: check_env({"HUGGINGFACE_CO_STAGING": "1"}))
        checks["refuse_transfer"] = refused(lambda: check_env({"HF_HUB_ENABLE_HF_TRANSFER": "1"}))
        checks["accept_clean_env"] = not refused(lambda: check_env({"PATH": "x"}))
        import huggingface_hub  # noqa: F401  (the guard below must see it loaded)

        checks["refuse_confine_after_import"] = refused(lambda: confine_env(base / "late"))

        # F1 regression: the real client in a child process, with inherited caches set.
        child_env = {
            k: v for k, v in os.environ.items() if not k.upper().startswith(SCRUB_PREFIXES)
        }
        child_env.update(
            HF_HOME=str(base / "inherited-home"),
            HF_HUB_CACHE=str(base / "inherited-hub"),
            HUGGINGFACE_HUB_CACHE=str(base / "inherited-legacy"),
            HF_XET_CACHE=str(base / "inherited-xet"),
            HF_TOKEN="selftest-not-a-token",
        )
        proc = subprocess.run(
            [sys.executable, __file__, "client-check", "--base", str(base / "client")],
            env=child_env,
            capture_output=True,
            text=True,
            timeout=300,
        )
        try:
            child = json.loads(proc.stdout.strip().splitlines()[-1])
        except (IndexError, ValueError):
            child = {}
            print(proc.stdout[-2000:], proc.stderr[-2000:])
        want_dropped = {"HF_HOME", "HF_HUB_CACHE", "HUGGINGFACE_HUB_CACHE", "HF_XET_CACHE"}
        checks["client_scrubs_inherited"] = proc.returncode == 0 and want_dropped | {
            "HF_TOKEN"
        } <= set(child.get("dropped", []))
        checks["client_caches_private"] = child.get("confined") == [
            "HF_ASSETS_CACHE",
            "HF_HOME",
            "HF_HUB_CACHE",
            "HF_XET_CACHE",
            "HUGGINGFACE_HUB_CACHE",
        ]
        checks["client_fresh_body"] = (
            child.get("body_calls") == 1 and child.get("content") == "fresh body"
        )
        checks["client_no_token"] = child.get("authorization_sent") is False
        checks["client_no_network"] = child.get("connects") == 0

        # Fixtures: a fake remote, a cached copy equal to it, and a fake installed folder.
        remote = base / "remote"
        cached = base / "cached"
        for i, r in enumerate(rows):
            for folder in (remote, cached):
                p = folder / str(r["rel"])
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(f"file {i}".encode())
        expect = {rel: sha256(cached / rel) for rel in EXPECT}

        def fake_fetch(commit: str | None) -> Fetch:
            def fetch(
                repo: str, filename: str, revision: str | None, local_dir: pathlib.Path
            ) -> pathlib.Path:
                rel = next(
                    str(r["rel"]) for r in rows if r["filename"] == filename and r["repo"] == repo
                )
                dst = local_dir / filename
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(remote / rel, dst)
                meta = local_dir / ".cache" / "huggingface" / "download" / f"{filename}.metadata"
                meta.parent.mkdir(parents=True, exist_ok=True)
                meta.write_text(
                    f"{commit or revision or 'main-commit'}\netag\n0\n", encoding="utf-8"
                )
                return dst

            return fetch

        got = download(rows, root / "dl-ok", fake_fetch(None))
        models = base / "home" / ".avkit" / "models"
        models.mkdir(parents=True)
        (models / "unrelated.txt").write_text("never opened", encoding="utf-8")
        have = installed(rows, models)
        checks["read_scope"] = sorted(have) == sorted(str(r["rel"]) for r in rows)
        checks["absent_recorded"] = all(v == "absent" for v in have.values())
        files, problems = compare(rows, cached, got, have, expect)
        checks["all_equal_ok"] = problems == [] and all(f["download_equals_cached"] for f in files)
        checks["absent_not_problem"] = all(f["installed_equals_cached"] is None for f in files)

        fp = "kokoro-v1.0-onnx/onnx/model_fp16.onnx"
        (models / fp).parent.mkdir(parents=True)
        shutil.copyfile(cached / fp, models / fp)
        files, problems = compare(rows, cached, got, installed(rows, models), expect)
        checks["installed_equal_ok"] = (
            problems == []
            and next(f for f in files if f["rel"] == fp)["installed_equals_cached"] is True
        )
        (models / fp).write_bytes(b"other bytes")
        _, problems = compare(rows, cached, got, installed(rows, models), expect)
        checks["installed_differs_fails"] = any(
            p.startswith("S18: the installed " + fp) for p in problems
        )

        (remote / fp).write_bytes(b"changed upstream")
        got_changed = download(rows, root / "dl-changed", fake_fetch(None))
        _, problems = compare(rows, cached, got_changed, installed(rows, base / "nohome"), expect)
        checks["download_differs_fails"] = problems == [
            f"S18: the downloaded {fp} differs from Session 52's copy"
        ]

        (remote / fp).write_bytes((cached / fp).read_bytes())
        got_commit = download(rows, root / "dl-commit", fake_fetch("0" * 40))
        _, problems = compare(rows, cached, got_commit, installed(rows, base / "nohome"), expect)
        pinned = sum(1 for r in rows if r["revision"] is not None)
        checks["wrong_commit_fails"] = (
            len([p for p in problems if "not the pinned revision" in p]) == pinned
        )

        _, problems = compare(rows, cached, got, installed(rows, base / "nohome"), {fp: "0" * 64})
        checks["cached_unexpected_fails"] = problems == [
            f"S10: the cached {fp} is not the planned file"
        ]

        def wrong_place(
            repo: str, filename: str, revision: str | None, local_dir: pathlib.Path
        ) -> pathlib.Path:
            dst = local_dir / "elsewhere.bin"
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(b"x")
            return dst

        checks["refuse_wrong_landing"] = refused(
            lambda: download(rows, root / "dl-wrong", wrong_place)
        )

        home = pathlib.Path("C:/Users/someone")
        escaped = json.dumps({"p": str(home) + "\\x", "q": home.as_posix() + "/y"})
        checks["redact"] = redact(escaped, home) == '{"p": "<HOME>\\\\x", "q": "<HOME>/y"}'
        checks["redact_refuses_leftover"] = refused(lambda: redact("c:/users/SOMEONE/z", home))
    finally:
        shutil.rmtree(base, ignore_errors=True)
    passed = sum(checks.values())
    for name, ok in checks.items():
        print(("ok   " if ok else "FAIL ") + name)
    print(f"fresh-inputs selftest: {passed} of {len(checks)}")
    return 0 if passed == len(checks) else 1


def client_check(base: pathlib.Path) -> int:
    """F1's offline regression, run only by ``selftest`` in a child process.

    The inherited ``HF_HUB_CACHE`` and the legacy cache already hold the file, and the
    destination already holds a stale copy with matching metadata. With the network forbidden,
    the metadata call and the body transfer stubbed, ``hf_fetch`` must still call the body
    transfer once and land its bytes. Prints one JSON line.
    """
    import socket
    from unittest import mock

    inherited = [pathlib.Path(os.environ[k]) for k in ("HF_HUB_CACHE", "HUGGINGFACE_HUB_CACHE")]
    hf_home = base / "hf-home"
    dropped = confine_env(hf_home)
    from huggingface_hub import file_download as fd

    confined = verify_client(hf_home)
    repo, filename, commit, etag = "selftest/repo", "onnx/model.bin", "1" * 40, "e" * 64
    for cache in inherited:
        snap = cache / fd.repo_folder_name(repo_id=repo, repo_type="model") / "snapshots"
        cached = snap / commit / filename
        cached.parent.mkdir(parents=True, exist_ok=True)
        cached.write_bytes(b"cached body")
        refs = cached.parents[2] / "refs" / commit
        refs.parent.mkdir(parents=True, exist_ok=True)
        refs.write_text(commit, encoding="utf-8")
    local_dir = base / "dl"
    stale = local_dir / filename
    stale.parent.mkdir(parents=True, exist_ok=True)
    stale.write_bytes(b"stale local")
    fd.write_download_metadata(local_dir, filename, commit, etag)
    seen = {"body_calls": 0, "connects": 0, "authorization_sent": False}

    def metadata(**kwargs: object) -> tuple[object, ...]:
        headers = kwargs.get("headers") or {}
        if any(str(k).lower() == "authorization" for k in headers):  # type: ignore[union-attr]
            seen["authorization_sent"] = True
        if kwargs.get("token") is not False:
            seen["authorization_sent"] = True
        return ("https://example.invalid/never", etag, commit, 10, None, None)

    def body(**kwargs: object) -> None:
        seen["body_calls"] += 1
        pathlib.Path(str(kwargs["destination_path"])).write_bytes(b"fresh body")

    def no_connect(*args: object, **kwargs: object) -> None:
        seen["connects"] += 1
        raise OSError("network forbidden in client-check")

    with (
        mock.patch.object(fd, "_get_metadata_or_catch_error", metadata),
        mock.patch.object(fd, "_download_to_tmp_and_move", body),
        mock.patch.object(socket.socket, "connect", no_connect),
    ):
        got = hf_fetch(repo, filename, commit, local_dir)
    result = {
        "dropped": dropped,
        "confined": confined,
        **seen,
        "content": got.read_bytes().decode("utf-8", "replace"),
    }
    print(json.dumps(result))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--dest", type=pathlib.Path, required=True)
    r.add_argument("--out", type=pathlib.Path, required=True)
    sub.add_parser("selftest")
    c = sub.add_parser("client-check")
    c.add_argument("--base", type=pathlib.Path, required=True)
    args = parser.parse_args()
    try:
        if args.cmd == "client-check":
            return client_check(args.base)
        return run(args.dest, args.out) if args.cmd == "run" else selftest()
    except InputError as exc:
        print(f"refused: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
