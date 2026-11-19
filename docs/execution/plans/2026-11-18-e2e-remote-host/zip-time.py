"""Measured reproduction for Session 96 (AC-16, part 1): the DOS times git archive writes.

``git archive --format=zip`` stamps every entry with the commit time as a DOS time in this
PC's local zone. Windows PowerShell 5.1 ``Expand-Archive`` on a host in another zone reads
that DOS time as host-local time, so a host three hours behind sees every file three hours
in the future, and ``global-setup.ts`` refuses the build as stale.

Usage: ``zip-time.py COMMIT OUT_DIR HOST_UTC_OFFSET_HOURS``. It writes ``OUT_DIR/zip-time.zip``
(exclusive create, removed again at the end), prints ASCII facts, and exits 0 only when
every entry carries one DOS time within 2 s of this PC's local wall-clock reading of the
commit time and the zip comment is the full commit id; else 1; 2 on usage.
"""

from __future__ import annotations

import datetime
import subprocess
import sys
import zipfile
from pathlib import Path


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: zip-time.py COMMIT OUT_DIR HOST_UTC_OFFSET_HOURS")
        return 2
    try:
        sha = git("rev-parse", "--verify", argv[0] + "^{commit}")
        offset = float(argv[2])
    except (subprocess.CalledProcessError, ValueError) as exc:
        print("usage:", ascii(str(exc)))
        return 2
    out = Path(argv[1]) / "zip-time.zip"
    if out.exists():
        print("refused: exists", ascii(str(out)))
        return 2
    epoch = int(git("log", "-1", "--format=%ct", sha))
    subprocess.run(["git", "archive", "--format=zip", "-o", str(out), sha], check=True)
    try:
        with zipfile.ZipFile(out) as z:
            infos = z.infolist()
            comment = z.comment.decode("ascii", "replace")
            dos = sorted({i.date_time for i in infos})
    finally:
        out.unlink()
    utc = datetime.datetime.fromtimestamp(epoch, datetime.UTC).replace(tzinfo=None)
    local = datetime.datetime.fromtimestamp(epoch)
    newest = datetime.datetime(*dos[-1])
    gap = abs((newest - local).total_seconds())
    host = utc + datetime.timedelta(hours=offset)
    skew = int((newest - host).total_seconds())
    print("commit:", sha)
    print("entries:", len(infos), "distinct DOS times:", len(dos))
    print("zip comment is the commit id:", comment == sha)
    print("newest DOS time:", newest.isoformat(), "dev-pc local commit time:", local.isoformat())
    print("DOS time is dev-pc local time (within 2 s):", gap <= 2)
    print(f"seconds a host at UTC{offset:+g} reads the files after the commit:", skew)
    return 0 if gap <= 2 and comment == sha and len(dos) == 1 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
