# Zorivest copies

av-kit's own copies of the Zorivest files its canon cites by path. av-kit never reads
the Zorivest checkout; these files record where a pattern or value came from. Session 31b
amendment A-1 (decisions D-89 to D-91, Mat 2026-10-17) made them.

- Each file is the blob at the named commit, taken with `git show <commit>:<path>`, never
  from a working tree.
- `blob` is the git object id; `git hash-object <file>` in this repository gives the same id.
- `sha256` is over the LF content (the stored blob), so a CRLF checkout still matches.
- `plan_checks.py decouple` (Session 31b) checks both for every row.
- A copy is never edited. To take a newer version, replace the file and its row together.
- Only `globals.css` stays in this repository. The `gui-actions-index.md` and
  `05n-agent-connect.md` copies were removed on 2026-11-03, before the repository went
  public, because Zorivest's source is closed.

| File | Source path | Commit | Date | Blob | sha256 | Bytes |
|------|-------------|--------|------|------|--------|-------|
| `globals.css` | `ui/src/renderer/src/globals.css` | `61243baff0c141aee318257df2ad844e52e4e83c` | 2026-10-16 | `f12b4614baee11f07eb4512dde34727c1a5e6b81` | `cee4f7dea9d4cbe31b31a75e35c426042c963f6668474f90766d971fd154404b` | 14513 |

## Why each copy exists

| File | Cited by | Use |
|------|----------|-----|
| `globals.css` | `ui/tests/unit/queue-canon.test.ts` (AC-41.3 `PILL_TOKEN_SOURCE`); `docs/build-plan/10-queue-card-ui.md` §Status token table | The palette av-kit's queue pills were seeded from (D-90: the commit before Zorivest MEU-662, which equals what av-kit ships) |
