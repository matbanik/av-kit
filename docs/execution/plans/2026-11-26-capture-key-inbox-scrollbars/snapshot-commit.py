"""Session 103 helper (task rows 1 and 10; D-1411): a commit object, on no ref. A copy of
Session 104's.

Copied unchanged in its logic from Session 100's
(2026-11-20-e2e-devpc-clipboard/snapshot-commit.py).

Copied unchanged in its logic from Session 98's (2026-11-20-e2e-clipboard-specs/snapshot-commit.py,
the newest ruff-clean copy), itself from Session 97's (its SNAPSHOT_NO_REF contract). Row 8 names
only this session's paths, so a parallel session's dirty files (Session 99) never reach the
second host.

    uv run --no-sync python <plan>/snapshot-commit.py --out <json> PATH...     # build the commit
    uv run --no-sync python <plan>/snapshot-commit.py --verify <json>          # bind it to the tree
    uv run --no-sync python <plan>/snapshot-commit.py --selftest <dir>         # temp-repo selftest

`tools/e2e_remote.py run COMMIT` archives a commit, and Session 100's work is uncommitted until
H2-5. This builds a commit object holding HEAD's tree plus the working-tree contents of the named
paths, and nothing else:

1. a temporary index (`GIT_INDEX_FILE` in a new temporary folder): `read-tree HEAD`, then
   `add -A -- PATH...` (a deleted path leaves the tree), then `write-tree`;
2. `commit-tree <tree> -p HEAD --no-gpg-sign`, with the author and committer taken from
   `git config user.name` and `user.email`. An address that is not a GitHub noreply address
   stops the run before any object is written.

It changes no ref, no index and no HEAD: `git status --porcelain=v1 -z`, then the bytes of
`.git/index` (read after the status), `git for-each-ref` and `HEAD`'s target are read before and
after, and any change is a failure (exit 1). Every git call runs with `GIT_OPTIONAL_LOCKS=0`
(expert pass M2), so the status never refreshes and rewrites the index itself; a changed index is
then another process's write (a parallel session), and the run stops naming it, with no retry.

Every scope path must differ between HEAD and the snapshot (M2): a path that did not change
would silently run HEAD's version on the second host, so the build refuses it, and `--verify`
reports it. The commit is reachable from no ref; `git gc` may prune it after the session, which
is fine, because the receipt keeps its id and the archive's zip comment names it.

`--out` is created exclusively (an existing file refuses) and holds the commit, tree, parent,
the scope paths with each blob id (or `null` for a deleted path) and the guard values.

`--verify <json>` re-reads the receipt and checks, against the current working tree: the commit
exists and its parent is still HEAD; `diff-tree -r --name-only HEAD <commit>` names only scope
paths and names every scope path; each scope path's blob equals
`git hash-object --path=<p> <p>` of the working file (with the same clean filters), or the path
is absent in both. Exit 0 when bound, 1 otherwise.

`--selftest <dir>` makes a throwaway repo under `<dir>` (which must not exist), commits two
files, edits both plus an out-of-scope file, builds a snapshot of the two, and checks: the
guards hold, the out-of-scope edit is not in the commit, `--verify` passes, an edit after the
build fails `--verify`, a deleted scope path leaves the tree, an existing `--out` refuses, a
non-noreply address refuses, an unchanged scope path refuses, and the guard's status leaves a
stat-dirty index's bytes as they were.

Exit 0 on success, 1 on a failed check or refusal, 2 on an argument problem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
NOREPLY = "@users.noreply.github.com"
MESSAGE = "capture-key-inbox-scrollbars snapshot for the second-host run (on no ref)"


class Refusal(Exception):
    pass


def git(repo: Path, *args: str, env: dict[str, str] | None = None) -> str:
    """Run git with GIT_OPTIONAL_LOCKS=0, so a read never rewrites the index (M2)."""
    r = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        env={**(os.environ if env is None else env), "GIT_OPTIONAL_LOCKS": "0"},
        check=False,
    )
    if r.returncode != 0:
        tail = r.stderr.decode("utf-8", "replace").strip().splitlines()
        raise Refusal(f"git {args[0]} exit {r.returncode}: {tail[-1] if tail else ''}")
    return r.stdout.decode("utf-8", "replace")


def index_sha(repo: Path) -> str:
    index = Path(git(repo, "rev-parse", "--absolute-git-dir").strip()) / "index"
    return hashlib.sha256(index.read_bytes()).hexdigest() if index.is_file() else "none"


def guard(repo: Path) -> dict[str, str]:
    """The status first, then the index bytes (M2 b), the refs and HEAD."""
    status = git(repo, "status", "--porcelain=v1", "-z")
    return {
        "status_sha256": hashlib.sha256(status.encode()).hexdigest(),
        "index_sha256": index_sha(repo),
        "refs_sha256": hashlib.sha256(git(repo, "for-each-ref").encode()).hexdigest(),
        "head": git(repo, "rev-parse", "HEAD").strip(),
        "head_ref": git(repo, "symbolic-ref", "-q", "HEAD").strip(),
    }


def identity(repo: Path) -> tuple[str, str]:
    name = git(repo, "config", "user.name").strip()
    email = git(repo, "config", "user.email").strip()
    if not name or not email.endswith(NOREPLY):
        raise Refusal("the configured git identity is not a GitHub noreply address")
    return name, email


def blob_of(repo: Path, commit: str, path: str) -> str | None:
    listed = git(repo, "ls-tree", commit, "--", path).strip()
    if not listed:
        return None
    return listed.split()[2]


def build(repo: Path, paths: list[str], out: Path) -> dict[str, object]:
    if not paths:
        raise Refusal("no scope paths")
    if out.exists():
        raise Refusal(f"--out exists: {out.name}")
    name, email = identity(repo)
    before = guard(repo)
    head = before["head"]
    with tempfile.TemporaryDirectory(prefix="cki-snapshot-") as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(tmp) / "index")}
        git(repo, "read-tree", head, env=env)
        git(repo, "add", "-A", "--", *paths, env=env)
        tree = git(repo, "write-tree", env=env).strip()
        env.update(
            GIT_AUTHOR_NAME=name,
            GIT_AUTHOR_EMAIL=email,
            GIT_COMMITTER_NAME=name,
            GIT_COMMITTER_EMAIL=email,
        )
        commit = git(
            repo, "commit-tree", tree, "-p", head, "--no-gpg-sign", "-m", MESSAGE, env=env
        ).strip()
    after = guard(repo)
    if after != before:
        changed = sorted(k for k in before if before[k] != after[k])
        if changed == ["index_sha256"]:
            raise Refusal(
                "INDEX_CHANGED: .git/index changed during the build while every read ran with"
                " GIT_OPTIONAL_LOCKS=0, so another process wrote it (a parallel session?);"
                " stop and record it, do not retry"
            )
        raise Refusal(f"the build changed {', '.join(changed)}")
    unchanged = [p for p in paths if blob_of(repo, commit, p) == blob_of(repo, head, p)]
    if unchanged:
        raise Refusal(f"UNCHANGED_SCOPE: the snapshot equals HEAD at {unchanged}")
    record: dict[str, object] = {
        "commit": commit,
        "tree": tree,
        "parent": head,
        "paths": {p: blob_of(repo, commit, p) for p in paths},
        "guard_before": before,
        "guard_after": after,
        "guards_equal": True,
    }
    with out.open("x", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(record, indent=2) + "\n")
    return record


def verify(repo: Path, receipt: Path) -> list[str]:
    record = json.loads(receipt.read_text(encoding="utf-8"))
    commit = str(record["commit"])
    paths = list(record["paths"])
    problems: list[str] = []
    if git(repo, "cat-file", "-t", commit).strip() != "commit":
        return [f"{commit[:12]} is not a commit"]
    parent = git(repo, "rev-parse", f"{commit}^").strip()
    head = git(repo, "rev-parse", "HEAD").strip()
    if parent != head:
        problems.append(f"parent {parent[:12]} is not HEAD {head[:12]}")
    changed = git(repo, "diff-tree", "-r", "--name-only", "--no-commit-id", head, commit)
    outside = sorted(set(changed.splitlines()) - set(paths))
    if outside:
        problems.append(f"changed outside the scope: {outside}")
    missing = sorted(set(paths) - set(changed.splitlines()))
    if missing:
        problems.append(f"scope paths equal to HEAD in the commit: {missing}")
    for path in paths:
        in_commit = blob_of(repo, commit, path)
        on_disk = (repo / path).is_file()
        if not on_disk:
            if in_commit is not None:
                problems.append(f"{path}: deleted on disk but in the commit")
            continue
        now = git(repo, "hash-object", f"--path={path}", "--", path).strip()
        if now != in_commit:
            problems.append(f"{path}: working file {now[:12]} != commit {str(in_commit)[:12]}")
    return problems


def selftest(root: Path) -> int:
    fails: list[str] = []

    def check(name: str, ok: bool) -> None:
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
        if not ok:
            fails.append(name)

    root.mkdir(parents=True)
    repo = root / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.name", "selftest")
    git(repo, "config", "user.email", "1+selftest" + NOREPLY)
    git(repo, "config", "commit.gpgsign", "false")
    for name in ("a.txt", "b.txt", "c.txt", "gone.txt", "same.txt"):
        (repo / name).write_bytes(f"{name} one\n".encode())
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    (repo / "a.txt").write_bytes(b"a two\n")
    (repo / "b.txt").write_bytes(b"b two\n")
    (repo / "c.txt").write_bytes(b"c two, out of scope\n")
    (repo / "gone.txt").unlink()
    (repo / "new.txt").write_bytes(b"new\n")
    stamp = (repo / "same.txt").stat().st_mtime + 120
    os.utime(repo / "same.txt", (stamp, stamp))
    index_before = index_sha(repo)
    guard(repo)
    check("the guard's status leaves a stat-dirty index's bytes", index_sha(repo) == index_before)
    scope = ["a.txt", "b.txt", "gone.txt", "new.txt"]
    receipt = root / "snap.json"
    record = build(repo, scope, receipt)
    commit = str(record["commit"])
    check("guards equal", record["guard_before"] == record["guard_after"])
    check(
        "the commit's parent is HEAD",
        git(repo, "rev-parse", f"{commit}^").strip() == record["parent"],
    )
    check("a.txt carries the edit", git(repo, "show", f"{commit}:a.txt") == "a two\n")
    check("c.txt keeps HEAD's content", git(repo, "show", f"{commit}:c.txt") == "c.txt one\n")
    check("gone.txt left the tree", blob_of(repo, commit, "gone.txt") is None)
    check("new.txt joined the tree", blob_of(repo, commit, "new.txt") is not None)
    check("no ref names the commit", commit not in git(repo, "for-each-ref"))
    check("the index still shows c.txt modified", " M c.txt" in git(repo, "status", "--porcelain"))
    check("verify passes", verify(repo, receipt) == [])
    (repo / "b.txt").write_bytes(b"b three\n")
    check("an edit after the build fails verify", any("b.txt" in p for p in verify(repo, receipt)))
    (repo / "b.txt").write_bytes(b"b two\n")
    check("verify passes again", verify(repo, receipt) == [])
    try:
        build(repo, scope, receipt)
        check("an existing --out refuses", False)
    except Refusal:
        check("an existing --out refuses", True)
    try:
        build(repo, [*scope, "same.txt"], root / "snap3.json")
        check("an unchanged scope path refuses", False)
    except Refusal as exc:
        check("an unchanged scope path refuses", "UNCHANGED_SCOPE" in str(exc))
    git(repo, "config", "user.email", "not-a-noreply-address")
    try:
        build(repo, scope, root / "snap2.json")
        check("a non-noreply address refuses", False)
    except Refusal:
        check("a non-noreply address refuses", not (root / "snap2.json").exists())
    print(f"snapshot-commit selftest: {len(fails)} failure(s)")
    return 1 if fails else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path, help="build; write the receipt to this new file")
    mode.add_argument("--verify", type=Path, help="check a receipt against the working tree")
    mode.add_argument("--selftest", type=Path, help="run the selftest in this new folder")
    parser.add_argument("paths", nargs="*", help="repo-relative scope paths (with --out)")
    args = parser.parse_args()
    try:
        if args.selftest is not None:
            return selftest(args.selftest)
        if args.verify is not None:
            problems = verify(REPO, args.verify)
            for p in problems:
                print(f"UNBOUND: {p}")
            print(f"snapshot-commit verify: {'bound' if not problems else 'NOT bound'}")
            return 1 if problems else 0
        record = build(REPO, [p.replace("\\", "/") for p in args.paths], args.out)
        print(
            f"snapshot-commit: commit {record['commit']} tree {record['tree']}"
            f" parent {str(record['parent'])[:12]}, {len(args.paths)} path(s), guards equal"
        )
        return 0
    except (Refusal, OSError, ValueError, KeyError) as exc:
        print(f"REFUSED: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
